import reflex as rx
from app.states.state import ChatState
from app.states.settings_state import SettingsState
from app.states.mcp_state import McpState
from app.components.settings_modal import settings_modal
from app.components.mcp_modal import mcp_modal


def sidebar_chat_item(chat_id: str) -> rx.Component:
    """A sidebar item for a single chat session."""
    return rx.el.button(
        rx.el.div(
            rx.icon("message-circle", size=16, class_name="mr-2 shrink-0"),
            rx.el.p(chat_id.replace("_", " ").title(), class_name="truncate"),
            class_name="flex items-center",
        ),
        on_click=lambda: ChatState.set_current_chat_id(chat_id),
        class_name=rx.cond(
            ChatState.current_chat_id == chat_id,
            "w-full text-left px-3 py-2 rounded-lg bg-gray-200 text-gray-800 font-medium",
            "w-full text-left px-3 py-2 rounded-lg hover:bg-gray-100 text-gray-600",
        ),
    )


def sidebar() -> rx.Component:
    """The sidebar component for navigation and chat history."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("bot-message-square", size=24, class_name="text-violet-500"),
                rx.el.h2("DeepChat", class_name="text-xl font-bold text-gray-800"),
                class_name="flex items-center gap-2 p-4 border-b border-gray-200",
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("plus", size=16, class_name="mr-2"),
                    "New Chat",
                    on_click=ChatState.new_chat,
                    class_name="flex items-center justify-center w-full px-3 py-2 rounded-lg bg-violet-500 text-white hover:bg-violet-600 font-medium",
                ),
                class_name="p-4",
            ),
            rx.el.div(
                rx.el.h3(
                    "Conversations",
                    class_name="px-4 text-sm font-semibold text-gray-500 mb-2",
                ),
                rx.el.div(
                    rx.foreach(ChatState.chat_titles, sidebar_chat_item),
                    class_name="flex flex-col gap-1 px-4",
                ),
                class_name="flex-grow overflow-y-auto",
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("cog", size=16, class_name="mr-2"),
                    "MCP Services",
                    on_click=McpState.toggle_mcp_modal,
                    class_name="flex items-center w-full px-3 py-2 rounded-lg hover:bg-gray-100 text-gray-600",
                ),
                rx.el.button(
                    rx.icon("settings", size=16, class_name="mr-2"),
                    "Settings",
                    on_click=SettingsState.toggle_settings,
                    class_name="flex items-center w-full px-3 py-2 rounded-lg hover:bg-gray-100 text-gray-600",
                ),
                class_name="p-4 border-t border-gray-200 flex flex-col gap-2",
            ),
            class_name="flex flex-col h-full",
        ),
        settings_modal(),
        mcp_modal(),
        class_name="w-72 h-screen bg-gray-50 border-r border-gray-200 relative",
    )