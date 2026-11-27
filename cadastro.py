
import streamlit as st
import mysql.connector
import bcrypt
from getpass import getpass

# ========================
# CONFIGURAÇÃO
# ========================

st.set_page_config(
    page_title="Cadastro de Usuários",
    page_icon="⚙️",
    layout="centered"
)

st.title("Sistema Supervisório")
st.subheader("Cadastro de Usuários")

# ========================
# CONEXÃO MYSQL
# ========================

def conectar_banco():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="madu1234",
        database="supervisorio_industrial"
    )

# ========================
# CRIAR O ADMIN
# ========================

def criar_admin_inicial():

    conexao = conectar_banco()
    cursor = conexao.cursor()

    usuario = "admin"

    cursor.execute(
        "SELECT id FROM usuarios WHERE usuario = %s",
        (usuario,)
    )

    if cursor.fetchone() is None:

        print("\n===== CONFIGURAÇÃO DO ADMINISTRADOR =====")

        senha = getpass("Digite a senha do administrador: ")
        confirmar_senha = getpass("Confirme a senha: ")

        if not senha:
            print("A senha não pode ser vazia.")

        elif senha != confirmar_senha:
            print("As senhas não coincidem.")

        else:

            senha_hash = bcrypt.hashpw(
                senha.encode("utf-8"),
                bcrypt.gensalt()
            )

            cursor.execute(
                """
                INSERT INTO usuarios
                (usuario, senha_hash, tipo_usuario)
                VALUES (%s, %s, %s)
                """,
                (
                    usuario,
                    senha_hash.decode("utf-8"),
                    "Administrador"
                )
            )

            conexao.commit()

            print("Administrador criado com sucesso!")

    else:

        print("Administrador já cadastrado.")

    cursor.close()
    conexao.close()

# Executa a criação do administrador
criar_admin_inicial()

# ========================
# CADASTRO
# ========================

def cadastrar_usuario(usuario, senha, tipo_usuario):

    conexao = None
    cursor = None

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute(
            "SELECT id FROM usuarios WHERE usuario = %s",
            (usuario,)
        )

        if cursor.fetchone():
            return False, "Usuário já cadastrado."

        senha_hash = bcrypt.hashpw(
            senha.encode("utf-8"),
            bcrypt.gensalt()
        )

        cursor.execute(
            """
            INSERT INTO usuarios
            (usuario, senha_hash, tipo_usuario)
            VALUES (%s, %s, %s)
            """,
            (
                usuario,
                senha_hash.decode("utf-8"),
                tipo_usuario
            )
        )

        conexao.commit()

        return True, "Usuário cadastrado com sucesso!"

    except mysql.connector.Error as erro:
        return False, f"Erro ao acessar o MySQL: {erro}"

    finally:
        if cursor:
            cursor.close()

        if conexao and conexao.is_connected():
            conexao.close()

# ========================
# INTERFACE DE CADASTRO
# ========================

with st.form("form_cadastro"):

    usuario = st.text_input("Nome de usuário")

    senha = st.text_input(
        "Senha",
        type="password"
    )

    confirmar_senha = st.text_input(
        "Confirmar senha",
        type="password"
    )

    tipo_usuario = st.selectbox(
        "Tipo de usuário",
        [
            "Administrador",
            "Operador",
            "Engenheiro"
        ]
    )

    cadastrar = st.form_submit_button(
        "Cadastrar usuário",
        use_container_width=True
    )

    if cadastrar:

        if not usuario.strip() or not senha or not confirmar_senha:
            st.error("Preencha todos os campos.")

        elif senha != confirmar_senha:
            st.error("As senhas não coincidem.")

        else:
            sucesso, mensagem = cadastrar_usuario(
                usuario.strip(),
                senha,
                tipo_usuario
            )

            if sucesso:
                st.success(mensagem)
            else:
                st.error(mensagem)
