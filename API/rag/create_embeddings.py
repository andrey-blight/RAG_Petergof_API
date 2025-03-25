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


def get_embeddings(file_name_txt):
    file_name_json = os.path.splitext(file_name_txt)[0] + ".json"
    
    folder_path = f"knowledge/{DATA_DIR}"
    metadata_file = os.path.join(METADATA_PATH, "metadata.json")

    sdk = YCloudML(folder_id=YC_FOLDER_ID, auth=YC_API_KEY)
    doc_model = sdk.models.text_embeddings("doc")
    
    metadata = {}
    if os.path.exists(metadata_file):
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    
    file_path = os.path.join(folder_path, file_name_json)
    file = {}
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
                file = json.load(f)
    
    chunks_file = os.path.join(CHUNKS_PATH, f"{file_name_txt}_chunks.json")
    chunks_data = {'data': []}
    total_chunks = []
    entry_index = 0
    
    for value in file['data']:
        page = value['page']
        text = value['text']
        
        file_chunks = splitter.split_text(text)
        total_chunks += file_chunks
        
        for chunk in file_chunks:
            chunks_data["data"].append({"text": chunk, "page": page})
            entry_index += 1
 
    embeddings = np.array([doc_model.run(chunk) for chunk in total_chunks], dtype="float32")
    embedding_file = os.path.join(EMBEDS_PATH, f"{file_name_txt}.npy")
    np.save(embedding_file, embeddings)
    
    
    with open(chunks_file, "w", encoding="utf-8") as f:
        json.dump(chunks_data, f, ensure_ascii=False, indent=4)
        
    metadata[file_name_txt] = {
        "chunks_file": chunks_file,
        "embedding_file": embedding_file,
        "num_chunks": len(total_chunks)
    }
    with open(metadata_file, "w", encoding="utf-8") as meta_file:
        json.dump(metadata, meta_file, ensure_ascii=False, indent=4)
        
    shutil.move(file_path, os.path.join(DEST_DIR, file_name_json))

                

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Недостаточно параметров запуска")
        sys.exit(1)
    
    file_name = sys.argv[1]
    get_embeddings(file_name)
