import telebot
import subprocess
import sys
import os

# --- SUAS CREDENCIAIS ---
TOKEN_TELEGRAM = "SEU_TOKEN_AQUI"

# Inicializa o bot em modo de escuta
bot = telebot.TeleBot(TOKEN_TELEGRAM)

print("🎧 Orquestrador ligado! O bot está aguardando comandos no Telegram...")

# ==========================================
# MAPEAMENTO DE PASTAS (O SEGREDO PARA NÃO DAR ERRO)
# ==========================================
# 1. Descobre onde o orquestrador está a correr agora:
pasta_atual = os.path.dirname(os.path.abspath(__file__))

# 2. Descobre qual é a pasta "pai" (uma acima):
pasta_acima = os.path.dirname(pasta_atual)

# 3. Monta os caminhos exatos para os ficheiros:
caminho_rpa = os.path.join(pasta_acima, "azul_bot.py")
caminho_agente = os.path.join(pasta_atual, "agente_leitor_excel.py")

# Cria um gatilho para o comando /buscar
@bot.message_handler(commands=['buscar'])
def comando_buscar(mensagem):
    # 1. Dá um feedback imediato no seu telemóvel
    bot.reply_to(mensagem, "✈️ Entendido, chefe! Acordando o robô...\n\nVou abrir o navegador, buscar os preços de hoje e logo em seguida passo para a IA analisar. Isso leva cerca de 2 minutos. ⏳")
    
    print("\n[🤖 COMANDO RECEBIDO] Iniciando a esteira de automação...")
    
    try:
        # 2. Chama o seu script RPA na pasta de cima
        print(f"-> Executando o RPA em: {caminho_rpa}")
        subprocess.run([sys.executable, caminho_rpa], check=True)
        
        # 3. Chama o Agente de IA na pasta atual
        print(f"-> Executando o Agente de IA em: {caminho_agente}")
        subprocess.run([sys.executable, caminho_agente], check=True)
        
        print("✅ Esteira concluída com sucesso. Aguardando novos comandos.")
        
    except Exception as e:
        erro_msg = f"❌ Ocorreu um erro durante a execução da esteira: {e}"
        print(erro_msg)
        bot.reply_to(mensagem, erro_msg)

# Mantém o script rodando em loop infinito à prova de quedas de rede

bot.infinity_polling(timeout=10, long_polling_timeout=5)
