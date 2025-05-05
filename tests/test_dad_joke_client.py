import pytest
import logging
import requests
from unittest.mock import patch, Mock
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
    assert isinstance(dad_joke_client, DadJokeClient)
    assert dad_joke_client.BASE_URL == "https://icanhazdadjoke.com/"
    assert dad_joke_client.logger is not None

def test_logger_configuration(dad_joke_client):
    """Test that logger is properly configured."""
    assert dad_joke_client.logger.level == logging.INFO
    assert len(dad_joke_client.logger.handlers) > 0

@patch('requests.get')
def test_get_random_joke_logging(mock_get, dad_joke_client, caplog):
    """Test logging for random joke retrieval."""
    caplog.set_level(logging.INFO)
    
    mock_response_data = {
        "id": "abc123",
        "joke": "Why don't scientists trust atoms? Because they make up everything!",
        "status": 200
    }
    mock_get.return_value = MockResponse(mock_response_data)

    joke = dad_joke_client.get_random_joke()
    
    assert "Fetching random dad joke" in caplog.text
    assert "Successfully fetched dad joke with ID: abc123" in caplog.text
    assert joke['id'] == "abc123"

@patch('requests.get')
def test_search_jokes_logging(mock_get, dad_joke_client, caplog):
    """Test logging for joke search."""
    caplog.set_level(logging.INFO)
    
    mock_response_data = {
        "results": [
            {"id": "joke1", "joke": "Funny joke 1"},
            {"id": "joke2", "joke": "Funny joke 2"}
        ]
    }
    mock_get.return_value = MockResponse(mock_response_data)

    jokes = dad_joke_client.search_jokes("funny", limit=2)
    
    assert "Searching dad jokes with term: 'funny'" in caplog.text
    assert "Found 2 jokes matching the search term" in caplog.text
    assert len(jokes) == 2

def test_search_jokes_error_logging(dad_joke_client, caplog):
    """Test logging for invalid search input."""
    caplog.set_level(logging.ERROR)
    
    with pytest.raises(ValueError, match="Search term must be a non-empty string"):
        dad_joke_client.search_jokes("")
    
    assert "Invalid search term" in caplog.text

@patch('requests.get')
def test_get_random_joke_error_logging(mock_get, dad_joke_client, caplog):
    """Test logging for connection errors."""
    caplog.set_level(logging.ERROR)
    
    mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

    with pytest.raises(ConnectionError):
        dad_joke_client.get_random_joke()
    
    assert "Failed to fetch dad joke" in caplog.text