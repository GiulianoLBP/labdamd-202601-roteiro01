import socket
import threading
import time

HOST = '127.0.0.1'
PORT = 65432

def cliente_nervoso(id_cliente):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        client.settimeout(15)
        
        print(f"[CLIENTE {id_cliente:02d}] 🟡 Tentando entrar...")
        client.connect((HOST, PORT))
        
        print(f"[CLIENTE {id_cliente:02d}] 🟢 Conectou! Enviando mensagem...")
        client.send(f"Olá do cliente {id_cliente:02d}".encode('utf-8'))
        
        msg = client.recv(1024)
        print(f"[CLIENTE {id_cliente:02d}] 🏆 SUCESSO: {msg.decode()}")
        
    except socket.timeout:
        print(f"[CLIENTE {id_cliente:02d}] ⏱️ TIMEOUT: O servidor demorou demais para aceitar!")
    except ConnectionRefusedError:
        print(f"[CLIENTE {id_cliente:02d}] ⛔ RECUSADO: A fila estava cheia!")
    except Exception as e:
        print(f"[CLIENTE {id_cliente:02d}] ❌ ERRO: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    NUM_CLIENTES = 200

    print(f"--- INICIANDO ATAQUE DE {NUM_CLIENTES} CLIENTES SIMULTÂNEOS ---")
    
    threads = []
    for i in range(1, NUM_CLIENTES + 1):
        t = threading.Thread(target=cliente_nervoso, args=(i,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()