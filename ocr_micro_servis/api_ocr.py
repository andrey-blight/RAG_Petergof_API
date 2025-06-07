import asyncio
import json
import boto3
import os
import subprocess
import logging
from OCR_async import YandexOCRAsync
from dotenv import load_dotenv
# from rag import create_embeddings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ApiOCR:
    def __init__(self):
        self.running_ocr = False

    def change_running(self, value: bool):
        self.running_ocr = value

    async def is_running(self):
        """
        Return state of processing
        """
        state = self.running_ocr
        return state

    async def upload_pdf(self, pdf_file: bytes, pdf_name: str, begin_page: int):
        """
        Convert pdf file to json and txt, upload their into S3 
        """

        def delete_garbage(pdf_folder):
            """
            Removes unnecessary files.
            """
            for file_name in os.listdir(pdf_folder):
                if file_name.startswith(f"{pdf_name}") or file_name.endswith(".pdf") \
                    or file_name.endswith(".json"):
                    file_path = os.path.join(pdf_folder, file_name)
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        logger.error(f'Не удалось удалить файл {file_path}. Ошибка: {str(e)}')

        def get_iam_token():
            """
            Get IAM-token
            """
            try:
                result = subprocess.run(["yc", "iam", "create-token"], 
                                       capture_output=True,
                                       text=True, 
                                       check=True)
                return result.stdout.strip()
            except subprocess.CalledProcessError as e:
                logger.error(f"Ошибка при получении токена: {e.stderr}", exc_info=True)
                return None
            except Exception as e:
                logger.error(f"Неожиданная ошибка при получении токена: {str(e)}", exc_info=True)
                return None

        try:
            self.change_running(True)
            logger.info(f"Начало обработки PDF: {pdf_name}")
            
            load_dotenv()
            FOLDER_ID = os.getenv("FOLDER_ID")
            IAM_TOKEN = get_iam_token()

            ocr = YandexOCRAsync(IAM_TOKEN, FOLDER_ID)

            CURRENT_DIRECTORY = "./"
            pdf_path = os.path.join(CURRENT_DIRECTORY, pdf_name)
            
            with open(pdf_path, "wb") as f:
                f.write(pdf_file)

            # Send a pdf file for processing
            processed_files = []
            logger.info(f"Начало OCR обработки файла: {pdf_path}")
            
            try:
                all_jsons = await ocr.process_pdf(
                    input_path=pdf_path,
                    input_name=pdf_name,
                    begin_page=begin_page
                )
                logger.info(f"OCR обработка завершена, получено {len(all_jsons) if all_jsons else 0} результатов")
            except Exception as e:
                logger.error(f"Ошибка при обработке PDF: {str(e)}", exc_info=True)
                self.change_running(False)
                delete_garbage(pdf_folder=CURRENT_DIRECTORY)
                return None

            # Filter json 
            all_jsons = [item for item in all_jsons if isinstance(item["text"], str)]
            
            processed_files += all_jsons
            processed_files.sort(key=lambda x: x["page"])

            # Save processed file
            result_json = {
                "data": processed_files
            }

            delete_garbage(pdf_folder=CURRENT_DIRECTORY)
            
            # create_embeddings(pdf_name_txt)
            self.change_running(False)
            logger.info(f"Успешно завершена обработка PDF: {pdf_name}")
            return result_json

        except Exception as e:
            logger.error(f"Критическая ошибка в upload_pdf: {str(e)}", exc_info=True)
            self.change_running(False)
            delete_garbage(pdf_folder=CURRENT_DIRECTORY)
            return None

if __name__ == "__main__":
    
    load_dotenv()
    ACCESS_KEY = os.getenv("ACCESS_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY_OCR")
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    DIRECTORY_FOR_SAVE = "test_ocr_dir/result_pdf"
    
    s3_client = boto3.client(
        "s3",
        endpoint_url="https://storage.yandexcloud.net",
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
    )
    
    type = "convert"
    link =  LINK_DIR = "test_ocr_dir/started_pdf/"
    title = "7-й_Конгресс_18.05_0.pdf"
    path_index = "0"
    
    logger.info(f"Загрузка файла из S3: {link + title}")
    s3_client.download_file(
        BUCKET_NAME,
        (link + title),
        title
    )
    logger.info(f"Файл загружен: {title}")
    
    with open(title, "rb") as file:
        pdf_bytes = file.read()
    
    logger.info(f"Отправка PDF на OCR обработку: {title}")
    ocr = ApiOCR()
    json_data = asyncio.run(ocr.upload_pdf(
        pdf_file=pdf_bytes,
        pdf_name=title[:-4]
    ))
    
    name_json = f"./{title[:-4]}" + '.json'
    logger.info(f"Сохранение JSON результата: {name_json}")
    with open(name_json, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)
        
    s3_upload_path = os.path.join(DIRECTORY_FOR_SAVE, os.path.basename(name_json))
    logger.info(f"Загрузка JSON в S3: {s3_upload_path}")
    s3_client.upload_file(
        name_json,
        BUCKET_NAME,
        s3_upload_path
    )