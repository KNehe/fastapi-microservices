import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
import aio_pika

# Mock Database for Inventory
inventory_db = {
    99: {"name": "Super Fast Laptop", "stock": 10}
}

async def process_message(message: aio_pika.abc.AbstractIncomingMessage):
    async with message.process(): # This automatically ACKs the message if no errors occur
        event_data = json.loads(message.body.decode())
        print(f"📦 Received Event: {event_data}")
       
        product_id = event_data.get("product_id")
       
        # Simulate business logic: Reduce stock
        if product_id in inventory_db and inventory_db[product_id]["stock"] > 0:
            inventory_db[product_id]["stock"] -= 1
            print(f"✅ Stock reduced! Remaining stock for product {product_id}: {inventory_db[product_id]['stock']}")
        else:
            print(f"❌ Out of stock or invalid product: {product_id}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Connect to RabbitMQ
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672/")
    channel = await connection.channel()
   
    # 2. Ensure the queue exists
    queue = await channel.declare_queue("order_events", durable=True)
   
    # 3. Start listening in the background
    await queue.consume(process_message)
    print("🎧 Inventory Service is now listening for order events...")
   
    yield
   
    await connection.close()

app = FastAPI(lifespan=lifespan)

# A simple endpoint to check current stock
@app.get("/inventory/{product_id}")
def get_stock(product_id: int):
    return inventory_db.get(product_id, {"error": "Product not found"})