✈️ Flight Price Tracker (Azul Airlines) & Data Pipeline

Um bot de automação RPA e pipeline de dados construído em Python. Ele monitora autonomamente os preços de passagens aéreas (em pontos) no site da Azul, registra o histórico em uma base de dados local sincronizada na nuvem e emite alertas em tempo real via Telegram quando uma meta de preço é atingida.

🎯 O Desafio e a Visão do Produto

O monitoramento manual de passagens aéreas exige tempo e é ineficiente frente às flutuações dinâmicas de preços. O objetivo deste projeto foi construir um MVP autônomo (rodando invisível via Agendador de Tarefas do Windows) para realizar a extração de dados contínua, garantindo a captura da melhor oportunidade de compra baseada em uma meta predefinida.

🛠️ Arquitetura e Tecnologias

Este projeto vai além de um simples web scraper, funcionando como uma mini-esteira de Engenharia de Dados:

- Python 3: Linguagem base do projeto.

- Playwright: Responsável pela navegação headless, bypass de interações complexas (comboboxes) e extração do DOM.

- OpenPyxl: Manipulação e injeção cirúrgica de dados no Excel, utilizando formatação ISO/Data Nativa para evitar quebra de leitura.

- Google Sheets (Dashboard): A base .xlsx local é sincronizada na nuvem, alimentando uma Tabela Dinâmica que exibe a variação temporal do menor preço agrupado por dia.

- Telegram Bot API: Sistema de push notification imediato quando a regra de negócio (Target Price) é atingida.

⚙️ Como o fluxo funciona

1. Sessão Única: O script abre uma instância persistente do Chromium, navegando por múltiplas datas de voo sem reiniciar o processo.

2. Resiliência: Implementação de retentativas automáticas (try/except) para lidar com lentidões ou indisponibilidades temporárias do site.

3. ETL Básico: Extrai a string de preço, limpa os caracteres, converte para inteiro e compara com a constante META_PONTOS.

4. Armazenamento Inteligente: O bot varre a base de dados buscando a primeira linha vazia real, inserindo carimbos de data/hora padronizados.

5. Encerramento: Após a rotina, o script comanda a suspensão (hibernação) da máquina hospedeira para economia de recursos.

## 🚀 Como Executar Localmente

1. Clone este repositório.
2. Instale as dependências (ex: `pip install playwright openpyxl requests`).
3. Instale os navegadores do Playwright executando `playwright install`.
4. No ficheiro `azul_bot.py`, insira as suas credenciais em `TOKEN_TELEGRAM` e `CHAT_ID`.
5. Ajuste os caminhos de diretório locais para o padrão da sua máquina.
6. **Para execução manual:** Corra o script Python diretamente.
7. **Para execução autónoma (Agendada):** Importe ou aponte o Agendador de Tarefas do Windows para o ficheiro `executar_robo.bat` fornecido, permitindo que o robô corra de madrugada de forma invisível.



👤 Autor Arlindo Júnior Honorato

Technical Product Manager | Automação | IA aplicada a Produtos Financeiros e Eficiência de Backoffice
