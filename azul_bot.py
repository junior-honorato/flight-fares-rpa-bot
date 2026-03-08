import os
import time
import logging
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Alignment

# ==========================================
# CONFIGURAÇÃO DO TELEGRAM E META
# ==========================================
TOKEN_TELEGRAM = "SEU_TOKEN_AQUI" # <-- NÃO ESQUEÇA DE COLOCAR O SEU TOKEN REAL AQUI!
CHAT_ID_ARLINDO = "SEU_CHAT_ID_AQUI"
META_PONTOS = 120000

def enviar_telegram(mensagem):
    try:
        url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
        params = {
            "chat_id": CHAT_ID_ARLINDO,
            "text": mensagem,
            "parse_mode": "Markdown"
        }
        response = requests.get(url, params=params)

        if response.status_code == 200:
            logging.info("[TELEGRAM] Alerta enviado com sucesso!")
        else:
            logging.error(f"[TELEGRAM] Erro na API: {response.text}")
    except Exception as e:
        logging.error(f"[TELEGRAM] Erro de conexão: {e}")

def salvar_historico_excel(origem, destino, data_voo_formatada, menor_preco):
    arquivo_excel = r"C:\Caminho\Para\Sua\Pasta\historico_precos_azul.xlsx"
    
    # O SEGREDO: Pegamos o objeto de data e hora REAL (sem converter para texto)
    agora = datetime.now() 
    
    try:
        if not os.path.exists(arquivo_excel):
            wb = Workbook()
            ws = wb.active
            ws.title = "Historico_Precos"
            ws.append(["Data/Hora da Busca", "Origem", "Destino", "Data do Voo", "Preço (Pontos)"])
        else:
            wb = load_workbook(arquivo_excel)
            ws = wb["Historico_Precos"]
        
        # Varre para achar a primeira linha vazia exata
        primeira_linha_vazia = 2
        for row in range(2, ws.max_row + 100): 
            valor_celula = ws.cell(row=row, column=1).value
            if valor_celula is None or str(valor_celula).strip() == "":
                primeira_linha_vazia = row
                break
        
        # Insere a DATA COMO OBJETO e aplica a máscara brasileira
        celula_data = ws.cell(row=primeira_linha_vazia, column=1, value=agora)
        celula_data.number_format = 'dd/mm/yyyy hh:mm:ss'
        
        # Insere o resto dos dados
        ws.cell(row=primeira_linha_vazia, column=2, value=origem)
        ws.cell(row=primeira_linha_vazia, column=3, value=destino)
        ws.cell(row=primeira_linha_vazia, column=4, value=data_voo_formatada)
        ws.cell(row=primeira_linha_vazia, column=5, value=menor_preco)
        
        wb.save(arquivo_excel)
        logging.info(f"[PLANILHA] Histórico salvo na linha {primeira_linha_vazia}: {data_voo_formatada} - {menor_preco} pontos.")
        
    except PermissionError:
        logging.error("🚨 [ERRO] O arquivo Excel está ABERTO no seu computador! Feche o arquivo.")
    except Exception as e:
        logging.error(f"🚨 [ERRO] Falha ao salvar no Excel: {e}")

