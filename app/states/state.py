import reflex as rx
from typing import TypedDict, Literal, cast
import asyncio
import logging
from openai import OpenAI, APIError
from app.states.settings_state import SettingsState


class Message(TypedDict):
    """Represents a single chat message with its role and content."""

    role: Literal["user", "assistant"]
    content: str


class StreamResponseResult:
    """Explicit result type for LLM responses."""
    def __init__(self, stream=None, error=None):
        self.stream = stream  # async generator or None
        self.error = error    # str or None
        self.is_stream = stream is not None


class ChatState(rx.State):
    """Manages the state of the chat application."""

    chats: dict[str, list[Message]] = {"new chat": []}
    current_chat_id: str = "new chat"
    is_streaming: bool = False

    @rx.var
    def chat_titles(self) -> list[str]:
        """A list of titles for all chat sessions."""
        return list(self.chats.keys())

    @rx.var
    def current_chat(self) -> list[Message]:
        """The list of messages in the current chat session."""
        return self.chats.get(self.current_chat_id, [])

    @rx.event
    def new_chat(self):
        """Creates a new chat session."""
        new_id = f"chat_{len(self.chats)}"
        self.chats[new_id] = []
        self.current_chat_id = new_id

    @rx.event
    def set_current_chat_id(self, chat_id: str):
        """Sets the current chat session.

        Args:
            chat_id: The ID of the chat to set as current.
        """
        self.current_chat_id = chat_id

    async def _stream_openai_compatible_response(
        self, client: OpenAI, model: str, messages: list[Message]
    ):
        try:
            stream = await asyncio.to_thread(
                client.chat.completions.create,
                model=model,
                messages=messages,
                stream=True,
            )
            assistant_message_content = ""
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    char = chunk.choices[0].delta.content
                    assistant_message_content += char
                    async with self:
                        self.chats[self.current_chat_id][-1]["content"] = (
                            assistant_message_content
                        )
                    yield
        except APIError as e:
            error_message = f"API Error: {e.code} - {e.message}"
            logging.exception(error_message)
            async with self:
                self.chats[self.current_chat_id][-1]["content"] = error_message

    async def _process_and_stream_response(self):
        """Helper to process and stream the response from the LLM.

        Returns:
            StreamResponseResult: Contains either an async generator (stream) or an error string.
        """
        settings = await self.get_state(SettingsState)
        provider = settings.selected_provider
        model_id = settings.selected_model_id
        api_key = settings.api_keys.get(provider)
        ollama_url = settings.api_keys.get("ollama", "http://localhost:11434")

        if not provider or not model_id:
            return StreamResponseResult(error="No model selected. Please select a model in settings.")

        base_urls = {
            "openai": None, "groq": "https://api.groq.com/openai/v1", "deepseek": "https://api.deepseek.com",
            "openrouter": "https://openrouter.ai/api/v1", "moonshot": "https://api.moonshot.cn/v1",
            "ollama": ollama_url.strip("/") + "/v1",
        }
        openai_compatible_providers = list(base_urls.keys())
        messages_to_send = self.chats[self.current_chat_id][:-1]

        if provider in openai_compatible_providers:
            if not api_key and provider not in ["openrouter", "ollama"]:
                return StreamResponseResult(error=f"API key for {provider} not set.")

            client = OpenAI(api_key=api_key, base_url=base_urls.get(provider))
            stream = self._stream_openai_compatible_response(
                client, model_id, cast(list[Message], messages_to_send)
            )
            return StreamResponseResult(stream=stream)
        else:
            return StreamResponseResult(error=f"Provider '{provider}' is not yet supported for chat.")

    @rx.event(background=True)
    async def handle_submit(self, form_data: dict):
        """Handles the submission of a new message."""
        message_text = form_data.get("message", "").strip()
        if not message_text:
            return

        async with self:
            user_message: Message = {"role": "user", "content": message_text}
            self.chats[self.current_chat_id].append(user_message)
            if (
                len(self.chats[self.current_chat_id]) == 1
                and self.current_chat_id.startswith("new chat")
            ):
                new_title = message_text[:20]
                self.chats[new_title] = self.chats.pop(self.current_chat_id)
                self.current_chat_id = new_title

            self.is_streaming = True
            assistant_message: Message = {"role": "assistant", "content": ""}
            self.chats[self.current_chat_id].append(assistant_message)
            yield

        try:
            result = await self._process_and_stream_response()
            if result.is_stream:
                async for _ in result.stream:
                    yield
            else:
                async with self:
                    self.chats[self.current_chat_id][-1]["content"] = result.error
        finally:
            async with self:
                self.is_streaming = False
