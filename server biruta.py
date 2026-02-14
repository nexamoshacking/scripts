import asyncio
import websockets
from cryptography.fernet import Fernet

KEY = b'3o7V9y1FZ0N5uFJm7c9qY2m0Qn8kZBzQbJ6XkZPZ0eI='
cipher = Fernet(KEY)

clients = set()

async def handler(ws):
    clients.add(ws)
    try:
        async for msg in ws:
            try:
                # valida se a mensagem é válida
                cipher.decrypt(msg.encode())
            except:
                continue

            # broadcast
            dead = set()
            for c in clients:
                try:
                    await c.send(msg)
                except:
                    dead.add(c)

            clients.difference_update(dead)
    finally:
        clients.discard(ws)

async def main():
    print("[+] Servidor rodando em 0.0.0.0:8765")
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()

asyncio.run(main())
