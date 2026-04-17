import socket
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=9011)
parser.add_argument("--url", type=str, required=True)
parser.add_argument("--ipv6", action="store_true")
args = parser.parse_args()

PORT = 9011
URL = args.url
IPV6 = args.ipv6


if not IPV6:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
        cliente.connect(("127.0.0.1", PORT))

        mensaje = json.dumps({"url": URL})
        cliente.send(mensaje.encode("utf-8"))

        respuesta = cliente.recv(4096).decode("utf-8")
        print(respuesta)
else:
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as cliente:
        cliente.connect(("::1", PORT, 0, 0))

        mensaje = json.dumps({"url": URL})
        cliente.send(mensaje.encode("utf-8"))

        respuesta = cliente.recv(4096).decode("utf-8")
        print(respuesta)
