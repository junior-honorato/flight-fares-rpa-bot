# CLAUDE.md — flight-fares-rpa-bot

Agente de emissões Azul: RPA (Playwright) raspa preços de passagens, grava em Excel e agentes Gemini enviam análises via bot do Telegram.

## Stack

- Python 3, Playwright + playwright-stealth, pandas, openpyxl, google-genai (Gemini), pyTelegramBotAPI, python-dotenv, requests.
- `azul_bot.py` (raiz): RPA extrator; lê `datas_viagem.txt` (formato `Data alvo: DDMMAAAA`) e grava na planilha.
- `agente-emissoes-azul/bot_listener.py`: orquestrador do Telegram (/buscar, /analise, /simular, /datas, /ajuda); dispara os outros scripts via `subprocess`.
- `agente_leitor_excel.py`, `agente_analise.py`, `agente_simulador.py`: agentes LLM.

## Como rodar localmente (macOS)

```bash
python3 -m venv venv && source venv/bin/activate
pip install playwright playwright-stealth pandas openpyxl google-genai pyTelegramBotAPI python-dotenv requests
playwright install chromium
python agente-emissoes-azul/bot_listener.py   # ou: python azul_bot.py (só a extração)
```

## Variáveis de ambiente (`.env` na raiz)

`TOKEN_TELEGRAM`, `CHAT_ID_ARLINDO`, `CHAVE_API_GOOGLE`, `CAMINHO_PLANILHA`, `CAMINHO_PERFIL_CHROME`, `SALDO_AZUL`, `QTD_PASSAGEIROS`, `META_PONTOS`

## Armadilhas

- Não há `requirements.txt` nem `.env.example`; dependências estão só no README.
- `azul_bot.py` usa `launch_persistent_context(channel="chrome", headless=False)` com o perfil do Chrome em `CAMINHO_PERFIL_CHROME`: exige Google Chrome instalado e abre janela visível.
- Os agentes em `agente-emissoes-azul/` leem o `.env` da pasta pai (raiz do repo).
- `log_azul_bot.txt` é sobrescrito a cada execução (ignorado pelo git).

## Fluxo de trabalho

- Autonomia para commitar e dar push na main (projeto pessoal).
- Responder sempre em português do Brasil.
