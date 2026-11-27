
from opcua import Client, ua


class Coneccao_Opc:

    def __init__(self, url):

        # Endereço do servidor OPC UA
        self.url = url

        # Tempo máximo para tentar conectar
        self.timeout = 5

    # =================================
    # LEITURA DE VARIÁVEIS
    # =================================

    def leitura_valor(self, node):

        cliente = Client(
            self.url,
            timeout=self.timeout
        )

        conectado = False

        try:

            cliente.connect()
            conectado = True

            no_leitura = cliente.get_node(node)

            valor = no_leitura.get_value()

            return valor

        finally:

            if conectado:
                cliente.disconnect()

    # =================================
    # ESCRITA DE VARIÁVEIS BOOLEANAS
    # =================================

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

            no_escrita = cliente.get_node(node)

            no_escrita.set_value(
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

    # =================================
    # ESCRITA DE VARIÁVEIS REAIS
    # =================================

    def escrita_real(self, node, valor):

        if isinstance(valor, bool):
            raise TypeError(
                "O valor precisa ser numérico."
            )

        cliente = Client(
            self.url,
            timeout=self.timeout
        )

        conectado = False

        try:

            cliente.connect()
            conectado = True

            no_escrita = cliente.get_node(node)

            no_escrita.set_value(
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
