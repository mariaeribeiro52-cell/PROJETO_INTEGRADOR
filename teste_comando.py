
from classe_OPC import Coneccao_Opc
import time


# =====================================
# CONFIGURAÇÕES
# =====================================

URL_OPC = "opc.tcp://127.0.0.1:4843"

START = "ns=1;s=Main.Start"
SENSOR = "ns=1;s=Main.Sensor"
MOTOR = "ns=1;s=Main.Motor"


# =====================================
# CONEXÃO OPC UA
# =====================================

conexao = Coneccao_Opc(URL_OPC)

comando_enviado = False


try:

    print("\n====================================")
    print(" TESTE DE COMANDO - ESTEIRA")
    print("====================================")

    # Verifica o sensor antes de iniciar
    estado_sensor = conexao.leitura_valor(SENSOR)

    print(f"\nSensor antes da partida: {estado_sensor}")

    if estado_sensor:

        print("\nSensor acionado!")
        print("Libere o sensor antes de testar a partida.")

    else:

        # Envia comando de partida
        print("\nEnviando comando para ligar a esteira...")

        conexao.escrita_bool(START, True)
        comando_enviado = True

        # Monitora o processo por até 6 segundos
        inicio = time.monotonic()

        while time.monotonic() - inicio < 6:

            estado_sensor = conexao.leitura_valor(SENSOR)
            estado_motor = conexao.leitura_valor(MOTOR)

            print(
                f"Sensor: {estado_sensor} | "
                f"Motor: {estado_motor}"
            )

            # Interrompe o teste se o sensor detectar a caixa
            if estado_sensor:
                print("\nCaixa detectada pelo sensor!")
                break

            time.sleep(1000)


finally:

    # Garante o envio do comando de parada
    if comando_enviado:

        print("\nEnviando comando para desligar a esteira...")

        conexao.escrita_bool(START, False)

        time.sleep(1000)

        estado_start = conexao.leitura_valor(START)
        estado_motor = conexao.leitura_valor(MOTOR)

        print(f"Start após parada: {estado_start}")
        print(f"Motor após parada: {estado_motor}")

    print("\n====================================")
    print(" TESTE FINALIZADO")
    print("====================================")
