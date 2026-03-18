import telebot
import subprocess
import time
import sys
import os
from dotenv import load_dotenv

# Carrega os segredos do arquivo .env para a memória do sistema
load_dotenv()

# Puxa o token com segurança
TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM") # <-- AJUSTADO: Para o nome exato que está no seu .env

# Se o token não for encontrado, ele avisa para evitar que o robô quebre em silêncio
if not TOKEN_TELEGRAM:
    raise ValueError("❌ Erro: TOKEN_TELEGRAM não encontrado. Verifique o seu arquivo .env!")

# ==========================================
# TRATAMENTO DE ERROS DE REDE (A BLINDAGEM)
# ==========================================
class BotExceptionHandler:
    def handle(self, exception):
        print(f"⚠️ [ALERTA DE REDE INTERNO] Ocorreu uma oscilação na conexão com o Telegram: {exception}")
        print("🔄 O bot irá ignorar o erro e tentar reconectar automaticamente...")
        return True 

# Inicializa o bot em modo de escuta passando o escudo de erros
bot = telebot.TeleBot(TOKEN_TELEGRAM, exception_handler=BotExceptionHandler())

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
caminho_analise = os.path.join(pasta_atual, "agente_analise.py") 
caminho_datas = os.path.join(pasta_acima, "datas_viagem.txt")

# ==========================================
# FUNÇÕES DE APOIO (LÊ E ESCREVE NO FORMATO CORRETO)
# ==========================================
def ler_datas_arquivo():
    """Lê o arquivo de texto e retorna apenas os 8 dígitos válidos."""
    datas = []
    if os.path.exists(caminho_datas):
        with open(caminho_datas, "r", encoding="utf-8") as f:
            for linha in f.readlines():
                if ":" in linha:
                    data = linha.split(":")[1].strip()
                    if len(data) == 8 and data.isdigit():
                        datas.append(data)
    return datas

def salvar_datas_arquivo(lista_datas):
    """Reescreve o arquivo inteiro mantendo o cabeçalho e a formatação (Data alvo: X)."""
    texto_manual = (
        "=== MANUAL DE DATAS PARA O ROBÔ ===\n"
        "# O robô só fará a leitura de linhas que contenham o caractere \":\"\n"
        "# Digite a data com 8 dígitos, sem barras.\n\n"
    )
    # Formata a lista para o padrão que o azul_bot.py espera ler
    linhas_datas = [f"Data alvo: {d}" for d in lista_datas]
    
    with open(caminho_datas, "w", encoding="utf-8") as f:
        f.write(texto_manual + "\n".join(linhas_datas) + "\n")

# ==========================================
# COMANDOS DO TELEGRAM
# ==========================================

# --- GATILHO: /buscar ---
@bot.message_handler(commands=['buscar'])
def comando_buscar(mensagem):
    # 1. Dá um feedback imediato no seu telemóvel
    bot.reply_to(mensagem, "✈️ Entendido, chefe, vamos que vamo! Acordando o robô...\n\nVou abrir o navegador, buscar os preços de hoje e logo em seguida passo para a IA analisar. Isso leva cerca de 6 minutos. ⏳")
    
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

# --- GATILHO: /datas ---
@bot.message_handler(commands=['datas'])
def painel_datas(mensagem):
    datas = ler_datas_arquivo()
    
    # Formata a lista atual para ficar bonita na tela (mostrando com barras para facilitar a leitura)
    if datas:
        texto_lista = "\n".join([f"🔸 {d[:2]}/{d[2:4]}/{d[4:]} (Código: `{d}`)" for d in datas])
    else:
        texto_lista = "A sua lista está vazia."

    msg_bot = (
        "📅 **PAINEL DE GERENCIAMENTO DE DATAS**\n\n"
        "**Sua lista atual:**\n"
        f"{texto_lista}\n\n"
        "O que você deseja fazer? Escolha UMA das opções:\n\n"
        "➕ **INCLUIR:** `+ 20092026`\n"
        "➖ **EXCLUIR:** `- 16092026`\n"
        "🔄 **ALTERAR:** `16092026 > 25092026`\n"
        "📝 **SUBSTITUIR TUDO:** Envie as novas datas com vírgula (Ex: `10092026, 11092026`)\n\n"
        "❌ **SAIR:** Digite `Cancelar`"
    )
    # Envia o painel e fica "escutando" a próxima mensagem do usuário
    msg = bot.reply_to(mensagem, msg_bot, parse_mode="Markdown")
    bot.register_next_step_handler(msg, processar_acao_data)

