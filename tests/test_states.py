import pytest
from app.states.state import ChatState, StreamResponseResult
from app.states.settings_state import SettingsState
from app.states.mcp_state import McpState
from openai import AuthenticationError
import httpx
import asyncio

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
    assert set(state.chat_titles) == {"new chat", "chat_1"}
    assert state.current_chat == []

def test_set_current_chat_id():
    """Tests the set_current_chat_id method."""
    state = ChatState()
    state.new_chat()
    state.set_current_chat_id("new chat")
    assert state.current_chat_id == "new chat"
    assert state.current_chat == []

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
    assert state.filtered_models == state.models
    state.set_model_search_term("provider1", "model-a")
    assert state.filtered_models["provider1"] == ["model-a"]
    assert state.filtered_models["provider2"] == state.models["provider2"]
    state.set_model_search_term("provider1", "common")
    state.set_model_search_term("provider2", "common")
    assert state.filtered_models["provider1"] == ["common-model"]
    assert state.filtered_models["provider2"] == ["common-model"]

def test_mcp_state_initial_state():
    """Tests the initial state of the McpState."""
    state = McpState()
    assert not state.show_mcp_modal
    assert not state.show_custom_server_form
    assert "web-search" in state.servers

def test_toggle_mcp_modal():
    """Tests the toggle_mcp_modal method."""
    state = McpState()
    state.toggle_mcp_modal()
    assert state.show_mcp_modal

def test_install_server():
    """Tests the install_server method."""
    state = McpState()
    state.install_server("web-search")
    assert state.servers["web-search"]["installed"]

def test_toggle_server_running():
    """Tests the toggle_server_running method."""
    state = McpState()
    state.install_server("web-search")
    state.toggle_server_running("web-search")
    assert state.servers["web-search"]["running"]

def test_add_custom_server_success():
    """Tests successfully adding a custom server."""
    state = McpState()
    state.custom_server_name = "My Test Server"
    state.custom_server_description = "A test description"
    state.add_custom_server()
    assert "my-test-server" in state.servers

# Async tests
@pytest.mark.asyncio
async def test_fetch_openai_compatible_models_success(mocker):
    """Tests successful fetching of openai compatible models."""
    class MockModel:
        def __init__(self, id): self.id = id
    class MockData:
        data = [MockModel("gpt-4"), MockModel("gpt-3.5-turbo")]

    mocker.patch("app.states.settings_state.asyncio.to_thread", return_value=MockData())

    state = SettingsState()
    state.api_keys["openai"] = "test_key"
    models, error = await state._fetch_openai_compatible_models("openai")

    assert models == ["gpt-3.5-turbo", "gpt-4"]
    assert error is None

@pytest.mark.asyncio
async def test_fetch_openai_compatible_models_auth_error(mocker):
    """Tests authentication error during model fetching."""
    mock_response = httpx.Response(401, request=httpx.Request("GET", ""))
    mocker.patch(
        "app.states.settings_state.asyncio.to_thread",
        side_effect=AuthenticationError("Invalid API Key.", response=mock_response, body=None),
    )

    state = SettingsState()
    state.api_keys["openai"] = "invalid_key"
    models, error = await state._fetch_openai_compatible_models("openai")

    assert models == []
    assert error == "Invalid API Key."

@pytest.mark.asyncio
async def test_process_and_stream_response_no_model(mocker):
    """Tests the case where no model is selected."""
    mock_settings_state = SettingsState()
    mocker.patch.object(ChatState, "get_state", return_value=mock_settings_state)
    state = ChatState()

    result = await state._process_and_stream_response()
    assert isinstance(result, StreamResponseResult)
    assert result.error == "No model selected. Please select a model in settings."
    assert not result.is_stream

@pytest.mark.asyncio
async def test_process_and_stream_response_success(mocker):
    """Tests a successful response stream."""
    mock_settings_state = SettingsState()
    mock_settings_state.selected_model = "openai:gpt-4"
    mock_settings_state.api_keys["openai"] = "fake_key"
    mocker.patch.object(ChatState, "get_state", return_value=mock_settings_state)
    mock_stream = mocker.AsyncMock()
    mocker.patch.object(ChatState, "_stream_openai_compatible_response", return_value=mock_stream)

    state = ChatState()
    result = await state._process_and_stream_response()

    assert isinstance(result, StreamResponseResult)
    assert result.stream == mock_stream
    assert result.is_stream
    ChatState._stream_openai_compatible_response.assert_called_once()
