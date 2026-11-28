
from classe_OPC import (
    Coneccao_Opc,
    URL_OPC,
    NODES_OPC
)


conexao = Coneccao_Opc(URL_OPC)

print("\n====================================")
print(" TESTE DE COMUNICACAO OPC UA")
print("====================================\n")

try:

    dados = conexao.leitura_varios(NODES_OPC)

    for nome, valor in dados.items():

        print(f"{nome}: {valor}")

    print("\nComunicacao OPC UA realizada com sucesso!")

except Exception as erro:

    print("\nFalha na comunicacao OPC UA:")
    print(erro)

print("\n====================================")
print(" TESTE FINALIZADO")
print("====================================")
