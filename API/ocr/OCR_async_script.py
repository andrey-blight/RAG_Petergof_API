import os
import json
import boto3
import re
import asyncio
from OCR_async import YandexOCRAsync 
from dotenv import load_dotenv, dotenv_values, set_key
from pathlib import Path 

is_running = False
def change_running(value: bool):
    is_running = value

def delete_garbage(pdf_folder):
    """
    Removes unnecessary files.
    """
    for file_name in os.listdir(pdf_folder):
        if file_name.startswith("temp_") \
            or file_name.endswith(".txt") \
            or file_name.endswith(".json"):
            file_path = os.path.join(pdf_folder, file_name)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f'Не удалось удалить файл {file_path}. Ошибка: {e}')


change_running(True)
load_dotenv("consts.env")

FOLDER_ID = os.getenv("FOLDER_ID")
IAM_TOKEN = os.getenv("IAM_TOKEN")
ACCESS_KEY=os.getenv("ACCESS_KEY")
SECRET_KEY=os.getenv("SECRET_KEY")
BUCKET_NAME = "markup-baket"

s3_client = boto3.client(
    "s3",
    endpoint_url="https://storage.yandexcloud.net",
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)

ocr = YandexOCRAsync(IAM_TOKEN, FOLDER_ID)

PDF_FOLDER = "./new_pdf_files"
CURRENT_DIRECTORY = "./"

pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]
pdf_path = ""

# Copy pdfiles current directory
for pdf_file in pdf_files:
    src_path = os.path.join(PDF_FOLDER, pdf_file)
    dst_path = os.path.join(CURRENT_DIRECTORY, pdf_file)
    with open(src_path, "rb") as src, open(dst_path, "wb") as dst:
        dst.write(src.read())

for pdf_file in pdf_files:
    delete_garbage(pdf_folder=CURRENT_DIRECTORY)
    
    pdf_path = os.path.join(CURRENT_DIRECTORY, pdf_file)
    file_name = os.path.splitext(pdf_file)[0]
    
    # Send a pdf file for processing
    processed_files = []
    print(f"Обрабатываем файл: {pdf_file}")
    all_jsons = asyncio.run(ocr.process_pdf(pdf_file))
    print(f"Распознанный текст сохранён")
    
    processed_files += all_jsons
    processed_files.sort(key=lambda x: x["page"])

    # Save processed file
    result_json = {
        "data": processed_files
    }
    file_name_json = file_name + '.json'
    with open(file_name_json, "w", encoding="utf-8") as f:
        json.dump(result_json, f, indent=4, ensure_ascii=False)

    s3_client.upload_file(
        file_name_json,
        BUCKET_NAME,
        os.path.join("started_pdf", os.path.basename(file_name_json))
    )
    print(f"Файл {file_name_json} загружен в бакет {BUCKET_NAME} / started_pdf")
    
    try:
        file_name_txt = file_name + '.txt'
        with open(file_name_txt, 'w', encoding='utf-8') as f:
            f.write("\n".join(item["text"] for item in processed_files))
        
        s3_client.upload_file(
            file_name_txt,
            BUCKET_NAME,
            os.path.join("started_pdf", os.path.basename(file_name_txt))
        )
        print(f"Файл {file_name_txt} загружен в бакет {BUCKET_NAME} / started_pdf")
    except:
        print("Текст содержит вложенные структуры данных")
        
    delete_garbage(pdf_folder=CURRENT_DIRECTORY)
    
for pdf_file in pdf_files:
    os.remove(pdf_file)
change_running(False)