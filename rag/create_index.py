import os
import faiss
import numpy as np
import pickle
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from transformers import AutoModel, AutoTokenizer
import torch

load_dotenv()
DATA_DIR = os.getenv("DATA_DIR")


def create_index():
    
    folder_path = f"knowledge/{DATA_DIR}"
    file_texts = {}

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as file:
                file_texts[filename] = file.read()

    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=400)
    chunks = []
    metadata = []

    for filename, text in file_texts.items():
        file_chunks = splitter.split_text(text)
        chunks.extend(file_chunks)
        metadata.extend([filename] * len(file_chunks))

    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(chunks)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))

    faiss.write_index(index, "data/text_index.faiss")

    with open("data/metadata.pkl", "wb") as f:
        pickle.dump(metadata, f)

    with open("data/chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)

    print("Индекс и метаданные успешно сохранены.")
    
    
if __name__ == "__main__":
    create_index()
