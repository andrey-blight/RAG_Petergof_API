import os
import json

def get_files():
    metadata_filepath = "data/metadata/metadata.json"
    metadata = {}
    if os.path.exists(metadata_filepath):
        with open(metadata_filepath, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    
    return sorted(metadata.keys())
    
    
if __name__ == "__main__":
    get_files()
    