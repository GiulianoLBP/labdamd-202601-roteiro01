# Relatório Técnico — Laboratório 2: Concorrência e Gargalos em Servidores TCP

**Aluno:** Giuliano Percope
**Disciplina:** Laboratório de Desenvolvimento de Aplicações Móveis e Distribuídas  
**Data:** 23/02/2026

---

## Questão 1 — Backlog e Recusa de Conexões

**Pergunta:** O `clientenervoso.py` apresentou falhas (`ConnectionRefusedError` ou Timeout) ao testar o `servergargalo.py`, mas obteve sucesso imediato contra o `server.py`. Explique o motivo técnico.

**Resposta:**

O `servergargalo.py` chama `server.listen(1)`, sinalizando ao kernel do Sistema Operacional que deseja uma fila de conexões pendentes (backlog) de tamanho 1. O backlog TCP é uma fila mantida pelo kernel para armazenar conexões que completaram o handshake de três vias (SYN → SYN-ACK → ACK) mas ainda não foram retiradas da fila pela aplicação via `accept()`. Como o servidor não usa threads e fica bloqueado 5 segundos processando cada cliente, ele não chama `accept()` durante esse tempo, e a fila rapidamente esgota.

Quando a fila está cheia, o comportamento do kernel varia por plataforma (conforme documentado em `man 2 listen`):
- **Linux:** pode rejeitar o SYN imediatamente, resultando em `ConnectionRefusedError` no cliente.
- **Windows:** pode silenciosamente descartar o SYN ou manter a conexão pendente, resultando em `socket.timeout` caso o cliente aguarde com `settimeout(2)`.

Já o `server.py` utiliza Threads: assim que aceita uma conexão, imediatamente delega o processamento para uma nova thread e volta ao `accept()`, mantendo a fila sempre drenada. Por isso, todos os 10 clientes simultâneos são aceitos sem falhas.

---

## Questão 2 — Custo de Recursos: Threads vs. Event Loop

**Pergunta:** Com base no número máximo de threads simultâneas observado no `server.py`, explique a diferença no consumo de memória e uso de CPU entre Multithread e Assíncrono.

**Observação experimental:** Ao executar `server.py` com `clientenervoso.py` (10 clientes), o log exibiu:

```
[ATIVO] Conexões simultâneas: 200
```

**Resposta:**

Com o modelo Multithread (`server.py`), o servidor criou **[10] threads simultâneas** para atender os clientes. Cada thread gerenciada pelo SO consome:

- **Memória de pilha (stack):** tipicamente entre 512 KB e 8 MB por thread (depende da plataforma). Para 10 threads: aproximadamente **5 MB a 80 MB** somente de overhead de pilha.
- **Overhead de CPU:** o SO realiza *Context Switch* a cada quantum de tempo para alternar entre as threads. Com 10 threads bloqueadas em `time.sleep(5)` (que é uma syscall bloqueante), o escalonador precisa gerenciar todas elas mesmo que apenas aguardem I/O.

Com o modelo Assíncrono (`server_async.py`), **uma única thread** gerencia todas as 10 conexões via corrotinas e o Event Loop do `asyncio`. O `await asyncio.sleep(5)` apenas suspende a corrotina e cede o controle ao Event Loop — sem criar threads, sem Context Switch do SO. O consumo de memória é proporcional ao tamanho das corrotinas (dezenas de KB, não MB), e o uso de CPU durante a espera é praticamente zero.

**Conclusão:** para cargas com alto volume de I/O (como conexões de rede), o modelo assíncrono escala com muito menos recursos que o modelo baseado em Threads, pois elimina o overhead de criação de threads e troca de contexto do kernel.

---

## Desafio Extra — 200 Conexões Simultâneas

Foi modificado o `clientenervoso.py` para disparar 200 conexões simultâneas contra o `server_async.py`.

**Screenshot da execução:**

![200 conexões simultâneas](../image.png)


**Resultado:** O `server_async.py` suportou as 200 conexões simultâneas com uma única thread, demonstrando a superioridade do modelo Event Loop em cenários de alta concorrência de I/O.

---

## Referências

- TANENBAUM, A. S.; WETHERALL, D. *Computer Networks*. 5. ed. Prentice Hall, 2011. Cap. 6.
- SILBERSCHATZ, A.; GALVIN, P. B.; GAGNE, G. *Operating System Concepts*. 10. ed. Wiley, 2018. Cap. 4.
- KEGEL, D. *The C10K Problem*. 2006. Disponível em: http://www.kegel.com/c10k.html
- OUSTERHOUT, J. *Why Threads Are A Bad Idea (for most purposes)*. USENIX Technical Conference, 1996.
- Python Software Foundation. *asyncio — Asynchronous I/O*. Disponível em: https://docs.python.org/3/library/asyncio.html
