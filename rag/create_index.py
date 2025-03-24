import os
import sys
import faiss
import numpy as np
import pickle
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import AutoModel, AutoTokenizer
import torch
from dotenv import load_dotenv
from yandex_cloud_ml_sdk import YCloudML
from tqdm import tqdm
import json
from rank_bm25 import BM25Okapi
import re

load_dotenv()
DATA_DIR = os.getenv("DATA_DIR")
YC_API_KEY = os.getenv("YC_API_KEY")
YC_FOLDER_ID = os.getenv("YC_FOLDER_ID")


RAG_PATH = "data/rag"
METADATA_PATH = "data/metadata"
CHUNKS_PATH = "data/chunks"
EMBEDS_PATH = "data/embeddings"
USING_FILES_PATH = "data/using_files/files.txt"

def preprocess_text(text):
    text = re.sub(r"[^\w\s]", "", text).lower()
    return text.split()

def get_selected_files():
    files = []
    with open(USING_FILES_PATH, "r", encoding="utf-8") as file:
        for line in file.readlines():
            filename = line.strip()
            if filename:
                files.append(filename)
    return files


def create_index(name):
    meta_path = os.path.join(METADATA_PATH, "metadata.json")
    if not os.path.exists(meta_path):
        print("Нет сохранённого индекса.")
        return

    with open(meta_path, "r", encoding="utf-8") as meta_file:
        metadata = json.load(meta_file)

    selected_files = get_selected_files()
    if not selected_files:
        print("Нет выбранных файлов для загрузки в индекс.")
        return
    print(selected_files)

    all_embeddings = []
    all_chunks = []
    all_metadata = []

    for filename in selected_files:
        if filename not in metadata:
            continue

        file_info = metadata[filename]
        embeddings = np.load(file_info["embedding_file"])
        with open(file_info["chunks_file"], "r", encoding="utf-8") as f:
            chunks = json.load(f)
        
        all_embeddings.append(embeddings)
        all_chunks.extend([chunks[str(index)]["text"] for index in range(len(chunks))])
        all_metadata.extend([(filename, chunks[str(index)]["page"]) for index in range(len(chunks))])

    if not all_embeddings:
        print("Нет эмбеддингов для добавления в индекс.")
        return

    all_embeddings = np.vstack(all_embeddings)
    
    dimension = 256
    M = 256
    efConstruction = 400
    index = faiss.IndexHNSWFlat(dimension, M)
    index.hnsw.efConstruction = efConstruction
    index.hnsw.efSearch = 256
    print("nice")
    
    tokenized_chunks = [preprocess_text(chunk) for chunk in all_chunks]
    bm25 = BM25Okapi(tokenized_chunks)
    
    index.add(all_embeddings)

    faiss.write_index(index, (os.path.join(RAG_PATH, f"index_{name}.faiss")))
    
    with open(os.path.join(RAG_PATH, f"metadata_{name}.pkl"), "wb") as f:
        pickle.dump(all_metadata, f)

    with open(os.path.join(RAG_PATH, f"chunks_{name}.pkl"), "wb") as f:
        pickle.dump(all_chunks, f)
       
    with open(os.path.join(RAG_PATH, f"bm25_{name}.pkl"), 'wb') as f:
        pickle.dump(bm25, f)

    print(f"Индекс сохранён. Записей: {index.ntotal}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Недостаточно параметров запуска")
        sys.exit(1)

    create_index(sys.argv[1])
