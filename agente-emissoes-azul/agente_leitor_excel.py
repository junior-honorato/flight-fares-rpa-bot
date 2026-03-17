import os
import requests
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai
import telebot

# ==========================================
# CONFIGURAÇÃO DE SEGURANÇA E AMBIENTE
# ==========================================
# Carrega os segredos do arquivo .env para a memória
load_dotenv()

# Resgata as chaves de forma segura
TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
CHAT_ID_ARLINDO = os.getenv("CHAT_ID_ARLINDO")
CHAVE_API_GOOGLE = os.getenv("CHAVE_API_GOOGLE")

# Validação de segurança (evita que o script rode cego)
if not all([TOKEN_TELEGRAM, CHAT_ID_ARLINDO, CHAVE_API_GOOGLE]):
    raise ValueError("❌ Erro Crítico: Uma ou mais credenciais (Telegram, Chat ID ou Google API) estão faltando no arquivo .env!")

# ==========================================
# INICIALIZAÇÃO DOS SERVIÇOS
# ==========================================
# Configura o cérebro da IA (Gemini)
genai.configure(api_key=CHAVE_API_GOOGLE)

# Configura o mensageiro (Telegram)
bot = telebot.TeleBot(TOKEN_TELEGRAM)

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
Atue como um sistema de notificação executiva. O seu objetivo é gerar um "Flash Report" para ser lido em 5 segundos no ecrã de um celular.

CONTEXTO FINANCEIRO DO USUÁRIO:
- Objetivo: Viagem de 14 dias para a Europa (Portugal/Itália) em setembro de 2026 para 2 passageiros (titular e esposa).
- Saldo atualizado na Azul: 75.000 pontos (55.000 da conta Safira + 20.000 da conta da esposa).
- Ativos extras para cobrir déficit: Cartão de crédito C6 Carbon (que permite transferência para a Azul) e assinatura mensal do Clube Azul 10k (que injeta 10.000 pontos/mês).

DADOS EXTRAÍDOS HOJE:
{dados_para_ia}

INSTRUÇÕES RIGOROSAS DE FORMATAÇÃO:
1. NÃO inclua saudações, introduções ("Fala galera", "Aqui está o resumo") ou despedidas. 
2. Retorne APENAS os 4 tópicos abaixo, sendo o mais direto possível.

MENSAGEM A GERAR:
🎯 Melhor Preço: [Menor preço encontrado e data]
🧮 Custo Total (2 pax): [Total em pontos]
💰 Balanço: Faltam [X] pontos para os 75k atuais.
⚖️ Veredito: [1 frase direta. Se faltarem pontos, calcule quantos meses de Clube Azul 10k seriam necessários para cobrir, ou sugira avaliar o saldo do C6 Carbon. Nunca mande transferir sem avisar para checar o saldo].
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
            "chat_id": CHAT_ID_ARLINDO,
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
