import json
from abc import ABC, abstractmethod
from typing import Dict, Any

class ConfigHandler(ABC):
    """
    Abstract base class for configuration handlers.
    """

    @abstractmethod
    def load_config(self, file_path: str) -> Dict[str, Any]:
        """
        Load configuration from a file.

        Args:
            file_path (str): The path to the configuration file.

        Returns:
            Dict[str, Any]: The loaded configuration as a dictionary.
        """
        pass

class JSONConfigHandler(ConfigHandler):
    """
    Configuration handler for JSON files.
    """

    def load_config(self, file_path: str) -> Dict[str, Any]:
        """
        Load configuration from a JSON file.

        Args:
            file_path (str): The path to the JSON configuration file.

        Returns:
            Dict[str, Any]: The loaded configuration as a dictionary.
        """
        with open(file_path, 'r') as file:
            return json.load(file)