import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from pdf_processor import SEOAnalyzer, get_available_groups
import traceback

# Configuração da página
st.set_page_config(
    page_title="Análise SEO - Grupo Lider vs Concorrência",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("📊 Dashboard de Análise Competitiva - Grupo Lider")

try:
    # Inicialização do analisador
    analyzer = SEOAnalyzer("analise-performance")
    
    # Sidebar para filtros
    st.sidebar.title("Filtros")
    
    # Obtém grupos disponíveis
    available_groups = get_available_groups("analise-performance")
    
    if not available_groups:
        st.error("Nenhum grupo encontrado na pasta analise-performance. Verifique se os arquivos estão no local correto.")
        st.stop()
    
    grupo_select = st.sidebar.multiselect(
        "Selecione os Grupos",
        available_groups,
        default=["grupo-lider"] if "grupo-lider" in available_groups else None
    )
    
    if not grupo_select:
        st.warning("Por favor, selecione pelo menos um grupo para análise.")
        st.stop()
    
    # Mostrar progresso do processamento
    with st.spinner("Processando dados dos PDFs..."):
        df_comparison = analyzer.compare_groups(grupo_select)
    
    if df_comparison.empty:
        st.error("Não foi possível extrair dados dos PDFs selecionados. Verifique se os arquivos estão corretos.")
        st.stop()
    
    # Layout principal com tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Visão Geral", 
        "🔍 Análise SEO", 
        "⚡ Performance", 
        "🎯 Palavras-chave"
    ])

    with tab1:
        st.header("Visão Geral do Mercado")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Market Share Digital")
            try:
                if 'organic_traffic' in df_comparison.columns:
                    fig = px.pie(
                        df_comparison,
                        names='group',
                        values='organic_traffic',
                        title='Distribuição de Tráfego Orgânico'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Dados de tráfego orgânico não disponíveis")
            except Exception as e:
                st.error(f"Erro ao gerar gráfico de Market Share: {str(e)}")
        
        with col2:
            st.subheader("Performance Média por Grupo")
            try:
                metrics = ['performance_score', 'seo_score', 'mobile_score']
                available_metrics = [m for m in metrics if m in df_comparison.columns]
                
                if available_metrics:
                    fig = px.bar(
                        df_comparison.groupby('group')[available_metrics].mean().reset_index(),
                        x='group',
                        y=available_metrics,
                        title='Scores Médios por Grupo',
                        barmode='group'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Dados de performance não disponíveis")
            except Exception as e:
                st.error(f"Erro ao gerar gráfico de Performance: {str(e)}")

    with tab2:
        st.header("Análise SEO")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Rankings Orgânicos")
            try:
                if all(col in df_comparison.columns for col in ['seo_score', 'organic_traffic']):
                    fig = px.scatter(
                        df_comparison,
                        x='seo_score',
                        y='organic_traffic',
                        color='group',
                        size='performance_score',
                        hover_data=['site'],
                        title='SEO Score vs Tráfego Orgânico'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Dados de SEO não disponíveis")
            except Exception as e:
                st.error(f"Erro ao gerar gráfico de Rankings: {str(e)}")
        
        with col2:
            st.subheader("Distribuição de SEO Scores")
            try:
                if 'seo_score' in df_comparison.columns:
                    fig = px.box(
                        df_comparison,
                        x='group',
                        y='seo_score',
                        title='Distribuição de SEO Scores por Grupo'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Dados de SEO score não disponíveis")
            except Exception as e:
                st.error(f"Erro ao gerar gráfico de Distribuição: {str(e)}")

    with tab3:
        st.header("Performance e Experiência do Usuário")
        
        try:
            group_means = df_comparison.groupby('group').mean()
            
            for group in grupo_select:
                if group in group_means.index:
                    st.subheader(f"Métricas: {group}")
                    cols = st.columns(3)
                    
                    metrics_map = {
                        'loading_time': ('Tempo de Carregamento Médio', 's'),
                        'performance_score': ('Performance Score', '/100'),
                        'mobile_score': ('Mobile Score', '/100')
                    }
                    
                    for i, (metric, (label, unit)) in enumerate(metrics_map.items()):
                        if metric in group_means.columns:
                            with cols[i]:
                                value = group_means.loc[group, metric]
                                if metric == 'loading_time':
                                    formatted_value = f"{value:.2f}{unit}"
                                else:
                                    formatted_value = f"{value:.0f}{unit}"
                                st.metric(label=label, value=formatted_value)
                        else:
                            with cols[i]:
                                st.info(f"{label} não disponível")
        except Exception as e:
            st.error(f"Erro ao exibir métricas de performance: {str(e)}")

    with tab4:
        st.header("Análise de Palavras-chave")
        
        try:
            if 'keywords' in df_comparison.columns:
                # Agregando keywords de todos os sites
                all_keywords = []
                for keywords in df_comparison['keywords']:
                    if isinstance(keywords, list):
                        all_keywords.extend(keywords)
                
                if all_keywords:
                    keyword_counts = pd.Series(all_keywords).value_counts()
                    
                    st.subheader("Top 10 Palavras-chave mais Frequentes")
                    fig = px.bar(
                        x=keyword_counts.head(10).index,
                        y=keyword_counts.head(10).values,
                        title="Palavras-chave mais Frequentes"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Nenhuma palavra-chave encontrada nos dados")
            else:
                st.info("Dados de palavras-chave não disponíveis")
        except Exception as e:
            st.error(f"Erro ao gerar análise de palavras-chave: {str(e)}")

except Exception as e:
    st.error(f"Erro inesperado: {str(e)}")
    st.error(f"Detalhes do erro: {traceback.format_exc()}")

# Footer com informações adicionais
st.markdown("---")
st.markdown("### 📝 Notas e Observações")
st.markdown("""
- Os dados são extraídos diretamente dos relatórios de performance
- As métricas são atualizadas conforme novos relatórios são adicionados
- A análise compara apenas os grupos selecionados
""") 