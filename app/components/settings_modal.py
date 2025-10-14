import reflex as rx
from app.states.settings_state import SettingsState


def model_list(provider: str) -> rx.Component:
    """Component to display the list of models for a provider."""
    models_for_provider = SettingsState.filtered_models.get(provider, [])

    def model_row(model: str):
        model_id = f"{provider}:{model}"
        is_selected = SettingsState.selected_model == model_id
        return rx.el.div(
            rx.el.button(
                model,
                on_click=lambda: SettingsState.select_model(model_id),
                class_name=rx.cond(
                    is_selected,
                    "w-full text-left px-3 py-1.5 text-sm font-medium text-violet-700 bg-violet-100",
                    "w-full text-left px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100",
                ),
            ),
            class_name="w-full",
        )

    return rx.el.div(
        rx.el.input(
            placeholder="Search models...",
            on_change=lambda value: SettingsState.set_model_search_term(
                provider, value
            ),
            class_name="w-full px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-1 focus:ring-violet-400 mb-2",
        ),
        rx.el.div(
            rx.cond(
                models_for_provider.length() > 0,
                rx.foreach(models_for_provider, model_row),
                rx.el.div(
                    "No models found or yet to be loaded.",
                    class_name="px-3 py-2 text-sm text-gray-500",
                ),
            ),
            class_name="max-h-48 overflow-y-auto border rounded-lg bg-gray-50/50",
        ),
        class_name="mt-2",
    )


def provider_input(provider: str) -> rx.Component:
    is_expanded = SettingsState.expanded_providers.contains(provider)
    is_loading = SettingsState.loading_models.contains(provider)
    has_key_or_url = (SettingsState.api_keys[provider] != "") | (provider == "ollama")
    error_message = SettingsState.error_messages.get(provider, "")
    return rx.el.div(
        rx.el.label(
            rx.cond(
                provider == "ollama", "Ollama Base URL", f"{provider.title()} API Key"
            ),
            class_name="block text-sm font-medium text-gray-700 mb-1",
        ),
        rx.el.div(
            rx.el.input(
                placeholder=rx.cond(
                    provider == "ollama",
                    "http://localhost:11434",
                    f"Enter your {provider.title()} API Key",
                ),
                default_value=SettingsState.api_keys[provider],
                on_change=lambda value: SettingsState.set_api_key(
                    provider, value
                ).debounce(500),
                type=rx.cond(provider == "ollama", "text", "password"),
                class_name="w-full px-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-1 focus:ring-violet-500",
            ),
            rx.cond(
                has_key_or_url,
                rx.el.div(
                    rx.el.button(
                        rx.icon(
                            tag=rx.cond(is_expanded, "chevron-up", "chevron-down"),
                            size=16,
                        ),
                        on_click=lambda: SettingsState.toggle_provider_expansion(
                            provider
                        ),
                        class_name="p-1 text-gray-500 hover:bg-gray-100 rounded",
                        disabled=is_loading,
                    ),
                    rx.el.button(
                        rx.icon(
                            tag="refresh-cw",
                            size=14,
                            class_name=rx.cond(is_loading, "animate-spin", ""),
                        ),
                        on_click=lambda: SettingsState.refresh_models(provider),
                        class_name="p-1 text-gray-500 hover:bg-gray-100 rounded",
                        disabled=is_loading,
                    ),
                    class_name="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1 bg-white pl-2",
                ),
                rx.fragment(),
            ),
            class_name="relative w-full",
        ),
        rx.cond(
            error_message != "",
            rx.el.p(error_message, class_name="text-sm text-red-500 mt-1"),
            rx.fragment(),
        ),
        rx.cond(is_expanded & has_key_or_url, model_list(provider), rx.fragment()),
        class_name="w-full",
    )


def settings_modal() -> rx.Component:
    """The settings modal component."""
    return rx.cond(
        SettingsState.show_settings,
        rx.el.div(
            rx.el.div(
                rx.el.h2("Settings", class_name="text-lg font-semibold text-gray-900"),
                rx.el.p(
                    "Manage your API keys and other settings.",
                    class_name="text-sm text-gray-500",
                ),
                class_name="border-b border-gray-200 pb-4",
            ),
            rx.el.div(
                rx.el.h3(
                    "LLM Providers",
                    class_name="text-md font-semibold text-gray-800 mb-2",
                ),
                rx.el.div(
                    rx.foreach(SettingsState.api_keys.keys(), provider_input),
                    class_name="flex flex-col gap-4",
                ),
                class_name="py-4 max-h-[60vh] overflow-y-auto pr-2",
            ),
            rx.el.div(
                rx.el.button(
                    "Close",
                    on_click=SettingsState.toggle_settings,
                    class_name="px-4 py-2 rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200 font-medium",
                ),
                class_name="flex justify-end pt-4 border-t border-gray-200",
            ),
            class_name="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[90vw] max-w-lg bg-white p-6 rounded-2xl shadow-lg z-50",
        ),
    )