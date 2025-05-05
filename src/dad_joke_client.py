import requests
import logging

class DadJokeClient:
    """
    A client for fetching dad jokes from the icanhazdadjoke API.
    """
    BASE_URL = "https://icanhazdadjoke.com/"

    def __init__(self, api_key=None, logger=None):
        """
        Initialize the Dad Joke Client.

        :param api_key: Optional API key for future use (currently not required by this API)
        :param logger: Optional custom logger. If not provided, a default logger is created.
        """
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "Prometheus Development Dad Joke Client (https://github.com/your-repo)"
        }
        
        # Configure logging
        self.logger = logger or logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def get_random_joke(self):
        """
        Fetch a random dad joke.

        :return: A dictionary containing the joke details
        :raises ConnectionError: If there's an issue connecting to the API
        :raises ValueError: If the API response is invalid
        """
        try:
            self.logger.info(f"Fetching random dad joke from {self.BASE_URL}")
            response = requests.get(self.BASE_URL, headers=self.headers)
            response.raise_for_status()  # Raise an error for bad status codes
            
            joke_data = response.json()
            joke_info = {
                "id": joke_data.get("id"),
                "joke": joke_data.get("joke"),
                "status": response.status_code
            }
            
            self.logger.info(f"Successfully fetched dad joke with ID: {joke_info['id']}")
            return joke_info
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch dad joke: {str(e)}")
            raise ConnectionError(f"Failed to fetch dad joke: {str(e)}")
        except ValueError as e:
            self.logger.error(f"Invalid API response: {str(e)}")
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
            self.logger.error("Invalid search term: must be a non-empty string")
            raise ValueError("Search term must be a non-empty string")

        try:
            params = {
                "term": term,
                "limit": limit
            }
            self.logger.info(f"Searching dad jokes with term: '{term}', limit: {limit}")
            response = requests.get(f"{self.BASE_URL}search", 
                                    headers=self.headers, 
                                    params=params)
            response.raise_for_status()
            
            search_data = response.json()
            jokes = [{
                "id": joke.get("id"),
                "joke": joke.get("joke")
            } for joke in search_data.get("results", [])]
            
            self.logger.info(f"Found {len(jokes)} jokes matching the search term")
            return jokes
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to search dad jokes: {str(e)}")
            raise ConnectionError(f"Failed to search dad jokes: {str(e)}")
        except ValueError as e:
            self.logger.error(f"Invalid API response: {str(e)}")
            raise ValueError(f"Invalid API response: {str(e)}")