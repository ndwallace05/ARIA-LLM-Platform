import reflex as rx
from app.states.state import ChatState
from app.states.settings_state import SettingsState
from typing import TypedDict, Literal


class Message(TypedDict):
    role: Literal["user", "assistant"]
    content: str


def message_bubble(message: Message) -> rx.Component:
    """Creates a message bubble component for a single message.

    Args:
        message: A dictionary containing the message role and content.

    Returns:
        A reflex component representing the message bubble.
    """
    is_user = message["role"] == "user"
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.image(
                    src=rx.cond(
                        is_user,
                        "https://api.dicebear.com/9.x/initials/svg?seed=User",
                        "/favicon.ico",
                    ),
                    class_name="size-8 rounded-full",
                ),
                class_name="flex items-start",
            ),
            rx.el.div(
                rx.markdown(
                    message["content"],
                    component_map={
                        "code": lambda text: rx.el.code(
                            text,
                            class_name="text-sm font-mono bg-gray-100 px-1 py-0.5 rounded",
                        )
                    },
                    class_name="p-4 rounded-xl max-w-2xl",
                ),
                class_name=rx.cond(
                    is_user, "bg-white border border-gray-200", "bg-violet-50"
                ),
            ),
            class_name="flex gap-3",
        ),
        class_name=rx.cond(is_user, "justify-end", "justify-start"),
        width="100%",
    )




def chat_header() -> rx.Component:
    """Creates the header component for the chat interface.

    The header displays the currently selected model.

    Returns:
        A reflex component representing the chat header.
    """
    return rx.el.div(
        rx.el.div(
            rx.el.p("Model:", class_name="text-sm text-gray-500"),
            rx.el.p(
                rx.cond(
                    SettingsState.selected_model,
                    SettingsState.selected_model,
                    "No model selected",
                ),
                class_name="text-sm font-medium text-gray-900",
            ),
            class_name="flex items-center gap-2",
        ),
        class_name="w-full p-4 border-b border-gray-200 bg-gray-50/50 flex justify-center",
    )


def chat_interface() -> rx.Component:
    """Creates the main chat interface component.

    This component includes the chat header, message display area,
    and the message input form.

    Returns:
        A reflex component representing the chat interface.
    """
    return rx.el.div(
        rx.el.div(
            chat_header(),
            rx.el.div(
                rx.foreach(ChatState.current_chat, message_bubble),
                class_name="flex flex-col gap-6 w-full px-4 md:px-12 py-8 overflow-y-auto flex-grow",
            ),
            rx.el.div(
                rx.el.form(
                    rx.el.input(
                        name="message",
                        placeholder="Type your message...",
                        class_name="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:outline-none focus:border-violet-400",
                        disabled=ChatState.is_streaming,
                    ),
                    rx.el.button(
                        rx.icon("send", size=20),
                        type="submit",
                        class_name="absolute right-3 top-1/2 -translate-y-1/2 p-2 rounded-lg bg-violet-500 text-white hover:bg-violet-600 disabled:opacity-50",
                        disabled=ChatState.is_streaming
                        | (SettingsState.selected_model == ""),
                    ),
                    on_submit=ChatState.handle_submit,
                    reset_on_submit=True,
                    width="100%",
                    class_name="relative",
                ),
                class_name="w-full max-w-3xl p-4 border-t border-gray-200 bg-white",
            ),
            class_name="flex flex-col items-center h-full w-full bg-white",
        ),
        rx.cond(
            SettingsState.show_settings,
            rx.el.div(
                class_name="fixed inset-0 bg-black/50 z-40",
                on_click=SettingsState.toggle_settings,
            ),
        ),
    )