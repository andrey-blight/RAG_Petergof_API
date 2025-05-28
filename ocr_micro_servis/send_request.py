import aio_pika
import json
import base64
import asyncio

async def process_order(order_data, connection):
    """
    Sends one order and processes the response
    """
    channel = await connection.channel()
    
    orders_exchange = await channel.declare_exchange("orders", aio_pika.ExchangeType.DIRECT)
    responses_exchange = await channel.declare_exchange("order_responses", aio_pika.ExchangeType.DIRECT)
    
    response_queue = await channel.declare_queue(exclusive=True)
    await response_queue.bind(responses_exchange, routing_key=response_queue.name)
    
    message = aio_pika.Message(
        body=json.dumps(order_data).encode(),
        reply_to=response_queue.name,
        correlation_id=str(order_data['order_id'])
    )
    
    await orders_exchange.publish(message, routing_key="convert")
    print(f"Заказ {order_data['order_id']} отправлен")
    
    async with response_queue.iterator() as queue_iter:
        async for message in queue_iter:
            if message.correlation_id == str(order_data['order_id']):
                response = json.loads(message.body.decode())
                print(f"Ответ для заказа {order_data['order_id']}: {response}")
                await message.ack()
                break
    
    await channel.close()

async def main():
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    
    try:
        orders = []
        
        with open('Морские_сражения_русского_флота_Воспоминания,_дневники,_письма_Сборник-1-5.pdf', 'rb') as file:
            pdf_bytes = base64.b64encode(file.read()).decode('utf-8')
        
        orders.append({
            "order_id": 1,
            "type": "convert",
            "path": pdf_bytes,
            "file_name": "Морские_сражения_русского_флота_Воспоминания,_дневники,_письма_Сборник-1-5.pdf"
        })
        
        with open('Морские_сражения_русского_флота_Воспоминания,_дневники,_письма_Сборник-1-5 copy.pdf', 'rb') as file:
            pdf_bytes = base64.b64encode(file.read()).decode('utf-8')
        
        orders.append({
            "order_id": 2,
            "type": "convert",
            "path": pdf_bytes,
            "file_name": "Морские_сражения_русского_флота_Воспоминания,_дневники,_письма_Сборник-1-5 copy.pdf"
        })
        
        await asyncio.gather(*[process_order(order, connection) for order in orders])
    
    finally:
        await connection.close()

if __name__ == "__main__":
    asyncio.run(main())