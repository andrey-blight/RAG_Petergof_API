import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
YANDEX_API_KEY = os.getenv("YC_API_KEY")
YANDEX_FOLDER_ID = os.getenv("YC_FOLDER_ID")


async def get_indexes(to_sort=False):
    '''
    Возвращает список названий всех индексов
    names = ['name1', 'name2', ..., 'nameN']
    По умолчанию возвращает в порядке создания индексов.
    '''
    client = AsyncOpenAI(
        api_key=YANDEX_API_KEY,
        base_url="https://ai.api.cloud.yandex.net/v1",
        project=YANDEX_FOLDER_ID,
    )

    vector_stores = await client.vector_stores.list()
    names = []
    for i in vector_stores.data:
        names.append(i.name)

    if to_sort:
        names = list(sorted(names))

    return names


async def get_indexes_names_and_ids(to_sort=False):
    '''
    Возвращает список кортежей названий и айдишников всех индексов
    names = [('name1', 'id1'), ('name2', 'id2'), ..., ('nameN', 'idN')]
    По умолчанию возвращает в порядке создания индексов.
    '''
    client = AsyncOpenAI(
        api_key=YANDEX_API_KEY,
        base_url="https://ai.api.cloud.yandex.net/v1",
        project=YANDEX_FOLDER_ID,
    )

    vector_stores = await client.vector_stores.list()
    res = []
    for i in vector_stores.data:
        res.append((i.name, i.id))

    if to_sort:
        res = list(sorted(res, key=lambda x: x[0]))

    return res
