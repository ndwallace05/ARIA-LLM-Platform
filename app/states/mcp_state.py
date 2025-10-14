import reflex as rx
from typing import TypedDict, cast


class McpServer(TypedDict):
    name: str
    description: str
    repo: str
    installed: bool
    running: bool


class McpState(rx.State):
    servers: dict[str, McpServer] = {
        "web-search": {
            "name": "Web Search",
            "description": "Enables the model to search the web using various search engines.",
            "repo": "https://github.com/mcp-ai/web-search-mcp-server",
            "installed": False,
            "running": False,
        },
        "code-interpreter": {
            "name": "Code Interpreter",
            "description": "A Node.js code interpreter for executing code.",
            "repo": "https://github.com/mcp-ai/node-code-interpreter-mcp-server",
            "installed": False,
            "running": False,
        },
        "time": {
            "name": "Time",
            "description": "Provides time and timezone conversion capabilities.",
            "repo": "https://github.com/model-context-protocol/time",
            "installed": False,
            "running": False,
        },
        "puppeteer": {
            "name": "Puppeteer",
            "description": "Browser automation and web scraping.",
            "repo": "https://github.com/model-context-protocol/puppeteer",
            "installed": False,
            "running": False,
        },
        "serper-mcp-server": {
            "name": "Serper Search",
            "description": "A Google Search API connector via serper.dev.",
            "repo": "https://github.com/garymeng/serper-mcp-server",
            "installed": False,
            "running": False,
        },
    }
    show_mcp_modal: bool = False
    show_custom_server_form: bool = False
    custom_server_name: str = ""
    custom_server_description: str = ""
    custom_server_repo: str = ""
    custom_server_form_error: str = ""

    def _reset_custom_server_form(self):
        self.custom_server_name = ""
        self.custom_server_description = ""
        self.custom_server_repo = ""
        self.custom_server_form_error = ""

    @rx.event
    def toggle_mcp_modal(self):
        self.show_mcp_modal = not self.show_mcp_modal
        if not self.show_mcp_modal:
            self.show_custom_server_form = False
            self._reset_custom_server_form()

    @rx.event
    def install_server(self, server_name: str):
        if server_name in self.servers:
            self.servers[server_name]["installed"] = True

    @rx.event
    def toggle_server_running(self, server_name: str):
        if server_name in self.servers and self.servers[server_name]["installed"]:
            self.servers[server_name]["running"] = not self.servers[server_name][
                "running"
            ]

    @rx.event
    def toggle_custom_server_form(self):
        self.show_custom_server_form = not self.show_custom_server_form
        self._reset_custom_server_form()

    @rx.event
    def add_custom_server(self):
        if not self.custom_server_name or not self.custom_server_description:
            self.custom_server_form_error = "Name and description are required."
            return
        server_key = self.custom_server_name.lower().replace(" ", "-")
        if server_key in self.servers:
            self.custom_server_form_error = "A server with this name already exists."
            return
        self.servers[server_key] = {
            "name": self.custom_server_name,
            "description": self.custom_server_description,
            "repo": self.custom_server_repo,
            "installed": False,
            "running": False,
        }
        self.show_custom_server_form = False
        self._reset_custom_server_form()