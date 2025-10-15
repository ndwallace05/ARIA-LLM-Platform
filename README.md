# DeepChat

DeepChat is a versatile and extensible web-based chat application built with the [Reflex](https://reflex.dev/) framework. It provides a unified interface to interact with a variety of Large Language Models (LLMs) from different providers.

## Features

- **Multi-Provider Support**: Connect to various LLM providers, including OpenAI, Anthropic, Gemini, Groq, and any OpenAI-compatible API.
- **Local LLM Integration**: Supports local models through Ollama.
- **Model Management**: Easily switch between different models from the settings panel.
- **API Key Management**: Securely store and manage your API keys within the application.
- **Extensible Capabilities**: Integrates with the Model Context Protocol (MCP) to add extended functionalities like web search, code interpretation, and more.
- **Chat History**: Conversations are saved and can be revisited later.

## Getting Started

Follow these instructions to get a local copy of DeepChat up and running.

### Prerequisites

- Python 3.8+
- [Poetry](https://python-poetry.org/docs/#installation) for managing Python dependencies.
- Node.js 16+

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/deepchat.git
    cd deepchat
    ```

2.  **Install Python dependencies using Poetry:**
    ```bash
    poetry install
    ```

3.  **Initialize the Reflex application:**
    This command sets up the necessary frontend dependencies.
    ```bash
    poetry run reflex init
    ```

4.  **Run the application:**
    ```bash
    poetry run reflex run
    ```

The application will now be running at `http://localhost:3000`.

## Usage

1.  **Open the application** in your web browser.
2.  Click on the **Settings** button in the sidebar.
3.  **Add your API keys** for the LLM providers you want to use. For Ollama, you can specify the base URL if it's not running on the default `http://localhost:11434`.
4.  After adding an API key or URL, the application will fetch the available models for that provider.
5.  **Select a model** from the list.
6.  Close the settings modal and start a **New Chat**.
7.  Type your messages in the input box and press Enter.

## Project Structure

-   `app/`: The core application source code.
    -   `components/`: UI components used to build the interface (e.g., `sidebar.py`, `chat.py`).
    -   `states/`: State management classes that handle the application's logic (e.g., `ChatState.py`, `SettingsState.py`).
    -   `app.py`: The main application entry point that defines the overall layout.
-   `assets/`: Static files like images and favicons.
-   `requirements.txt`: A list of Python dependencies.
-   `rxconfig.py`: The Reflex configuration file.

## Contributing

Contributions are welcome! If you have suggestions for improvements or want to add new features, please feel free to open an issue or submit a pull request.
