# ✈️ Agente Autônomo de Emissões (RPA + LLM)

Este projeto evoluiu de um simples bot de extração de dados (RPA) para uma **Arquitetura Event-Driven de Agente Autônomo**. Ele combina automação web clássica com a capacidade analítica da Inteligência Artificial (Google Gemini) e comandos via ChatOps (Telegram), permitindo total controle dinâmico pelo celular.

## 🧠 Arquitetura do Sistema

O sistema separa claramente o "Músculo" (extração de dados brutos), o "Cérebro" (tomada de decisão) e a "Interface" (gestão do usuário via Telegram).

```mermaid
flowchart LR
    A[📱 Usuário no<br>Telegram]

    subgraph Backend [Back-end da Aplicação Local]
        direction TB
        
        subgraph L1 [Linha 1: Automação e Extração]
            direction LR
            B(🎧 Orquestrador:<br>bot_listener.py) -.->|Lê/Grava| F[📝 datas_viagem.txt]
            B -->|Aciona| C{🤖 RPA Extrator:<br>azul_bot.py}
            F -.->|Alimenta| C
        end
        
        subgraph L2 [Linha 2: Dados e IA]
            direction LR
            D[(📊 Planilha<br>Excel)] -->|Lê Última Linha| E{🧠 Agente Flash:<br>agente_leitor_excel.py}
            D -->|Lê Histórico 30d| G{🧠 Agente Analista:<br>agente_analise.py}
            H{🧮 Agente Simulador:<br>agente_simulador.py}
        end
        
        %% A MÁGICA ACONTECE AQUI: Elo invisível para forçar a L2 abaixo da L1
        L1 ~~~ L2
        
        C -->|Grava Dados| D
        B -->|Aciona| E
        B -->|Aciona| G
        B -->|Aciona| H
    end

    A <-->|Comandos ChatOps| B
    E -.->|Envia Flash Report| A
    G -.->|Envia Tendência| A
    H -.->|Envia Plano Financeiro| A
```

## 🌟 Novas Funcionalidades (v2.0)
* **Módulo Cientista de Dados (RAG Avançado):** O comando `/analise` recupera o histórico de raspagem (últimos 30 registros do Excel), injeta no LLM via *Retrieval-Augmented Generation* (RAG) e gera um relatório estatístico de tendência de preços e viabilidade de emissão.
* **Consultor Financeiro (Simulador):** O novo comando `/simular` utiliza LLM para cruzar dados paramétricos (Saldo, Meta e geração do Clube Azul) e projetar matematicamente planos de ação sobre a transferência de pontos de cartões de crédito (C6 Carbon).
* **Resiliência de Rede e Multi-threading:** O orquestrador (`bot_listener.py`) foi construído com *Exception Handlers* customizados para ignorar quedas de API do Telegram (ex: `ReadTimeout`, `ConnectionResetError`) e delega as chamadas de automação para *threads* independentes, evitando o congelamento da interface.
* **Arquitetura Multi-Chat (Sala de Guerra):** O bot é agnóstico a chat, operando perfeitamente em grupos fechados (casal/equipe), com menus responsivos embutidos na interface do Telegram.
* **Gestão Dinâmica de Estado (CRUD):** Através do comando `/datas` no Telegram, é possível listar, incluir, excluir ou substituir as datas de busca em tempo real, sem precisar tocar no código.
* **Segurança Aprimorada (.env):** Todos os tokens, chaves de API e variáveis de regras de negócio (Passageiros, Metas e Saldos) foram isolados usando a biblioteca `python-dotenv`.
* **IA Otimizada (Flash Report):** O prompt do LLM foi refinado para gerar um relatório executivo de leitura rápida (5 segundos), direto ao ponto (Melhor Preço, Custo Total, Balanço e Veredito).

## 🛠️ Tecnologias Utilizadas
* **RPA (Automação Web):** Python + Playwright
* **Manipulação de Dados:** Pandas + Openpyxl
* **Inteligência Artificial (LLM):** Google GenAI (Gemini 2.5 Flash)
* **Orquestração e Notificação:** pyTelegramBotAPI (Long Polling)
* **Segurança:** python-dotenv

## ⚙️ Como Funciona
1. **O Listener (Recepção 24/7):** O `bot_listener.py` fica hospedado ouvindo comandos no Telegram. O menu de onboarding pode ser acessado a qualquer momento enviando `/ajuda`.
2. **Gestão de Parâmetros:** O usuário envia o comando `/datas` via chat, e o bot abre um painel interativo para atualizar o arquivo `datas_viagem.txt` dinamicamente.
3. **Extração sob demanda:** Ao receber `/buscar`, o robô Playwright navega na Azul, burla proteções antibot básicas, raspa os preços das datas alvo e salva na base de dados. A IA então emite um alerta instantâneo com o menor preço do dia.
4. **Análise de Tendência (RAG):** Com o comando `/analise`, o Agente de IA (`agente_analise.py`) lê o histórico de buscas em massa, identifica padrões de queda ou alta e avalia a janela de oportunidade de compra.
5. **Simulação e Consultoria Financeira:** Ao receber `/simular`, a IA cruza o saldo atual, a meta de pontos e a geração mensal (Clube Azul), emitindo um plano de ação matemático detalhando o déficit exato e recomendando a transferência ou espera orgânica.
6. **Relatório Executivo NLG:** A IA atua como cientista de dados e envia um parecer tático diretamente formatado e limpo para o Telegram.

## 🚀 Como Executar Localmente
1. Clone o repositório.
2. Instale as dependências: `pip install playwright pandas openpyxl google-genai pyTelegramBotAPI python-dotenv requests`
3. Instale os navegadores do Playwright: `playwright install chromium`
4. Crie um arquivo chamado `.env` na raiz do projeto e preencha suas chaves e métricas:
   ```env
   # Credenciais
   TOKEN_TELEGRAM=seu_token_aqui
   CHAT_ID_ARLINDO=seu_chat_id_aqui_ou_id_do_grupo
   CHAVE_API_GOOGLE=sua_chave_gemini_aqui
   
   # Caminhos Locais
   CAMINHO_PLANILHA=sua_pasta_planilha
   CAMINHO_PERFIL_CHROME=seu_perfil_Chrome
   
   # Regras de Negócio e Finanças
   SALDO_AZUL=seu_saldo_azul_atual
   QTD_PASSAGEIROS=quantidade_passageiros
   META_PONTOS=meta_pontos_passagem
   ```

---
👤 **Autor:** Arlindo Júnior Honorato  
Technical Product Manager | Automação | IA aplicada a Produtos Financeiros e Eficiência de Backoffice