def processar_acao_data(mensagem):
    texto = mensagem.text.strip().upper()

    if texto == 'CANCELAR':
        bot.reply_to(mensagem, "✅ Ação cancelada. A sua lista não foi alterada.")
        return

    datas_atuais = ler_datas_arquivo()
    acao_sucesso = False
    feedback_msg = ""

    # Lógica 1: INCLUSÃO
    if texto.startswith('+'):
        nova_data = texto.replace('+', '').strip()
        if len(nova_data) == 8 and nova_data.isdigit():
            if nova_data not in datas_atuais:
                datas_atuais.append(nova_data)
                acao_sucesso = True
                feedback_msg = f"✅ Data **{nova_data}** INCLUÍDA com sucesso!"
            else:
                feedback_msg = "⚠️ Esta data já existe na sua lista."
        else:
            feedback_msg = "❌ Formato inválido! Envie 8 números (Ex: + 18092026)."

    # Lógica 2: EXCLUSÃO
    elif texto.startswith('-'):
        data_remover = texto.replace('-', '').strip()
        if data_remover in datas_atuais:
            datas_atuais.remove(data_remover)
            acao_sucesso = True
            feedback_msg = f"🗑️ Data **{data_remover}** EXCLUÍDA com sucesso!"
        else:
            feedback_msg = "⚠️ Esta data não foi encontrada na lista atual."

    # Lógica 3: ALTERAÇÃO
    elif '>' in texto:
        partes = texto.split('>')
        if len(partes) == 2:
            data_antiga = partes[0].strip()
            data_nova = partes[1].strip()

            if len(data_nova) == 8 and data_nova.isdigit():
                if data_antiga in datas_atuais:
                    index = datas_atuais.index(data_antiga)
                    datas_atuais[index] = data_nova
                    acao_sucesso = True
                    feedback_msg = f"🔄 Data **{data_antiga}** ALTERADA para **{data_nova}**!"
                else:
                    feedback_msg = f"⚠️ A data antiga ({data_antiga}) não está na lista."
            else:
                feedback_msg = "❌ Nova data em formato inválido! Use 8 números (Ex: 16092026 > 25092026)."
        else:
            feedback_msg = "❌ Formato inválido! Use apenas um sinal de maior (Ex: 16092026 > 25092026)."

    # Lógica 4: SUBSTITUIÇÃO EM MASSA (Separado por vírgula)
    elif ',' in texto:
        # Separa o que você digitou pelas vírgulas e limpa os espaços
        novas_datas = [d.strip() for d in texto.split(',')]
        
        # Filtra apenas as que têm exatamente 8 números
        datas_validas = [d for d in novas_datas if len(d) == 8 and d.isdigit()]
        
        if datas_validas:
            # A lista atual recebe APENAS as datas novas, apagando as velhas
            datas_atuais = datas_validas 
            acao_sucesso = True
            feedback_msg = f"📝 Lista inteira SUBSTITUÍDA por {len(datas_validas)} novas datas!"
        else:
            feedback_msg = "❌ Formato inválido! Certifique-se de mandar 8 números separados por vírgula."
            
    # Nenhuma das opções acima
    else:
        feedback_msg = "❌ Comando não reconhecido. Use `+`, `-`, `>`, ou separe por vírgula conforme as instruções."

    # Se a ação deu certo, grava no arquivo e devolve o feedback com a nova lista
    if acao_sucesso:
        salvar_datas_arquivo(datas_atuais)
        datas_atualizadas = ler_datas_arquivo()
        texto_lista_nova = "\n".join([f"🔸 {d}" for d in datas_atualizadas]) if datas_atualizadas else "Lista vazia."

        mensagem_final = (
            f"{feedback_msg}\n\n"
            "📅 **SUA LISTA ATUALIZADA:**\n"
            f"{texto_lista_nova}\n\n"
            "Para iniciar a busca com essas novas datas, digite `/buscar`."
        )
        bot.reply_to(mensagem, mensagem_final, parse_mode="Markdown")
    else:
        bot.reply_to(mensagem, feedback_msg)

