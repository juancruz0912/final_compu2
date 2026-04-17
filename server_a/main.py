import asyncio
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=9011)
args = parser.parse_args()

PORT = args.port

client_counter = 0
clientes = {}


async def manejar_cliente(reader, writer):
    global client_counter # Contador global para asignar IDs únicos a cada cliente

    client_id = client_counter
    client_counter += 1

    try:
        data = await reader.read(4096)
        if not data:
            return

        mensaje = json.loads(data.decode("utf-8"))
        url = mensaje.get("url", "")

        clientes[client_id] = {"url": url, "imagenes": []}

        respuesta = json.dumps({"status": "ok", "client_id": client_id})
        writer.write(respuesta.encode("utf-8"))
        await writer.drain()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        writer.close()
        await writer.wait_closed()


async def main():
    servers = []

    for host in ("127.0.0.1", "::1"):
        try:
            server = await asyncio.start_server(manejar_cliente, host, PORT)
            servers.append(server)
        except OSError as e:
            print(f"No se pudo abrir {host}:{PORT} -> {e}")

    if not servers:
        raise RuntimeError("No se pudo iniciar ningun listener")

    for server in servers:
        for sock in server.sockets or []:
            print(f"Servidor escuchando en {sock.getsockname()}")

    await asyncio.gather(*(server.serve_forever() for server in servers))


if __name__ == "__main__":
    asyncio.run(main())
