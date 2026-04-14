import os
import sys
import requests
import pandas as pd
from dotenv import load_dotenv
from google import genai

sys.stdout.reconfigure(encoding='utf-8')

# ==========================================
# CONFIGURAÇÃO DE SEGURANÇA E AMBIENTE
# ==========================================
# 1. Descobre a pasta atual e sobe um nível para achar o .env na raiz do projeto
pasta_atual = os.path.dirname(os.path.abspath(__file__))
pasta_raiz = os.path.dirname(pasta_atual)
caminho_env = os.path.join(pasta_raiz, '.env')

# Carrega os segredos forçando a leitura do arquivo correto
load_dotenv(caminho_env, override=True)

# Resgata as chaves de forma segura (Atenção ao nome exato no .env)
TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
CHAT_ID_ARLINDO = os.getenv("CHAT_ID_ARLINDO")
CHAVE_API_GOOGLE = os.getenv("CHAVE_API_GOOGLE")

SALDO_AZUL = os.getenv("SALDO_AZUL", "75000")
QTD_PASSAGEIROS = os.getenv("QTD_PASSAGEIROS", "2")

# Validação de segurança
if not all([TOKEN_TELEGRAM, CHAT_ID_ARLINDO, CHAVE_API_GOOGLE]):
    raise ValueError(f"❌ Erro Crítico: Credenciais ausentes. Verifique o arquivo .env no caminho: {caminho_env}")

# ==========================================
# INICIALIZAÇÃO DA IA
# ==========================================
# Inicialização exclusiva do pacote google-genai
cliente = genai.Client(api_key=CHAVE_API_GOOGLE)

# ==========================================
# 3. LEITURA DE DADOS (RAG - ÚLTIMA BUSCA)
# ==========================================
caminho_excel = os.getenv("CAMINHO_PLANILHA")

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
# O CÉREBRO DA IA (O AGENTE)
# ==========================================
prompt_agente = f"""
Atue como um sistema de notificação executiva. O seu objetivo é gerar um "Flash Report" para ser lido em 5 segundos no ecrã de um celular.

CONTEXTO FINANCEIRO DO USUÁRIO:
- Objetivo: Viagem de 14 dias para a Europa (Portugal/Itália) em setembro de 2026.
- Passageiros: {QTD_PASSAGEIROS}.
- Saldo atualizado na Azul: {SALDO_AZUL} pontos.
- Ativos extras para cobrir déficit: Cartão de crédito C6 Carbon (transferível para a Azul) e assinatura mensal do Clube Azul 10k.

DADOS EXTRAÍDOS HOJE:
{dados_para_ia}

INSTRUÇÕES RIGOROSAS DE FORMATAÇÃO:
1. NÃO inclua saudações, introduções ("Fala galera", "Aqui está o resumo") ou despedidas. 
2. Retorne APENAS os 4 tópicos abaixo, sendo o mais direto possível.
3. Formate a resposta usando HTML básico (use <b>texto</b> para negrito). NUNCA use caracteres de Markdown como asteriscos (**) ou underlines (_).

MENSAGEM A GERAR:
🎯 Melhor Preço: [Menor preço encontrado e data]
🧮 Custo Total ({QTD_PASSAGEIROS} pax): [Total em pontos]
💰 Balanço: Faltam [X] pontos para os {SALDO_AZUL} atuais.
⚖️ Veredito: [1 frase direta. Se faltarem pontos, calcule quantos meses de Clube Azul 10k seriam necessários para cobrir, ou sugira avaliar o saldo do C6 Carbon. Nunca mande transferir sem avisar para checar o saldo].
"""

print("✈️ O Agente está a analisar e a redigir a mensagem para o Telegram...\n")
try:
    resposta = cliente.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt_agente
    )
    relatorio_final = resposta.text
    print("Mensagem gerada pela IA:\n", relatorio_final)
except Exception as e:
    print(f"❌ Erro ao gerar resposta com a IA: {e}")
    exit()

# ==========================================
# DISPARO AUTÔNOMO
# ==========================================
def enviar_telegram(mensagem):
    try:
        url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
        # O POST com JSON é a melhor prática para mensagens grandes e estruturadas
        payload = {
            "chat_id": CHAT_ID_ARLINDO,
            "text": mensagem,
            "parse_mode": "HTML" # Garante que as formatações e emojis funcionem
        }
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            print("✅ [TELEGRAM] Alerta inteligente enviado com sucesso no seu celular!")
        else:
            print(f"❌ [TELEGRAM] Erro na API: {response.text}")
    except Exception as e:
        print(f"❌ [TELEGRAM] Erro de conexão: {e}")

print("\n📱 A enviar alerta para o Telegram de Arlindo...")
enviar_telegram(relatorio_final)
