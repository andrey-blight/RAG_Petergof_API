import faiss
import numpy as np
import pickle
import sys
import os
from time import time
from sentence_transformers import SentenceTransformer
from yandex_cloud_ml_sdk import YCloudML
from transformers import AutoModel, AutoTokenizer
import torch
from dotenv import load_dotenv
import boto3
import io

from rank_bm25 import BM25Okapi
import re
from collections import defaultdict

load_dotenv()

YC_API_KEY = os.getenv("YC_API_KEY")
YC_FOLDER_ID = os.getenv("YC_FOLDER_ID")
ACCESS_KEY=os.getenv("ACCESS_KEY")
SECRET_KEY=os.getenv("SECRET_KEY_OCR")
BUCKET_NAME = "markup-baket"
RAG_PATH = "data/rag"

def preprocess_text(text):
    text = re.sub(r"[^\w\s]", "", text).lower()
    return text.split()


async def get_answer(index_name, question):
    t = time()
    s3_client = boto3.client(
        "s3",
        endpoint_url="https://storage.yandexcloud.net",
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
    )
    # index = faiss.read_index(f"data/rag/index_{index_name}.faiss")
    
    LOCAL_FILE = f"/tmp/index_{index_name}.faiss"
    
    s3_client.download_file(BUCKET_NAME, f"{RAG_PATH}/index_{index_name}.faiss", LOCAL_FILE)
    index = faiss.read_index(LOCAL_FILE)
    os.remove(LOCAL_FILE)
    
    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=f"{RAG_PATH}/metadata_{index_name}.pkl")
    pickle_buffer = io.BytesIO(response['Body'].read())
    metadata = pickle.load(pickle_buffer)

    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=f"{RAG_PATH}/chunks_{index_name}.pkl")
    pickle_buffer = io.BytesIO(response['Body'].read())
    chunks = pickle.load(pickle_buffer)
        
    # with open(f"data/rag/bm25_{index_name}.pkl", "rb") as f:
    #     bm25 = pickle.load(f)
    
    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=f"{RAG_PATH}/bm25_{index_name}.pkl")
    pickle_buffer = io.BytesIO(response['Body'].read())
    bm25 = pickle.load(pickle_buffer)
        
    print("Openings:", time() - t)
    t = time()
    
    sdk = YCloudML(
        folder_id=YC_FOLDER_ID,
        auth=YC_API_KEY,
    )

    query_model = sdk.models.text_embeddings("query")
    query_embedding = np.array([query_model.run(question)], dtype=np.float32)
    print("Querry embedding:", time() - t)
    t = time()
    
    top_k = 18
    distances, indices = index.search(query_embedding, top_k)
    print("Index search:", time() - t)
    t = time()
    
    top_k_bm25 = 3
    bm25_scores = bm25.get_scores(preprocess_text(question))
    top_bm25_indices = np.argsort(bm25_scores)[-top_k_bm25:][::-1]
    print("BM25 search:", time() - t)
    t = time()

    result = ""
    for i, idx in enumerate(indices[0]):
        if idx < len(chunks):
            result += f"Текст {i+1}:\nФайл: {metadata[idx][0]}, страница: {metadata[idx][1]}\nТекст: {chunks[idx]}\n\n"
    
    for i, idx in enumerate(top_bm25_indices):
        result += f"Текст {top_k + i + 1} (BM25):\nФайл: {metadata[idx]}\nТекст: {chunks[idx]}\n\n"
    messages = [
        {
            "role": "user",
            "text": f"Вы ассистируете научного руководителя музейного комплекса Петергоф. Ниже вам дан контекст, откуда брать информацию. Разрешено брать сразу несколько текстов. Отвечайте на вопросы, которые он задает. Игнорируйте контекст, если считаете его нерелевантным. Ответь на вопрос: {question}. Вместе с ответом также напишите название файла и страницу, откуда была взята информация.\nКонтекст:\n" + result,
        },
    ]
    print("Forming result:", time() - t)
    t = time()
    # print(result)
    resultt = sdk.models.completions("yandexgpt").configure(temperature=0.2).run(messages)
    print("YaGPT time:", time() - t)
    
    return resultt[0].text

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Недостаточно параметров запуска")
        sys.exit(1)
    
    index_name = sys.argv[1]
    question = sys.argv[2]
    result = get_answer(index_name, question)
    
    print(result)
    

    