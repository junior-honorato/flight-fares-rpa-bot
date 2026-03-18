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

segredos = dotenv_values(caminho_env)
TOKEN_TELEGRAM = segredos.get("TOKEN_TELEGRAM")
CHAT_ID_ARLINDO = segredos.get("CHAT_ID_ARLINDO")
CHAVE_API_GOOGLE = segredos.get("CHAVE_API_GOOGLE")

if not all([TOKEN_TELEGRAM, CHAT_ID_ARLINDO, CHAVE_API_GOOGLE]):
    raise ValueError("❌ Erro Crítico: Chaves ausentes no .env")

# ==========================================
# 2. INICIALIZAÇÃO DA IA
# ==========================================
cliente = genai.Client(api_key=CHAVE_API_GOOGLE)

# ==========================================
# 3. LEITURA DE DADOS (RAG - HISTÓRICO EXPANDIDO)
# ==========================================
caminho_excel = r"C:\Users\junio\Desktop\Automacao_Azul\historico_precos_azul.xlsx"

print("📊 Extraindo histórico completo do Excel para análise de tendências...")
try:
    df = pd.read_excel(caminho_excel, sheet_name="Historico_Precos")
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
Atue como um Cientista de Dados e Consultor Financeiro focado em emissão de passagens aéreas.

CONTEXTO DA VIAGEM:
- Destino: Portugal e Itália (setembro de 2026).
- Passageiros: 2 (Titular e esposa).
- Saldo Azul Atual: 75.000 pontos (Nível Safira).
- Geração mensal: Clube Azul 10k.
- Backup financeiro: Cartão C6 Carbon (pontos Átomos transferíveis para Azul).

BASE DE DADOS HISTÓRICA (ÚLTIMAS BUSCAS DO ROBÔ):
{dados_rag}

Sua missão é ler este histórico de preços e gerar um relatório analítico tático para o Telegram.

IINSTRUÇÕES RIGOROSAS:
1. Não use saudações ou despedidas. Vá direto ao ponto.
2. Formate a resposta usando HTML básico (use <b>texto</b> para negrito). NUNCA use caracteres de Markdown como asteriscos (**) ou underlines (_).
3. O relatório DEVE conter exatamente estas 3 seções:
   - 📈 <b>Tendência do Mercado:</b> Os preços estão subindo, caindo ou estáveis nos últimos dias monitorados?
   - 🔢 <b>Estatísticas Chave:</b> Qual foi o menor preço histórico registrado na base acima e qual a média de preço atual?
   - 💡 <b>Recomendação Tática:</b> Cruzando o preço atual com os 75k de saldo e a geração do Clube 10k, compensa transferir pontos do C6 Carbon agora para garantir a emissão, ou o gráfico sugere que é melhor aguardar uma nova queda?

Gere o relatório analítico:
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
