import asyncio
import os
import json
import base64
import boto3
import subprocess
from OCR_async import YandexOCRAsync
from dotenv import load_dotenv
# from rag import create_embeddings

class ApiOCR:
    def __init__(self):
        self.running_ocr = False

    def change_running(self, value: bool):
        self.running_ocr = value

    async def is_running(self):
        """
        Return state of processing
        """
        return self.running_ocr

    async def upload_pdf(self, pdf_file: bytes, pdf_name: str):
        """
        Convert pdf file to json and txt, upload their into S3 
        """

        def delete_garbage(pdf_folder):
            """
            Removes unnecessary files.
            """
            for file_name in os.listdir(pdf_folder):
                if file_name.startswith(f"{pdf_name}") \
                    or file_name.endswith(".pdf"):
                    file_path = os.path.join(pdf_folder, file_name)
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f'Не удалось удалить файл {file_path}. Ошибка: {e}')

        def get_iam_token():
            """
            Get IAM-token
            """
            try:
                result = subprocess.run(["yc", "iam", "create-token"], capture_output=True,
                                        text=True, check=True)
                return result.stdout.strip()
            except subprocess.CalledProcessError as e:
                print(f"Error getting token: {e.stderr}")
                return None

        self.change_running(True)
        load_dotenv()
        FOLDER_ID = os.getenv("FOLDER_ID")
        ACCESS_KEY = os.getenv("ACCESS_KEY")
        SECRET_KEY = os.getenv("SECRET_KEY_OCR")
        BUCKET_NAME = os.getenv("BUCKET_NAME")
        IAM_TOKEN = get_iam_token()

        s3_client = boto3.client(
            "s3",
            endpoint_url="https://storage.yandexcloud.net",
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
        )

        ocr = YandexOCRAsync(IAM_TOKEN, FOLDER_ID)

        CURRENT_DIRECTORY = "./"
        pdf_path = os.path.join(CURRENT_DIRECTORY, pdf_name)
        with open(pdf_path, "wb") as f:
            f.write(pdf_file)

        # Send a pdf file for processing
        processed_files = []
        print(f"Обрабатываем файл: {pdf_path}")
        try:
            all_jsons = await ocr.process_pdf(pdf_path)
        except Exception as e:
            print(e)
            self.change_running(False)
            delete_garbage(pdf_folder=CURRENT_DIRECTORY)
            return
        print(f"Распознанный текст сохранён")

        # Filter json 
        all_jsons = [item for item in all_jsons if isinstance(item["text"], str)]
        processed_files += all_jsons
        processed_files.sort(key=lambda x: x["page"])

        # Save processed file
        result_json = {
            "data": processed_files
        }
        pdf_name_json = f"./{pdf_name}" + '.json'
        with open(pdf_name_json, "w", encoding="utf-8") as f:
            json.dump(result_json, f, indent=4, ensure_ascii=False)

        s3_client.upload_file(
            pdf_name_json,
            BUCKET_NAME,
            os.path.join("test_ocr_dir", os.path.basename(pdf_name_json))
        )
        print(f"Файл {pdf_name_json} загружен в бакет {BUCKET_NAME}/knowledge/data_0")

        pdf_name_txt = f"./{pdf_name}.txt"
        with open(pdf_name_txt, 'w', encoding='utf-8') as f:
            f.write("\n".join(item["text"] for item in processed_files))

        s3_client.upload_file(
            pdf_name_txt,
            BUCKET_NAME,
            os.path.join("test_ocr_dir", os.path.basename(pdf_name_txt))
        )
        print(f"Файл {pdf_name_txt} загружен в бакет {BUCKET_NAME} / started_pdf")

        delete_garbage(pdf_folder=CURRENT_DIRECTORY)
        
        # create_embeddings(pdf_name_txt)
        self.change_running(False)
        return result_json