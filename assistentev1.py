import oci

# Configuração do ambiente
compartment_id = "ocid1.tenancy.oc1..aaaaaaaahqt2p7d7dgi4y7d3vlmqmfxeh3rkcuyjxcifg6tzdlotqqovfdda"
CONFIG_PROFILE = "DEFAULT"
config = oci.config.from_file(r"C:\Users\adria\.oci\config", CONFIG_PROFILE)

# Endpoint do serviço Generative AI
endpoint = "https://inference.generativeai.sa-saopaulo-1.oci.oraclecloud.com"

# Inicializando o cliente
generative_ai_inference_client = oci.generative_ai_inference.GenerativeAiInferenceClient(
    config=config, service_endpoint=endpoint, retry_strategy=oci.retry.NoneRetryStrategy(), timeout=(10, 240)
)

def consultar_modelo(pergunta):
    try:
        # Criando a solicitação de chat
        chat_request = oci.generative_ai_inference.models.CohereChatRequest()
        chat_request.message = pergunta
        chat_request.max_tokens = 600
        chat_request.temperature = 0.25
        chat_request.frequency_penalty = 0
        chat_request.top_p = 0.75
        chat_request.top_k = 0

        # Configuração do chat
        chat_detail = oci.generative_ai_inference.models.ChatDetails()
        chat_detail.serving_mode = oci.generative_ai_inference.models.DedicatedServingMode(
            endpoint_id="ocid1.generativeaiendpoint.oc1.sa-saopaulo-1.amaaaaaaj6wdqoyayulrohfwrlvlag2zi3ecbsa6gxjqektgu5r2gx2vadjq"
        )
        chat_detail.chat_request = chat_request
        chat_detail.compartment_id = compartment_id

        # Envio da solicitação para o modelo
        chat_response = generative_ai_inference_client.chat(chat_detail)

        # Obtendo a resposta correta
        if hasattr(chat_response.data, 'chat_response') and hasattr(chat_response.data.chat_response, 'text'):
            return chat_response.data.chat_response.text
        return "A resposta não contém texto gerado."

    except Exception as e:
        return f"Erro ao interagir com a API: {str(e)}"

# Loop do chatbot
print("Chatbot Generativo - Digite 'sair' para encerrar.")
while True:
    pergunta = input("Você: ")
    if pergunta.lower() == "sair":
        print("Encerrando o chatbot.")
        break
    resposta = consultar_modelo(pergunta)
    print(f"Chatbot: {resposta}")