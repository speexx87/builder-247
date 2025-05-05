import logging
import pytest
import requests
from unittest.mock import Mock, patch
from src.dad_joke_client import DadJokeClient

class MockResponse:
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(f"HTTP Error: {self.status_code}")

@pytest.fixture
def mock_logger():
    """Create a mock logger for testing."""
    logger = logging.getLogger('test_dad_joke_client')
    logger.setLevel(logging.INFO)
    return logger

@pytest.fixture
def dad_joke_client(mock_logger):
    return DadJokeClient(logger=mock_logger)

def test_client_initialization(dad_joke_client):
    """Test that the client is initialized correctly."""
    assert isinstance(dad_joke_client, DadJokeClient)
    assert dad_joke_client.BASE_URL == "https://icanhazdadjoke.com/"
    assert dad_joke_client._logger is not None

def test_default_logger_setup():
    """Test the default logger setup when no logger is provided."""
    client = DadJokeClient()
    assert client._logger is not None
    assert len(client._logger.handlers) > 0

@patch('requests.get')
def test_get_random_joke_success(mock_get, dad_joke_client, caplog):
    """Test successful random joke retrieval."""
    caplog.set_level(logging.INFO)
    
    mock_response_data = {
        "id": "abc123",
        "joke": "Why don't scientists trust atoms? Because they make up everything!",
    }
    mock_get.return_value = MockResponse(mock_response_data)

    joke = dad_joke_client.get_random_joke()
    
    assert joke['id'] == "abc123"
    assert "Successfully fetched dad joke" in caplog.text

@patch('requests.get')
def test_search_jokes_success(mock_get, dad_joke_client, caplog):
    """Test successful joke search."""
    caplog.set_level(logging.INFO)
    
    mock_response_data = {
        "results": [
            {"id": "joke1", "joke": "Funny joke 1"},
            {"id": "joke2", "joke": "Funny joke 2"}
        ]
    }
    mock_get.return_value = MockResponse(mock_response_data)

    jokes = dad_joke_client.search_jokes("funny", limit=2)
    
    assert len(jokes) == 2
    assert "Found 2 jokes matching search term" in caplog.text

def test_search_jokes_invalid_input(dad_joke_client, caplog):
    """Test invalid search term handling."""
    caplog.set_level(logging.ERROR)
    
    with pytest.raises(ValueError, match="Search term must be a non-empty string"):
        dad_joke_client.search_jokes("")
    
    with pytest.raises(ValueError, match="Search term must be a non-empty string"):
        dad_joke_client.search_jokes(None)
    
    assert "Invalid search term provided" in caplog.text

@patch('requests.get')
def test_get_random_joke_network_error(mock_get, dad_joke_client, caplog):
    """Test network error handling for random joke retrieval."""
    caplog.set_level(logging.ERROR)
    
    mock_get.side_effect = requests.exceptions.ConnectionError("Network failure")

    with pytest.raises(ConnectionError):
        dad_joke_client.get_random_joke()
    
    assert "Network error fetching dad joke" in caplog.text

@patch('requests.get')
def test_search_jokes_network_error(mock_get, dad_joke_client, caplog):
    """Test network error handling for joke search."""
    caplog.set_level(logging.ERROR)
    
    mock_get.side_effect = requests.exceptions.ConnectionError("Network failure")

    with pytest.raises(ConnectionError):
        dad_joke_client.search_jokes("test")
    
    assert "Network error searching jokes" in caplog.text