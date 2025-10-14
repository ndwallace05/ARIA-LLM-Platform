import reflex as rx
import httpx
from openai import OpenAI, AuthenticationError
import google.generativeai as genai
import asyncio
import logging
from typing import cast


class SettingsState(rx.State):
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
        if ":" in self.selected_model:
            return self.selected_model.split(":")[0]
        return ""

    @rx.var
    def selected_model_id(self) -> str:
        if ":" in self.selected_model:
            return self.selected_model.split(":", 1)[1]
        return ""

    async def _fetch_openai_compatible_models(
        self, provider: str, base_url: str | None = None
    ):
        api_key = self.api_keys.get(provider)
        if not api_key:
            return []
        try:
            client = OpenAI(api_key=api_key, base_url=base_url)
            models_response = await asyncio.to_thread(client.models.list)
            return sorted([model.id for model in models_response.data])
        except AuthenticationError as e:
            logging.exception(f"Authentication error for {provider}: {e}")
            async with self:
                self.error_messages[provider] = "Invalid API Key."
            return []
        except Exception as e:
            logging.exception(
                f"Error fetching openai-compatible models for {provider}: {e}"
            )
            async with self:
                self.error_messages[provider] = f"Error: {e}"
            return []

    async def _fetch_gemini_models(self):
        api_key = self.api_keys.get("gemini")
        if not api_key:
            return []
        try:
            genai.configure(api_key=api_key)
            models_response = await asyncio.to_thread(genai.list_models)
            return sorted(
                [
                    m.name.replace("models/", "")
                    for m in models_response
                    if "generateContent" in m.supported_generation_methods
                ]
            )
        except Exception as e:
            logging.exception(f"Error fetching gemini models: {e}")
            async with self:
                self.error_messages["gemini"] = f"Error: {e}"
            return []

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
                return sorted([model["id"] for model in models_data])
        except httpx.HTTPStatusError as e:
            logging.exception(f"HTTPStatusError fetching openrouter models: {e}")
            async with self:
                self.error_messages["openrouter"] = f"Error: {e.response.status_code}"
            return []
        except Exception as e:
            logging.exception(f"Error fetching openrouter models: {e}")
            async with self:
                self.error_messages["openrouter"] = f"Error: {e}"
            return []

    async def _fetch_moonshot_models(self):
        api_key = self.api_keys.get("moonshot")
        if not api_key:
            return []
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {api_key}"}
                response = await client.get(
                    "https://api.moonshot.cn/v1/models", headers=headers
                )
                response.raise_for_status()
                models_data = response.json()["data"]
                return sorted([model["id"] for model in models_data])
        except Exception as e:
            logging.exception(f"Error fetching moonshot models: {e}")
            async with self:
                self.error_messages["moonshot"] = f"Error: {e}"
            return []

    async def _fetch_ollama_models(self):
        base_url = self.api_keys.get("ollama", "http://localhost:11434").strip("/")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{base_url}/api/tags")
                response.raise_for_status()
                models_data = response.json().get("models", [])
                return sorted([model["name"] for model in models_data])
        except (httpx.ConnectError, httpx.RequestError) as e:
            logging.exception(f"Connection error fetching ollama models: {e}")
            async with self:
                self.error_messages["ollama"] = "Connection failed. Is Ollama running?"
            return []
        except Exception as e:
            logging.exception(f"Error fetching ollama models: {e}")
            async with self:
                self.error_messages["ollama"] = f"Error: {e}"
            return []

    @rx.event
    def toggle_settings(self):
        self.show_settings = not self.show_settings

    @rx.event
    def set_api_key(self, provider: str, key: str):
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
        async with self:
            if provider in self.loading_models:
                return
            self.loading_models.add(provider)
            self.expanded_providers.add(provider)
            self.error_messages.pop(provider, None)
            self.models.pop(provider, None)
        fetched_models = []
        if provider == "openai":
            fetched_models = await self._fetch_openai_compatible_models("openai")
        elif provider == "groq":
            fetched_models = await self._fetch_openai_compatible_models(
                "groq", "https://api.groq.com/openai/v1"
            )
        elif provider == "deepseek":
            fetched_models = await self._fetch_openai_compatible_models(
                "deepseek", "https://api.deepseek.com"
            )
        elif provider == "gemini":
            fetched_models = await self._fetch_gemini_models()
        elif provider == "openrouter":
            fetched_models = await self._fetch_openrouter_models()
        elif provider == "moonshot":
            fetched_models = await self._fetch_moonshot_models()
        elif provider == "ollama":
            fetched_models = await self._fetch_ollama_models()
        elif provider == "anthropic":
            fetched_models = [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
            ]
        async with self:
            if fetched_models:
                self.models[provider] = fetched_models
            self.loading_models.remove(provider)

    @rx.event
    def set_model_search_term(self, provider: str, term: str):
        self.model_search_terms[provider] = term

    @rx.var
    def filtered_models(self) -> dict[str, list[str]]:
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
        self.selected_model = model_id