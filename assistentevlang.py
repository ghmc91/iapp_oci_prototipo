import oci
from langchain.memory import ConversationBufferMemory

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

# Criando memória com LangChain
memory = ConversationBufferMemory(memory_key="historico", return_messages=True)

# Perfis disponíveis
PERSONAS = {
    "Professor": "Explique de maneira clara e didática, como se estivesse ensinando um aluno.",
    "Suporte Técnico": "Responda de forma objetiva e técnica, como um especialista em TI ajudando um usuário.",
    "Contador de Histórias": "Use uma linguagem envolvente e criativa, como um contador de histórias.",
}

# Estilos disponíveis
ESTILOS = {
    "Formal": "Utilize um tom respeitoso e formal.",
    "Técnico": "Responda com detalhes técnicos e termos precisos.",
    "Simples": "Explique de forma curta e direta, para fácil entendimento.",
}

def formatar_historico():
    """Recupera o histórico de interações usando LangChain."""
    return memory.load_memory_variables({})["historico"]

def criar_chat_request(pergunta, persona, estilo):
    """Configura e retorna o objeto de requisição para a IA."""
    contexto = formatar_historico()
    
    # Define o tom baseado na persona e no estilo escolhidos pelo usuário
    instrucoes = f"{PERSONAS[persona]} {ESTILOS[estilo]}"
    
    mensagem_completa = f"{instrucoes}\n{contexto}\nUsuário: {pergunta}\nChatbot: "

    chat_request = oci.generative_ai_inference.models.CohereChatRequest()
    chat_request.message = mensagem_completa
    chat_request.max_tokens = 600
    chat_request.temperature = 0.25
    chat_request.top_p = 0.75
    return chat_request

def criar_chat_detail(chat_request):
    """Cria o objeto de detalhes do chat."""
    chat_detail = oci.generative_ai_inference.models.ChatDetails()
    chat_detail.serving_mode = oci.generative_ai_inference.models.DedicatedServingMode(endpoint_id=ENDPOINT_ID)
    chat_detail.chat_request = chat_request
    chat_detail.compartment_id = COMPARTMENT_ID
    return chat_detail

def consultar_modelo(pergunta, persona, estilo):
    """Interage com a IA da Oracle e retorna a resposta gerada."""
    try:
        chat_request = criar_chat_request(pergunta, persona, estilo)
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
    """Armazena a interação na memória do LangChain."""
    memory.save_context({"input": pergunta}, {"output": resposta})

def registrar_feedback(pergunta, resposta, feedback):
    """Registra a avaliação do usuário sobre a resposta recebida."""
    return {"pergunta": pergunta, "resposta": resposta, "feedback": feedback}
