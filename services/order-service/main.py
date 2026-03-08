import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
import aio_pika

# Global connection variable
rabbitmq_connection = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global rabbitmq_connection
    # Connect to RabbitMQ container
    rabbitmq_connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672/")
    print("Connected to RabbitMQ!")
    yield
    # Cleanup on shutdown
    await rabbitmq_connection.close()

app = FastAPI(lifespan=lifespan)

@app.post("/orders/")
async def place_order(product_id: int, user_id: int):
    # 1. Create the event data
    order_event = {
        "event": "OrderPlaced",
        "product_id": product_id,
        "user_id": user_id,
        "status": "pending"
    }

    # 2. Publish to RabbitMQ
    async with rabbitmq_connection.channel() as channel:
        message = aio_pika.Message(body=json.dumps(order_event).encode())
        await channel.default_exchange.publish(
            message,
            routing_key="order_events" # This is the queue name
        )

    # 3. Return instantly!
    return {"message": "Order received and is being processed in the background."}
