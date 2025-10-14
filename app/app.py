import reflex as rx
from app.components.sidebar import sidebar
from app.components.chat import chat_interface


def index() -> rx.Component:
    """Renders the main page of the application.

    This function combines the sidebar and chat interface components
    to create the main user interface.

    Returns:
        A reflex component representing the main page.
    """
    return rx.el.main(
        rx.el.div(sidebar(), chat_interface(), class_name="flex h-screen"),
        class_name="font-['Inter'] bg-gray-50 text-gray-800",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index)