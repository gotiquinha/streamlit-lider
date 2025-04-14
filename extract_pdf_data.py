import os
import re
import PyPDF2
import pandas as pd
from pathlib import Path

def extract_semrush_data(pdf_path):
    """
    Extrai dados de performance do PDF do SEMrush
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            # Padrões para encontrar as métricas
            performance_pattern = r"Performance Score:\s*(\d+)"
            top3_pattern = r"Top 3 Positions:\s*(\d+)"
            ctr_pattern = r"CTR:\s*([\d.]+)%"
            volume_pattern = r"Total Search Volume:\s*([\d,]+)"
            
            # Extrair dados usando regex
            performance = re.search(performance_pattern, text)
            top3 = re.search(top3_pattern, text)
            ctr = re.search(ctr_pattern, text)
            volume = re.search(volume_pattern, text)
            
            # Extrair grupo e marca do caminho do arquivo
            path_parts = pdf_path.split(os.sep)
            grupo = path_parts[1] if len(path_parts) > 1 else ""
            marca = path_parts[2] if len(path_parts) > 2 else ""
            
            data = {
                'grupo': grupo.replace('grupo-', ''),
                'marca': marca,
                'dominio': os.path.basename(pdf_path).split('-')[0],
                'performance': int(performance.group(1)) if performance else None,
                'palavras_top3': int(top3.group(1)) if top3 else None,
                'taxa_cliques': float(ctr.group(1)) if ctr else None,
                'volume_pesquisas': int(volume.group(1).replace(',', '')) if volume else None
            }
            
            print(f"Processando {data['dominio']}: Performance={data['performance']}, Top3={data['palavras_top3']}")
            return data
    except Exception as e:
        print(f"Erro ao processar {pdf_path}: {str(e)}")
        return None

def process_all_pdfs():
    """
    Processa todos os PDFs na estrutura de diretórios
    """
    base_dir = "analise-performance"
    all_data = []
    
    # Percorre toda a estrutura de diretórios
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                data = extract_semrush_data(pdf_path)
                if data:
                    all_data.append(data)
    
    # Criar DataFrame com todos os dados
    df = pd.DataFrame(all_data)
    
    # Agrupar por marca para análise
    df_marca = df.groupby('marca')[['performance', 'palavras_top3', 'taxa_cliques', 'volume_pesquisas']].mean()
    
    return df, df_marca

if __name__ == "__main__":
    # Instalar dependências necessárias
    os.system("pip install PyPDF2 pandas")
    
    # Processar PDFs e salvar resultados
    df, df_marca = process_all_pdfs()
    
    # Salvar dados detalhados
    df.to_csv("semrush_data_detalhado.csv", index=False)
    
    # Salvar dados agrupados por marca
    df_marca.to_csv("semrush_data_por_marca.csv")
    
    print("\nDados extraídos e salvos em:")
    print("- semrush_data_detalhado.csv (dados por domínio)")
    print("- semrush_data_por_marca.csv (médias por marca)") 