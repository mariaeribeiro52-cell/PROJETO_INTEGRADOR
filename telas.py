
import streamlit as st
import pandas as pd
import random
import bcrypt

from datetime import datetime
from autenticacao import ler_logs_local


# =====================================
# TELA DE LOGIN
# =====================================

def tela_login(sistema, conexao):

    st.title("🔐 Sistema Supervisório")

    st.subheader("Autenticação")

    usuario = st.text_input("Usuário")

    senha = st.text_input(
        "Senha",
        type="password"
    )

    if st.button("Entrar"):

        if sistema.autenticar(
            usuario,
            senha,
            conexao
        ):

            st.rerun()

        else:

            st.error(
                "Usuário ou senha inválidos"
            )


# =====================================
# MONITORAMENTO DE TEMPERATURA
# =====================================

@st.fragment(run_every=3)
def monitorar_temperatura():

    temperatura = random.uniform(40, 50)

    st.session_state.leituras.append(
        {
            "Horários": datetime.now().strftime("%H:%M:%S"),
            "Temperatura": temperatura
        }
    )

    st.session_state.leituras = (
        st.session_state.leituras[-20:]
    )

    st.metric(
        "Temperatura Atual",
        f"{temperatura:.2f} °C"
    )

    st.line_chart(
        st.session_state.leituras,
        x="Horários",
        y="Temperatura"
    )


# =====================================
# TELA DO PROCESSO
# =====================================

def tela_processo(sistema):

    st.title("⚙️ Controle do Processo")

    st.write(
        f"Usuário: **{st.session_state.usuario}**"
    )

    st.write(
        f"Perfil: **{st.session_state.perfil}**"
    )

    st.divider()

    st.subheader("Motor 01")


    # STATUS

    if st.session_state.motor_ligado:

        st.success("Motor ligado")

    else:

        st.error("Motor desligado")


    col1, col2 = st.columns(2)


    # LIGAR MOTOR

    with col1:

        if st.button("🟢 Ligar Motor"):

            st.session_state.motor_ligado = True

            sistema.registrar(
                "INFO",
                f"{st.session_state.usuario} ligou Motor 01"
            )

            st.rerun()


    # DESLIGAR MOTOR

    with col2:

        if st.button("🔴 Desligar Motor"):

            st.session_state.motor_ligado = False

            st.session_state.velocidade = 0

            sistema.registrar(
                "INFO",
                f"{st.session_state.usuario} desligou Motor 01"
            )

            st.rerun()


    st.divider()


    # VELOCIDADE

    velocidade = st.slider(
        "Velocidade do Motor",
        min_value=0,
        max_value=1800,
        value=st.session_state.velocidade,
        step=100
    )

    if st.button("Aplicar velocidade"):

        if not st.session_state.motor_ligado:

            st.warning("O motor está desligado.")

            sistema.registrar(
                "WARNING",
                f"{st.session_state.usuario} tentou alterar a velocidade com o motor desligado"
            )

        else:

            st.session_state.velocidade = velocidade

            sistema.registrar(
                "INFO",
                f"{st.session_state.usuario} alterou Motor 01 para {velocidade} RPM"
            )

            st.success(
                f"Velocidade alterada para {velocidade} RPM"
            )


    st.metric(
        "Velocidade atual",
        f"{st.session_state.velocidade} RPM"
    )

    st.divider()

    st.subheader("Temperatura do Processo")

    monitorar_temperatura()


# =====================================
# TELA DE GRÁFICOS
# =====================================

def tela_graficos():

    st.title("📊 Gráficos do Processo")

    st.subheader("Histórico de Temperatura")

    leituras = st.session_state.leituras

    if not leituras:

        st.info(
            "Ainda não existem leituras disponíveis. "
            "Acesse a tela Processo para iniciar o monitoramento."
        )

    else:

        df = pd.DataFrame(leituras)

        st.line_chart(
            df,
            x="Horários",
            y="Temperatura"
        )

        st.metric(
            "Temperatura média",
            f"{df['Temperatura'].mean():.2f} °C"
        )

        st.metric(
            "Temperatura máxima",
            f"{df['Temperatura'].max():.2f} °C"
        )

        st.metric(
            "Temperatura mínima",
            f"{df['Temperatura'].min():.2f} °C"
        )

        st.dataframe(
            df,
            use_container_width=True
        )


# =====================================
# MONITORAMENTO DE SEGURANÇA
# =====================================

