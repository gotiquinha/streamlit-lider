import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path
import os
import re

# Configuração da página
st.set_page_config(page_title="SEO Grupo Lider", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# Função auxiliar para criar tooltip
def metric_with_tooltip(label, value, delta, tooltip):
    return st.markdown(f"""
    <div title="{tooltip}" style="padding: 10px; border: 1px solid #f0f2f6; border-radius: 5px;">
        <small style="color: #808495">{label}</small>
        <h3 style="margin: 0; font-size: 1.5rem;">{value}</h3>
        <small style="color: #808495">{delta}</small>
    </div>
    """, unsafe_allow_html=True)

def extract_seo_metrics(json_path):
    """
    Extrai métricas de SEO do arquivo JSON
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            conteudo = data.get('conteudo', '')
            
            # Extrair grupo e marca do caminho do arquivo
            path_parts = str(Path(json_path)).split(os.sep)
            grupo = path_parts[-3] if len(path_parts) > 2 else ""
            marca = path_parts[-2] if len(path_parts) > 1 else ""
            
            # Função auxiliar para extrair números de strings
            def extract_number(text):
                numbers = re.findall(r'[\d,.]+', text)
                if numbers:
                    return float(numbers[0].replace('.', '').replace(',', '.'))
                return 0
            
            # Extrair métricas do conteúdo
            metrics = {
                'grupo': grupo.replace('grupo-', ''),
                'marca': marca,
                'dominio': '',
                'trafego_organico': 0,
                'trafego_pago': 0,
                'palavras_chave_organicas': 0,
                'palavras_chave_pagas': 0,
                'backlinks': 0,
                'dominos_referencia': 0,
                'posicao_media': 0,
                'ctr': 0,
                'intencao_palavras_chave': {},
                'distribuicao_paises': {},
                'top_palavras': []
            }
            
            # Extrair domínio
            domain_match = re.search(r'domínio: ([\w\.]+)', conteudo)
            if domain_match:
                metrics['dominio'] = domain_match.group(1)
            
            # Extrair métricas básicas
            for line in conteudo.split('\n'):
                if 'Tráfego estimado:' in line and 'Resumo da Busca Orgânica' in conteudo.split(line)[0][-50:]:
                    metrics['trafego_organico'] = extract_number(line)
                elif 'Palavras-chave orgânicas:' in line:
                    metrics['palavras_chave_organicas'] = extract_number(line)
                elif 'Total:' in line and 'Backlinks' in conteudo.split(line)[0][-20:]:
                    metrics['backlinks'] = extract_number(line)
                elif 'Domínios de referência:' in line:
                    metrics['dominos_referencia'] = extract_number(line)
                elif 'Posição no ranking' in line:
                    metrics['posicao_media'] = extract_number(line)
            
            # Extrair distribuição de países
            paises_section = re.search(r'Distribuição das Palavras-chave por País \(Busca Orgânica\):(.*?)(?=\n\n)', conteudo, re.DOTALL)
            if paises_section:
                for line in paises_section.group(1).split('\n'):
                    if ':' in line:
                        pais, percentual = line.split(':')
                        pais = pais.replace('-', '').strip()
                        metrics['distribuicao_paises'][pais] = extract_number(percentual)
            
            # Extrair intenção das palavras-chave
            intencao_section = re.search(r'Intenção das Palavras-chave:(.*?)(?=\n\n)', conteudo, re.DOTALL)
            if intencao_section:
                for line in intencao_section.group(1).split('\n'):
                    if ':' in line and 'palavras' in line.lower():
                        tipo, resto = line.split(':', 1)
                        tipo = tipo.replace('-', '').strip()
                        palavras = extract_number(resto.split('palavras')[0])
                        trafego = extract_number(resto.split('tráfego')[1]) if 'tráfego' in resto else 0
                        percentual = extract_number(resto.split('(')[-1]) if '(' in resto else 0
                        
                        metrics['intencao_palavras_chave'][tipo] = {
                            'palavras': int(palavras),
                            'trafego': int(trafego),
                            'percentual': percentual
                        }
            
            # Extrair palavras-chave mais buscadas
            palavras_section = re.search(r'Principais Palavras-chave Orgânicas:(.*?)(?=\n\nDistribuição das Posições)', conteudo, re.DOTALL)
            metrics['top_palavras'] = []
            
            if palavras_section:
                for line in palavras_section.group(1).split('\n'):
                    if '\"' in line and '–' in line:
                        partes = line.split('–')
                        if len(partes) >= 3:
                            palavra = partes[0].replace('\"', '').strip()
                            volume = extract_number(partes[2])
                            trafego = extract_number(partes[3]) if len(partes) > 3 else 0
                            if palavra and volume > 0:
                                metrics['top_palavras'].append({
                                    'palavra': palavra,
                                    'volume': int(volume),
                                    'trafego': trafego
                                })
            
            return metrics
    except Exception as e:
        print(f"Erro ao processar {json_path}: {str(e)}")
        return None

def load_seo_data():
    """
    Carrega todos os dados de SEO dos arquivos JSON
    """
    base_dir = "analise-performance"
    all_data = []
    
    # Percorre todos os arquivos JSON
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.json') and 'analise_detalhada' in file:
                json_path = os.path.join(root, file)
                metrics = extract_seo_metrics(json_path)
                if metrics:
                    all_data.append(metrics)
    
    return pd.DataFrame(all_data)

# Título compacto
st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>SEO Grupo Lider</h2>", unsafe_allow_html=True)

# Introdução
st.markdown("""
### Introdução
Este relatório apresenta uma análise comparativa de performance SEO entre o Grupo Lider e seus principais concorrentes no mercado automotivo. As análises são baseadas em dados reais coletados através do [SEMrush](https://pt.semrush.com/seo/).
""")

# Adicionar informação sobre a fonte dos dados
st.markdown("""
<div style='text-align: center; font-size: 0.8em; color: #666; margin-bottom: 20px;'>
    Dados coletados pelo SEMrush nos últimos 12 meses
</div>
""", unsafe_allow_html=True)

# Carregar dados de SEO
df_seo = load_seo_data()

if not df_seo.empty:
    # Função para formatar números no padrão brasileiro
    def format_br(value):
        if isinstance(value, float):
            return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        elif isinstance(value, int):
            return f"{value:,}".replace(",", ".")
        return value

    # Adicionar coluna para identificar se é do Grupo Líder
    df_seo['is_lider'] = df_seo['grupo'].str.lower().str.contains('lider')
    df_seo['marca_display'] = df_seo.apply(lambda x: f"{x['marca']} (Grupo Líder)" if x['is_lider'] else x['marca'], axis=1)

    # Configurar o estilo da tabela para ocultar a primeira coluna e usar formatação brasileira
    def style_dataframe(df):
        return df.style.format({
            'Volume de Buscas': format_br,
            '% Tráfego': lambda x: f"{x:.2f}%".replace(".", ","),
            'Marca': lambda x: x
        }).hide(axis='index')

    # Tabs principais
    tab1, tab2 = st.tabs(["📊 Visão Geral", "📈 Análise Competitiva"])

    with tab1:
        st.markdown("""
        ### 📌 Métricas do Grupo Líder
        Principais indicadores consolidados das marcas do Grupo Líder.
        """)
        
        # Calcular métricas reais do Grupo Líder
        df_lider = df_seo[df_seo['is_lider']]
        trafego_lider = df_lider['trafego_organico'].sum()
        palavras_lider = df_lider['palavras_chave_organicas'].sum()
        dominios_lider = df_lider['dominos_referencia'].sum()
        
        # Calcular share de tráfego
        trafego_total = df_seo['trafego_organico'].sum()
        share_lider = (trafego_lider / trafego_total * 100) if trafego_total > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            metric_with_tooltip(
                "Tráfego Orgânico Total",
                f"{trafego_lider:,.0f}",
                "Visitas/mês",
                "Total de visitas mensais das marcas do Grupo Líder"
            )
        
        with col2:
            metric_with_tooltip(
                "Palavras-chave Comerciais",
                f"{palavras_lider:,.0f}",
                "Total de palavras-chave",
                "Soma de palavras-chave das marcas do Grupo Líder"
            )
        
        with col3:
            metric_with_tooltip(
                "Autoridade do Domínio",
                f"{dominios_lider:,.0f}",
                "Domínios únicos",
                "Total de domínios que linkam para as marcas do Grupo Líder"
            )
            
        with col4:
            metric_with_tooltip(
                "Share de Tráfego",
                f"{share_lider:.1f}%",
                "Grupo Líder vs Concorrentes",
                "Porcentagem do tráfego total que pertence ao Grupo Líder"
            )

        # Adicionar seção de palavras-chave mais buscadas após as métricas do Grupo Líder
        st.markdown("""
        ### 🔍 Palavras-chave Mais Buscadas
        Análise das principais palavras-chave que direcionam tráfego para os sites.
        """)
        
        # Criar DataFrame com as palavras-chave mais relevantes
        keywords_data = {
            'Palavra-chave': [],
            'Volume de Buscas': [],
            '% Tráfego': [],
            'Marca': []
        }
        
        for idx, row in df_lider.iterrows():
            for kw in row.get('top_palavras', []):
                keywords_data['Palavra-chave'].append(kw['palavra'])
                keywords_data['Volume de Buscas'].append(kw['volume'])
                keywords_data['% Tráfego'].append(kw['trafego'])
                keywords_data['Marca'].append(row['marca'])
        
        df_keywords = pd.DataFrame(keywords_data)
        df_keywords = df_keywords.sort_values('Volume de Buscas', ascending=False)
        
        st.markdown("### Grupo Líder - Top Palavras-chave")
        st.markdown("Palavras-chave mais relevantes que direcionam tráfego para nossos sites, ordenadas por volume de busca.")
        
        # Aplicar o estilo e exibir a tabela com scroll
        st.dataframe(
            style_dataframe(df_keywords),
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Seção de Top Concorrentes
        st.markdown("""
        ### 📊 Top 5 Concorrentes por Tráfego
        Análise do tráfego mensal dos principais concorrentes baseada em dados reais.
        """)

        # Filtrar apenas concorrentes (excluindo o próprio grupo)
        df_concorrentes = df_seo[~df_seo['is_lider']]

        if not df_concorrentes.empty:
            # Ordenar por tráfego total e pegar os top 5
            df_top5 = df_concorrentes.nlargest(5, 'trafego_organico')
            
            # Criar tabela com métricas reais
            metricas_reais = pd.DataFrame({
                'Concorrente': df_top5['marca'],
                'Domínio': df_top5['dominio'],
                'Tráfego Orgânico': df_top5['trafego_organico'].round(0),
                'Palavras-chave': df_top5['palavras_chave_organicas'].round(0),
                'Backlinks': df_top5['backlinks'].round(0),
                'Domínios Referência': df_top5['dominos_referencia'].round(0)
            })
            
            st.dataframe(
                metricas_reais,
                column_config={
                    "Concorrente": "Concorrente",
                    "Domínio": "Domínio",
                    "Tráfego Orgânico": st.column_config.NumberColumn(
                        "Tráfego Orgânico",
                        help="Visitas mensais vindas de busca orgânica",
                        format="%d"
                    ),
                    "Palavras-chave": st.column_config.NumberColumn(
                        "Palavras-chave",
                        help="Total de palavras-chave ranqueadas",
                        format="%d"
                    ),
                    "Backlinks": st.column_config.NumberColumn(
                        "Backlinks",
                        help="Total de backlinks",
                        format="%d"
                    ),
                    "Domínios Referência": st.column_config.NumberColumn(
                        "Domínios Referência",
                        help="Número de sites únicos que fazem link",
                        format="%d"
                    )
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Gráfico de barras com dados reais
            st.markdown("### 📈 Tráfego dos Top 5 Concorrentes")
            
            fig_trafego = px.bar(
                df_top5,
                x='marca',
                y=['trafego_organico'],
                title="Tráfego Orgânico Mensal",
                labels={
                    'trafego_organico': 'Visitas Mensais',
                    'marca': 'Concorrente'
                }
            )
            st.plotly_chart(fig_trafego, use_container_width=True)
        
        else:
            st.info("Não foram encontrados dados de concorrentes nos arquivos JSON.")
        
        # Pontos de Decisão Estratégicos
        st.markdown("""
        ### 🎯 Pontos de Decisão Estratégicos

        #### Otimização para Buscadores
        - **Otimização de Conteúdo**: 
          - Desenvolver conteúdo mais relevante e otimizado para palavras-chave comerciais
          - Aumentar a produção de conteúdo técnico e informativo
          - Melhorar a estrutura de URLs e meta tags
        
        - **Construção de Links**:
          - Desenvolver estratégia de aquisição de backlinks de qualidade
          - Parcerias com sites relevantes do setor
          - Criação de conteúdo linkável (infográficos, guias, etc.)
        
        - **Performance Técnica**:
          - Otimizar velocidade de carregamento das páginas
          - Melhorar experiência móvel (Sinais Vitais da Web)
          - Implementar marcação estruturada para resultados enriquecidos
        
        #### Dispositivos Móveis
        - **Otimização para Móveis**:
          - Revisar e melhorar a experiência em dispositivos móveis
          - Implementar design responsivo em todas as páginas
          - Otimizar imagens e recursos para carregamento mais rápido
  
        
        #### Experiência do Usuário
        - **Navegação**:
          - Simplificar a estrutura de navegação
          - Melhorar a usabilidade em dispositivos móveis
          - Implementar navegação estruturada e menus intuitivos
        
        - **Conteúdo**:
          - Criar jornada do usuário mais clara
          - Melhorar elementos de chamada para ação
        """)
        
        # Gráfico 1: Share of Voice e Tráfego
        st.markdown("""
        ### 📊 Participação de Mercado e Tráfego
        Este gráfico mostra a distribuição de tráfego orgânico e palavras-chave entre as marcas.
        - **Barras azuis**: Tráfego orgânico mensal
        - **Barras laranja**: Número total de palavras-chave ranqueadas
        - **Marcas do Grupo Líder**: Identificadas com "(Grupo Líder)"
        """)
        
        fig_traffic = px.bar(
            df_seo.groupby('marca_display')[['trafego_organico', 'palavras_chave_organicas']].sum().reset_index(),
            x='marca_display',
            y=['trafego_organico', 'palavras_chave_organicas'],
            title="Tráfego e Palavras-chave por Marca",
            labels={
                'value': 'Volume',
                'variable': 'Métrica',
                'marca_display': 'Marca',
                'trafego_organico': 'Tráfego Orgânico',
                'palavras_chave_organicas': 'Palavras-chave'
            },
            barmode='group'
        )
        st.plotly_chart(fig_traffic, use_container_width=True)
        
    with tab2:
        st.markdown("""
        ### 📈 Análise Competitiva
        Nesta seção você encontra análises comparativas entre as marcas do Grupo Líder e seus concorrentes.
        """)
        
        # Gráfico: Posição Média vs Backlinks
        st.markdown("""
        ### 🎯 Posição Média vs Autoridade
        Este gráfico mostra a relação entre backlinks e posição média nos resultados de busca:
        - **Eixo X**: Número de backlinks (links recebidos de outros sites)
        - **Eixo Y**: Posição média nas buscas (quanto menor, melhor)
        - **Tamanho da bolha**: Volume de tráfego orgânico
        - **Cor**: Diferencia marcas do Grupo Líder dos concorrentes
        """)
        
        fig_position = px.scatter(
            df_seo,
            x="backlinks",
            y="posicao_media",
            size="trafego_organico",
            color="is_lider",
            hover_data=["marca_display", "dominio"],
            title="Relação entre Backlinks e Posição Média",
            labels={
                'backlinks': 'Número de Backlinks',
                'posicao_media': 'Posição Média',
                'trafego_organico': 'Tráfego Orgânico',
                'is_lider': 'Empresa'
            },
            color_discrete_map={
                True: '#0066CC',    # Azul do Grupo Líder
                False: '#FF8C00'    # Laranja escuro para concorrentes
            }
        )

        # Personalizar o layout do gráfico
        fig_position.update_layout(
            showlegend=True,
            legend_title="Empresa",
            plot_bgcolor='white',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99
            ),
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Arial"
            )
        )

        # Atualizar legendas para nomes mais claros
        fig_position.data[0].name = "Concorrentes"
        fig_position.data[1].name = "Grupo Líder"

        # Atualizar eixos
        fig_position.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray',
            title_font=dict(size=14),
            type='log',  # escala logarítmica para melhor visualização
            tickformat=",.0f"  # formato brasileiro para números
        )
        
        fig_position.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray',
            title_font=dict(size=14),
            tickformat=",.0f"  # formato brasileiro para números
        )

        # Atualizar marcadores
        fig_position.update_traces(
            marker=dict(
                line=dict(width=1, color='DarkSlateGrey')
            ),
            selector=dict(mode='markers'),
            hovertemplate="<b>%{customdata[0]}</b><br>" +
                         "Domínio: %{customdata[1]}<br>" +
                         "Backlinks: %{x:,.0f}<br>" +
                         "Posição Média: %{y:,.0f}<br>" +
                         "Tráfego Orgânico: %{marker.size:,.0f}<br>" +
                         "<extra></extra>"
        )

        st.plotly_chart(fig_position, use_container_width=True)
        
        # Tabela de Métricas Detalhadas
        st.markdown("""
        ### 📋 Métricas Competitivas Detalhadas
        Esta tabela apresenta todas as métricas importantes para cada marca:
        - **Tráfego Orgânico**: Visitas mensais vindas de busca orgânica
        - **Palavras-chave**: Total de palavras-chave ranqueadas
        - **Backlinks**: Número total de links recebidos
        - **Domínios Referência**: Número de sites únicos que fazem link
        - **Posição Média**: Posição média nas buscas (quanto menor, melhor)
        
        > **📌 Nota sobre Posição Média:**
        > - O Google geralmente mostra apenas os primeiros 1.000 resultados
        > - Os usuários raramente passam da primeira página (top 10 resultados)
        > - Quanto mais próximo de 1, melhor o posicionamento
        """)
        
        metricas_competitivas = df_seo.groupby('marca_display').agg({
            'trafego_organico': 'sum',
            'palavras_chave_organicas': 'sum',
            'backlinks': 'sum',
            'dominos_referencia': 'sum',
            'posicao_media': 'mean'
        }).round(2)
        
        # Renomear colunas para melhor visualização
        metricas_competitivas.columns = [
            'Tráfego Orgânico',
            'Palavras-chave',
            'Backlinks',
            'Domínios Referência',
            'Posição Média'
        ]
        
        # Aplicar formatação brasileira aos números
        st.dataframe(
            metricas_competitivas.style.format({
                'Tráfego Orgânico': lambda x: f'{x:,.0f}'.replace(',', '.'),
                'Palavras-chave': lambda x: f'{x:,.0f}'.replace(',', '.'),
                'Backlinks': lambda x: f'{x:,.0f}'.replace(',', '.'),
                'Domínios Referência': lambda x: f'{x:,.0f}'.replace(',', '.'),
                'Posição Média': lambda x: f'{x/1000:.1f}k'.replace('.', ',') if x >= 1000 else f'{x:.0f}'
            }),
            use_container_width=True
        )
else:
    st.warning("Nenhum dado de SEO encontrado. Verifique se os arquivos JSON estão no diretório correto.") 