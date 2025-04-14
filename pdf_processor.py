import os
from PyPDF2 import PdfReader
import pandas as pd
import re
from pathlib import Path
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SEOAnalyzer:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        
    def extract_metrics_from_pdf(self, pdf_path):
        """Extrai métricas principais do PDF de análise"""
        try:
            logger.info(f"Processando arquivo: {pdf_path}")
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
                
            # Extrair métricas básicas
            metrics = {
                'site': pdf_path.stem,
                'performance_score': self._extract_metric(text, r"Performance[:\s]+(\d+)", "performance_score"),
                'seo_score': self._extract_metric(text, r"SEO[:\s]+(\d+)", "seo_score"),
                'loading_time': self._extract_metric(text, r"Loading[:\s]Time[:\s]+([\d.]+)", "loading_time"),
                'mobile_score': self._extract_metric(text, r"Mobile[:\s]+(\d+)", "mobile_score"),
                'organic_traffic': self._extract_metric(text, r"Organic[:\s]+Traffic[:\s]+(\d+)", "organic_traffic")
            }
            
            # Extrair palavras-chave
            keywords = self._extract_keywords(text)
            if keywords:
                metrics['keywords'] = keywords
                
            # Log das métricas encontradas
            logger.info(f"Métricas extraídas para {pdf_path.name}: {metrics}")
            
            return metrics
        except Exception as e:
            logger.error(f"Erro ao processar {pdf_path}: {str(e)}")
            return None
    
    def _extract_metric(self, text, pattern, metric_name, default_value=None):
        """Extrai uma métrica específica do texto usando regex"""
        try:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1)
                if '.' in value:
                    return float(value)
                return int(value)
            logger.warning(f"Métrica {metric_name} não encontrada")
            return default_value
        except Exception as e:
            logger.error(f"Erro ao extrair {metric_name}: {str(e)}")
            return default_value
    
    def _extract_keywords(self, text):
        """Extrai as palavras-chave principais"""
        try:
            # Tentar diferentes padrões de palavras-chave
            patterns = [
                r"Keywords?[:\s]+(.*?)(?=\n\n)",
                r"Palavras?[- ]chave?[:\s]+(.*?)(?=\n\n)",
                r"Top[:\s]+Terms?[:\s]+(.*?)(?=\n\n)"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    keywords_text = match.group(1)
                    # Limpar e filtrar palavras-chave
                    keywords = [
                        kw.strip() for kw in re.split(r'[,\n]', keywords_text)
                        if kw.strip() and len(kw.strip()) > 2
                    ]
                    return keywords[:10]  # Retornar apenas as top 10 palavras-chave
            
            logger.warning("Nenhuma palavra-chave encontrada")
            return []
        except Exception as e:
            logger.error(f"Erro ao extrair palavras-chave: {str(e)}")
            return []
    
    def analyze_group(self, group_name):
        """Analisa todos os PDFs de um grupo específico"""
        group_path = self.base_path / group_name
        results = []
        
        if not group_path.exists():
            logger.error(f"Diretório não encontrado: {group_path}")
            return pd.DataFrame()
        
        # Processar todos os PDFs no diretório e subdiretórios
        for pdf_file in group_path.rglob("*.pdf"):
            metrics = self.extract_metrics_from_pdf(pdf_file)
            if metrics:
                metrics['group'] = group_name
                results.append(metrics)
        
        if not results:
            logger.warning(f"Nenhum resultado encontrado para o grupo {group_name}")
            return pd.DataFrame()
        
        df = pd.DataFrame(results)
        logger.info(f"Análise concluída para {group_name}. Shape: {df.shape}")
        return df
    
    def compare_groups(self, group_names):
        """Compara métricas entre diferentes grupos"""
        all_results = []
        
        for group in group_names:
            logger.info(f"Analisando grupo: {group}")
            group_results = self.analyze_group(group)
            if not group_results.empty:
                all_results.append(group_results)
        
        if not all_results:
            logger.warning("Nenhum resultado encontrado para comparação")
            return pd.DataFrame()
        
        df = pd.concat(all_results, ignore_index=True)
        logger.info(f"Comparação concluída. Shape final: {df.shape}")
        return df

def get_available_groups(base_path):
    """Retorna lista de grupos disponíveis para análise"""
    try:
        base_path = Path(base_path)
        if not base_path.exists():
            logger.error(f"Diretório base não encontrado: {base_path}")
            return []
        
        groups = [d.name for d in base_path.iterdir() if d.is_dir()]
        logger.info(f"Grupos encontrados: {groups}")
        return groups
    except Exception as e:
        logger.error(f"Erro ao listar grupos: {str(e)}")
        return [] 