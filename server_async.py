import asyncio

HOST = '127.0.0.1'
PORT = 65432

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """
    Corrotina chamada pelo Event Loop para cada nova conexão.
    Substitui a função que antes rodava em uma Thread separada.
    """
    addr = writer.get_extra_info('peername')
    print(f"[NOVA CONEXÃO] {addr}")

    # 1. Lê os dados enviados pelo cliente
    data = await reader.read(1024)
    mensagem = data.decode('utf-8') if data else "(sem dados)"
    print(f"[{addr}] Recebido: {mensagem}")

    # 2. Simula processamento pesado SEM bloquear a thread principal.
    #    asyncio.sleep suspende apenas esta corrotina, devolvendo o controle
    #    ao Event Loop para atender outras conexões enquanto "espera".
    #    time.sleep(5) bloquearia toda a thread — nunca usar aqui.
    print(f"[{addr}] Processando (5s sem bloquear o Event Loop)...")
    await asyncio.sleep(5)

    # 3. Envia a resposta ao cliente
    resposta = f"Processado (async): {mensagem}".encode('utf-8')
    writer.write(resposta)
    await writer.drain()  # garante que os dados foram enviados pelo buffer

    # 4. Fecha a conexão
    writer.close()
    await writer.wait_closed()

    print(f"[DESCONECTADO] {addr}")


async def main():
    """
    Ponto de entrada assíncrono: cria e inicia o servidor.
    """
    server = await asyncio.start_server(handle_client, HOST, PORT)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f"[ASSÍNCRONO] Servidor rodando em {addrs} — Event Loop ativo.")
    print("Uma única Thread gerencia todas as conexões via corrotinas.\n")

    # Mantém o servidor rodando indefinidamente dentro do context manager
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
