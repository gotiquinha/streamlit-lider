import os
import pandas as pd
from pathlib import Path

def extract_data_from_txt(txt_path):
    """
    Extrai dados de performance do arquivo TXT
    """
    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            text = file.read()
            
        # Extrair grupo e marca do caminho do arquivo
        path_parts = txt_path.split(os.sep)
        grupo = path_parts[1] if len(path_parts) > 1 else ""
        marca = path_parts[2] if len(path_parts) > 2 else ""
        
        data = {
            'grupo': grupo.replace('grupo-', ''),
            'marca': marca,
            'dominio': os.path.basename(txt_path).replace('.txt', ''),
            'performance': None,
            'palavras_top3': None,
            'taxa_cliques': None,
            'volume_pesquisas': None
        }
        
        # Extrair os dados do texto
        for line in text.split('\n'):
            if 'Performance:' in line:
                try:
                    data['performance'] = float(line.split(':')[1].strip().replace('%', ''))
                except:
                    pass
            elif 'TOP 3:' in line or 'palavras-chave no TOP 3' in line:
                try:
                    data['palavras_top3'] = int(''.join(filter(str.isdigit, line)))
                except:
                    pass
            elif 'taxa de cliques' in line.lower():
                try:
                    data['taxa_cliques'] = float(line.split('%')[0].split()[-1])
                except:
                    pass
            elif 'pesquisas por mês' in line.lower():
                try:
                    data['volume_pesquisas'] = int(''.join(filter(str.isdigit, line)))
                except:
                    pass
        
        print(f"Processando {data['dominio']}: Performance={data['performance']}, Top3={data['palavras_top3']}")
        return data
    except Exception as e:
        print(f"Erro ao processar {txt_path}: {str(e)}")
        return None

def process_all_files():
    """
    Processa todos os arquivos TXT na estrutura de diretórios
    """
    base_dir = "analise-performance"
    all_data = []
    
    # Percorre toda a estrutura de diretórios
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.txt'):
                txt_path = os.path.join(root, file)
                data = extract_data_from_txt(txt_path)
                if data:
                    all_data.append(data)
    
    # Criar DataFrame com todos os dados
    df = pd.DataFrame(all_data)
    
    # Remover linhas com dados incompletos
    df = df.dropna()
    
    # Agrupar por marca para análise
    df_marca = df.groupby('marca')[['performance', 'palavras_top3', 'taxa_cliques', 'volume_pesquisas']].mean()
    
    return df, df_marca

if __name__ == "__main__":
    # Processar arquivos e salvar resultados
    df, df_marca = process_all_files()
    
    # Salvar dados detalhados
    df.to_csv("analise_detalhada.csv", index=False)
    
    # Salvar dados agrupados por marca
    df_marca.to_csv("analise_por_marca.csv")
    
    print("\nDados extraídos e salvos em:")
    print("- analise_detalhada.csv (dados por domínio)")
    print("- analise_por_marca.csv (médias por marca)") 