import logging

class GerenciadorLog:

    def __init__(self, arquivo):

        self.arquivo = arquivo

        logging.basicConfig(
            filename=self.arquivo,
            level=logging.INFO,
            format=(
                "%(asctime)s - "
                "%(levelname)s - "
                "%(message)s"
            ),
            encoding="utf-8",
            force=True
        )


    def registrar(self, nivel, mensagem):

        if nivel == "INFO":

            logging.info(
                mensagem
            )

        elif nivel == "WARNING":

            logging.warning(
                mensagem
            )

        elif nivel == "ERROR":

            logging.error(
                mensagem
            )

        elif nivel == "CRITICAL":

            logging.critical(
                mensagem
            )