# ==========================================
# CONFIGURAÇÃO DO LOG
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("log_azul_bot.txt", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def buscar_passagem_azul(page, origem, destino, data_ida):
    """ Utiliza a aba única para buscar a passagem """
    try:
        # Voltar para a Home reseta o site para a próxima pesquisa
        page.goto("https://www.voeazul.com.br")

        try:
            page.locator("#onetrust-accept-btn-handler").click(timeout=3000)
        except: pass

        time.sleep(3) 
        page.keyboard.press("Escape")
        time.sleep(0.5)
        page.keyboard.press("Escape")
        time.sleep(1)

        # Origem
        campo_origem = page.locator("input[aria-label='Origem'][role='combobox']").first
        campo_origem.evaluate("node => node.focus()")
        campo_origem.evaluate("node => node.click()")
        time.sleep(0.5)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        campo_origem.press_sequentially(origem, delay=200) 
        time.sleep(2) 
        page.keyboard.press("ArrowDown")
        time.sleep(0.5)
        page.keyboard.press("Enter")

        # Destino
        campo_destino = page.locator("input[aria-label='Destino'][role='combobox']").first
        campo_destino.evaluate("node => node.focus()")
        campo_destino.evaluate("node => node.click()")
        time.sleep(0.5)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        campo_destino.press_sequentially(destino, delay=200)
        time.sleep(2)
        for _ in range(3):
            page.keyboard.press("ArrowDown")
            time.sleep(0.3) 
        time.sleep(0.5)
        page.keyboard.press("Enter")

        # Data
        campo_data = page.locator("input[aria-label='Data de ida']").first
        campo_data.evaluate("node => node.focus()")
        campo_data.evaluate("node => node.click()")
        time.sleep(0.5)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        campo_data.press_sequentially(data_ida, delay=150)
        time.sleep(1)
        page.keyboard.press("Enter")
        page.keyboard.press("Escape")
        time.sleep(1)

        # Usar Pontos
        try:
            page.locator("input[data-cy='checkbox-points']").evaluate("node => node.click()")
        except:
            try: page.locator("text='Usar pontos Azul'").evaluate("node => node.click()")
            except: pass
        time.sleep(1)

        # Buscar
        try:
            page.locator("button:has-text('Buscar passagens')").evaluate("node => node.click()")
        except:
            page.keyboard.press("Enter") 

        # Extração
        logging.info("Aguardando o carregamento dos voos...")
        seletor_preco = "[data-test-id*='fare-price-with-points']"
        
        page.wait_for_selector(seletor_preco, timeout=30000)
        time.sleep(2) 
        
        elementos_preco = page.locator(seletor_preco).all()
        lista_de_precos = []
        
        for elemento in elementos_preco:
            texto_limpo = elemento.inner_text().replace("pontos", "").replace(".", "").strip()
            try:
                lista_de_precos.append(int(texto_limpo))
            except ValueError:
                continue 
        
        # Processamento
        if len(lista_de_precos) > 0:
            menor_preco = min(lista_de_precos)
            data_formatada = f"{data_ida[:2]}/{data_ida[2:4]}/{data_ida[4:]}"
            preco_formatado = f"{menor_preco:,}".replace(",", ".")
            meta_formatada = f"{META_PONTOS:,}".replace(",", ".")
            
            logging.info(f" -> O MENOR PREÇO DO DIA {data_formatada} É: {preco_formatado} PONTOS! <- ")

            salvar_historico_excel(origem, destino, data_formatada, menor_preco)

            if menor_preco <= META_PONTOS:
                mensagem_alerta = (
                    f"🚨 *OPORTUNIDADE AZUL ENCONTRADA* 🚨\n\n"
                    f"📍 *Origem:* {origem}\n"
                    f"🏁 *Destino:* {destino}\n"
                    f"📅 *Data:* {data_formatada}\n"
                    f"💰 *Melhor Preço:* {preco_formatado} pontos\n\n"
                    f"⚠️ O valor está abaixo da meta de {meta_formatada} pontos!"
                )
                enviar_telegram(mensagem_alerta)
            return True 
        else:
            raise ValueError("Nenhum valor extraído da tela.")

    except Exception as erro:
        logging.error(f"Erro durante a extração: {erro}")
        raise 

if __name__ == "__main__":
    SIGLA_ORIGEM = "VCP"
    SIGLA_DESTINO = "LIS"
    DATAS_VIAGEM = ["04092026", "05092026", "06092026"] 
    MAX_TENTATIVAS = 3 
    
    # ==========================================
    # SESSÃO ÚNICA: Abre o navegador apenas uma vez
    # ==========================================
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=r"C:\Caminho\Para\Chrome_Profile",
            channel="chrome",                
            headless=False, 
            no_viewport=True, 
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"]
        )
        page = browser.new_page()

        for data in DATAS_VIAGEM:
            logging.info(f"\n==========================================")
            logging.info(f" INICIANDO FLUXO PARA A DATA: {data}")
            logging.info(f"==========================================")
            
            sucesso_na_data = False
            
            for tentativa in range(1, MAX_TENTATIVAS + 1):
                logging.info(f"Tentativa {tentativa} de {MAX_TENTATIVAS}...")
                try:
                    buscar_passagem_azul(page, SIGLA_ORIGEM, SIGLA_DESTINO, data)
                    sucesso_na_data = True
                    # Sai do loop de tentativas e avança para o próximo dia na MESMA tela
                    break 
                except Exception as e:
                    logging.warning(f"Falha na tentativa {tentativa} para a data {data}.")
                    if tentativa < MAX_TENTATIVAS:
                        logging.info("Aguardando 5 segundos antes de tentar novamente...")
                        time.sleep(5)
            
            if not sucesso_na_data:
                msg_erro = f"⚠️ *Alerta do Robô*\nNão consegui extrair os preços para o dia {data[:2]}/{data[2:4]} após {MAX_TENTATIVAS} tentativas."
                enviar_telegram(msg_erro)
                logging.error(f"Desistindo da data {data} após {MAX_TENTATIVAS} tentativas.")

        logging.info("\n==========================================")
        logging.info("Fechando o navegador...")
        browser.close()

    # ------------------------------------------
    # Finalização
    # ------------------------------------------
    logging.info("TODAS AS DATAS PROCESSADAS.")
    logging.info("Aguardando 60 segundos para sincronização da planilha na nuvem...")
    time.sleep(60) 
    
    logging.info("Suspendendo o PC agora.")
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
