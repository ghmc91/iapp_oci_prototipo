import oci

# TODO: Please update config profile name and use the compartmentId that has policies grant permissions for using Generative AI Service
compartment_id = "ocid1.tenancy.oc1..aaaaaaaahqt2p7d7dgi4y7d3vlmqmfxeh3rkcuyjxcifg6tzdlotqqovfdda"
CONFIG_PROFILE = "DEFAULT"
config = oci.config.from_file(r"C:\Users\adria\.oci\config", CONFIG_PROFILE)

# Service endpoint
endpoint = "https://inference.generativeai.sa-saopaulo-1.oci.oraclecloud.com"

generative_ai_inference_client = oci.generative_ai_inference.GenerativeAiInferenceClient(config=config, service_endpoint=endpoint, retry_strategy=oci.retry.NoneRetryStrategy(), timeout=(10,240))
chat_detail = oci.generative_ai_inference.models.ChatDetails()

chat_request = oci.generative_ai_inference.models.CohereChatRequest()
chat_request.message = "{Descreva a cidade de São Paulo em duas frases.}"
chat_request.max_tokens = 600
chat_request.temperature = 0.25
chat_request.frequency_penalty = 0
chat_request.top_p = 0.75
chat_request.top_k = 0
chat_request.seed = None


chat_detail.serving_mode = oci.generative_ai_inference.models.DedicatedServingMode(endpoint_id="ocid1.generativeaiendpoint.oc1.sa-saopaulo-1.amaaaaaaj6wdqoyayulrohfwrlvlag2zi3ecbsa6gxjqektgu5r2gx2vadjq")
chat_detail.chat_request = chat_request
chat_detail.compartment_id = compartment_id
chat_response = generative_ai_inference_client.chat(chat_detail)
# Print result
print("**************************Chat Result**************************")
print(vars(chat_response))
