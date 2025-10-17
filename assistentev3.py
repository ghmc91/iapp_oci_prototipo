import oci
import json
from typing import Dict, Any

# Configuração do ambiente OCI
CONFIG_PROFILE = "DEFAULT"
CONFIG_PATH = r"C:\Users\Usuario\.oci\config"
COMPARTMENT_ID = "ocid1.tenancy.oc1..aaaaaaaa2r7rgrqrxbbyaff7wk4iohx7zfldzcyw24z3eznmmg3mr7juhywa"
#ENDPOINT_ID = "ocid1.generativeaiendpoint.oc1.sa-saopaulo-1.amaaaaaaj6wdqoyayulrohfwrlvlag2zi3ecbsa6gxjqektgu5r2gx2vadjq"
ENDPOINT_URL = "https://inference.generativeai.sa-saopaulo-1.oci.oraclecloud.com"

# Inicializando o cliente OCI
config = oci.config.from_file(CONFIG_PATH, CONFIG_PROFILE)
generative_ai_client = oci.generative_ai_inference.GenerativeAiInferenceClient(
    config=config, service_endpoint=ENDPOINT_URL, retry_strategy=oci.retry.NoneRetryStrategy(), timeout=(10, 240)
)

# Histórico de conversas
historico = []
MAX_HISTORICO = 5  # Número máximo de interações armazenadas
feedbacks = []  # Lista para armazenar feedbacks


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
    """Formata o histórico como contexto para a IA."""
    contexto = ""
    for interacao in historico[-MAX_HISTORICO:]:
        contexto += f"Usuário: {interacao['pergunta']}\nChatbot: {interacao['resposta']}\n"
    return contexto

def criar_chat_request(pergunta, persona, estilo):
    """Configura e retorna o objeto de requisição para a IA."""
    contexto = formatar_historico()
    
    # Define o tom baseado na persona e no estilo escolhidos pelo usuário
    instrucoes = f"{PERSONAS[persona]} {ESTILOS[estilo]}"
    
    mensagem_completa = f"{instrucoes}\n{contexto}Usuário: {pergunta}\nChatbot: "

    chat_request = oci.generative_ai_inference.models.CohereChatRequest()
    chat_request.message = mensagem_completa
    chat_request.max_tokens = 600
    chat_request.temperature = 0.25
    chat_request.top_p = 0.75
    return chat_request

def criar_chat_detail(chat_request):
    """Cria o objeto de detalhes do chat."""
    chat_detail = oci.generative_ai_inference.models.ChatDetails()
    chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id="ocid1.generativeaimodel.oc1.sa-saopaulo-1.amaaaaaask7dceyaxu7lvx6k45r2hapxtuc2q5rleaujcowq6xbcywwtzhsq")
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
    """Armazena a interação no histórico."""
    historico.append({"pergunta": pergunta, "resposta": resposta})
    if len(historico) > MAX_HISTORICO:
        historico.pop(0)

def registrar_feedback(pergunta, resposta, feedback):
    """Registra a avaliação do usuário sobre a resposta recebida."""
    feedbacks.append({"pergunta": pergunta, "resposta": resposta, "feedback": feedback})


def carregar_dcns(caminho_arquivo: str) -> Dict[str, Any]:
    """
    Carrega o JSON das Diretrizes Curriculares Nacionais (DCNs) de Computação.

    Args:
        caminho_arquivo (str): Caminho para o arquivo JSON. Default: "dcns.json"

    Returns:
        dict: Estrutura do JSON carregada em um dicionário Python.
    """
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
        return dados
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {caminho_arquivo}")
        return {}
    except json.JSONDecodeError:
        print(f"❌ Erro ao decodificar JSON em {caminho_arquivo}")
        return {}

caminho = r'C:\Users\Usuario\Documents\IAPP\iapp_oci_prototipo\DCNS\DCN_COMPUTACACAO.json'
dados = carregar_dcns(caminho)
CURSO = dados['curso']
COMPETENCIAS_GERAIS = dados['competencias_gerais']