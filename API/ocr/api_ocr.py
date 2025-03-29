import os
import json
import boto3
import subprocess
from OCR_async import YandexOCRAsync
from dotenv import load_dotenv

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
                if file_name.endswith(".pdf") \
                    or file_name.endswith(".txt") \
                    or file_name.endswith(".json"):
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
                result = subprocess.run(["yc", "iam", "create-token"], capture_output=True, text=True, check=True)
                return result.stdout.strip()
            except subprocess.CalledProcessError as e:
                print(f"Error getting token: {e.stderr}")
                return None

        self.change_running(True)
        load_dotenv("consts.env")
        FOLDER_ID = os.getenv("FOLDER_ID")
        ACCESS_KEY = os.getenv("ACCESS_KEY")
        SECRET_KEY = os.getenv("SECRET_KEY")
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
        print(f"Обрабатываем файл: {pdf_name}")
        all_jsons = await ocr.process_pdf(pdf_name)
        print(f"Распознанный текст сохранён")
        
        processed_files += all_jsons
        processed_files.sort(key=lambda x: x["page"])

        # Save processed file
        result_json = {
            "data": processed_files
        }
        pdf_name_json = pdf_name + '.json'
        with open(pdf_name_json, "w", encoding="utf-8") as f:
            json.dump(result_json, f, indent=4, ensure_ascii=False)

        s3_client.upload_file(
            pdf_name_json,
            BUCKET_NAME,
            os.path.join("started_pdf", os.path.basename(pdf_name_json))
        )
        print(f"Файл {pdf_name_json} загружен в бакет {BUCKET_NAME} / started_pdf")
        
        try:
            pdf_name_txt = pdf_name + '.txt'
            with open(pdf_name_txt, 'w', encoding='utf-8') as f:
                f.write("\n".join(item["text"] for item in processed_files))
            
            s3_client.upload_file(
                pdf_name_txt,
                BUCKET_NAME,
                os.path.join("started_pdf", os.path.basename(pdf_name_txt))
            )
            print(f"Файл {pdf_name_txt} загружен в бакет {BUCKET_NAME} / started_pdf")
        except:
            print("Текст содержит вложенные структуры данных")
            
        delete_garbage(pdf_folder=CURRENT_DIRECTORY) 
        self.change_running(False)
        