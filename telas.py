import streamlit as st
from autenticacao import autenticar, ler_logs_local
import pandas as pd
import random
import time
from datetime import datetime
# =====================================
# TELA DE LOGIN
# =====================================
def tela_login(log):

    st.title(
        "🔐 Sistema Supervisório"
    )

    st.subheader(
        "Autenticação"
    )


    usuario = st.text_input(
        "Usuário"
    )


    senha = st.text_input(
        "Senha",
        type="password"
    )


    if st.button(
        "Entrar"
    ):
        if autenticar(
            usuario,
            senha,
            log
        ):
            st.rerun()

        else:

            st.error(
                "Usuário ou senha inválidos"
            )


    st.divider()

    st.write(
        "Usuários para teste:"
    )

    st.code(
        """
admin / admin123

operador / operador123
        """
    )

# =====================================
# TELA DO PROCESSO
# =====================================
@st.fragment(run_every=3)
def monitorar_temperatura():
    # Simular valor de temperatura:
    temp = random.uniform(40,50)
    # Adicionar ao historico do streamlit:
    st.session_state.leituras.append(
        {
            "Horários" : datetime.now().strftime("%H:%M:%S"),
            "Temperatura" : temp
        }
    )
    st.session_state.leituras = (
        st.session_state.leituras[-20:]
    )
    st.metric("Temperatura Atual",
             f"{temp:.2f}°C")
    #Grafico:
    st.scatter_chart(
        st.session_state.leituras,
        x="Horários",
        y="Temperatura"
    )



def tela_processo(log):

    st.title(
        "⚙️ Controle do Processo"
    )


    st.write(
        f"Usuário: "
        f"**{st.session_state.usuario}**"
    )


    st.write(
        f"Perfil: "
        f"**{st.session_state.perfil}**"
    )


    st.divider()


    # =================================
    # STATUS
    # =================================

    st.subheader(
        "Motor 01"
    )


    if st.session_state.motor_ligado:

        st.success(
            "Motor ligado"
        )

    else:

        st.error(
            "Motor desligado"
        )


    col1, col2 = st.columns(2)


    # =================================
    # LIGAR MOTOR
    # =================================

    with col1:

        if st.button(
            "🟢 Ligar Motor"
        ):

            st.session_state.motor_ligado = True


            log.registrar(
                "INFO",
                (
                    f"{st.session_state.usuario} "
                    f"ligou Motor 01"
                )
            )


            st.rerun()


    # =================================
    # DESLIGAR MOTOR
    # =================================

    with col2:

        if st.button(
            "🔴 Desligar Motor"
        ):

            st.session_state.motor_ligado = False

            st.session_state.velocidade = 0


            log.registrar(
                "INFO",
                (
                    f"{st.session_state.usuario} "
                    f"desligou Motor 01"
                )
            )


            st.rerun()


    st.divider()


    # =================================
    # VELOCIDADE
    # =================================

    velocidade = st.slider(
        "Velocidade do Motor",
        min_value=0,
        max_value=1800,
        value=st.session_state.velocidade,
        step=100
    )


    if st.button(
        "Aplicar velocidade"
    ):

        if not st.session_state.motor_ligado:

            st.warning(
                "O motor está desligado."
            )

            log.registrar(
                "WARNING",
                (
                    f"{st.session_state.usuario} "
                    f"tentou alterar a velocidade "
                    f"com o motor desligado"
                )
            )

        else:

            st.session_state.velocidade = (
                velocidade
            )


            log.registrar(
                "INFO",
                (
                    f"{st.session_state.usuario} "
                    f"alterou Motor 01 para "
                    f"{velocidade} RPM"
                )
            )


            st.success(
                f"Velocidade alterada para "
                f"{velocidade} RPM"
            )


    st.metric(
        "Velocidade atual",
        f"{st.session_state.velocidade} RPM"
    )
    st.divider()
    st.subheader("Monitoramento de Temperatura")
    monitorar_temperatura()

# =====================================
# TELA DO MONITORAMENTO DE LOG
# =====================================
def tela_monitoramento(log, arquivo):
    # Verificação de usuário:
    if st.session_state.perfil != "admin":
        st.error("Acesso não autorizado")
        log.registrar("WARNING",
        f"Tentativa de acesso não autorizado ao Monitoramento - usuário: {st.session_state.usuario}")
    else:
        st.title("🛡️ Monitoramento")
        st.write("Monitoramento de eventos de segurança")
        logs = ler_logs_local(arquivo)
        st.divider()
        if logs.empty:
            st.info("Nenhum Evento encontrado")
        else:
            total_logs = len(logs)
            total_info = (logs['nivel']=="INFO").sum()
            total_warn = (logs['nivel']=="WARNING").sum()
            total_erro = (logs['nivel']=="ERROR").sum()
            total_crit = (logs['nivel']=="CRITICAL").sum()
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
            minutos = st.text_input("Tempo para análise",
                                    value="60")
            inicio = pd.Timestamp.now() - pd.Timedelta(
                                    minutes = int(minutos))
            mask = (
                (pd.to_datetime(logs['data']) >= inicio) 
                &
                (logs['mensagem']
                        .astype(str)
                        .str.contains("Tentativa de login inválida",
                                    na=False,
                                    case=False,
                                    regex=False))
            )
            tentativas_invalidas = (mask.sum())
            st.subheader("Análise de Segurança")
            st.write(f"Tentativas inválidas: {tentativas_invalidas}")
            
            if tentativas_invalidas>=3:
                st.error("🚨 ALERTA: Possível ataque de força bruta!")
            else:
                st.success("Nenhum ataque de força bruta!")
            
            # Gráfico dos eventos:
            st.bar_chart(logs['nivel'].value_counts())

            
            #st.write(inicio)
            #st.write(pd.to_datetime(logs['data']).dtype)

            logs = logs.sort_index(ascending=False)
            st.subheader("Eventos Registrados:")
            filtro = st.selectbox(
                "Filtro por nível:",
                [
                    "Todos",
                    "INFO",
                    "WARNING",
                    "ERROR",
                    "CRITICAL"
                ]
            )
            if filtro == "Todos":
                logs = logs
            else:
                mask = logs['nivel'] == filtro
                logs=logs[mask]
            st.dataframe(logs)