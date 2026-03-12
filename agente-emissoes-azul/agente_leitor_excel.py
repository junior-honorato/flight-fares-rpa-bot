import os
import requests
import pandas as pd
from google import genai

# ==========================================
# 1. SUAS CREDENCIAIS (PREENCHA AQUI)
# ==========================================
TOKEN_TELEGRAM = "SEU_TOKEN_AQUI" 
CHAT_ID_USUARIO = "SEU_ID_AQUI"
CHAVE_API_GOOGLE = "SUA_CHAVE_AQUI" 

# ==========================================
# 2. LEITURA DOS DADOS (O RPA)
# ==========================================
cliente = genai.Client(api_key=CHAVE_API_GOOGLE)
caminho_excel = r"C:\Users\junio\Desktop\Automacao_Azul\historico_precos_azul.xlsx"

print("🔍 Lendo a aba 'Historico_Precos' do Excel...")
try:
    df = pd.read_excel(caminho_excel, sheet_name="Historico_Precos")
    df = df.dropna(subset=['Preço (Pontos)'])
    ultimas_buscas = df.tail(3)
    
    dados_para_ia = ""
    for index, row in ultimas_buscas.iterrows():
        dados_para_ia += f"- Origem: {row['Origem']} -> Destino: {row['Destino']}, Data: {row['Data do Voo']}, Preço: {row['Preço (Pontos)']} pontos\n"
except Exception as e:
    print(f"❌ Erro ao ler o Excel: {e}")
    exit()

if not dados_para_ia.strip():
    print("🚨 NENHUM DADO FOI ENCONTRADO NO EXCEL!")
    exit()

# ==========================================
# 3. O CÉREBRO DA IA (O AGENTE)
# ==========================================
prompt_agente = f"""
Atue como um analista executivo de emissões de passagens aéreas.

Cenário restrito:
- Viagem para a Europa (Portugal/Itália) em setembro de 2026.
- Total de passageiros: 2 pessoas.
- Saldo atualizado: 75.000 pontos Azul no total (sendo 55.000 pontos da minha conta Safira + 20.000 pontos da conta da minha esposa).

Aqui estão os resultados reais que o sistema extraiu hoje:
{dados_para_ia}

A tua tarefa:
Formule um relatório detalhado e estruturado para o Telegram, contendo os seguintes tópicos:
1. 🔍 RESUMO DA BUSCA: Liste o menor preço encontrado hoje, destacando o destino e a data do voo.
2. 🧮 CÁLCULO DE EMISSÃO: Mostre a matemática claramente (Custo da passagem x 2 passageiros = Custo Total).
3. 📊 BALANÇO FINANCEIRO: Compare o Custo Total com o nosso saldo combinado de 75.000 pontos (mencione a composição do saldo) e informe o déficit exato de pontos que faltam.
4. 🎯 VEREDITO: Uma recomendação clara e objetiva (Comprar ou Esperar).

Use emojis para organizar os tópicos, mas evite formatação Markdown excessiva (como negritos em todas as palavras) para manter o texto limpo no celular.
"""

print("✈️ O Agente está a analisar e a redigir a mensagem para o Telegram...\n")
resposta = cliente.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt_agente
)

relatorio_final = resposta.text
print("Mensagem gerada pela IA:\n", relatorio_final)

# ==========================================
# 4. DISPARO AUTÔNOMO (A SUA FUNÇÃO ORIGINAL)
# ==========================================
def enviar_telegram(mensagem):
    try:
        url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
        params = {
            "chat_id": CHAT_ID_USUARIO,
            "text": mensagem,
        }
        response = requests.get(url, params=params)

        if response.status_code == 200:
            print("✅ [TELEGRAM] Alerta inteligente enviado com sucesso no seu celular!")
        else:
            print(f"❌ [TELEGRAM] Erro na API: {response.text}")
    except Exception as e:
        print(f"❌ [TELEGRAM] Erro de conexão: {e}")

print("\n📱 A enviar alerta para o Telegram de Arlindo...")

# Aqui chamamos a sua função passando o texto que a IA acabou de escrever

enviar_telegram(relatorio_final)
