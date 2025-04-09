import streamlit as st
from assistentev2 import consultar_modelo, historico, exibir_historico, atualizar_historico

# Configurações da Interface Streamlit
st.title("Chatbot com Oracle Generative AI")

# Exibir o histórico de conversas no início
st.subheader("Histórico de Conversas")
for interacao in historico:
    st.write(f"**Usuário:** {interacao['pergunta']}")
    st.write(f"**Chatbot:** {interacao['resposta']}")
    st.write("---")

# Entrada do usuário
pergunta = st.text_input("Digite sua pergunta:")

# Botão de envio
if st.button("Enviar"):
    if pergunta:
        # Obtém a resposta do modelo e atualiza o histórico
        resposta = consultar_modelo(pergunta)

        # Exibe a resposta no Streamlit
        st.write(f"**Chatbot:** {resposta}")
        
        # Exibir o histórico atualizado
        st.subheader("Histórico de Conversas")
        for interacao in historico:
            st.write(f"**Usuário:** {interacao['pergunta']}")
            st.write(f"**Chatbot:** {interacao['resposta']}")
            st.write("---")
