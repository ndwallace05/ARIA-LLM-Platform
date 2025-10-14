import reflex as rx
import httpx
from openai import OpenAI, AuthenticationError
import google.generativeai as genai
import asyncio
import logging


class SettingsState(rx.State):
    """Manages the state for the settings modal."""

    show_settings: bool = False
    api_keys: dict[str, str] = {
        "openai": "",
        "anthropic": "",
        "gemini": "",
        "groq": "",
        "deepseek": "",
        "moonshot": "",
        "openrouter": "",
        "ollama": "",
    }
    models: dict[str, list[str]] = {}
    expanded_providers: set[str] = set()
    model_search_terms: dict[str, str] = {}
    loading_models: set[str] = set()
    error_messages: dict[str, str] = {}
    selected_model: str = ""

    @rx.var
    def selected_provider(self) -> str:
        """The provider of the currently selected model.

        Returns:
            The name of the provider.
        """
        if ":" in self.selected_model:
            return self.selected_model.split(":")[0]
        return ""

    @rx.var
    def selected_model_id(self) -> str:
        """The ID of the currently selected model.

        Returns:
            The ID of the model.
        """
        if ":" in self.selected_model:
            return self.selected_model.split(":", 1)[1]
        return ""

    async def _fetch_openai_compatible_models(
        self, provider: str, base_url: str | None = None
    ):
        api_key = self.api_keys.get(provider)
        if not api_key:
            return [], None
        try:
            client = OpenAI(api_key=api_key, base_url=base_url)
            models_response = await asyncio.to_thread(client.models.list)
            return sorted([model.id for model in models_response.data]), None
        except AuthenticationError as e:
            logging.exception(f"Authentication error for {provider}: {e}")
            return [], "Invalid API Key."
        except Exception as e:
            logging.exception(
                f"Error fetching openai-compatible models for {provider}: {e}"
            )
            return [], f"Error: {e}"

    async def _fetch_gemini_models(self):
        api_key = self.api_keys.get("gemini")
        if not api_key:
            return [], None
        try:
            genai.configure(api_key=api_key)
            models_response = await asyncio.to_thread(genai.list_models)
            models = sorted(
                [
                    m.name.replace("models/", "")
                    for m in models_response
                    if "generateContent" in m.supported_generation_methods
                ]
            )
            return models, None
        except Exception as e:
            logging.exception(f"Error fetching gemini models: {e}")
            return [], f"Error: {e}"

    async def _fetch_openrouter_models(self):
        api_key = self.api_keys.get("openrouter")
        try:
            async with httpx.AsyncClient() as client:
                headers = {}
                if api_key:
                    headers["Authorization"] = f"Bearer {api_key}"
                response = await client.get(
                    "https://openrouter.ai/api/v1/models", headers=headers
                )
                response.raise_for_status()
                models_data = response.json()["data"]
                return sorted([model["id"] for model in models_data]), None
        except httpx.HTTPStatusError as e:
            logging.exception(f"HTTPStatusError fetching openrouter models: {e}")
            return [], f"Error: {e.response.status_code}"
        except Exception as e:
            logging.exception(f"Error fetching openrouter models: {e}")
            return [], f"Error: {e}"

    async def _fetch_moonshot_models(self):
        api_key = self.api_keys.get("moonshot")
        if not api_key:
            return [], None
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {api_key}"}
                response = await client.get(
                    "https://api.moonshot.cn/v1/models", headers=headers
                )
                response.raise_for_status()
                models_data = response.json()["data"]
                return sorted([model["id"] for model in models_data]), None
        except Exception as e:
            logging.exception(f"Error fetching moonshot models: {e}")
            return [], f"Error: {e}"

    async def _fetch_ollama_models(self):
        base_url = self.api_keys.get("ollama", "http://localhost:11434").strip("/")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{base_url}/api/tags")
                response.raise_for_status()
                models_data = response.json().get("models", [])
                return sorted([model["name"] for model in models_data]), None
        except (httpx.ConnectError, httpx.RequestError) as e:
            logging.exception(f"Connection error fetching ollama models: {e}")
            return [], "Connection failed. Is Ollama running?"
        except Exception as e:
            logging.exception(f"Error fetching ollama models: {e}")
            return [], f"Error: {e}"

    @rx.event
    def toggle_settings(self):
        """Toggles the visibility of the settings modal."""
        self.show_settings = not self.show_settings

    @rx.event
    def set_api_key(self, provider: str, key: str):
        """Sets the API key for a given provider.

        Args:
            provider: The name of the provider.
            key: The API key.
        """
        self.api_keys[provider] = key
        self.error_messages.pop(provider, None)
        if not key:
            self.expanded_providers.discard(provider)
            if provider in self.models:
                del self.models[provider]
            if self.selected_provider == provider:
                self.selected_model = ""
        else:
            return SettingsState.refresh_models(provider)

    @rx.event
    def toggle_provider_expansion(self, provider: str):
        """Toggles the expansion of a provider's model list.

        Args:
            provider: The name of the provider to expand or collapse.
        """
        if provider in self.expanded_providers:
            self.expanded_providers.remove(provider)
        else:
            self.expanded_providers.add(provider)
            if provider not in self.models and (
                self.api_keys.get(provider) or provider == "ollama"
            ):
                return SettingsState.refresh_models(provider)

    @rx.event(background=True)
    async def refresh_models(self, provider: str):
        """Refreshes the list of models for a given provider.

        This is an async background task that fetches the models from the
        provider's API.

        Args:
            provider: The name of the provider to refresh models for.
        """
        async with self:
            if provider in self.loading_models:
                return
            self.loading_models.add(provider)
            self.expanded_providers.add(provider)
            self.error_messages.pop(provider, None)
            self.models.pop(provider, None)

        fetched_models, error = [], None
        if provider == "openai":
            fetched_models, error = await self._fetch_openai_compatible_models("openai")
        elif provider == "groq":
            fetched_models, error = await self._fetch_openai_compatible_models(
                "groq", "https://api.groq.com/openai/v1"
            )
        elif provider == "deepseek":
            fetched_models, error = await self._fetch_openai_compatible_models(
                "deepseek", "https://api.deepseek.com"
            )
        elif provider == "gemini":
            fetched_models, error = await self._fetch_gemini_models()
        elif provider == "openrouter":
            fetched_models, error = await self._fetch_openrouter_models()
        elif provider == "moonshot":
            fetched_models, error = await self._fetch_moonshot_models()
        elif provider == "ollama":
            fetched_models, error = await self._fetch_ollama_models()
        elif provider == "anthropic":
            fetched_models, error = [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
            ], None

        async with self:
            if error:
                self.error_messages[provider] = error
            elif fetched_models:
                self.models[provider] = fetched_models
            self.loading_models.remove(provider)

    @rx.event
    def set_model_search_term(self, provider: str, term: str):
        """Sets the search term for a provider's model list.

        Args:
            provider: The name of the provider.
            term: The search term.
        """
        self.model_search_terms[provider] = term

    @rx.var
    def filtered_models(self) -> dict[str, list[str]]:
        """A dictionary of models filtered by the search term.

        Returns:
            A dictionary where keys are provider names and values are
            lists of filtered model names.
        """
        filtered = {}
        for provider, models_list in self.models.items():
            search_term = self.model_search_terms.get(provider, "").lower()
            if not search_term:
                filtered[provider] = models_list
            else:
                filtered[provider] = [
                    model for model in models_list if search_term in model.lower()
                ]
        return filtered

    @rx.event
    def select_model(self, model_id: str):
        """Selects a model.

        Args:
            model_id: The ID of the model to select.
        """
        self.selected_model = model_id
