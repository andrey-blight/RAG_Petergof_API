import asyncio
import os
import subprocess
import logging
from OCR_async import YandexOCRAsync
from dotenv import load_dotenv
# from rag import create_embeddings

# Настройка логирования
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

    async def upload_pdf(self, pdf_file: bytes, pdf_name: str):
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
                logger.debug("Попытка получения IAM токена")
                result = subprocess.run(["yc", "iam", "create-token"], 
                                       capture_output=True,
                                       text=True, 
                                       check=True)
                logger.debug("IAM токен успешно получен")
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
                all_jsons = await ocr.process_pdf(pdf_path)
                logger.info(f"OCR обработка завершена, получено {len(all_jsons) if all_jsons else 0} результатов")
            except Exception as e:
                logger.error(f"Ошибка при обработке PDF: {str(e)}", exc_info=True)
                self.change_running(False)
                delete_garbage(pdf_folder=CURRENT_DIRECTORY)
                return None

            # Filter json 
            initial_count = len(all_jsons) if all_jsons else 0
            all_jsons = [item for item in all_jsons if isinstance(item["text"], str)]
            filtered_count = len(all_jsons)
            
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