import os
import sys
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
import torch
from dotenv import load_dotenv
from yandex_cloud_ml_sdk import YCloudML
from tqdm import tqdm
import json
import shutil
from collections import defaultdict

load_dotenv()
DATA_DIR = os.getenv("DATA_DIR")
YC_API_KEY = os.getenv("YC_API_KEY")
YC_FOLDER_ID = os.getenv("YC_FOLDER_ID")


METADATA_PATH = "data/metadata"
CHUNKS_PATH = "data/chunks"
EMBEDS_PATH = "data/embeddings"
DEST_DIR = "knowledge/data_embedded"

device = "cuda" if torch.cuda.is_available() else "cpu"

def group_files_by_name(folder_path):
    groups = defaultdict(list)
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        if os.path.isfile(file_path) and filename.endswith(".txt"):
            base_name = '_'.join(filename.split('_')[:-1])
            if base_name + ".txt" == file_name:
                groups[base_name].append(filename)
    return groups

def get_embeddings(file_name):
    folder_path = f"knowledge/{DATA_DIR}"
    metadata_file = os.path.join(METADATA_PATH, "metadata.json")

    sdk = YCloudML(folder_id=YC_FOLDER_ID, auth=YC_API_KEY)
    doc_model = sdk.models.text_embeddings("doc")
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    
    file_groups = group_files_by_name(folder_path)
    
    for base_name, filenames in tqdm(file_groups.items()):
        filename_total = base_name + ".txt"
        total_chunks = []
        total_text = ""
        chunks_data = {}
        
        page_num = 1
        entry_index = 0
        
        metadata = {}
        if os.path.exists(metadata_file):
             with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)
                
        chunks_file = os.path.join(CHUNKS_PATH, f"{filename_total}_chunks.json")
                    
        for filename in sorted(filenames):
            file_path = os.path.join(folder_path, filename)
            
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
            total_text += text + "\n"
            
            file_chunks = splitter.split_text(text)
            total_chunks += file_chunks
            
            for chunk in file_chunks:
                chunks_data[str(entry_index)] = {"text": chunk, "page": page_num}
                entry_index += 1

            page_num += 1
            
        embeddings = np.array([doc_model.run(chunk) for chunk in total_chunks], dtype="float32")
        embedding_file = os.path.join(EMBEDS_PATH, f"{filename_total}.npy")
        np.save(embedding_file, embeddings)
        
        with open(chunks_file, "w", encoding="utf-8") as f:
            json.dump(chunks_data, f, ensure_ascii=False, indent=4)
        
        metadata[filename_total] = {
            "chunks_file": chunks_file,
            "embedding_file": embedding_file,
            "num_chunks": len(total_chunks)
        }
        with open(metadata_file, "w", encoding="utf-8") as meta_file:
                json.dump(metadata, meta_file, ensure_ascii=False, indent=4)
        
        new_path = os.path.join(DEST_DIR, filename_total)
        with open(new_path, "w", encoding="utf-8") as f:
             f.write(total_text)
        
        for base_name, filenames in tqdm(file_groups.items()):
            for filename in sorted(filenames):
                file_path = os.path.join(folder_path, filename)
                os.remove(file_path)
                

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Недостаточно параметров запуска")
        sys.exit(1)
    
    file_name = sys.argv[1]
    get_embeddings(file_name)
