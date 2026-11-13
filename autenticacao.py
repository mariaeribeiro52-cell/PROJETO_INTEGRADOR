import streamlit as st
import pandas as pd
import bcrypt
import os

# =====================================
# AUTENTICAÇÃO
# =====================================

def autenticar(
    usuario,
    senha,
    log
):

    # Verifica se o usuário existe
    if usuario not in st.session_state.usuarios:

        log.registrar(
            "WARNING",
            f"Tentativa de login inválida - "
            f"usuário: {usuario}"
        )

        return False


    dados_usuario = (
        st.session_state.usuarios[
            usuario
        ]
    )


    # Verifica a senha
    if bcrypt.checkpw(
        senha.encode(),
        dados_usuario["senha_hash"]
    ):

        st.session_state.logado = True

        st.session_state.usuario = usuario

        st.session_state.perfil = (
            dados_usuario["perfil"]
        )


        log.registrar(
            "INFO",
            f"Login realizado - "
            f"usuário: {usuario}"
        )

        return True


    else:

        log.registrar(
            "WARNING",
            f"Tentativa de login inválida - "
            f"usuário: {usuario}"
        )

        return False

def logout(log):

    log.registrar(
        "INFO",
        f"Logout realizado - "
        f"usuário: "
        f"{st.session_state.usuario}"
    )

    st.session_state.logado = False
    st.session_state.usuario = None
    st.session_state.perfil = None

    st.rerun()

def ler_logs_local(nome_arquivo):
    dados = []
    if not os.path.exists(nome_arquivo):
        data = pd.DataFrame(columns=["data", "nível", "mensagem"])
        return data
    else:
        with open(
            nome_arquivo,
            'r',
            encoding='utf-8',
            errors="replace"
        ) as arquivo:
            for linha in arquivo:
                partes = linha.strip().split(" - ", 2)
                if len(partes) == 3:
                    dados.append({
                        "data" : partes[0],
                        "nivel" : partes[1],
                        "mensagem" : partes[2]
                    })
            data = pd.DataFrame(dados)
            return data
