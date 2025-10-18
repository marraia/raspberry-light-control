from socket import socket, AF_INET, SOCK_STREAM
import threading
import argparse
import os
from rabbit_listener import RabbitListener
from light_controller import LightController

class SocketListener:
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.light_controller = LightController()

    def listen(self):
        with socket(AF_INET, SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen()
            print(f"Listening for connections on {self.host}:{self.port}...")
            while True:
                client_socket, addr = server_socket.accept()
                print(f"Connection from {addr}")
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        with client_socket:
            message = client_socket.recv(1024).decode()
            print(f"Received message: {message}")
            if message == 'ON':
                self.light_controller.turn_on()
            elif message == 'OFF':
                self.light_controller.turn_off()

def parse_args():
    parser = argparse.ArgumentParser(description="Raspberry Light Control (RabbitMQ only)")
    parser.add_argument("--queue", default=os.getenv("RABBIT_QUEUE", "light_queue"), help="Nome da fila RabbitMQ")
    parser.add_argument("--host", default=os.getenv("RABBIT_HOST", "toucan.lmq.cloudamqp.com"), help="Endereço do servidor RabbitMQ")
    parser.add_argument("--port", type=int, default=int(os.getenv("RABBIT_PORT", "5672")), help="Porta do RabbitMQ")
    parser.add_argument("--user", default=os.getenv("RABBIT_USER", "blmfmpod"), help="Usuário RabbitMQ (opcional)")
    parser.add_argument("--pass", dest="password", default=os.getenv("RABBIT_PASS", "iLIyEexy85xzkbX8KATYHwPEsvwz-OP4"), help="Senha RabbitMQ (opcional)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    socket_listener = SocketListener()
    rabbit_listener = RabbitListener(
        queue_name=args.queue,
        host=args.host,
        port=args.port,
        username=args.user,
        password=args.password
    )

    #threading.Thread(target=socket_listener.listen).start()
    rabbit_listener.start_listening()