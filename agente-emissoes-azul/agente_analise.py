import os
import requests
import pandas as pd
from dotenv import dotenv_values
from google import genai

# ==========================================
# 1. CONFIGURAÇÃO DE AMBIENTE
# ==========================================
pasta_atual = os.path.dirname(os.path.abspath(__file__))
pasta_raiz = os.path.dirname(pasta_atual)
caminho_env = os.path.join(pasta_raiz, '.env')

# Cria um dicionário com todos os segredos do .env
segredos = dotenv_values(caminho_env)
TOKEN_TELEGRAM = segredos.get("TOKEN_TELEGRAM")
CHAT_ID_ARLINDO = segredos.get("CHAT_ID_ARLINDO")
CHAVE_API_GOOGLE = segredos.get("CHAVE_API_GOOGLE")
CAMINHO_PLANILHA = segredos.get("CAMINHO_PLANILHA")

# Extração dos Magic Numbers usando o mesmo dicionário de segredos
SALDO_AZUL = segredos.get("SALDO_AZUL", "75000")
QTD_PASSAGEIROS = segredos.get("QTD_PASSAGEIROS", "2")

if not all([TOKEN_TELEGRAM, CHAT_ID_ARLINDO, CHAVE_API_GOOGLE, CAMINHO_PLANILHA]):
    raise ValueError("❌ Erro Crítico: Chaves ou caminhos ausentes no .env")

# ==========================================
# 2. INICIALIZAÇÃO DA IA
# ==========================================
cliente = genai.Client(api_key=CHAVE_API_GOOGLE)

# ==========================================
# 3. LEITURA DE DADOS (RAG - HISTÓRICO EXPANDIDO)
# ==========================================
print("📊 Extraindo histórico completo do Excel para análise de tendências...")
try:
    df = pd.read_excel(CAMINHO_PLANILHA, sheet_name="Historico_Precos")
    df = df.dropna(subset=['Preço (Pontos)'])
    
    # Extrai as últimas 30 medições para ter amostragem suficiente
    historico_recente = df.tail(30)
    
    dados_rag = ""
    for index, row in historico_recente.iterrows():
        # Formata a data e hora da busca para ficar limpo para a IA
        data_busca = str(row['Data/Hora da Busca']).split('.')[0] 
        dados_rag += f"[{data_busca}] Voo para {row['Destino']} em {row['Data do Voo']} | Preço: {row['Preço (Pontos)']} pts\n"
        
except Exception as e:
    print(f"❌ Erro ao ler o Excel: {e}")
    exit()

if not dados_rag.strip():
    print("🚨 NENHUM DADO FOI ENCONTRADO NO EXCEL!")
    exit()

# ==========================================
# 4. O CÉREBRO DA IA (PROMPT DE ANALYTICS)
# ==========================================
prompt_analise = f"""
Atue como um Analista de Dados de Viagens e Especialista em Milhas.
Seu objetivo é analisar o histórico de preços e emitir um parecer técnico sobre a tendência de custo.

CONTEXTO DO USUÁRIO:
- Objetivo: Viagem de 14 dias para a Europa (Portugal/Itália) em setembro de 2026.
- Passageiros: {QTD_PASSAGEIROS}.
- Saldo Azul Atual: {SALDO_AZUL} pontos.
- Ativos extras: Cartão C6 Carbon e Clube Azul 10k.

DADOS HISTÓRICOS EXTRAÍDOS:
{dados_rag}

SUA TAREFA:
1. Identifique se o preço está em tendência de queda, alta ou estabilidade.
2. Com base no saldo de {SALDO_AZUL} pontos, estime se a meta de emissão está próxima ou se o usuário deve aguardar uma promoção de transferência do C6 Carbon.
3. Seja breve, use um tom profissional e direto.

INSTRUÇÕES DE FORMATAÇÃO:
- Use HTML (<b>negrito</b>).
- NÃO use Markdown (asteriscos).
- Retorne apenas a análise técnica em no máximo 3 parágrafos.
"""

print("🧠 IA a processar tendências e a calcular estatísticas...\n")
try:
    resposta = cliente.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt_analise
    )
    relatorio_tendencia = resposta.text
    print("✅ Análise gerada com sucesso!")
except Exception as e:
    print(f"❌ Erro ao gerar análise: {e}")
    exit()

# ==========================================
# 5. DISPARO PARA O TELEGRAM
# ==========================================
def enviar_telegram(mensagem):
    try:
        url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
        payload = {
            "chat_id": CHAT_ID_ARLINDO,
            "text": mensagem,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("✅ [TELEGRAM] Análise de Tendência enviada com sucesso!")
        else:
            print(f"❌ [TELEGRAM] Erro na API: {response.text}")
    except Exception as e:
        print(f"❌ [TELEGRAM] Erro de conexão: {e}")

enviar_telegram(relatorio_tendencia)
