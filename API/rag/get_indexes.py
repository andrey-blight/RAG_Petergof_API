import os
import json

def get_indexes():
    list_indexes_filepath = "rag/data/metadata/list_indexes.json"
    list_indexes = {}
    if os.path.exists(list_indexes_filepath):
        with open(list_indexes_filepath, "r", encoding="utf-8") as f:
            list_indexes = json.load(f)
    
    return list(list_indexes.keys())
    

def get_files_by_index_name(name):
    list_indexes_filepath = "rag/data/metadata/list_indexes.json"
    list_indexes = {}
    if os.path.exists(list_indexes_filepath):
        with open(list_indexes_filepath, "r", encoding="utf-8") as f:
            list_indexes = json.load(f)
            
    if name in list_indexes.keys():
        return sorted(list_indexes[name]['files'])
    
    print('Несуществующий индекс')
    return None
    
    
if __name__ == "__main__":
    get_indexes()
    get_files_by_index_name("new")
    