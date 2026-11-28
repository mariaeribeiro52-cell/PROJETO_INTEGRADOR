
import os

from dotenv import load_dotenv
from opcua import Client, ua

load_dotenv()


URL_OPC = os.getenv(
    "OPC_UA_URL",
    "opc.tcp://127.0.0.1:4843"
)


NODES_OPC = {

    "Start": "ns=1;s=Main.Start",
    "Sensor": "ns=1;s=Main.Sensor",
    "Motor": "ns=1;s=Main.Motor",
    "Velocidade": "ns=1;s=Main.Velocidade",
    "CaixasColetadas": "ns=1;s=Main.CaixasColetadas",
    "Armazenadas": "ns=1;s=Main.Armazenadas"

}


class Coneccao_Opc:

    def __init__(self, url=URL_OPC):

        self.url = url
        self.timeout = 5

    def leitura_valor(self, node):

        cliente = Client(
            self.url,
            timeout=self.timeout
        )

        conectado = False

        try:

            cliente.connect()
            conectado = True

            no = cliente.get_node(node)

            return no.get_value()

        finally:

            if conectado:
                cliente.disconnect()

    def leitura_varios(self, variaveis):

        cliente = Client(
            self.url,
            timeout=self.timeout
        )

        conectado = False

        try:

            cliente.connect()
            conectado = True

            resultados = {}

            for nome, node_id in variaveis.items():

                no = cliente.get_node(node_id)

                resultados[nome] = no.get_value()

            return resultados

        finally:

            if conectado:
                cliente.disconnect()

    def escrita_bool(self, node, valor):

        if not isinstance(valor, bool):

            raise TypeError(
                "O valor precisa ser True ou False."
            )

        cliente = Client(
            self.url,
            timeout=self.timeout
        )

        conectado = False

        try:

            cliente.connect()
            conectado = True

            no = cliente.get_node(node)

            no.set_value(
                ua.DataValue(
                    ua.Variant(
                        valor,
                        ua.VariantType.Boolean
                    )
                )
            )

        finally:

            if conectado:
                cliente.disconnect()

    def escrita_real(self, node, valor):

        if isinstance(valor, bool) or not isinstance(
            valor, (int, float)
        ):

            raise TypeError(
                "O valor precisa ser numerico."
            )

        cliente = Client(
            self.url,
            timeout=self.timeout
        )

        conectado = False

        try:

            cliente.connect()
            conectado = True

            no = cliente.get_node(node)

            no.set_value(
                ua.DataValue(
                    ua.Variant(
                        float(valor),
                        ua.VariantType.Float
                    )
                )
            )

        finally:

            if conectado:
                cliente.disconnect()
