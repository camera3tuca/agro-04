# 🌾 Agro Tracker - Sistema de Acompanhamento de Ativos do Agronegócio

Sistema em tempo real para monitoramento de ativos do agronegócio brasileiro listados na B3, desenvolvido com Python e Streamlit.

## 📋 Sobre o Projeto

O **Agro Tracker** é uma aplicação web que permite acompanhar em tempo real os principais ativos do agronegócio brasileiro, incluindo:

- **Ações** de empresas do setor agroindustrial
- **BDRs** de empresas internacionais do agro
- **FIAGROs** (Fundos de Investimento nas Cadeias Produtivas Agroindustriais)

### Ativos Monitorados

#### 📈 Ações (17 empresas)
- Brasil Agro (AGRO3)
- Agrogalaxy (AGXY3)
- Minerva Foods (BEEF3)
- BRF Foods (BRFS3)
- Camil (CAML3)
- PomiFrutas (FRTA3)
- Jalles Machado (JALL3)
- JBS (JBSS3)
- Josapar (JOPA3)
- Kepler Weber (KEPL3)
- Marfrig (MRFG3)
- M. Dias Branco (MDIA3)
- Raízen (RAIZ4)
- SLC Agrícola (SLCE3)
- São Martinho (SMTO3)
- Boa Safra (SOJA3)
- Três Tentos (TTEN3)

#### 🌎 BDRs (3 empresas internacionais)
- Archer Daniels Midland (A1DM34)
- Corteva Agriscience (C1TV34)
- Mosaic Company (MOSC34)

#### 🏦 FIAGROs (8 fundos)
- Exes Araguaia (AGRX11)
- BB Crédito (BBGO11)
- Santa Fé Terra Mater (FARM11)
- Galápagos Recebíveis (GCRA11)
- Kinea Crédito Agro (KNCA11)
- Itaú Asset Rural (RURA11)
- Suno Agro (SNAG11)
- XP Crédito Agrícola (XPCA11)

## 🚀 Funcionalidades

### 📊 Dashboard Principal
- **Cards interativos** com preço e variação via Brapi
- **Notícias em tempo real** do setor
- **Atualização automática** (60 segundos)
- **Exportação** para CSV/Excel

### 📈 Análise Técnica Avançada
- **Indicadores:** RSI, MACD, Estocástico, ADX, ATR
- **Médias Móveis:** SMA 20/50/200, EMA 12/26
- **Bandas de Bollinger**
- **Score técnico** (0-100) com recomendação
- **Análise de tendência** (Alta/Baixa/Neutro)
- **Suporte e resistência**

### 📰 Integração de Notícias
- **NewsAPI:** Últimas notícias em português
- **Finnhub:** Sentimento de mercado internacional
- **Filtros:** Agronegócio, commodities, empresas específicas

### 📉 Visualizações
- **Gráficos Candlestick** com indicadores
- **MACD e RSI** em painéis separados
- **Comparativo** de desempenho normalizado
- **Tabela consolidada** com todos os dados

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+**
- **Streamlit** - Framework web para aplicações de dados
- **yFinance** - API para dados financeiros
- **Pandas** - Manipulação de dados
- **Plotly** - Visualizações interativas

## 📦 Instalação e Execução

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passo a Passo

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/agro-tracker.git
cd agro-tracker
```

2. **Crie um ambiente virtual (recomendado)**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Execute a aplicação**
```bash
streamlit run app.py
```

5. **Acesse no navegador**
```
http://localhost:8501
```

## 📱 Como Usar

1. **Selecione a categoria** de ativos (Ações, BDRs ou FIAGROs)
2. **Escolha os ativos** que deseja monitorar
3. **Defina o período** de análise (1 dia até 1 ano)
4. **Ative a atualização automática** se desejar monitoramento contínuo
5. **Navegue pelas abas** para diferentes visualizações
6. **Exporte os dados** em CSV quando necessário

## 🎨 Interface

A interface é dividida em três abas principais:

### 📊 Gráficos de Preço
Visualização detalhada de cada ativo com:
- Gráfico de candlestick
- Métricas de preço, variação, máximas e mínimas

### 📉 Comparativo
Gráfico comparativo normalizado (base 100) permitindo analisar o desempenho relativo dos ativos selecionados.

### 📋 Tabela Resumo
Tabela completa com todos os ativos e suas métricas, com:
- Cores indicativas (verde para alta, vermelho para queda)
- Opção de download em CSV

## 📊 Fontes dos Dados

### APIs Integradas

**1. Brapi (Brazilian API)**
- Cotações em tempo real da B3
- Dados fundamentalistas
- Token: Configurável no código
- Limite: 1000 requisições/dia (plano gratuito)

**2. Yahoo Finance (yFinance)**
- Dados históricos e em tempo real
- Indicadores técnicos
- Fallback quando Brapi não disponível
- Sem limite (uso razoável)

**3. NewsAPI**
- Notícias sobre agronegócio em português
- Até 100 requisições/dia (plano gratuito)
- Fontes: G1, Valor, InfoMoney, etc.

**4. Finnhub**
- Sentimento de mercado
- Notícias internacionais
- 60 requisições/minuto (plano gratuito)

**Intervalo de atualização:** 
- Cotações: 5 minutos (cache)
- Notícias: 10 minutos (cache)
- Gráficos: Sob demanda

## ⚠️ Avisos Importantes

- Este sistema é apenas para fins **educacionais e informativos**
- **Não constitui recomendação de investimento**
- Os dados são fornecidos "como estão" e podem conter atrasos
- Sempre consulte um profissional qualificado antes de investir

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## 📝 Melhorias Futuras

- [ ] Alertas de preço personalizados
- [ ] Análise técnica com indicadores (RSI, MACD, etc.)
- [ ] Notificações via email/Telegram
- [ ] Integração com outras fontes de dados
- [ ] Machine Learning para previsões
- [ ] Modo dark/light
- [ ] Histórico de carteira pessoal

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

Desenvolvido com base nas informações do artigo da Toro Investimentos sobre [como investir no agronegócio](https://blog.toroinvestimentos.com.br/investimentos/como-investir-no-agronegocio/).

## 📞 Contato e Suporte

- Abra uma [Issue](https://github.com/seu-usuario/agro-tracker/issues) para reportar bugs
- Pull Requests são bem-vindos!

---

⭐ Se este projeto foi útil para você, considere dar uma estrela no repositório!

**Desenvolvido com 💚 para o setor do Agronegócio Brasileiro**
