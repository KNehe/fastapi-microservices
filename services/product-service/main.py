import grpc
from concurrent import futures
import product_pb2
import product_pb2_grpc

class ProductService(product_pb2_grpc.ProductServiceServicer):
    def GetProduct(self, request, context):
        print(f"Received request for proudct ID: {request.id}")

        return product_pb2.ProductResponse(
            id=request.id,
            name="Super Fast Laptop",
            price=1999.99
        )
def server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    product_pb2_grpc.add_ProductServiceServicer_to_server(ProductService(),server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    server()
