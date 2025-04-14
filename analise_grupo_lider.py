import os
import pandas as pd
import json
from pathlib import Path

def extract_metrics_from_json(json_path):
    """
    Extrai métricas do arquivo JSON
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Extrair grupo e marca do caminho do arquivo
        path_parts = str(Path(json_path)).split(os.sep)
        grupo = path_parts[1] if len(path_parts) > 1 else ""
        marca = path_parts[3] if len(path_parts) > 3 else ""
        concessionaria = path_parts[4] if len(path_parts) > 4 else ""
        
        # Extrair dados do conteúdo
        content = data.get('conteudo', '')
        lines = content.split('\n')
        
        # Inicializar variáveis
        dominio = ""
        trafego_estimado = 0
        palavras_top3 = 0
        
        # Extrair dados do texto
        for line in lines:
            # Extrair domínio
            if 'Relatório referente ao domínio:' in line:
                dominio = line.split(':')[1].strip()
            
            # Extrair dados de tráfego
            if 'Tráfego estimado:' in line:
                try:
                    trafego_estimado = int(line.split(':')[1].split('(')[0].strip().replace('.', ''))
                except:
                    pass
            
            # Extrair posições TOP 3
            if 'Posições 1-3:' in line:
                try:
                    palavras_top3 = int(line.split(':')[1].strip())
                except:
                    pass
        
        # Criar dicionário com as métricas
        metrics = {
            'grupo': grupo.replace('grupo-', ''),
            'marca': marca,
            'concessionaria': concessionaria,
            'dominio': dominio,
            'palavras_top3': palavras_top3,
            'volume_pesquisas': trafego_estimado
        }
        
        print(f"Processado: {metrics['grupo']} - {metrics['marca']} - {metrics['concessionaria']}")
        print(f"  Domínio: {metrics['dominio']}")
        print(f"  Palavras TOP 3: {metrics['palavras_top3']}")
        print(f"  Volume de Pesquisas: {metrics['volume_pesquisas']}")
        print("---")
        
        return metrics
        
    except Exception as e:
        print(f"Erro ao processar {json_path}: {str(e)}")
        return None

def analyze_grupo_lider():
    """
    Analisa dados do Grupo Líder e concorrentes usando arquivos JSON
    """
    base_dir = "analise-performance"
    all_data = []
    
    # Lista de grupos a analisar (Líder e concorrentes)
    grupos_interesse = ['grupo-lider', 'grupo-servopa', 'grupo-saga', 'grupo-barigui']
    
    # Percorre diretórios dos grupos de interesse
    for grupo in grupos_interesse:
        grupo_path = Path(base_dir) / grupo
        if not grupo_path.exists():
            continue
            
        # Procura arquivos JSON recursivamente no diretório do grupo
        for json_path in grupo_path.rglob('*.json'):
            if 'analise_detalhada_' in str(json_path):
                data = extract_metrics_from_json(str(json_path))
                if data and any(v is not None for v in [data['palavras_top3'], data['volume_pesquisas']]):
                    all_data.append(data)
    
    # Criar DataFrame
    df = pd.DataFrame(all_data)
    
    # Análises
    print("\n=== Análise do Grupo Líder e Concorrentes ===\n")
    
    # TOP 3 médio por grupo
    print("Média de Palavras no TOP 3 por Grupo:")
    print(df.groupby('grupo')['palavras_top3'].mean().sort_values(ascending=False))
    
    # Volume de pesquisas total por grupo
    print("\nVolume Total de Pesquisas por Grupo:")
    print(df.groupby('grupo')['volume_pesquisas'].sum().sort_values(ascending=False))
    
    # Análise por marca dentro do Grupo Líder
    print("\n=== Detalhamento do Grupo Líder por Marca ===\n")
    df_lider = df[df['grupo'] == 'lider']
    if not df_lider.empty:
        analise_marca = df_lider.groupby('marca').agg({
            'palavras_top3': 'mean',
            'volume_pesquisas': 'sum'
        }).sort_values('palavras_top3', ascending=False)
        
        print("TOP 10 Marcas por Palavras-chave no TOP 3:")
        print(analise_marca.head(10))
        
        print("\nTOP 10 Marcas por Volume de Pesquisas:")
        print(analise_marca.sort_values('volume_pesquisas', ascending=False).head(10))
    else:
        print("Nenhum dado encontrado para o Grupo Líder")
    
    return df

if __name__ == "__main__":
    df = analyze_grupo_lider() 