# --- GATILHO: /analise ---
@bot.message_handler(commands=['analise'])
def comando_analise(mensagem):
    bot.reply_to(mensagem, "📊 **Modo Cientista de Dados Ativado!**\n\nEstou a vasculhar o histórico completo do Excel e a cruzar com o seu saldo do Clube 10k e C6 Carbon. A sua análise estatística chega em poucos segundos... 🧠")
    
    print("\n[🤖 COMANDO RECEBIDO] Iniciando Análise de Tendências...")
    
    try:
        subprocess.run([sys.executable, caminho_analise], check=True)
        print("✅ Análise concluída.")
    except Exception as e:
        erro_msg = f"❌ Ocorreu um erro ao processar a análise: {e}"
        print(erro_msg)
        bot.reply_to(mensagem, erro_msg)

# --- GATILHO: /start ou /ajuda ---
@bot.message_handler(commands=['start', 'ajuda', 'help'])
def menu_ajuda(mensagem):
    texto_ajuda = (
        "🤖 **Bem-vindo ao seu Agente Autônomo de Emissões Azul!** ✈️\n\n"
        "Eu sou o seu assistente de Inteligência Artificial focado em encontrar as melhores oportunidades em milhas para a sua viagem a Portugal e Itália.\n\n"
        "Aqui estão os comandos disponíveis:\n\n"
        "🔍 **/buscar** - Aciona a esteira RPA. O robô varre o site da Azul buscando os preços das suas datas e a IA gera um Flash Report imediato com o menor valor.\n\n"
        "📅 **/datas** - Abre o painel interativo para você gerenciar, incluir, excluir ou alterar os dias que estou monitorando.\n\n"
        "📊 **/analise** - Ativa o modo Cientista de Dados (RAG). Eu leio todo o seu histórico no Excel, cruzo com o seu saldo (Azul + C6 Carbon) e te dou um parecer tático se é hora de emitir ou esperar.\n\n"
        "💡 *Dica de uso:* Verifique suas datas com `/datas` e depois rode uma `/analise` para ver a tendência do mercado hoje!"
    )
    
    bot.reply_to(mensagem, texto_ajuda, parse_mode="Markdown")


# ==========================================
# LOOP INFINITO (BLINDADO CONTRA QUEDAS DE REDE)
# ==========================================
print("📡 Iniciando o monitoramento contínuo. Conectado aos servidores do Telegram...")

try:
    # O loop infinito roda aqui dentro
    while True:
        try:
            bot.polling(non_stop=True, timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"⚠️ [QUEDA GRAVE] O loop principal falhou: {e}")
            print("🔄 Reiniciando o motor de escuta em 5 segundos...")
            time.sleep(5)

# O "Kill Switch" fica de fora, vigiando tudo
except KeyboardInterrupt:
    print("\n🛑 [SISTEMA] Orquestrador desligado manualmente pelo usuário (CTRL+C).")
    bot.stop_polling() # Força a biblioteca a soltar a conexão
    sys.exit(0)        # Mata o processo do Python imediatamente
