import grpc

grpc.protos()

port = input("Porta de execução: ") or "9090"

with grpc.insecure_channel(f"localhost:{port}") as channel:
    while True:
        a = channel.unary_unary("TableEntry")
        print(a.with_call())
        input()
        