from dataclasses import dataclass, asdict
from typing import Set, Optional
import json
from pathlib import Path

@dataclass
class Settings:
    """Application settings."""
    show_category: bool = True
    allow_duplicates: bool = False
    show_answer: bool = True
    selected_categories: Set[str] = None  # None means all categories
    
    @classmethod
    def load(cls, path: Path = Path("settings.json")) -> 'Settings':
        """Load settings from JSON file."""
        try:
            with open(path) as f:
                data = json.load(f)
                # Convert selected_categories back to set if it exists
                if data.get('selected_categories'):
                    data['selected_categories'] = set(data['selected_categories'])
                return cls(**data)
        except (FileNotFoundError, json.JSONDecodeError):
            return cls()  # Return default settings if file doesn't exist or is invalid

    def save(self, path: Path = Path("settings.json")) -> None:
        """Save settings to JSON file."""
        data = asdict(self)
        # Convert set to list for JSON serialization
        if data['selected_categories']:
            data['selected_categories'] = list(data['selected_categories'])
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)