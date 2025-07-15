"""
File binding system for Diablo II data files.
Loads JSON metadata from specs directory and creates dynamic bindings 
for .txt files loaded from anywhere on the system based on auto-detection.
Provides metadata integration and column descriptions.
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from file_parser import open_txt_file


class DataFileBinding:
    """Represents a binding between a JSON metadata file and its corresponding .txt data file."""
    
    def __init__(self, json_path: str, txt_path: str = None, metadata: Dict = None):
        self.json_path = json_path
        self.txt_path = txt_path
        self.metadata = metadata or {}
        self.base_name = Path(json_path).stem
        
    def load_metadata(self) -> Dict:
        """Load metadata from the JSON file."""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            return self.metadata
        except Exception as e:
            print(f"Error loading metadata from {self.json_path}: {e}")
            return {}
    
    def load_data(self):
        """Load the actual data from the .txt file."""
        if self.txt_path is None:
            raise ValueError("No txt file path set for this binding. Use create_dynamic_binding() first.")
        return open_txt_file(self.txt_path)
    
    def get_description(self) -> str:
        """Get the overview description from metadata."""
        return self.metadata.get('overview', 'No description available')
    
    def get_column_descriptions(self) -> Dict[str, str]:
        """Get column descriptions from metadata."""
        descriptions = {}
        for field in self.metadata.get('data_fields', []):
            if 'name' in field and 'description' in field:
                descriptions[field['name']] = field['description']
        return descriptions


class FileBindingManager:
    """Manages bindings between JSON metadata files and .txt data files."""
    
    def __init__(self, json_dir: str = "specs"):
        self.json_dir = json_dir
        self.bindings: Dict[str, DataFileBinding] = {}
        self._discover_metadata_files()
    
    def _discover_metadata_files(self):
        """Discover and load JSON metadata files for dynamic binding."""
        print(f"Loading metadata files from: {self.json_dir}")
        
        if not os.path.exists(self.json_dir):
            print(f"ERROR: JSON directory does not exist: {self.json_dir}")
            return
        
        # Get all JSON files and load their metadata
        json_files = [f for f in os.listdir(self.json_dir) if f.endswith('.json')]
        print(f"Found {len(json_files)} JSON metadata files")
        
        for json_file in json_files:
            json_path = os.path.join(self.json_dir, json_file)
            base_name = Path(json_file).stem.lower()
            
            try:
                # Create a metadata-only binding (no txt_path yet)
                binding = DataFileBinding(json_path, None)
                binding.load_metadata()
                self.bindings[base_name] = binding
                print(f"Loaded metadata: {json_file}")
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
    
    def create_dynamic_binding(self, file_type: str, txt_path: str) -> Optional[DataFileBinding]:
        """Create a dynamic binding for a detected file type and specific txt file."""
        # Look for metadata that matches the detected file type
        if file_type.lower() in self.bindings:
            metadata_binding = self.bindings[file_type.lower()]
            # Create a new binding with the actual txt file path
            dynamic_binding = DataFileBinding(metadata_binding.json_path, txt_path, metadata_binding.metadata)
            print(f"Created dynamic binding: {file_type} -> {os.path.basename(txt_path)}")
            return dynamic_binding
        
        print(f"No metadata found for file type: {file_type}")
        return None
    

    
    def get_binding(self, file_key: str) -> Optional[DataFileBinding]:
        """Get a binding by file key (case-insensitive)."""
        return self.bindings.get(file_key.lower())
    
    def get_all_bindings(self) -> Dict[str, DataFileBinding]:
        """Get all available bindings."""
        return self.bindings
    
    def get_binding_names(self) -> List[str]:
        """Get a list of all binding names."""
        return list(self.bindings.keys())
    
    def refresh_bindings(self):
        """Refresh the metadata files."""
        self.bindings.clear()
        self._discover_metadata_files()


# Global instance
_binding_manager = None

def get_binding_manager() -> FileBindingManager:
    """Get the global file binding manager instance."""
    global _binding_manager
    if _binding_manager is None:
        _binding_manager = FileBindingManager()
    return _binding_manager

def reset_binding_manager():
    """Reset the global binding manager to force re-discovery."""
    global _binding_manager
    _binding_manager = None


def get_file_binding(file_key: str) -> Optional[DataFileBinding]:
    """Convenience function to get a file binding."""
    return get_binding_manager().get_binding(file_key)


def get_all_file_bindings() -> Dict[str, DataFileBinding]:
    """Convenience function to get all file bindings."""
    return get_binding_manager().get_all_bindings()


def refresh_file_bindings():
    """Convenience function to refresh file bindings."""
    get_binding_manager().refresh_bindings() 