
import logging
import os
import time
import boto3


class GerenciadorLog:

    def __init__(
        self,
        arquivo,
        grupo_cloudwatch="Projeto-Integrador",
        stream_cloudwatch="supervisorio-python"
    ):

        self.arquivo = arquivo
        self.grupo_cloudwatch = grupo_cloudwatch
        self.stream_cloudwatch = stream_cloudwatch

        self.regiao = os.getenv(
            "AWS_DEFAULT_REGION",
            "us-east-1"
        )

        # =================================
        # CONFIGURAÇÃO DO LOG LOCAL
        # =================================

        self.logger = logging.getLogger(
            f"supervisorio_{os.path.abspath(arquivo)}"
        )

        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        # Evita adicionar o mesmo FileHandler
        # novamente durante os reruns do Streamlit
        handler_existente = any(
            isinstance(handler, logging.FileHandler)
            and handler.baseFilename == os.path.abspath(arquivo)
            for handler in self.logger.handlers
        )

        if not handler_existente:

            handler = logging.FileHandler(
                self.arquivo,
                encoding="utf-8"
            )

            formatter = logging.Formatter(
                "%(asctime)s - "
                "%(levelname)s - "
                "%(message)s"
            )

            handler.setFormatter(formatter)

            self.logger.addHandler(handler)

        # =================================
        # CLIENTE AWS CLOUDWATCH
        # =================================

        self.cliente_cloudwatch = boto3.client(
            "logs",
            region_name=self.regiao
        )

    # =====================================
    # ENVIO PARA CLOUDWATCH
    # =====================================

    def enviar_cloudwatch(self, nivel, mensagem):

        try:

            timestamp = int(time.time() * 1000)

            self.cliente_cloudwatch.put_log_events(
                logGroupName=self.grupo_cloudwatch,
                logStreamName=self.stream_cloudwatch,
                logEvents=[
                    {
                        "timestamp": timestamp,
                        "message": f"{nivel} - {mensagem}"
                    }
                ]
            )

        except Exception as erro:

            # Registra a falha somente no arquivo local.
            # Não chama registrar() novamente para evitar recursão.
            self.logger.error(
                "Falha ao enviar evento para o CloudWatch: %s",
                erro
            )

    # =====================================
    # REGISTRO DE LOG
    # =====================================

    def registrar(self, nivel, mensagem):

        niveis = {
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }

        nivel = nivel.upper()

        if nivel not in niveis:
            raise ValueError(
                f"Nível de log inválido: {nivel}"
            )

        # Primeiro registra localmente
        self.logger.log(
            niveis[nivel],
            mensagem
        )

        # Depois envia para o CloudWatch
        self.enviar_cloudwatch(
            nivel,
            mensagem
        )
