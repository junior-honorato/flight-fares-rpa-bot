import os
from google import genai

# 1. Apresentamos o "crachá" para o Google
chave_api = "AIzaSyAhbCfHXUoqLxaj1TinfjwlSHLcLSN6rUY"
cliente = genai.Client(api_key=chave_api)

# 2. Escrevemos a nossa pergunta (O Prompt)
pergunta = "Qual é a diferença entre um script RPA comum e um Agente de IA?"

print("🧠 Pensando...\n")

# 3. Mandamos a pergunta para o modelo Gemini 2.5 Flash (rápido e gratuito)
resposta = cliente.models.generate_content(
    model='gemini-2.5-flash',
    contents=pergunta
)

# 4. Imprimimos a resposta que a IA nos devolveu
print(resposta.text)