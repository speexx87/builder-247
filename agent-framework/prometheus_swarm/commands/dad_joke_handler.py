from typing import Dict, Any
import requests

class DadJokeCommandHandler:
    """
    A command handler for retrieving dad jokes.
    
    This class provides methods to fetch dad jokes from an external API.
    """
    
    def __init__(self, api_url: str = "https://icanhazdadjoke.com/"):
        """
        Initialize the Dad Joke Command Handler.
        
        Args:
            api_url (str, optional): The API endpoint for fetching dad jokes. 
                                     Defaults to "https://icanhazdadjoke.com/".
        """
        self.api_url = api_url
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "Prometheus Swarm Dad Joke Command Handler"
        }
    
    def get_joke(self) -> Dict[str, Any]:
        """
        Fetch a random dad joke from the API.
        
        Returns:
            Dict[str, Any]: A dictionary containing the joke details.
            
        Raises:
            Exception: If there's an error fetching the joke.
        """
        try:
            response = requests.get(self.api_url, headers=self.headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch dad joke: {str(e)}")
    
    def execute_command(self, command: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute a command for the Dad Joke handler.
        
        Args:
            command (str): The command to execute.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        
        Returns:
            Dict[str, Any]: Result of the command execution.
        
        Raises:
            ValueError: If an unsupported command is provided.
        """
        if command.lower() == "get_joke":
            return self.get_joke()
        else:
            raise ValueError(f"Unsupported command: {command}")