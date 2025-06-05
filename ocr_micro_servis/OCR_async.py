import os
import base64
import asyncio
import aiohttp
import logging
from PyPDF2 import PdfReader, PdfWriter

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class YandexOCRAsync:
    def __init__(self, iam_token, folder_id):
        """
        Initialize Yandex OCR client with async support
        """
        self.iam_token = iam_token
        self.folder_id = folder_id
        self.headers = {
            "Authorization": f"Bearer {iam_token}",
            "x-folder-id": folder_id
        }

    def encode_pdf(self, file_path):
        """Encode PDF file to Base64."""
        try:
            with open(file_path, 'rb') as file:
                encoded = base64.b64encode(file.read()).decode('utf-8')
                return encoded
        except Exception as e:
            logger.error(f"Ошибка кодирования файла {file_path}: {str(e)}", exc_info=True)
            raise

    def split_pdf(self, input_path, pages_per_chunk=1):
        """
        Split PDF into smaller chunks.
        """
        try:
            chunks = []
            reader = PdfReader(input_path)
            total_pages = len(reader.pages)

            for start_page in range(0, total_pages, pages_per_chunk):
                end_page = min(start_page + pages_per_chunk, total_pages)
                writer = PdfWriter()

                for page_num in range(start_page, end_page):
                    writer.add_page(reader.pages[page_num])

                chunk_path = f"./temp_chunk_{start_page}.pdf"
                with open(chunk_path, 'wb') as output:
                    writer.write(output)
                chunks.append((chunk_path, start_page))

            return chunks
        except Exception as e:
            logger.error(f"Ошибка при разделении PDF: {str(e)}", exc_info=True)
            raise

    async def recognize_pdf(self, session, file_path):
        """
        Async submit PDF for OCR recognition.
        """
        url = "https://ocr.api.cloud.yandex.net/ocr/v1/recognizeTextAsync"
        logger.debug(f"Отправка запроса распознавания для {file_path}")

        body = {
            "mimeType": "application/pdf",
            "languageCodes": ["*"],
            "model": "page",
            "content": self.encode_pdf(file_path)
        }
        
        retry_count = 0
        current_delay = 0.3
        
        while retry_count < 3:
            try:
                
                async with session.post(
                        url,
                        headers={**self.headers, "Content-Type": "application/json"},
                        json=body
                ) as response:
                    if response.status == 429:
                        await asyncio.sleep(current_delay)
                        retry_count += 1
                        continue
                    
                    if response.status == 200:
                        data = await response.json()
                        operation_id = data.get("id")
                        if not operation_id:
                            logger.error(f"Не удалось получить ID операции для файла {file_path}")
                            return None
                        logger.debug(f"Успешно отправлен запрос распознавания, ID операции: {operation_id}")
                        return operation_id
                    
                    error_text = await response.text()
                    logger.error(f"Ошибка распознавания (код {response.status}): {error_text}")
                    return None
                
            except Exception as e:
                logger.error(f"Ошибка в recognize_pdf: {str(e)}", exc_info=True)
                return None

    async def get_operation_result(self, session, operation_id, max_retries=10, delay=10):
        """
        Async get OCR operation result with retries.
        """
        url = f"https://ocr.api.cloud.yandex.net/ocr/v1/getRecognition?operationId={operation_id}"
        logger.debug(f"Запрос результата операции {operation_id}")

        for attempt in range(max_retries):
            try:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.debug(f"Успешно получен результат для операции {operation_id}")
                        return result
                    elif response.status == 404:
                        logger.debug(f"Операция {operation_id} еще выполняется (попытка {attempt+1}/{max_retries})")
                        await asyncio.sleep(delay)
                    else:
                        error_text = await response.text()
                        logger.warning(f"Ошибка запроса результата (код {response.status}): {error_text}")
                        return None
            except Exception as e:
                logger.warning(f"Ошибка при запросе результата (попытка {attempt+1}): {str(e)}")
        
        logger.error(f"Превышено максимальное количество попыток ({max_retries}) для операции {operation_id}")
        return None

    def extract_text_from_result(self, ocr_result):
        """
        Extract text blocks with coordinates & bounding box from the OCR result.
        """
        try:
            full_text = []

            if not ocr_result or 'result' not in ocr_result:
                logger.warning("Пустой результат OCR или отсутствует ключ 'result'")
                return ""

            result = ocr_result['result']
            t_annot = result.get('textAnnotation', {})
            blocks = t_annot.get('blocks', [])

            for block in blocks:
                for line in block.get('lines', []):
                    if 'text' not in line:
                        continue
                    full_text.append(line['text'])

            extracted_text = '\n'.join(full_text)
            return extracted_text
        except Exception as e:
            logger.error(f"Ошибка извлечения текста: {str(e)}", exc_info=True)
            return ""

    async def process_chunk(self, session, chunk_path, page_number, semaphore):
        """
        Process single PDF chunk with semaphore for concurrency control.
        """
        async with semaphore:
            try:
                operation_id = await self.recognize_pdf(session, chunk_path)
                if operation_id is None:
                    raise Exception("Не удалось получить ID операции распознавания")
                
                ocr_result = await self.get_operation_result(session, operation_id)
                if not ocr_result:
                    raise Exception("Не удалось получить результат распознавания")
                
                result = {
                    "page": page_number + 1,
                    "text": self.extract_text_from_result(ocr_result)
                }
                return result
            except Exception as e:
                logger.error(f"Ошибка обработки чанка {chunk_path}: {str(e)}", exc_info=True)
                return {
                    "page": page_number + 1,
                    "text": "",
                    "error": str(e)
                }

    async def process_pdf(self, input_path, max_concurrent=10):
        """
        Main method to process entire PDF with parallel chunk processing.
        """
        try:
            logger.info(f"Начало обработки PDF файла: {input_path}")
            logger.info(f"Максимальное количество параллельных запросов: {max_concurrent}")
            
            chunks = self.split_pdf(input_path)
            semaphore = asyncio.Semaphore(max_concurrent)

            async with aiohttp.ClientSession() as session:
                tasks = [
                    asyncio.create_task(self.process_chunk(session, chunk_path, page_number, semaphore))
                    for page_number, (chunk_path, _) in enumerate(chunks)
                ]
                
                ocr_results = await asyncio.gather(*tasks)
                
                # Удаление временных файлов чанков
                for chunk_path, _ in chunks:
                    try:
                        os.remove(chunk_path)
                    except Exception as e:
                        logger.warning(f"Не удалось удалить временный файл {chunk_path}: {str(e)}")
                
                sorted_results = sorted(ocr_results, key=lambda x: x["page"])
                logger.info(f"Обработка PDF {input_path} завершена, получено {len(sorted_results)} результатов")
                return sorted_results
        except Exception as e:
            logger.error(f"Критическая ошибка в process_pdf: {str(e)}", exc_info=True)
            raise