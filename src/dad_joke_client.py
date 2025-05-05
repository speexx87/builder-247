import logging
import requests
from typing import Dict, List, Optional, Union

class DadJokeClient:
    """
    A robust client for fetching dad jokes from the icanhazdadjoke API.

    Attributes:
        BASE_URL (str): Base URL for the icanhazdadjoke API
        _logger (logging.Logger): Logger for tracking API interactions
    """
    BASE_URL = "https://icanhazdadjoke.com/"

    def __init__(
        self, 
        api_key: Optional[str] = None, 
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the Dad Joke Client.

        Args:
            api_key (Optional[str]): Optional API key (currently unused)
            logger (Optional[logging.Logger]): Custom logger for API interactions
        """
        self._headers = {
            "Accept": "application/json",
            "User-Agent": "Prometheus Dad Joke Client"
        }
        
        # Configure logging
        self._logger = logger or self._setup_default_logger()

    def _setup_default_logger(self) -> logging.Logger:
        """
        Set up a default logger if no custom logger is provided.

        Returns:
            logging.Logger: Configured logger for the client
        """
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        # Create console handler only if no handlers exist
        if not logger.handlers:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger

    def get_random_joke(self) -> Dict[str, Union[str, int]]:
        """
        Fetch a random dad joke from the API.

        Returns:
            Dict containing joke details with keys: 'id', 'joke', 'status'

        Raises:
            ConnectionError: If network issues prevent joke retrieval
            ValueError: If API response is invalid
        """
        try:
            self._logger.info("Attempting to fetch random dad joke")
            response = requests.get(
                self.BASE_URL, 
                headers=self._headers
            )
            response.raise_for_status()
            
            joke_data = response.json()
            joke_info = {
                "id": joke_data.get("id", ""),
                "joke": joke_data.get("joke", ""),
                "status": response.status_code
            }
            
            self._logger.info(f"Successfully fetched dad joke (ID: {joke_info['id']})")
            return joke_info
        
        except requests.exceptions.RequestException as e:
            self._logger.error(f"Network error fetching dad joke: {e}")
            raise ConnectionError(f"Failed to fetch dad joke: {e}")
        
        except (KeyError, ValueError) as e:
            self._logger.error(f"Invalid API response: {e}")
            raise ValueError(f"Invalid API response: {e}")

    def search_jokes(
        self, 
        term: str, 
        limit: int = 5
    ) -> List[Dict[str, str]]:
        """
        Search for dad jokes matching a specific term.

        Args:
            term (str): Search term for jokes
            limit (int, optional): Maximum number of jokes to return. Defaults to 5.

        Returns:
            List of jokes matching the search term

        Raises:
            ValueError: If search term is invalid
            ConnectionError: If network issues prevent joke retrieval
        """
        if not term or not isinstance(term, str):
            self._logger.error("Invalid search term provided")
            raise ValueError("Search term must be a non-empty string")

        try:
            params = {"term": term, "limit": limit}
            self._logger.info(f"Searching jokes with term: '{term}', limit: {limit}")
            
            response = requests.get(
                f"{self.BASE_URL}search", 
                headers=self._headers,
                params=params
            )
            response.raise_for_status()
            
            search_data = response.json()
            jokes = [{
                "id": joke.get("id", ""),
                "joke": joke.get("joke", "")
            } for joke in search_data.get("results", [])]
            
            self._logger.info(f"Found {len(jokes)} jokes matching search term")
            return jokes
        
        except requests.exceptions.RequestException as e:
            self._logger.error(f"Network error searching jokes: {e}")
            raise ConnectionError(f"Failed to search dad jokes: {e}")
        
        except (KeyError, ValueError) as e:
            self._logger.error(f"Invalid API response: {e}")
            raise ValueError(f"Invalid API response: {e}")