
import os
import streamlit as st
import mysql.connector

from dotenv import load_dotenv

from classe_OPC import (
    Coneccao_Opc,
    URL_OPC,
    NODES_OPC
)

load_dotenv()


# =====================================
# CONEXAO COM MYSQL
# =====================================

def conectar_banco_eventos():

    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )


# =====================================
# CRIACAO DA TABELA DE OPERACOES
# =====================================

def preparar_tabela_operacoes():

    conexao = conectar_banco_eventos()

    cursor = conexao.cursor()

    try:

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS operacoes_processo (

                id BIGINT AUTO_INCREMENT PRIMARY KEY,

                equipamento VARCHAR(100) NOT NULL,

                operacao VARCHAR(255) NOT NULL,

                usuario VARCHAR(100) NOT NULL,

                data_hora DATETIME NOT NULL
                    DEFAULT CURRENT_TIMESTAMP

            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )

        conexao.commit()

    finally:

        cursor.close()
        conexao.close()


# =====================================
# REGISTRO DE OPERACOES NO MYSQL
# =====================================

def salvar_operacao(equipamento, operacao, usuario):

    conexao = conectar_banco_eventos()

    cursor = conexao.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO operacoes_processo
            (equipamento, operacao, usuario)
            VALUES (%s, %s, %s)
            """,
            (
                equipamento,
                operacao,
                usuario
            )
        )

        conexao.commit()

    finally:

        cursor.close()
        conexao.close()


# =====================================
# REGISTRO LOCAL E CLOUDWATCH
# =====================================

def registrar_evento(sistema, equipamento, operacao, usuario):

    sistema.registrar(
        "INFO",
        (
            f"Equipamento: {equipamento} | "
            f"Operação: {operacao} | "
            f"Usuário: {usuario}"
        )
    )

    try:

        salvar_operacao(
            equipamento,
            operacao,
            usuario
        )

        return True

    except Exception as erro:

        st.warning(
            "O comando foi executado, mas não foi possível "
            f"salvar o histórico no MySQL: {erro}"
        )

        return False


# =====================================
# CONSULTA DO HISTORICO
# =====================================

def consultar_operacoes():

    conexao = conectar_banco_eventos()

    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT

                DATE_FORMAT(
                    data_hora,
                    '%d/%m/%Y %H:%i:%s'
                ) AS data_hora,

                equipamento,
                operacao,
                usuario

            FROM operacoes_processo

            ORDER BY id DESC

            LIMIT 50
            """
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        conexao.close()


# =====================================
# TABELA VISUAL DE OPERACOES
# =====================================

@st.fragment(run_every="5s")
def tabela_operacoes():

    try:

        registros = consultar_operacoes()

        if registros:

            st.dataframe(
                registros,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "data_hora": st.column_config.TextColumn(
                        "Data e hora"
                    ),
                    "equipamento": st.column_config.TextColumn(
                        "Equipamento"
                    ),
                    "operacao": st.column_config.TextColumn(
                        "Operação"
                    ),
                    "usuario": st.column_config.TextColumn(
                        "Usuário"
                    )
                }
            )

        else:

            st.info(
                "Nenhuma operação registrada até o momento."
            )

    except Exception as erro:

        st.error(
            f"Não foi possível consultar o histórico: {erro}"
        )


# =====================================
# MONITORAMENTO OPC UA
# =====================================

@st.fragment(run_every="2s")
def monitoramento_processo_opc():

    conexao_opc = Coneccao_Opc(URL_OPC)

    try:

        dados = conexao_opc.leitura_varios(
            NODES_OPC
        )

        st.success(
            "Comunicação com o Open Industry estabelecida."
        )

        # =================================
        # INDICADORES PRINCIPAIS
        # =================================

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Estado da esteira",
                "LIGADA" if dados["Motor"] else "DESLIGADA"
            )

        with col2:

            st.metric(
                "Sensor de presença",
                "ACIONADO" if dados["Sensor"] else "LIVRE"
            )

        with col3:

            st.metric(
                "Caixas coletadas",
                int(dados["CaixasColetadas"])
            )

        st.divider()

        # =================================
        # INDICADORES COMPLEMENTARES
        # =================================

        col4, col5 = st.columns(2)

        with col4:

            st.metric(
                "Velocidade",
                f"{float(dados['Velocidade']):.2f} m/s"
            )

        with col5:

            st.metric(
                "Caixas armazenadas",
                int(dados["Armazenadas"])
            )

        # =================================
        # SITUACAO DO PROCESSO
        # =================================

        st.markdown("### Situação do processo")

        if dados["Motor"]:

            st.success(
                "Esteira em funcionamento."
            )

        else:

            st.warning(
                "Esteira parada."
            )

        if dados["Sensor"]:

            st.warning(
                "Caixa detectada pelo sensor."
            )

        else:

            st.info(
                "Sensor livre."
            )

    except Exception as erro:

        st.error(
            f"Falha na comunicação OPC UA: {erro}"
        )


