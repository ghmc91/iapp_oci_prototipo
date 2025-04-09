import oci

# Configuração do ambiente OCI
CONFIG_PROFILE = "DEFAULT"
CONFIG_PATH = r"C:\Users\adria\.oci\config"
COMPARTMENT_ID = "ocid1.tenancy.oc1..aaaaaaaahqt2p7d7dgi4y7d3vlmqmfxeh3rkcuyjxcifg6tzdlotqqovfdda"
ENDPOINT_ID = "ocid1.generativeaiendpoint.oc1.sa-saopaulo-1.amaaaaaaj6wdqoyayulrohfwrlvlag2zi3ecbsa6gxjqektgu5r2gx2vadjq"
ENDPOINT_URL = "https://inference.generativeai.sa-saopaulo-1.oci.oraclecloud.com"

# Inicializando o cliente OCI
config = oci.config.from_file(CONFIG_PATH, CONFIG_PROFILE)
generative_ai_client = oci.generative_ai_inference.GenerativeAiInferenceClient(
    config=config, service_endpoint=ENDPOINT_URL, retry_strategy=oci.retry.NoneRetryStrategy(), timeout=(10, 240)
)

# Histórico de conversas
historico = []
MAX_HISTORICO = 5  # Número máximo de interações armazenadas

def formatar_historico():
    """Formata o histórico como contexto para a IA."""
    contexto = ""
    for interacao in historico[-MAX_HISTORICO:]:  # Mantém apenas as últimas N interações
        contexto += f"Usuário: {interacao['pergunta']}\nChatbot: {interacao['resposta']}\n"
    return contexto

def criar_chat_request(pergunta):
    """Configura e retorna o objeto de requisição para a IA."""
    contexto = formatar_historico()
    mensagem_completa = f"{contexto}Usuário: {pergunta}\nChatbot: "

    chat_request = oci.generative_ai_inference.models.CohereChatRequest()
    chat_request.message = mensagem_completa
    chat_request.max_tokens = 600
    chat_request.temperature = 0.25
    chat_request.frequency_penalty = 0
    chat_request.top_p = 0.75
    chat_request.top_k = 0
    return chat_request

def criar_chat_detail(chat_request):
    """Cria o objeto de detalhes do chat, incluindo o endpoint e compartment_id."""
    chat_detail = oci.generative_ai_inference.models.ChatDetails()
    chat_detail.serving_mode = oci.generative_ai_inference.models.DedicatedServingMode(endpoint_id=ENDPOINT_ID)
    chat_detail.chat_request = chat_request
    chat_detail.compartment_id = COMPARTMENT_ID
    return chat_detail

def consultar_modelo(pergunta):
    """Interage com a IA da Oracle e retorna a resposta gerada."""
    try:
        chat_request = criar_chat_request(pergunta)
        chat_detail = criar_chat_detail(chat_request)

        chat_response = generative_ai_client.chat(chat_detail)

        if hasattr(chat_response.data, 'chat_response') and hasattr(chat_response.data.chat_response, 'text'):
            resposta = chat_response.data.chat_response.text
            atualizar_historico(pergunta, resposta)
            return resposta
        
        return "A resposta não contém texto gerado."

    except Exception as e:
        return f"Erro ao interagir com a API: {str(e)}"

def atualizar_historico(pergunta, resposta):
    """Armazena a interação no histórico e limita o tamanho máximo."""
    historico.append({"pergunta": pergunta, "resposta": resposta})
    if len(historico) > MAX_HISTORICO:
        historico.pop(0)  # Remove a interação mais antiga

def exibir_historico():
    """Mostra o histórico de conversas."""
    print("\n--- Histórico de Conversas ---")
    for interacao in historico:
        print(f"Usuário: {interacao['pergunta']}")
        print(f"Chatbot: {interacao['resposta']}")
        print("----------------------------")
    print()

def iniciar_chat_cli():
    """Executa o chatbot no terminal (CLI)."""
    print("Chatbot Generativo - Digite 'sair' para encerrar.")
    while True:
        pergunta = input("Você: ")
        if pergunta.lower() == "sair":
            print("Encerrando o chatbot.")
            break
        resposta = consultar_modelo(pergunta)
        print(f"Chatbot: {resposta}")
        exibir_historico()

# Inicia o chatbot no terminal
if __name__ == "__main__":
    iniciar_chat_cli()
