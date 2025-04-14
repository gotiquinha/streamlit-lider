# Relatório SEO - Dashboard

Dashboard interativo para análise de métricas SEO e comparação competitiva.

## Instalação Local

1. Clone o repositório:
```bash
git clone [URL_DO_SEU_REPOSITORIO]
cd relatorio-seo
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute a aplicação:
```bash
streamlit run app_v2.py
```

## Acesso Online

Você pode acessar o dashboard de duas formas:

1. **Rede Local**:
   - URL Local: http://localhost:8502
   - URL da Rede: http://192.168.0.5:8502 (para acesso na mesma rede)

2. **Acesso Público**:
   - URL: [ADICIONAR_URL_DO_STREAMLIT_CLOUD]
   - Disponível 24/7 para qualquer pessoa com o link

## Funcionalidades

- Análise de tráfego orgânico e pago
- Comparação com principais concorrentes
- Métricas de palavras-chave e backlinks
- Visualização de dados em tempo real
- Gráficos interativos

## Dados

Os dados são extraídos de análises SEO reais armazenadas em arquivos JSON na pasta `analise-performance/`.

## Estrutura do Projeto

```
relatorio-seo/
├── app_v2.py              # Aplicação principal
├── analise_grupo_lider.py # Script de análise
├── analise-performance/   # Dados de performance
│   ├── eagle/
│   ├── honda/
│   ├── hyundai/
│   ├── jeep/
│   ├── ram/
│   ├── toyota/
│   └── vitoria/
└── README.md
```

## Dados Analisados

O dashboard utiliza dados extraídos de relatórios do SEMrush, incluindo:

- Palavras-chave no TOP 3
- Volume de pesquisas
- Tráfego estimado
- Taxa de cliques
- Performance geral

## Métricas Principais

- **Performance Média**: 89.1
- **Visitas Totais**: 195,000/mês
- **Taxa de Conversão**: 3.2%
- **Mobile Score**: 97
- **SEO Score**: 95 