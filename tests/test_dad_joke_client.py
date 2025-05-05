import pytest
import requests
from unittest.mock import patch
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
def dad_joke_client():
    return DadJokeClient()

def test_client_initialization(dad_joke_client):
    assert isinstance(dad_joke_client, DadJokeClient)
    assert dad_joke_client.BASE_URL == "https://icanhazdadjoke.com/"

@patch('requests.get')
def test_get_random_joke_success(mock_get, dad_joke_client):
    mock_response_data = {
        "id": "abc123",
        "joke": "Why don't scientists trust atoms? Because they make up everything!",
        "status": 200
    }
    mock_get.return_value = MockResponse(mock_response_data)

    joke = dad_joke_client.get_random_joke()
    
    assert joke['id'] == "abc123"
    assert joke['joke'] == "Why don't scientists trust atoms? Because they make up everything!"
    assert joke['status'] == 200
    mock_get.assert_called_once_with(dad_joke_client.BASE_URL, headers=dad_joke_client.headers)

@patch('requests.get')
def test_get_random_joke_connection_error(mock_get, dad_joke_client):
    mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

    with pytest.raises(ConnectionError, match="Failed to fetch dad joke"):
        dad_joke_client.get_random_joke()

@patch('requests.get')
def test_search_jokes_success(mock_get, dad_joke_client):
    mock_response_data = {
        "results": [
            {"id": "joke1", "joke": "Funny joke 1"},
            {"id": "joke2", "joke": "Funny joke 2"}
        ]
    }
    mock_get.return_value = MockResponse(mock_response_data)

    jokes = dad_joke_client.search_jokes("funny", limit=2)
    
    assert len(jokes) == 2
    assert jokes[0]['id'] == "joke1"
    assert jokes[0]['joke'] == "Funny joke 1"
    mock_get.assert_called_once_with(
        f"{dad_joke_client.BASE_URL}search", 
        headers=dad_joke_client.headers, 
        params={'term': 'funny', 'limit': 2}
    )

def test_search_jokes_invalid_input(dad_joke_client):
    with pytest.raises(ValueError, match="Search term must be a non-empty string"):
        dad_joke_client.search_jokes("")
    
    with pytest.raises(ValueError, match="Search term must be a non-empty string"):
        dad_joke_client.search_jokes(None)

@patch('requests.get')
def test_search_jokes_connection_error(mock_get, dad_joke_client):
    mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

    with pytest.raises(ConnectionError, match="Failed to search dad jokes"):
        dad_joke_client.search_jokes("test")