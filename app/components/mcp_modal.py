import reflex as rx
from app.states.mcp_state import McpState, McpServer
from typing import cast


def mcp_server_card(item: list) -> rx.Component:
    """Creates a card component for a single MCP server.

    The card displays the server's name, description, and repository link,
    along with buttons to start, stop, or install the server.

    Args:
        item: A list containing the server name and the McpServer object.

    Returns:
        A reflex component representing the server card.
    """
    server_name = cast(str, item[0])
    server = cast(McpServer, item[1])
    return rx.el.div(
        rx.el.div(
            rx.el.h4(server["name"], class_name="font-semibold text-gray-800"),
            rx.el.p(server["description"], class_name="text-sm text-gray-600 mt-1"),
            rx.el.a(
                "View on GitHub",
                rx.icon("external-link", size=14, class_name="mr-1"),
                href=server["repo"],
                target="_blank",
                class_name="text-sm text-violet-600 hover:underline mt-2 flex items-center gap-1",
                rel="noopener noreferrer",
            ),
            class_name="flex-grow",
        ),
        rx.el.div(
            rx.cond(
                server["installed"],
                rx.el.div(
                    rx.el.button(
                        rx.cond(server["running"], "Stop", "Start"),
                        on_click=lambda: McpState.toggle_server_running(server_name),
                        class_name=rx.cond(
                            server["running"],
                            "px-3 py-1.5 text-sm rounded-md bg-red-100 text-red-700 hover:bg-red-200",
                            "px-3 py-1.5 text-sm rounded-md bg-green-100 text-green-700 hover:bg-green-200",
                        ),
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.button(
                    "Install",
                    on_click=lambda: McpState.install_server(server_name),
                    class_name="px-3 py-1.5 text-sm rounded-md bg-blue-500 text-white hover:bg-blue-600",
                ),
            ),
            class_name="flex items-center",
        ),
        class_name="flex justify-between items-center p-4 border border-gray-200 rounded-lg bg-white",
    )


def custom_mcp_server_form() -> rx.Component:
    """Creates a form for adding a custom MCP server.

    The form includes fields for the server name, description, and
    repository URL, along with buttons to cancel or add the server.

    Returns:
        A reflex component representing the custom server form.
    """
    return rx.el.div(
        rx.el.h3(
            "Add Custom MCP Server",
            class_name="text-md font-semibold text-gray-800 mb-3",
        ),
        rx.el.div(
            rx.el.label(
                "Server Name", class_name="block text-sm font-medium text-gray-700 mb-1"
            ),
            rx.el.input(
                placeholder="My Custom Server",
                on_change=McpState.set_custom_server_name,
                class_name="w-full px-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-1 focus:ring-violet-500",
            ),
            class_name="mb-3",
        ),
        rx.el.div(
            rx.el.label(
                "Description", class_name="block text-sm font-medium text-gray-700 mb-1"
            ),
            rx.el.input(
                placeholder="A brief description of the server.",
                on_change=McpState.set_custom_server_description,
                class_name="w-full px-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-1 focus:ring-violet-500",
            ),
            class_name="mb-3",
        ),
        rx.el.div(
            rx.el.label(
                "Repository URL (Optional)",
                class_name="block text-sm font-medium text-gray-700 mb-1",
            ),
            rx.el.input(
                placeholder="https://github.com/user/repo",
                on_change=McpState.set_custom_server_repo,
                class_name="w-full px-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-1 focus:ring-violet-500",
            ),
            class_name="mb-4",
        ),
        rx.cond(
            McpState.custom_server_form_error != "",
            rx.el.p(
                McpState.custom_server_form_error,
                class_name="text-sm text-red-500 mb-3",
            ),
        ),
        rx.el.div(
            rx.el.button(
                "Cancel",
                on_click=McpState.toggle_custom_server_form,
                class_name="px-4 py-2 rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200 font-medium",
            ),
            rx.el.button(
                "Add Server",
                on_click=McpState.add_custom_server,
                class_name="px-4 py-2 rounded-lg bg-violet-500 text-white hover:bg-violet-600 font-medium",
            ),
            class_name="flex justify-end gap-3",
        ),
        class_name="p-4 border border-gray-200 rounded-lg bg-white mt-4",
    )


def mcp_modal() -> rx.Component:
    """Creates the modal component for managing MCP services.

    The modal displays a list of available MCP servers, allows users
    to add custom servers, and provides a way to close the modal.

    Returns:
        A reflex component representing the MCP services modal.
    """
    return rx.cond(
        McpState.show_mcp_modal,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "MCP Services",
                            class_name="text-lg font-semibold text-gray-900",
                        ),
                        rx.el.p(
                            "Manage Model Context Protocol services for extended capabilities.",
                            class_name="text-sm text-gray-500",
                        ),
                    ),
                    class_name="border-b border-gray-200 pb-4",
                ),
                rx.el.div(
                    rx.foreach(McpState.servers.items(), mcp_server_card),
                    class_name="flex flex-col gap-4 py-4 max-h-[60vh] overflow-y-auto pr-2",
                ),
                rx.cond(
                    McpState.show_custom_server_form,
                    custom_mcp_server_form(),
                    rx.el.div(
                        rx.el.a(
                            rx.icon("search", size=16, class_name="mr-2"),
                            "Browse mcp.so",
                            href="https://mcp.so/servers",
                            target="_blank",
                            class_name="flex-1 text-center px-4 py-2 rounded-lg border-2 border-dashed border-gray-300 text-gray-600 hover:bg-gray-100 hover:border-gray-400 font-medium flex items-center justify-center",
                            rel="noopener noreferrer",
                        ),
                        rx.el.button(
                            rx.icon("plus", size=16, class_name="mr-2"),
                            "Add Custom Server",
                            on_click=McpState.toggle_custom_server_form,
                            class_name="flex-1 text-center px-4 py-2 rounded-lg border-2 border-dashed border-gray-300 text-gray-600 hover:bg-gray-100 hover:border-gray-400 font-medium flex items-center justify-center",
                        ),
                        class_name="py-2 flex gap-3",
                    ),
                ),
                rx.el.div(
                    rx.el.button(
                        "Close",
                        on_click=McpState.toggle_mcp_modal,
                        class_name="px-4 py-2 rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200 font-medium",
                    ),
                    class_name="flex justify-end pt-4 border-t border-gray-200",
                ),
                class_name="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[90vw] max-w-2xl bg-gray-50 p-6 rounded-2xl shadow-lg z-50",
            ),
            rx.el.div(
                class_name="fixed inset-0 bg-black/50 z-40",
                on_click=McpState.toggle_mcp_modal,
            ),
        ),
    )