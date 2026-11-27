
from classe_OPC import Coneccao_Opc


# =====================================
# CONFIGURAÇÃO OPC UA
# =====================================

URL_OPC = "opc.tcp://127.0.0.1:4843"


# =====================================
# VARIÁVEIS DO OPEN INDUSTRY
# =====================================

VARIAVEIS = {

    "Start": "ns=1;s=Main.Start",

    "Sensor": "ns=1;s=Main.Sensor",

    "Motor": "ns=1;s=Main.Motor",

    "Velocidade": "ns=1;s=Main.Velocidade"

}


# =====================================
# CONEXÃO
# =====================================

conexao = Coneccao_Opc(URL_OPC)


# =====================================
# TESTE DE LEITURA
# =====================================

print("\n====================================")
print(" TESTE DE COMUNICAÇÃO OPC UA")
print("====================================\n")


falhas = []

for nome, node in VARIAVEIS.items():

    try:

        valor = conexao.leitura_valor(node)

        print(f"{nome}: {valor}")

    except Exception as erro:

        falhas.append(nome)

        print(f"{nome}: ERRO - {erro}")


# =====================================
# RESULTADO
# =====================================

print("\n====================================")

if not falhas:

    print("COMUNICAÇÃO OPC UA REALIZADA!")

else:

    print("FORAM ENCONTRADAS FALHAS.")

    print("Variáveis com erro:", ", ".join(falhas))

print("====================================")