def tela_monitoramento(sistema, arquivo):

    # ADMINISTRADOR E ENGENHEIRO

    if st.session_state.perfil not in [
        "admin",
        "engenheiro"
    ]:

        st.error("Acesso não autorizado.")

        sistema.registrar(
            "WARNING",
            f"Tentativa de acesso não autorizado ao monitoramento - usuário: {st.session_state.usuario}"
        )

        return


    st.title("🛡️ Monitoramento")

    st.write(
        "Monitoramento de eventos de segurança"
    )

    logs = ler_logs_local(arquivo)

    st.divider()


    if logs.empty:

        st.info("Nenhum evento encontrado.")

        return


    # INDICADORES

    total_logs = len(logs)

    total_info = (logs["nivel"] == "INFO").sum()

    total_warn = (logs["nivel"] == "WARNING").sum()

    total_erro = (logs["nivel"] == "ERROR").sum()

    total_crit = (logs["nivel"] == "CRITICAL").sum()


    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Eventos", total_logs)

    with col2:
        st.metric("INFO", total_info)

    with col3:
        st.metric("WARNING", total_warn)

    with col4:
        st.metric("ERROR", total_erro)

    with col5:
        st.metric("CRITICAL", total_crit)


    st.divider()


    # ANÁLISE DE LOGIN

    minutos = st.number_input(
        "Período de análise em minutos",
        min_value=1,
        value=60
    )

    inicio = pd.Timestamp.now() - pd.Timedelta(
        minutes=minutos
    )


    mask = (
        (pd.to_datetime(logs["data"]) >= inicio)
        &
        (
            logs["mensagem"]
            .astype(str)
            .str.contains(
                "Tentativa de login inválida",
                na=False,
                case=False,
                regex=False
            )
        )
    )

    tentativas_invalidas = mask.sum()


    st.subheader("Análise de Segurança")

    st.write(
        f"Tentativas inválidas: {tentativas_invalidas}"
    )


    if tentativas_invalidas >= 3:

        st.error(
            "🚨 ALERTA: Possível ataque de força bruta!"
        )

    else:

        st.success(
            "Nenhum ataque de força bruta identificado."
        )


    # GRÁFICO DE LOGS

    st.subheader("Eventos por nível")

    st.bar_chart(
        logs["nivel"].value_counts()
    )


    # TABELA

    logs = logs.sort_values(
        "data",
        ascending=False
    )

    st.subheader("Eventos registrados")

    filtro = st.selectbox(
        "Filtro por nível",
        [
            "Todos",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL"
        ]
    )

    if filtro != "Todos":

        logs = logs[
            logs["nivel"] == filtro
        ]

    st.dataframe(
        logs,
        use_container_width=True
    )


# =====================================
# CADASTRAR USUÁRIO
# =====================================

def cadastrar_usuario(conexao, usuario, senha, tipo_usuario):

    cursor = None

    try:

        cursor = conexao.cursor()


        # VERIFICAR DUPLICIDADE

        cursor.execute(
            """
            SELECT id
            FROM usuarios
            WHERE usuario = %s
            """,
            (usuario,)
        )

        if cursor.fetchone():

            return False, "Usuário já cadastrado."


        # HASH DA SENHA

        senha_hash = bcrypt.hashpw(
    senha.encode("utf-8"),
    bcrypt.gensalt()
).decode("utf-8")

        # INSERT

        cursor.execute(
            """
            INSERT INTO usuarios
            (usuario, senha_hash, tipo_usuario)
            VALUES (%s, %s, %s)
            """,
            (
                usuario,
                senha_hash,
                tipo_usuario
            )
        )

        conexao.commit()

        return True, "Usuário cadastrado com sucesso!"


    except Exception as erro:

        conexao.rollback()

        return False, f"Erro ao cadastrar usuário: {erro}"


    finally:

        if cursor:
            cursor.close()


# =====================================
# TELA DE CADASTRO DE USUÁRIOS
# =====================================

def tela_cadastro(sistema, conexao):

    # APENAS ADMINISTRADOR

    if st.session_state.perfil != "admin":

        st.error("Acesso não autorizado.")

        sistema.registrar(
            "WARNING",
            f"Tentativa de acesso ao cadastro de usuários - usuário: {st.session_state.usuario}"
        )

        return


    st.title("👤 Cadastro de Usuários")

    st.subheader("Cadastrar novo usuário")

    st.divider()


    # FORMULÁRIO

    with st.form("form_cadastro_usuario"):

        usuario = st.text_input(
            "Nome de usuário"
        )

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


    # VALIDAÇÕES

    if cadastrar:

        if not usuario.strip() or not senha or not confirmar_senha:

            st.error("Preencha todos os campos.")

        elif senha != confirmar_senha:

            st.error("As senhas não coincidem.")

        else:

            sucesso, mensagem = cadastrar_usuario(
                conexao,
                usuario.strip(),
                senha,
                tipo_usuario
            )


            if sucesso:

                st.success(mensagem)

                sistema.registrar(
                    "INFO",
                    f"{st.session_state.usuario} cadastrou o usuário {usuario.strip()} - Perfil: {tipo_usuario}"
                )

            else:

                st.error(mensagem)

                sistema.registrar(
                    "WARNING",
                    f"Falha ao cadastrar usuário {usuario.strip()} - {mensagem}"
                )
