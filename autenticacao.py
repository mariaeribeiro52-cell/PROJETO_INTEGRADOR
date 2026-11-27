
import streamlit as st
import pandas as pd
import bcrypt
import os


# =====================================
# CLASSE SISTEMA
# =====================================

class Sistema:

    def __init__(self, gerenciador_log):

        self.log = gerenciador_log


    # =================================
    # REGISTRO DE LOG
    # =================================

    def registrar(self, nivel, mensagem):

        # Log local atual
        self.log.registrar(
            nivel,
            mensagem
        )

        # FUTURA INTEGRAÇÃO:
        # Enviar o evento ao AWS CloudWatch
        #
        # Exemplo futuro:
        # self.registrar_cloudwatch(nivel, mensagem)


    # =================================
    # AUTENTICAÇÃO
    # =================================

    def autenticar(self, usuario, senha, conexao):

        cursor = None

        try:

            cursor = conexao.cursor()

            cursor.execute(
                """
                SELECT usuario, senha_hash, tipo_usuario, status
                FROM usuarios
                WHERE usuario = %s
                """,
                (usuario,)
            )

            dados_usuario = cursor.fetchone()


            # USUÁRIO NÃO ENCONTRADO

            if dados_usuario is None:

                self.registrar(
                    "WARNING",
                    f"Tentativa de login inválida - usuário: {usuario}"
                )

                return False


            nome_usuario, senha_hash, perfil, status = dados_usuario


            # USUÁRIO INATIVO

            if not status:

                self.registrar(
                    "WARNING",
                    f"Tentativa de login em usuário inativo - usuário: {usuario}"
                )

                return False


            # VALIDAR SENHA

            senha_hash_bytes = senha_hash.encode("utf-8")

            if bcrypt.checkpw(
                senha.encode("utf-8"),
                senha_hash_bytes
            ):


                # LOGIN

                st.session_state.logado = True

                st.session_state.usuario = nome_usuario


                # PERFIL

                if perfil == "Administrador":

                    st.session_state.perfil = "admin"

                elif perfil == "Operador":

                    st.session_state.perfil = "operador"

                elif perfil == "Engenheiro":

                    st.session_state.perfil = "engenheiro"


                self.registrar(
                    "INFO",
                    f"Login realizado com sucesso - usuário: {usuario}"
                )

                return True


            # SENHA INCORRETA

            else:

                self.registrar(
                    "WARNING",
                    f"Tentativa de login inválida - usuário: {usuario}"
                )

                return False


        except Exception as erro:

            self.registrar(
                "ERROR",
                f"Erro durante autenticação: {erro}"
            )

            st.error(
                "Erro ao realizar autenticação."
            )

            return False


        finally:

            if cursor:
                cursor.close()


# =====================================
# LOGOUT
# =====================================

def logout(sistema):

    sistema.registrar(
        "INFO",
        f"Logout realizado - usuário: {st.session_state.usuario}"
    )

    st.session_state.logado = False
    st.session_state.usuario = None
    st.session_state.perfil = None

    st.rerun()


# =====================================
# LEITURA DOS LOGS
# =====================================

def ler_logs_local(nome_arquivo):

    dados = []

    if not os.path.exists(nome_arquivo):

        return pd.DataFrame(
            columns=["data", "nivel", "mensagem"]
        )


    with open(
        nome_arquivo,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as arquivo:

        for linha in arquivo:

            partes = linha.strip().split(" - ", 2)

            if len(partes) == 3:

                dados.append(
                    {
                        "data": partes[0],
                        "nivel": partes[1],
                        "mensagem": partes[2]
                    }
                )


    return pd.DataFrame(dados)
