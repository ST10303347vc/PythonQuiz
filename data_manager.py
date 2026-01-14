import json
import os
from typing import Any, Optional

class DataManager:
    """
    A helper class to handle file I/O operations for JSON data.
    """

    @staticmethod
    def load_analytics(filename: str) -> Any:
        """
        Loads analytics data and migrates old format if necessary.
        
        Args:
            filename (str): The path to the analytics JSON file.
            
        Returns:
             Any: The analytics data in the new format.
        """
        default_data = {"streak": 0, "performance": {}}
        
        if not os.path.exists(filename):
            return default_data

        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
            # Migration Logic: Check for old keys
            if "total_attempted" in data:
                print("Migrating analytics data to new format...")
                migrated_data = {
                    "streak": data.get("streak", 0),
                    "performance": {
                        "Legacy": {
                            "correct": data.get("total_correct", 0),
                            "total": data.get("total_attempted", 0)
                        }
                    }
                }
                # Save immediately to complete migration
                DataManager.save_json(filename, migrated_data)
                return migrated_data
                
            return data
        except Exception as e:
            print(f"Error loading analytics: {e}. Starting fresh.")
            return default_data

    @staticmethod
    def load_json(filename: str, default: Optional[Any] = None) -> Any:
        """
        Loads data from a JSON file.

        Args:
            filename (str): The path to the JSON file.
            default (Optional[Any]): The default value to return if the file 
                                     doesn't exist or is corrupt. Defaults to None.

        Returns:
            Any: The data loaded from the JSON file, or the default value.
        """
        if not os.path.exists(filename):
            print(f"Info: File '{filename}' not found. Using default data.")
            return default
        
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error: Failed to decode JSON from '{filename}'. Using default data.")
            return default
        except Exception as e:
            print(f"Error reading file '{filename}': {e}")
            return default

    @staticmethod
    def save_json(filename: str, data: Any) -> None:
        """
        Saves data to a JSON file.

        Args:
            filename (str): The path to the JSON file.
            data (Any): The data to save (must be serializable to JSON).
        """
        try:
            with open(filename, 'w+') as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"Error saving data to '{filename}': {e}")
        except TypeError as e:
            print(f"Error serializing data for '{filename}': {e}")

    @staticmethod
    def get_unique_categories(questions: list) -> list:
        """
        Extracts a sorted list of unique categories from the questions list.
        """
        categories = set()
        for q in questions:
            categories.add(q.get('category', 'Uncategorized'))
        return sorted(list(categories))
