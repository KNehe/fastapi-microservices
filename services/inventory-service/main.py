import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
import aio_pika

# Mock Database for Inventory
inventory_db = {
    99: {"name": "Super Fast Laptop", "stock": 10}
}

async def process_message(message: aio_pika.abc.AbstractIncomingMessage):
    try: 
        event_data = json.loads(message.body.decode())
        print(f"📦 Received Event: {event_data}")
    
        product_id = event_data.get("product_id")
        
        # SIMULATE A FATAL ERROR
        if product_id == 999:
            print("❌ Fatal error: Simulated crash! Rejecting message.")

            # Reject the message and DO NOT requeue it
            # This triggers the Dead Letter Exchange (DLX)
            await message.reject(requeue=False)    
            return 
        
        # Normal business logic
        if product_id in inventory_db and inventory_db[product_id]["stock"] > 0:
            inventory_db[product_id]["stock"] -= 1
            print(f"✅ Stock reduced! Remaining stock for product {product_id}: {inventory_db[product_id]['stock']}")
        else:
            print(f"❌ Out of stock or invalid product: {product_id}")
        
        # Manually acknowledge the message was processed successfully
        await message.ack()
    except Exception as e:
        print(f"❌ Error processing message: {e}")
        # If any Python error occurs, safely dead-letter the message
        await message.reject(requeue=False)

import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Connect to RabbitMQ with retry
    for i in range(5):
        try:
            connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672/")
            channel = await connection.channel()
            break
        except Exception as e:
            print(f"RabbitMQ not ready yet, retrying in 2 seconds (attempt {i+1}/5)...")
            await asyncio.sleep(2)
    else:
        raise Exception("Failed to connect to RabbitMQ after 5 attempts")
    
    # 2. Declare the Dead Letter Exchange (DLX) and Dead Letter Queue (DLQ)
    dlx = await channel.declare_exchange("dlx", aio_pika.ExchangeType.DIRECT)
    dlq = await channel.declare_queue("order_events_dlq", durable=True)
    await dlq.bind(dlx, routing_key="order_events")
    
    # 3. Declare the main queue and tell it to route failures to the DLX
    arguments = {
        "x-dead-letter-exchange": "dlx",
        "x-dead-letter-routing-key": "order_events",
    }
    queue = await channel.declare_queue("order_events", durable=True, arguments=arguments)
    
    # 4. Consume messages
    await queue.consume(process_message)
    print("🎧 Inventory Service is now listening for order events...")
   
    yield
   
    await connection.close()

app = FastAPI(lifespan=lifespan)

# A simple endpoint to check current stock
@app.get("/inventory/{product_id}")
def get_stock(product_id: int):
    return inventory_db.get(product_id, {"error": "Product not found"})