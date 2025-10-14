import pytest
from app.states.state import ChatState

def test_chat_state_initial_state():
    """Tests the initial state of the ChatState."""
    initial_state = ChatState()
    assert initial_state.chats == {"new chat": []}
    assert initial_state.current_chat_id == "new chat"
    assert not initial_state.is_streaming

def test_chat_titles_property_initial():
    """Tests the chat_titles computed property on an initial state."""
    initial_state = ChatState()
    assert initial_state.chat_titles == ["new chat"]

def test_current_chat_property_initial():
    """Tests the current_chat computed property on an initial state."""
    initial_state = ChatState()
    assert initial_state.current_chat == []

def test_new_chat():
    """Tests the new_chat method."""
    state = ChatState()
    state.new_chat()
    assert len(state.chats) == 2
    assert "chat_1" in state.chats
    assert state.current_chat_id == "chat_1"
    # The order of keys in a dictionary is not guaranteed in older python versions
    # but is insertion order from 3.7+. Let's test with a set for robustness.
    assert set(state.chat_titles) == {"new chat", "chat_1"}
    assert state.current_chat == []

def test_set_current_chat_id():
    """Tests the set_current_chat_id method."""
    state = ChatState()
    state.new_chat()  # Create a second chat to switch to
    state.set_current_chat_id("new chat")
    assert state.current_chat_id == "new chat"
    assert state.current_chat == []


from app.states.settings_state import SettingsState

def test_settings_state_initial_state():
    """Tests the initial state of the SettingsState."""
    state = SettingsState()
    assert not state.show_settings
    assert state.selected_model == ""
    assert all(key == "" for key in state.api_keys.values())
    assert state.models == {}
    assert state.expanded_providers == set()
    assert state.loading_models == set()

def test_toggle_settings():
    """Tests the toggle_settings method."""
    state = SettingsState()
    assert not state.show_settings
    state.toggle_settings()
    assert state.show_settings
    state.toggle_settings()
    assert not state.show_settings

def test_select_model_and_computed_vars():
    """Tests selecting a model and the dependent computed properties."""
    state = SettingsState()
    assert state.selected_provider == ""
    assert state.selected_model_id == ""

    state.select_model("openai:gpt-4")
    assert state.selected_model == "openai:gpt-4"
    assert state.selected_provider == "openai"
    assert state.selected_model_id == "gpt-4"

    state.select_model("ollama:llama2:latest")
    assert state.selected_model == "ollama:llama2:latest"
    assert state.selected_provider == "ollama"
    assert state.selected_model_id == "llama2:latest"


def test_filtered_models():
    """Tests the filtered_models computed property."""
    state = SettingsState()
    state.models = {
        "provider1": ["model-a", "model-b", "common-model"],
        "provider2": ["model-c", "model-d", "common-model"],
    }

    # No search term
    assert state.filtered_models == state.models

    # Search term for provider1
    state.set_model_search_term("provider1", "model-a")
    assert state.filtered_models["provider1"] == ["model-a"]
    assert state.filtered_models["provider2"] == state.models["provider2"]

    # Search term for common model
    state.set_model_search_term("provider1", "common")
    state.set_model_search_term("provider2", "common")
    assert state.filtered_models["provider1"] == ["common-model"]
    assert state.filtered_models["provider2"] == ["common-model"]


from app.states.mcp_state import McpState

def test_mcp_state_initial_state():
    """Tests the initial state of the McpState."""
    state = McpState()
    assert not state.show_mcp_modal
    assert not state.show_custom_server_form
    assert state.custom_server_name == ""
    assert state.custom_server_description == ""
    assert state.custom_server_repo == ""
    assert state.custom_server_form_error == ""
    # Check if a default server exists
    assert "web-search" in state.servers

def test_toggle_mcp_modal():
    """Tests the toggle_mcp_modal method."""
    state = McpState()
    state.show_custom_server_form = True # Set to non-default
    state.toggle_mcp_modal()
    assert state.show_mcp_modal
    state.toggle_mcp_modal()
    assert not state.show_mcp_modal
    # Check that closing the modal also closes the form
    assert not state.show_custom_server_form

def test_install_server():
    """Tests the install_server method."""
    state = McpState()
    server_name = "web-search"
    assert not state.servers[server_name]["installed"]
    state.install_server(server_name)
    assert state.servers[server_name]["installed"]

def test_toggle_server_running():
    """Tests the toggle_server_running method."""
    state = McpState()
    server_name = "web-search"
    # Should not start if not installed
    state.toggle_server_running(server_name)
    assert not state.servers[server_name]["running"]

    # Should start and stop once installed
    state.install_server(server_name)
    state.toggle_server_running(server_name)
    assert state.servers[server_name]["running"]
    state.toggle_server_running(server_name)
    assert not state.servers[server_name]["running"]

def test_add_custom_server_success():
    """Tests successfully adding a custom server."""
    state = McpState()
    state.custom_server_name = "My Test Server"
    state.custom_server_description = "A test description"
    state.custom_server_repo = "http://github.com"
    state.show_custom_server_form = True

    state.add_custom_server()

    server_key = "my-test-server"
    assert server_key in state.servers
    assert state.servers[server_key]["name"] == "My Test Server"
    assert state.servers[server_key]["description"] == "A test description"
    assert not state.show_custom_server_form
    assert state.custom_server_form_error == ""

def test_add_custom_server_validation():
    """Tests the validation for adding a custom server."""
    state = McpState()
    # Test missing name
    state.add_custom_server()
    assert state.custom_server_form_error == "Name and description are required."

    # Test missing description
    state.custom_server_name = "Test"
    state.add_custom_server()
    assert state.custom_server_form_error == "Name and description are required."

    # Test duplicate name
    state.custom_server_description = "A description"
    state.custom_server_name = "Web Search" # Default server
    state.add_custom_server()
    assert state.custom_server_form_error == "A server with this name already exists."
