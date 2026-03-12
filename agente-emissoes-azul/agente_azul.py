import os
from google import genai

# 1. Autenticação
chave_api = "SUA_CHAVE_AQUI"
cliente = genai.Client(api_key=chave_api)

# 2. Simulando os dados que o seu robô RPA extraiu do site (Mock Data)
# Numa versão final, o seu robô geraria esta lista automaticamente.
dados_voos = """
[
  {"destino": "Lisboa (LIS)", "data": "10/09/2026", "preco_pontos_por_pessoa": 45000, "taxa_embarque_reais": 250},
  {"destino": "Roma (FCO)", "data": "12/09/2026", "preco_pontos_por_pessoa": 35000, "taxa_embarque_reais": 300},
  {"destino": "Lisboa (LIS)", "data": "15/09/2026", "preco_pontos_por_pessoa": 40000, "taxa_embarque_reais": 200}
]
"""

# 3. O "System Prompt" - Aqui é onde a mágica acontece!
# Vamos dar uma identidade e regras matemáticas estritas para a IA.
prompt_agente = f"""
Atue como um analista de emissões de passagens aéreas de alta performance.

O nosso cenário é o seguinte:
- Estou a planear uma viagem de 14 dias para a Europa com a minha esposa em setembro de 2026.
- O foco da viagem será Portugal e Itália.
- O nosso saldo combinado é de exatos 75.000 pontos na Azul.
- Eu sou cliente categoria Safira.

Aqui estão os resultados que o meu sistema de monitorização acabou de extrair do site da Azul:
{dados_voos}

A tua tarefa:
1. Calcule o custo total em pontos para duas pessoas (eu e a minha esposa) para cada opção.
2. Verifique se alguma destas opções cabe no nosso orçamento atual de 75.000 pontos.
3. Formule uma resposta curta, direta e num tom de "alerta executivo" informando qual é a melhor jogada que eu devo fazer hoje.
"""

print("✈️ O Agente está a analisar os voos da Azul...\n")

# 4. Enviamos o contexto e os dados para a IA pensar
resposta = cliente.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt_agente
)

# 5. Imprimimos a decisão do Agente
print(resposta.text)