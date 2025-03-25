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
from get_indexes import get_indexes
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

def create_index(name, selected_files):
    if name in get_indexes():
        print("Индекс с таким именем уже существует")
        return
    
    meta_path = os.path.join(METADATA_PATH, "metadata.json")
    if not os.path.exists(meta_path):
        print("Нет сохранённого индекса.")
        return

    with open(meta_path, "r", encoding="utf-8") as meta_file:
        metadata = json.load(meta_file)

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
        all_chunks.extend([elem["text"] for elem in chunks['data']])
        all_metadata.extend([(filename, elem["page"]) for elem in chunks['data']])

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
    
    list_indexes_path = os.path.join(METADATA_PATH, "list_indexes.json")
    list_indexes = {}
    if os.path.exists(list_indexes_path):
        with open(list_indexes_path, "r", encoding="utf-8") as f:
            list_indexes = json.load(f)
            
    list_indexes[name] = {"files": selected_files}
    with open(os.path.join(list_indexes_path), "w", encoding="utf-8") as f:
        json.dump(list_indexes, f, ensure_ascii=False, indent=4)
    
    print(f"Индекс сохранён. Записей: {index.ntotal}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Недостаточно параметров запуска")
        sys.exit(1)
    
    lst = ['ещание_Петра_Великого_Российская_история_2010.txt', 'bd3ef0b4c0389a171f8f2e7.txt', 'Военные_журналы_юрналы_Петра_1.txt']

    create_index(sys.argv[1], lst)
