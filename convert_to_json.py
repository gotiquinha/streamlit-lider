import os
import json
from pathlib import Path
import sys

def convert_txt_to_json(txt_path):
    """
    Converte um arquivo TXT para JSON extraindo as métricas principais
    """
    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            text = file.read()
        
        # Extrair grupo e marca do caminho do arquivo
        path_parts = str(Path(txt_path)).split(os.sep)
        grupo = path_parts[1] if len(path_parts) > 1 else ""
        marca = path_parts[2] if len(path_parts) > 2 else ""
        
        data = {
            'grupo': grupo.replace('grupo-', ''),
            'marca': marca,
            'dominio': Path(txt_path).stem,
            'metricas': {
                'performance': None,
                'palavras_top3': None,
                'taxa_cliques': None,
                'volume_pesquisas': None
            }
        }
        
        # Extrair os dados do texto
        for line in text.split('\n'):
            if 'Performance:' in line:
                try:
                    data['metricas']['performance'] = float(line.split(':')[1].strip().replace('%', ''))
                except:
                    pass
            elif 'TOP 3:' in line or 'palavras-chave no TOP 3' in line:
                try:
                    data['metricas']['palavras_top3'] = int(''.join(filter(str.isdigit, line)))
                except:
                    pass
            elif 'taxa de cliques' in line.lower():
                try:
                    data['metricas']['taxa_cliques'] = float(line.split('%')[0].split()[-1])
                except:
                    pass
            elif 'pesquisas por mês' in line.lower():
                try:
                    data['metricas']['volume_pesquisas'] = int(''.join(filter(str.isdigit, line)))
                except:
                    pass
        
        # Criar arquivo JSON
        json_path = str(Path(txt_path)).replace('.txt', '.json')
        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
        
        sys.stdout.write(f"\rConvertido: {Path(txt_path).name} -> {Path(json_path).name}")
        sys.stdout.flush()
        return True
        
    except Exception as e:
        print(f"\nErro ao processar {txt_path}: {str(e)}")
        return False

def convert_all_files():
    """
    Converte todos os arquivos TXT para JSON
    """
    base_dir = "analise-performance"
    converted = 0
    errors = 0
    total_files = 0
    
    # Conta total de arquivos
    for root, dirs, files in os.walk(base_dir):
        total_files += len([f for f in files if f.endswith('.txt')])
    
    print(f"Encontrados {total_files} arquivos TXT para converter\n")
    
    # Percorre toda a estrutura de diretórios
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.txt'):
                txt_path = os.path.join(root, file)
                if convert_txt_to_json(txt_path):
                    converted += 1
                else:
                    errors += 1
                sys.stdout.write(f" ({converted}/{total_files})\n")
                sys.stdout.flush()
    
    print(f"\n\nConversão concluída:")
    print(f"- {converted} arquivos convertidos com sucesso")
    print(f"- {errors} erros encontrados")
    print(f"- Total processado: {converted + errors} de {total_files}")

if __name__ == "__main__":
    convert_all_files() 