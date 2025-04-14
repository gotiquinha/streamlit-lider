import os
import json
import glob

# Diretório onde estão os arquivos TXT
diretorio = r"C:\Users\isabela\OneDrive\Desktop\analise-performance - Copia\wtotal"

# Lista todos os arquivos TXT no diretório
arquivos_txt = glob.glob(os.path.join(diretorio, "*.txt"))

# Processa cada arquivo TXT
for arquivo_txt in arquivos_txt:
    # Lê o conteúdo do arquivo TXT
    with open(arquivo_txt, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Cria o nome do arquivo JSON
    arquivo_json = arquivo_txt.replace('.txt', '.json')
    
    # Cria a estrutura JSON
    dados_json = {
        "conteudo": conteudo
    }
    
    # Salva o arquivo JSON
    with open(arquivo_json, 'w', encoding='utf-8') as f:
        json.dump(dados_json, f, ensure_ascii=False, indent=4)
    
    print(f"Arquivo convertido: {arquivo_json}")

print("Conversão concluída!") 