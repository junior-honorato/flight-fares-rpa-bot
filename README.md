# ✈️ Agente Autônomo de Emissões (RPA + LLM)

Este projeto evoluiu de um simples bot de extração de dados (RPA) para uma **Arquitetura Event-Driven de Agente Autônomo**, combinando automação web clássica com a capacidade analítica da Inteligência Artificial (Google Gemini) e comandos via ChatOps (Telegram).

## 🧠 Arquitetura do Sistema

O sistema separa claramente o "Músculo" (extração de dados brutos) do "Cérebro" (tomada de decisão baseada em contexto financeiro).

```mermaid
graph TD
    A[Usuário no Telegram] -->|/buscar| B(Orquestrador: bot_listener.py)
    B -->|Aciona| C{RPA: azul_bot.py}
    C -->|Web Scraping| D[(Planilha Excel)]
    B -->|Aciona| E{Agente IA: agente_leitor.py}
    D -->|Lê Dados Reais| E
    E -->|Analisa Saldo x Custo| E
    E -->|Envia Relatório Executivo| A
