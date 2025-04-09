import streamlit as st
from assistentevapi import consultar_modelo, registrar_feedback, memory, PERSONAS, ESTILOS

# Configuração da Interface
st.title("Chatbot com Oracle Generative AI")

# Inicializa histórico no session_state
if "historico" not in st.session_state:
    st.session_state.historico = []

# Escolha da Persona
st.subheader("Escolha uma Persona")
persona = st.selectbox("Selecione um perfil:", list(PERSONAS.keys()))

# Escolha do Estilo
st.subheader("Escolha o Estilo de Resposta")
estilo = st.selectbox("Selecione um tom:", list(ESTILOS.keys()))

# Exibir histórico de conversas
st.subheader("Histórico de Conversas")
for interacao in st.session_state.historico:
    st.write(f"**Usuário:** {interacao['pergunta']}")
    st.write(f"**Chatbot:** {interacao['resposta']}")
    
    # Botões de feedback
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("👍", key=f"like_{interacao['pergunta']}"):
            registrar_feedback(interacao['pergunta'], interacao['resposta'], "positivo")
            st.rerun()
    with col2:
        if st.button("👎", key=f"dislike_{interacao['pergunta']}"):
            registrar_feedback(interacao['pergunta'], interacao['resposta'], "negativo")
            st.rerun()

    st.write("---")

# Entrada do usuário
pergunta = st.text_input("Digite sua pergunta:")

# Botão de envio
if st.button("Enviar"):
    if pergunta:
        resposta = consultar_modelo(pergunta, persona, estilo)
        
        # Atualiza histórico com a memória do LangChain
        memory.save_context({"input": pergunta}, {"output": resposta})
        st.session_state.historico.append({"pergunta": pergunta, "resposta": resposta})
        
        # Recarrega a interface para mostrar novo histórico
        st.rerun()
