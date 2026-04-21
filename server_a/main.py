import asyncio
import json
import argparse
from scraper import Scraper

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=9011)
args = parser.parse_args()

PORT = args.port

client_counter = 0
clientes = {}


async def manejar_cliente(reader, writer):
    global client_counter

    client_id = client_counter
    client_counter += 1

    addr = writer.get_extra_info('peername')
    print(f"Cliente {client_id} conectado desde {addr}")

    try:
        data = await reader.read(4096)
        if not data:
            print(f"Cliente {client_id} cerró conexión")
            return

        mensaje = json.loads(data.decode("utf-8"))
        url = mensaje.get("url", "")

        print(f"Cliente {client_id} solicitó: {url}")

        scraper = Scraper()
        imagenes = await scraper.scrape_catalogo(url)
        clientes[client_id] = {"url": url, "imagenes": imagenes}

        respuesta = json.dumps({
            "status": "ok",
            "client_id": client_id,
            "url": url,
            "imagenes": imagenes
        })

        writer.write(respuesta.encode("utf-8"))
        await writer.drain()

        print(f"Respuesta enviada a cliente {client_id}")

    except Exception as e:
        print(f"Error manejando cliente {client_id}: {e}")
    finally:
        writer.close()
        await writer.wait_closed()
        print(f"Conexión cerrada con cliente {client_id}")


async def main():
    servers = []

    for host in ("127.0.0.1", "::1"):
        try:
            server = await asyncio.start_server(manejar_cliente, host, PORT)
            servers.append(server)
            print(f"Servidor escuchando en {host}:{PORT}")
        except OSError as e:
            print(f"No se pudo abrir {host}:{ PORT} -> {e}")

    if not servers:
        raise RuntimeError("No se pudo iniciar ningún listener")

    try:
        await asyncio.gather(*(server.serve_forever() for server in servers))
    except asyncio.CancelledError:
        print("Servidor deteniéndose...")


if __name__ == "__main__":
    asyncio.run(main())