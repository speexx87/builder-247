import requests

class DadJokeClient:
    """
    A client for fetching dad jokes from the icanhazdadjoke API.
    """
    BASE_URL = "https://icanhazdadjoke.com/"

    def __init__(self, api_key=None):
        """
        Initialize the Dad Joke Client.

        :param api_key: Optional API key for future use (currently not required by this API)
        """
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "Prometheus Development Dad Joke Client (https://github.com/your-repo)"
        }

    def get_random_joke(self):
        """
        Fetch a random dad joke.

        :return: A dictionary containing the joke details
        :raises ConnectionError: If there's an issue connecting to the API
        :raises ValueError: If the API response is invalid
        """
        try:
            response = requests.get(self.BASE_URL, headers=self.headers)
            response.raise_for_status()  # Raise an error for bad status codes
            
            joke_data = response.json()
            return {
                "id": joke_data.get("id"),
                "joke": joke_data.get("joke"),
                "status": response.status_code
            }
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to fetch dad joke: {str(e)}")
        except ValueError as e:
            raise ValueError(f"Invalid API response: {str(e)}")

    def search_jokes(self, term, limit=5):
        """
        Search for dad jokes containing a specific term.

        :param term: Search term for jokes
        :param limit: Maximum number of jokes to return (default: 5)
        :return: A list of jokes matching the search term
        :raises ConnectionError: If there's an issue connecting to the API
        :raises ValueError: If the API response is invalid
        """
        if not term or not isinstance(term, str):
            raise ValueError("Search term must be a non-empty string")

        try:
            params = {
                "term": term,
                "limit": limit
            }
            response = requests.get(f"{self.BASE_URL}search", 
                                    headers=self.headers, 
                                    params=params)
            response.raise_for_status()
            
            search_data = response.json()
            return [{
                "id": joke.get("id"),
                "joke": joke.get("joke")
            } for joke in search_data.get("results", [])]
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to search dad jokes: {str(e)}")
        except ValueError as e:
            raise ValueError(f"Invalid API response: {str(e)}")