import os
import sys
import requests
from dotenv import dotenv_values
from google import genai

# Força codificação UTF-8 no terminal
sys.stdout.reconfigure(encoding='utf-8')

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

# Extração de Variáveis Financeiras
SALDO_AZUL = segredos.get("SALDO_AZUL", "75000")
META_PONTOS = segredos.get("META_PONTOS", "120000")
QTD_PASSAGEIROS = segredos.get("QTD_PASSAGEIROS", "2")

if not all([TOKEN_TELEGRAM, CHAT_ID_ARLINDO, CHAVE_API_GOOGLE]):
    raise ValueError("❌ Erro Crítico: Chaves ausentes no .env")

# ==========================================
# 2. INICIALIZAÇÃO DA IA
# ==========================================
cliente = genai.Client(api_key=CHAVE_API_GOOGLE)

# ==========================================
# 3. O CÉREBRO DA IA (PROMPT DE SIMULAÇÃO MATEMÁTICA)
# ==========================================
prompt_simulador = f"""
Atue como um Planejador Financeiro especialista no programa TudoAzul e em emissão de passagens.

O usuário quer emitir uma passagem para a Europa (Setembro 2026) para {QTD_PASSAGEIROS} passageiros.
A meta máxima que ele aceita pagar (por trecho ou total, dependendo da estratégia dele) é de {META_PONTOS} pontos.

CENÁRIO FINANCEIRO ATUAL DO USUÁRIO:
- Saldo em conta: {SALDO_AZUL} pontos.
- Assinatura Ativa: Clube Azul 10.000 pontos por mês.
- Cartão de Crédito Principal: C6 Carbon (Pontos Átomos, transferíveis para a Azul).

SUA MISSÃO:
Faça uma simulação matemática exata focada no DÉFICIT de pontos, assumindo o pior cenário (onde a passagem custe exatamente o teto da meta de {META_PONTOS} pontos).

Forneça um relatório direto com os seguintes tópicos:
1. O Déficit: Calcule a diferença matemática entre a Meta ({META_PONTOS}) e o Saldo ({SALDO_AZUL}). 
2. Projeção Orgânica: Considerando a injeção de 10k pontos por mês do Clube Azul, em quantos meses o saldo empatará com a meta de forma orgânica?
3. Plano de Ação C6 Carbon: Recomende uma estratégia. O usuário deve focar em acumular no C6 e transferir agora com bônus (ex: 80% a 100%), ou o tempo até 2026 permite que o acúmulo orgânico do Clube seja suficiente sem queimar os pontos Átomos?

REGRAS RÍGIDAS DE FORMATAÇÃO (PARA TELEGRAM):
- Você SÓ ESTÁ AUTORIZADO a usar a tag HTML <b> para colocar textos em destaque.
- É ESTRITAMENTE PROIBIDO usar as tags <ul>, <ol>, <li>, <p> ou <br>.
- Para fazer listas, use apenas traços (-) ou emojis.
- NÃO use caracteres de Markdown como asteriscos (**).
"""

print("🧮 IA a processar cálculos e cenários financeiros...\n")
try:
    resposta = cliente.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt_simulador
    )
    relatorio_simulacao = resposta.text
    print("✅ Simulação gerada com sucesso!")
except Exception as e:
    print(f"❌ Erro ao gerar simulação: {e}")
    exit()

# ==========================================
# 4. DISPARO PARA O TELEGRAM
# ==========================================
def enviar_telegram(mensagem):
    try:
        url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
        payload = {
            "chat_id": CHAT_ID_ARLINDO,
            "text": mensagem,
            "parse_mode": "HTML"
        }
        
        # Faz o disparo e guarda a resposta do servidor
        response = requests.post(url, json=payload)
        
        # Verifica se o Telegram aceitou
        if response.status_code == 200:
            print("✅ [TELEGRAM] Relatório financeiro enviado com sucesso para o seu celular!")
        else:
            print(f"❌ [TELEGRAM] Erro na API (Formatação inválida): {response.text}")
            print("⚠️ Ativando plano de contingência: Reenviando sem formatação HTML...")
            
            # Fallback: Tenta enviar a mensagem de novo, mas como texto puro
            payload["parse_mode"] = None
            requests.post(url, json=payload)
            print("✅ [TELEGRAM] Mensagem enviada em modo de texto puro!")
            
    except Exception as e:
        print(f"❌ [TELEGRAM] Erro de rede/conexão: {e}")

enviar_telegram(relatorio_simulacao)
