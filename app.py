
import os

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import mysql.connector
import bcrypt

from classe_gerenciador import GerenciadorLog
from autenticacao import Sistema, logout
from telas import (
    tela_login,
    tela_processo,
    tela_graficos,
    tela_monitoramento,
    tela_cadastro
)


# =====================================
# CONFIGURAÇÕES
# =====================================

st.set_page_config(
    page_title="Sistema Supervisório",
    page_icon="⚙️",
    layout="wide"
)

ARQUIVO_LOG = "sistema.log"


# =====================================
# GERENCIADOR DE LOG
# =====================================

log = GerenciadorLog(
    arquivo=ARQUIVO_LOG,
    grupo_cloudwatch="Projeto-Integrador",
    stream_cloudwatch="supervisorio-python"
)


# =====================================
# OBJETO SISTEMA
# =====================================

sistema = Sistema(log)


# =====================================
# VARIÁVEIS DE SESSÃO
# =====================================

if "logado" not in st.session_state:
    st.session_state.logado = False

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if "perfil" not in st.session_state:
    st.session_state.perfil = None

if "motor_ligado" not in st.session_state:
    st.session_state.motor_ligado = False

if "velocidade" not in st.session_state:
    st.session_state.velocidade = 0

if "leituras" not in st.session_state:
    st.session_state.leituras = []


# =====================================
# REGISTRO DE INICIALIZAÇÃO
# =====================================

# O Streamlit executa novamente o app
# em determinadas interações.
# Registramos a inicialização apenas uma
# vez por sessão do usuário.

if "inicio_registrado" not in st.session_state:

    log.registrar(
        "INFO",
        "Sistema supervisório inicializado."
    )

    st.session_state.inicio_registrado = True


# =====================================
# CONEXÃO COM MYSQL
# =====================================

def conectar_banco():

    conexao = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

    # Evita repetir a mensagem de conexão
    # em todos os reruns do Streamlit.

    if not st.session_state.get(
        "mysql_conexao_registrada",
        False
    ):

        log.registrar(
            "INFO",
            "Primeira conexão com MySQL da sessão estabelecida."
        )

        st.session_state.mysql_conexao_registrada = True

    return conexao


# =====================================
# ADMINISTRADOR INICIAL
# =====================================

def verificar_admin_inicial(conexao):

    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT id
        FROM usuarios
        WHERE tipo_usuario = 'Administrador'
        LIMIT 1
        """
    )

    admin = cursor.fetchone()

    cursor.close()

    if admin is not None:
        return

    print("\n====================================")
    print(" CONFIGURAÇÃO INICIAL DO SUPERVISÓRIO")
    print("====================================")
    print("Nenhum administrador encontrado.")
    print("Cadastre o administrador inicial.\n")

    usuario = input("Usuário administrador: ").strip()

    while not usuario:
        print("Usuário não pode ser vazio.")
        usuario = input("Usuário administrador: ").strip()

    senha = input("Senha: ")

    while not senha:
        print("Senha não pode ser vazia.")
        senha = input("Senha: ")

    confirmar_senha = input("Confirmar senha: ")

    while senha != confirmar_senha:

        print("As senhas não coincidem.")

        senha = input("Senha: ")
        confirmar_senha = input("Confirmar senha: ")

    senha_hash = bcrypt.hashpw(
        senha.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO usuarios
        (usuario, senha_hash, tipo_usuario, status)
        VALUES (%s, %s, %s, %s)
        """,
        (
            usuario,
            senha_hash,
            "Administrador",
            True
        )
    )

    conexao.commit()
    cursor.close()

    # Registro local e CloudWatch

    log.registrar(
        "INFO",
        f"Administrador inicial criado - usuário: {usuario}"
    )

    print("\nAdministrador criado com sucesso!")
    print("Agora realize o login pelo supervisório.\n")


# =====================================
# EXECUÇÃO DO SISTEMA
# =====================================

conexao = None

try:

    conexao = conectar_banco()

    # Verifica o administrador inicial
    verificar_admin_inicial(conexao)


    # =================================
    # LOGIN
    # =================================

    if not st.session_state.logado:

        tela_login(
            sistema,
            conexao
        )


    # =================================
    # USUÁRIO LOGADO
    # =================================

    else:

        st.sidebar.write(
            f"👤 {st.session_state.usuario}"
        )

        st.sidebar.write(
            f"Perfil: {st.session_state.perfil}"
        )

        st.sidebar.divider()


        # =================================
        # ADMINISTRADOR
        # =================================

        if st.session_state.perfil == "admin":

            telas_disponiveis = [
                "Processo",
                "Gráficos",
                "Monitoramento",
                "Cadastro de usuários"
            ]


        # =================================
        # OPERADOR
        # =================================

        elif st.session_state.perfil == "operador":

            telas_disponiveis = [
                "Processo",
                "Gráficos"
            ]


        # =================================
        # ENGENHEIRO
        # =================================

        elif st.session_state.perfil == "engenheiro":

            telas_disponiveis = [
                "Processo",
                "Gráficos",
                "Monitoramento"
            ]


        else:

            telas_disponiveis = []


        # =================================
        # NAVEGAÇÃO
        # =================================

        if telas_disponiveis:

            tela = st.sidebar.radio(
                "Navegação",
                telas_disponiveis
            )

            st.sidebar.divider()


            # =================================
            # LOGOUT
            # =================================

            if st.sidebar.button("Sair"):

                # O próprio logout registra o evento
                # por meio do GerenciadorLog.

                logout(sistema)


            # =================================
            # CONTROLE DAS TELAS
            # =================================

            if tela == "Processo":

                tela_processo(sistema)


            elif tela == "Gráficos":

                tela_graficos()


            elif tela == "Monitoramento":

                tela_monitoramento(
                    sistema,
                    ARQUIVO_LOG
                )


            elif tela == "Cadastro de usuários":

                tela_cadastro(
                    sistema,
                    conexao
                )

        else:

            st.error(
                "Perfil de usuário não reconhecido."
            )


# =====================================
# TRATAMENTO DE ERROS
# =====================================

except mysql.connector.Error as erro:

    log.registrar(
        "ERROR",
        f"Falha na conexão ou operação MySQL: {type(erro).__name__}"
    )

    st.error(
        "Não foi possível acessar o banco de dados."
    )


except Exception as erro:

    log.registrar(
        "ERROR",
        f"Erro inesperado na execução: {type(erro).__name__}"
    )

    st.error(
        "Ocorreu um erro interno no sistema. "
        "O evento foi registrado nos logs."
    )


# =====================================
# ENCERRAMENTO
# =====================================

finally:

    if conexao is not None and conexao.is_connected():

        conexao.close()
