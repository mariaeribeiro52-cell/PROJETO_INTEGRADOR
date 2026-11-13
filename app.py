import streamlit as st
import pandas as pd
import logging
import os
import bcrypt
from classe_gerenciador import GerenciadorLog
from autenticacao import autenticar, logout, ler_logs_local
from telas import tela_login, tela_processo, tela_monitoramento

# =====================================
# CONFIGURAÇÕES
# =====================================

ARQUIVO_LOG = "sistema.log"


# =====================================
# OBJETO DE LOG
# =====================================

log = GerenciadorLog(
    ARQUIVO_LOG
)


# =====================================
# USUÁRIOS
# =====================================

# Os usuários são criados apenas na
# primeira execução da sessão. Já vimos como fazer isso com 
# Banco de Dados

if "usuarios" not in st.session_state:

    st.session_state.usuarios = {
        "admin": {
            "senha_hash": bcrypt.hashpw(
                "admin123".encode(),
                bcrypt.gensalt()
            ),
            "perfil": "admin"
        },
        "operador": {
            "senha_hash": bcrypt.hashpw(
                "operador123".encode(),
                bcrypt.gensalt()
            ),
            "perfil": "operador"
        }
    }


# =====================================
# VARIÁVEIS DA SESSÃO
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

##############################################
# CONTROLE DO SUPERVISÓRIO
##############################################
if st.session_state.logado == False:
    tela_login(log)
else:
    ##############################################
    # Sidebar
    ##############################################
    # Configurações da tela de sidebar
    st.sidebar.write(f"👤 {st.session_state.usuario}")
    st.sidebar.write(f"Perfil: {st.session_state.perfil}")
    st.sidebar.divider()
    # admin
    if st.session_state.perfil =="admin":
        tela = st.sidebar.radio(
            "Navegação",
            [
                "Processo",
                "Monitoramento"
            ]
        )
    # outros usuários (operador)    
    else:
        tela = "Processo"
        st.sidebar.info("Acesso somente ao processo")
    st.sidebar.divider()
    if st.sidebar.button("Sair"):
        logout(log)
    ##############################################
    # Telas do projeto
    ##############################################
    if tela == "Processo":
        tela_processo(log)