# =====================================
# TELA DE PROCESSOS
# =====================================

def tela_processo(sistema):

    st.title("Supervisório Industrial")

    st.subheader("Controle da esteira transportadora")

    st.caption(
        "Controle e monitoramento do processo industrial "
        "através do Open Industry Project."
    )

    usuario = st.session_state.get(
        "usuario",
        "desconhecido"
    )

    conexao_opc = Coneccao_Opc(URL_OPC)

    # =================================
    # PREPARACAO DO HISTORICO
    # =================================

    if not st.session_state.get(
        "tabela_operacoes_preparada",
        False
    ):

        try:

            preparar_tabela_operacoes()

            st.session_state.tabela_operacoes_preparada = True

        except Exception as erro:

            st.warning(
                f"Não foi possível preparar o histórico de operações: {erro}"
            )

    # =================================
    # COMANDOS DA ESTEIRA
    # =================================

    st.markdown("### Comandos da esteira")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "LIGAR ESTEIRA",
            type="primary",
            use_container_width=True,
            key="botao_ligar_esteira"
        ):

            try:

                conexao_opc.escrita_bool(
                    NODES_OPC["Start"],
                    True
                )

                sucesso = registrar_evento(
                    sistema,
                    "Esteira transportadora",
                    "Esteira ligada",
                    usuario
                )

                st.success(
                    "Comando de partida enviado ao CLP."
                )

                if sucesso:
                    st.toast("Operação registrada no histórico.")

            except Exception as erro:

                sistema.registrar(
                    "ERROR",
                    f"Falha ao ligar esteira: {type(erro).__name__}"
                )

                st.error(
                    f"Não foi possível ligar a esteira: {erro}"
                )

    with col2:

        if st.button(
            "PARAR ESTEIRA",
            type="secondary",
            use_container_width=True,
            key="botao_parar_esteira"
        ):

            try:

                conexao_opc.escrita_bool(
                    NODES_OPC["Start"],
                    False
                )

                sucesso = registrar_evento(
                    sistema,
                    "Esteira transportadora",
                    "Esteira desligada",
                    usuario
                )

                st.warning(
                    "Comando de parada enviado ao CLP."
                )

                if sucesso:
                    st.toast("Operação registrada no histórico.")

            except Exception as erro:

                sistema.registrar(
                    "ERROR",
                    f"Falha ao parar esteira: {type(erro).__name__}"
                )

                st.error(
                    f"Não foi possível parar a esteira: {erro}"
                )

    # =================================
    # AJUSTE DE VELOCIDADE
    # =================================

    st.divider()

    st.markdown("### Ajuste de velocidade")

    velocidade = st.number_input(
        "Velocidade desejada (m/s)",
        min_value=0.1,
        max_value=2.0,
        value=0.5,
        step=0.1,
        key="velocidade_desejada"
    )

    if st.button(
        "APLICAR VELOCIDADE",
        key="botao_aplicar_velocidade"
    ):

        try:

            conexao_opc.escrita_real(
                NODES_OPC["Velocidade"],
                velocidade
            )

            sucesso = registrar_evento(
                sistema,
                "Esteira transportadora",
                f"Velocidade alterada para {velocidade:.2f} m/s",
                usuario
            )

            st.success(
                "Nova velocidade enviada ao CLP."
            )

            if sucesso:
                st.toast("Alteração registrada no histórico.")

        except Exception as erro:

            sistema.registrar(
                "ERROR",
                f"Falha ao alterar velocidade: {type(erro).__name__}"
            )

            st.error(
                f"Não foi possível alterar a velocidade: {erro}"
            )

    # =================================
    # MONITORAMENTO
    # =================================

    st.divider()

    st.markdown("### Monitoramento do processo")

    st.caption(
        "Informações atualizadas automaticamente a cada 2 segundos."
    )

    monitoramento_processo_opc()

    # =================================
    # HISTORICO DE OPERACOES
    # =================================

    st.divider()

    st.markdown("### Registro de operações")

    st.caption(
        "Histórico das operações realizadas pelos usuários. "
        "Atualização automática a cada 5 segundos."
    )

    tabela_operacoes()
