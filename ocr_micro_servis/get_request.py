import aio_pika
import json
import api_ocr
import base64
import asyncio
from aio_pika import Exchange, Queue

async def process_execution(order):
    """
    Processing one order
    """
    if order['type'] == "convert":
        await asyncio.sleep(0.1)
        ocr = api_ocr.ApiOCR()
        new_file = base64.b64decode(order['path'])
        json_data = await ocr.upload_pdf(
            pdf_file=new_file, 
            pdf_name=order['file_name']
        )
        return {
            'order_id': order['order_id'],
            'status': 'success',
            'json_data': json_data
        }

async def process_message(message: aio_pika.IncomingMessage, response_exchange: Exchange):
    """
    Asynchronous processing of a single message
    """
    async with message.process():
        order = json.loads(message.body.decode())
        print(f"Начало обработки заказа {order['order_id']}")
        
        result = await process_execution(order)
        response = {
            "order_id": order["order_id"],
            "status": result['status'],
            "result": result.get('json_data')
        }
        
        await response_exchange.publish(
            aio_pika.Message(
                body=json.dumps(response).encode(),
                correlation_id=message.correlation_id
            ),
            routing_key=message.reply_to
        )
        print(f"Заказ {order['order_id']} успешно обработан")

async def create_worker(queue: Queue, response_exchange: Exchange):
    """
    Creates an asynchronous worker
    """
    async for message in queue:
        asyncio.create_task(process_message(message, response_exchange))

async def setup_rabbitmq():
    """Setup RabbitMQ"""
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)
    
    orders_exchange = await channel.declare_exchange("orders", aio_pika.ExchangeType.DIRECT)
    orders_queue = await channel.declare_queue("order_processing", durable=True)
    await orders_queue.bind(orders_exchange, routing_key="convert")
    
    responses_exchange = await channel.declare_exchange("order_responses", aio_pika.ExchangeType.DIRECT)
    
    return connection, orders_queue, responses_exchange

async def consume_orders(num_workers: int = 10):
    """
    The main function for consuming messages
    """
    connection, orders_queue, responses_exchange = await setup_rabbitmq()
    
    workers = [create_worker(orders_queue, responses_exchange) for _ in range(num_workers)]
    
    try:
        await asyncio.gather(*workers)
    except asyncio.CancelledError:
        print("Получен сигнал остановки...")
    finally:
        await connection.close()
        print("Соединение с RabbitMQ закрыто")

if __name__ == "__main__":
    try:
        print("Запуск consumer'а...")
        asyncio.run(consume_orders(num_workers=10))
    except KeyboardInterrupt:
        print("Приложение остановлено пользователем")