import os
import json
import logging
import pika
from light_controller import LightController

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

class RabbitListener:
    def __init__(self, queue_name=None, url=None, host=None, port=None, username=None, password=None, vhost=None):
        self.queue_name = queue_name or os.getenv('RABBIT_QUEUE', 'light_queue')
        self.url = url or os.getenv('RABBIT_URL', 'amqps://blmfmpod:iLIyEexy85xzkbX8KATYHwPEsvwz-OP4@toucan.lmq.cloudamqp.com/blmfmpod')

        self.host = host or os.getenv('RABBIT_HOST')
        self.port = int(port or os.getenv('RABBIT_PORT', '5672')) if (port or os.getenv('RABBIT_PORT')) else None
        self.username = username or os.getenv('RABBIT_USER')
        self.password = password or os.getenv('RABBIT_PASS')
        self.vhost = vhost or os.getenv('RABBIT_VHOST', '/')

        self.light_controller = LightController()
        self.connection = None
        self.channel = None

    def connect(self):
        if self.url:
            params = pika.URLParameters(self.url)
        else:
            if self.username and self.password:
                creds = pika.PlainCredentials(self.username, self.password)
                params = pika.ConnectionParameters(host=self.host, port=self.port, virtual_host=self.vhost, credentials=creds)
            else:
                params = pika.ConnectionParameters(host=self.host, port=self.port, virtual_host=self.vhost)

        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)
        logger.info("Connected to RabbitMQ (queue=%s)", self.queue_name)

    def callback(self, ch, method, properties, body):
        # decode and log arrival
        try:
            payload = body.decode() if isinstance(body, (bytes, bytearray)) else str(body)
        except Exception:
            payload = str(body)
        payload = payload.strip()
        logger.info("Message received -> queue=%s delivery_tag=%s properties=%s payload=%r",
                    self.queue_name,
                    getattr(method, "delivery_tag", None),
                    properties,
                    payload)

        # try JSON first
        action = None
        try:
            message = json.loads(payload)
            action = message.get('action') or message.get('cmd') or message.get('command')
            logger.info("Parsed JSON message: %s", message)
        except Exception:
            # not JSON — treat raw payload as action
            action = payload

        if not action:
            logger.warning("No action found in message: %r", payload)
            return

        action_norm = str(action).strip().lower()
        logger.info("Interpreted action: %s", action_norm)

        if action_norm in ('turn_on', 'on', '1', 'true'):
            logger.info("Executing turn_on")
            try:
                self.light_controller.turn_on()
                logger.info("turn_on executed")
            except Exception:
                logger.exception("Error executing turn_on")
        elif action_norm in ('turn_off', 'off', '0', 'false'):
            logger.info("Executing turn_off")
            try:
                self.light_controller.turn_off()
                logger.info("turn_off executed")
            except Exception:
                logger.exception("Error executing turn_off")
        else:
            logger.warning("Unknown action received: %s", action_norm)

    def start_listening(self):
        self.connect()
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback, auto_ack=True)
        logger.info("Listening for messages on queue=%s", self.queue_name)
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Stopped consuming (KeyboardInterrupt)")
        except Exception:
            logger.exception("Error while consuming")

    def close(self):
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("RabbitMQ connection closed")
        except Exception:
            logger.exception("Error closing RabbitMQ connection")
        try:
            if self.light_controller:
                self.light_controller.cleanup()
                logger.info("LightController cleaned up")
        except Exception:
            logger.exception("Error cleaning up LightController")