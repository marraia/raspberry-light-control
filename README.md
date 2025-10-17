# Raspberry Light Control

This project allows you to control a light connected to a Raspberry Pi using either socket communication or RabbitMQ messaging. The application listens for incoming signals and turns the light on or off based on the received commands.

## Project Structure

```
raspberry-light-control
├── src
│   ├── main.py            # Entry point of the application
│   ├── socket_listener.py  # Socket listener for incoming connections
│   ├── rabbit_listener.py  # RabbitMQ listener for message processing
│   └── light_controller.py # Controls the light's state
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/raspberry-light-control.git
   cd raspberry-light-control
   ```

2. **Install dependencies:**
   Make sure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your environment:**
   Ensure that your Raspberry Pi is set up to control the light (e.g., using GPIO pins).

## Usage

To start the application, run the following command:

```bash
python src/main.py
```

You can choose to send commands via socket or RabbitMQ to control the light. 

### Example Commands

- **Socket Command:**
  Send a message "ON" to turn the light on and "OFF" to turn it off.

- **RabbitMQ Command:**
  Publish a message to the appropriate queue to control the light.

## Contributing

Feel free to submit issues or pull requests if you have suggestions or improvements for the project.