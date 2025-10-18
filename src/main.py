from socket import socket, AF_INET, SOCK_STREAM
import threading
import argparse
import os
from rabbit_listener import RabbitListener

def parse_args():
    parser = argparse.ArgumentParser(description="Raspberry Light Control (RabbitMQ only)")
    parser.add_argument("--queue", default=os.getenv("RABBIT_QUEUE", "light_queue"), help="Nome da fila RabbitMQ")
    parser.add_argument("--url", default=os.getenv("RABBIT_URL", "amqps://blmfmpod:iLIyEexy85xzkbX8KATYHwPEsvwz-OP4@toucan.lmq.cloudamqp.com/blmfmpod"), help="Full AMQP(S) URL (overrides host/user/pass/vhost)")
    parser.add_argument("--host", default=os.getenv("RABBIT_HOST"), help="Endereço do servidor RabbitMQ (opcional)")
    parser.add_argument("--port", type=int, default=int(os.getenv("RABBIT_PORT", "5672")), help="Porta do RabbitMQ (opcional)")
    parser.add_argument("--user", default=os.getenv("RABBIT_USER"), help="Usuário RabbitMQ (opcional)")
    parser.add_argument("--pass", dest="password", default=os.getenv("RABBIT_PASS"), help="Senha RabbitMQ (opcional)")
    parser.add_argument("--vhost", default=os.getenv("RABBIT_VHOST", "/"), help="Virtual host RabbitMQ (opcional)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    listener = RabbitListener(
        queue_name=args.queue,
        url=args.url,
        host=args.host,
        port=args.port,
        username=args.user,
        password=args.password,
        vhost=args.vhost
    )

    try:
        print(f"Starting Rabbit listener -> queue: {args.queue}")
        listener.start_listening()
    except KeyboardInterrupt:
        print("Stopping listener (KeyboardInterrupt).")
    finally:
        try:
            listener.close()
        except Exception:
            pass