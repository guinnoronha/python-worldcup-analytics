# 🌎 FIFA World Cup Analytics

Análise histórica completa das Copas do Mundo FIFA utilizando Engenharia de Dados, Análise Exploratória e Visualização de Dados com Python.

---

## ⚽ Sobre o Projeto

Este projeto foi desenvolvido com o objetivo de transformar dados históricos da Copa do Mundo em insights analíticos e visualizações modernas.

Através de técnicas de:
- Data Analytics
- Data Visualization
- Data Engineering
- Exploratory Data Analysis (EDA)

o projeto entrega uma experiência visual e analítica inspirada em dashboards profissionais.

---

## 🚀 Objetivos

- Consolidar dados históricos das Copas do Mundo
- Criar análises exploratórias relevantes
- Construir visualizações impactantes
- Desenvolver um dashboard em HTML com tema dark
- Demonstrar habilidades de manipulação de dados com Pandas

---

# 🏆 Principais Insights

O projeto analisa:

- Países com mais títulos mundiais
- Evolução da média de gols ao longo das Copas
- Estádios que mais receberam partidas
- Evolução do público total
- Seleções com maior poder ofensivo
- Quantidade de partidas por edição
- Crescimento do torneio ao longo da história

---

# 🛠️ Tecnologias Utilizadas

## Linguagem
- Python

## Bibliotecas
- Pandas

## Visualização
- HTML5
- CSS3

## IA
- Claude Code

---

# 📁 Estrutura do Projeto

```bash
worldcup_analytics/
│
├── data/
│   └── full/
│       └── WorldCupFull.csv
│   └── raw/
│       └── WorldCupFullDescription.csv
│       └── WorldCupMatches.csv
│       └── WorldCups.csv
│
├── notebooks/
│   └── 01_exploracao.ipynb
│
├── dash/
│   └── world_cup_dashboard.html
│   └── build_dashboard.py
│
├── README.md
│
└── requirements.txt
```

---

# 📊 Dashboard

O dashboard apresenta:
- KPIs automáticos
- Gráficos históricos
- Visual moderno em tema escuro
- Layout responsivo
- Indicadores analíticos

---

# ✨ Funcionalidades

## 🔎 Filtros Multi-Seleção
- Selecione **múltiplas** edições (ano), fases, seleções e países sede simultaneamente
- Chips removíveis exibem as seleções ativas abaixo da barra de filtros
- Botão **Resetar** limpa todos os filtros de uma vez
- Todos os KPIs, gráficos e tabelas atualizam instantaneamente sem reload

## 📊 KPIs (8 cards — 4 por linha)
| Card | Descrição |
|------|-----------|
| ⚽ Total de Partidas | Contagem de jogos no recorte |
| 🎯 Total de Gols | Soma de gols marcados |
| 📈 Gols por Partida | Média de gols por jogo |
| 🏆 Seleções | Quantidade distinta de seleções |
| 👥 Público Total | Total de espectadores (formato K/M) |
| 🔄 Partidas c/ Pênaltis | Jogos decididos nos pênaltis |
| 🕐 Só Prorrogação | Jogos com prorrogação sem pênaltis |
| 🌍 Edições no recorte | Número de Copas filtradas |

## 📉 Gráficos (Plotly.js)
- **Evolução histórica** — gols totais por Copa + linha de média por partida (eixo duplo)
- **Rankings Top 5** — Mais vitórias, Mais gols marcados, Mais gols sofridos, Mais derrotas (barras horizontais)
- **Histograma** — distribuição de gols por partida
- **Pênaltis por ano** — disputas de pênaltis em cada edição
- **Desfecho empilhado** — Tempo Normal × Prorrogação × Pênaltis por Copa

## 📋 Tabelas Interativas
- **Por Seleção** — 83 seleções com jogos, vitórias, empates, derrotas, gols pró/contra, saldo, médias | ordenável por qualquer coluna | pesquisa em tempo real
- **Por Edição** — 20 Copas com país sede, campeão, vice, 3º lugar, gols, partidas, público total/médio

## 💡 Insights Automáticos
Gerados em runtime com base no recorte atual:
- Copa com mais gols
- Maior média de gols por partida
- Seleção com mais vitórias no recorte
- Total e % de disputas de pênaltis
- Partida com mais gols
- Maior goleada

---

# 🔥 Destaques Técnicos

- Merge de datasets históricos
- Tratamento de dados inconsistentes
- Conversão e padronização de colunas
- Construção de métricas analíticas
- Geração automatizada de gráficos
- Exportação de dashboard HTML

---

# 🚀 Como usar

## Opção 1 — Abrindo direto no navegador
Baixe `world_cup_dashboard.html` e abra no navegador. Nenhuma instalação necessária.

## Opção 2 — Regenerando o HTML a partir do CSV

**Pré-requisitos:** Python 3.8+

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/world-cup-dashboard.git
cd world-cup-dashboard

# 2. Coloque o WorldCupFull.csv na pasta Downloads (ou ajuste o caminho no script)

# 3. Gere os dados processados
python build_dashboard.py
```

O script irá:
1. Ler e limpar o `WorldCupFull.csv`
2. Calcular todas as agregações (por partida, por seleção, por edição)
3. Embutir os dados como JSON no HTML
4. Salvar `world_cup_dashboard.html` (~200 KB, autocontido)

---

# 📌 Próximas Evoluções

- Dashboard interativo com Plotly
- Deploy em Streamlit
- Machine Learning para previsão de resultados
- Comparação entre eras da Copa
- API de dados esportivos
- Atualização automática dos datasets

---

# 🌍 Fonte dos Dados

## 📦 Dataset

**Fonte:** [FIFA World Cup — Kaggle](https://www.kaggle.com/datasets/abecklas/fifa-world-cup)

**Arquivo:** `WorldCupFull.csv`

### Esquema principal

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `Year` | float64 | Ano da edição |
| `Stage` | string | Fase do torneio |
| `Home Team Name` | string | Time mandante |
| `Away Team Name` | string | Time visitante |
| `Home Team Goals` | float64 | Gols do mandante |
| `Away Team Goals` | float64 | Gols do visitante |
| `Win conditions` | string | Condição de vitória (prorrogação, pênaltis etc.) |
| `Attendance_matches` | float64 | Público da partida |
| `Country` | string | País sede da edição |
| `Winner` | string | Campeão da edição |
| `GoalsScored` | float64 | Total de gols da edição |
| `Attendance_cup` | string | Público total da edição |

---

# ⭐ Resultado Final

Este projeto demonstra competências importantes para:
- Engenharia de Dados
- Business Intelligence
- Data Analytics
- Visualização de Dados
- Storytelling com Dados

---

# 🏆 FIFA World Cup Analytics

> “Football is played with the head. Your feet are just the tools.”
> — Andrea Pirlo

---

# 👨‍💻 Criado por

**Desenvolvido por:** Guilherme Noronha Mello<br>
**Linkedin:** linkedin.com/guilherme-noronha-mello<br>
**Github:** github.com/guinnoronha

Projeto criado para estudos, portfólio e evolução profissional na área de Dados.
