import faiss
import asyncio
import numpy as np
import pickle
import os
from sentence_transformers import SentenceTransformer
from yandex_cloud_ml_sdk import YCloudML

from dotenv import load_dotenv

load_dotenv()

YC_API_KEY = os.getenv("YC_API_KEY")
YC_FOLDER_ID = os.getenv("YC_FOLDER_ID")


async def get_answer(question):
    index = faiss.read_index("rag/data/text_index.faiss")
    with open("rag/data/metadata.pkl", "rb") as f:
        metadata = pickle.load(f)

    with open("rag/data/chunks.pkl", "rb") as f:
        chunks = pickle.load(f)

    model = SentenceTransformer('all-MiniLM-L6-v2')
    question_embedding = model.encode([question])

    k = 5
    distances, indices = index.search(np.array(question_embedding), k)

    result = ""

    for i, idx in enumerate(indices[0]):
        file_name = metadata[idx]
        text_chunk = chunks[idx]
        result += f"Текст {i + 1}:\nФайл: {file_name}\nТекст: {text_chunk}\n"

    messages = [
        {
            "role": "user",
            "text": f"Вы ассистируете научного руководителя музейного комплекса Петергоф. Ниже вам дан контекст, откуда брать информацию. Отвечайте на вопросы, которые он задает. Игнорируйте контекст, если считаете его нерелевантным. Ответь на вопрос: {question}. Вместе с ответом также пишите из какого файла взята информация." + result,
        },
    ]

    sdk = YCloudML(
        folder_id=YC_FOLDER_ID,
        auth=YC_API_KEY,
    )

    result = sdk.models.completions("yandexgpt").configure(temperature=0.2).run(messages)

    return result[0].text


if __name__ == "__main__":
    question = "Что стало самой яркой чертой преобразований русского двора?"
    res = asyncio.run(get_answer(question))

    print(res)
