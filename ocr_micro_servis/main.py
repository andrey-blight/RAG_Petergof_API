import glob
import os
import aio_pika
import json
import api_ocr
import boto3
import asyncio
import logging
from dotenv import load_dotenv
from aio_pika import Exchange, Queue

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DIRECTORY_FOR_SAVE = "test_ocr_dir/result_pdf"

async def process_execution(request):
    """
    Processing one request
    """
    def delete_garbage(pdf_folder):
        """
        Removes unnecessary files.
        """
        for file_name in os.listdir(pdf_folder):
            if file_name.endswith(".json"):
                file_path = os.path.join(pdf_folder, file_name)
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.error(f'Не удалось удалить файл {file_path}. Ошибка: {str(e)}')
    
    try:
        load_dotenv()
        ACCESS_KEY = os.getenv("ACCESS_KEY")
        SECRET_KEY = os.getenv("SECRET_KEY_OCR")
        BUCKET_NAME = os.getenv("BUCKET_NAME")
        
        s3_client = boto3.client(
            "s3",
            endpoint_url="https://storage.yandexcloud.net",
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
        )
        
        if request['type'] == "convert":
            await asyncio.sleep(0.2)
            logger.info(f"Загрузка файла из S3: {request['link'] + request['title']}")
            s3_client.download_file(
                BUCKET_NAME,
                (request['link'] + request['title']),
                request['title']
            )
            logger.info(f"Файл загружен: {request['title']}")
            
            with open(request['title'], "rb") as file:
                pdf_bytes = file.read()
            
            logger.info(f"Отправка PDF на OCR обработку: {request['title']}")
            ocr = api_ocr.ApiOCR()
            json_data = await ocr.upload_pdf(
                pdf_file=pdf_bytes,
                pdf_name=request['title'][:-4],
                begin_page=request['path_index'] * 10
            )
            
            name_json = f"./{request['title'][:-4]}" + '.json'
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
            
            return {
                'title': request['title'],
                'link': DIRECTORY_FOR_SAVE,
                'path_index': request['path_index'],
                'status': 'success'
            }
        
        if request['type'] == "merge":
            await asyncio.sleep(0.2)
            logger.info(f"Загрузка файлов из S3: {request['link'] + request['title']}_*")
            
            for idx in request['path_index']:
                s3_client.download_file(
                    BUCKET_NAME,
                    f"{request['link']}{request['title']}_{idx}.json",
                    f"{request['title']}_{idx}.json"
                )
            logger.info(f"Файлы из {request['title']} загружены")
            
            logger.info(f"Мержим JSONs в один JSON: {request['title']}")
            file_pattern = f"./{request['title']}_*.json"
            files = glob.glob(file_pattern)
            files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
            
            merged_data = {
                "data": [
                    
                ]
            }
            for file in files:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    merged_data["data"] += data["data"]
            
            name_json = f"{request['title']}.json"
            logger.info(f"Сохранение JSON результата: {name_json}")
            with open(name_json, 'w', encoding='utf-8') as f:
                json.dump(merged_data, f, ensure_ascii=False, indent=4)
            
            logger.info(f"Файлы объеденны в {request['title']}")
                
            s3_upload_path = os.path.join(DIRECTORY_FOR_SAVE, os.path.basename(name_json))
            logger.info(f"Загрузка JSON в S3: {s3_upload_path}")
            s3_client.upload_file(
                name_json,
                BUCKET_NAME,
                s3_upload_path
            )
            
            return {
                'title': request['title'],
                'link': DIRECTORY_FOR_SAVE,
                'path_index': request['path_index'],
                'status': 'success'
            }
            
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса {request.get('path_index')}: {str(e)}", exc_info=True)
        return {
            'title': request['title'],
            'link': DIRECTORY_FOR_SAVE,
            'path_index': request['path_index'],
            'status': 'error',
            'error': str(e)
        }
    finally:
        delete_garbage("./")

async def process_message(message: aio_pika.IncomingMessage, response_exchange: Exchange):
    """
    Asynchronous processing of a single message
    """
    try:
        async with message.process():
            request = json.loads(message.body.decode())
            logger.info(f"Начало обработки заказа {request['path_index']}")
            
            result = await process_execution(request)
            response = {
                'title': result['title'],
                'link': result['link'],
                "path_index": result["path_index"],
                "status": result['status'],
                "error": result.get('error')
            }
            
            await response_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(response).encode(),
                    correlation_id=message.correlation_id
                ),
                routing_key=message.reply_to
            )
            logger.info(f"Заказ {request['path_index']} обработан, статус: {result['status']}")
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {str(e)}", exc_info=True)

async def create_worker(queue: Queue, response_exchange: Exchange):
    """
    Creates an asynchronous worker that processes messages one by one
    """
    try:
        async for message in queue:
            await process_message(message, response_exchange)
    except Exception as e:
        logger.error(f"Ошибка в worker: {str(e)}", exc_info=True)

async def setup_rabbitmq():
    """
    Setup RabbitMQ
    """
    try:
        connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)
        
        requests_exchange = await channel.declare_exchange("requests", aio_pika.ExchangeType.DIRECT)
        requests_queue = await channel.declare_queue("requests_processing", durable=True)
        await requests_queue.bind(requests_exchange, routing_key="convert")
        
        responses_exchange = await channel.declare_exchange("requests_responses", aio_pika.ExchangeType.DIRECT)
        
        logger.info("RabbitMQ подключение и настройка завершены")
        return connection, requests_queue, responses_exchange
    except Exception as e:
        logger.error(f"Ошибка при настройке RabbitMQ: {str(e)}", exc_info=True)
        raise

async def consume_orders():
    """
    The main function for consuming messages
    """
    try:
        logger.info("Запуск consumer для последовательной обработки запросов")
        connection, requests_queue, responses_exchange = await setup_rabbitmq()
        
        worker_task = asyncio.create_task(create_worker(requests_queue, responses_exchange))
        
        await asyncio.Future()
        
    except asyncio.CancelledError:
        logger.info("Получен сигнал остановки...")
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass
    except Exception as e:
        logger.error(f"Ошибка в consume_orders: {str(e)}", exc_info=True)
    finally:
        await connection.close()
        logger.info("Соединение с RabbitMQ закрыто")

if __name__ == "__main__":
    try:
        logger.info("Запуск OCR consumer сервиса...")
        asyncio.run(consume_orders())
    except KeyboardInterrupt:
        logger.info("Приложение остановлено пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}", exc_info=True)