import aio_pika
import json
import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def process_request(request_data, connection):
    """
    Sends one request and processes the response
    """
    channel = await connection.channel()
    
    requests_exchange = await channel.declare_exchange("requests", aio_pika.ExchangeType.DIRECT)
    responses_exchange = await channel.declare_exchange("request_responses", aio_pika.ExchangeType.DIRECT)
    
    response_queue = await channel.declare_queue(exclusive=True)
    await response_queue.bind(responses_exchange, routing_key=response_queue.name)
    
    message = aio_pika.Message(
        body=json.dumps(request_data).encode(),
        reply_to=response_queue.name,
        correlation_id=str(request_data['path_index'])
    )
    
    await requests_exchange.publish(message, routing_key="convert")
    logger.info(f"Заказ {request_data['path_index']} отправлен")
    
    async with response_queue.iterator() as queue_iter:
        async for message in queue_iter:
            if message.correlation_id == str(request_data['path_index']):
                response = json.loads(message.body.decode())
                logger.info(f"Ответ для заказа {request_data['path_index']}: {response}")
                await message.ack()
                break
    
    await channel.close()

async def main():
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    
    try:
        requests = []
        LINK_DIR = "test_ocr_dir/started_pdf/"
        
        # requests.append({
        #     "type": "convert",
        #     "link": LINK_DIR,
        #     "title": "7-й_Конгресс_18.05_0.pdf",
        #     "path_index": 0
        # })
        
        # requests.append({
        #     "type": "convert",
        #     "link": LINK_DIR,
        #     "title": "7-й_Конгресс_18.05_1.pdf",
        #     "path_index": 1
        # })
        
        requests.append({
            "type": "merge",
            "link": "test_ocr_dir/result_pdf/",
            "title": "7-й_Конгресс_18.05",
            "path_index": [0, 1]
        })
        
        logger.info("Начало обработки запросов")
        await asyncio.gather(*[process_request(request, connection) for request in requests])
        logger.info("Все запросы обработаны")
    
    except Exception as e:
        logger.error(f"Ошибка в main: {str(e)}", exc_info=True)
    finally:
        await connection.close()
        logger.info("Соединение закрыто")

if __name__ == "__main__":
    try:
        logger.info("Запуск сервиса")
        asyncio.run(main())
        logger.info("Сервис завершил работу")
    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}", exc_info=True)