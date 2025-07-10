# gerar_csv_candidatos.py

import csv

dados_candidatos = [
    # Cabeçalhos
    ["Nome do Candidato", "Numero de Inscricao", "Cargo/Funcao", "requisito", "avaliacao", "justificativa", "observacao"],
    # Dados dos candidatos
    ["João Silva", "1001", "Desenvolvedor", "", "", "", ""],
    ["Maria Oliveira", "1002", "Analista de Dados", "", "", "", ""],
    ["Pedro Souza", "1003", "Gerente de Projetos", "", "", "", ""],
    ["Ana Costa", "1004", "Recursos Humanos", "", "", "", ""],
    ["Carlos Santos", "1005", "Designer UX/UI", "", "", "", ""],
]

nome_arquivo_saida = "candidatos_para_importar.csv" # Nome do novo arquivo CSV

try:
    with open(nome_arquivo_saida, 'w', newline='', encoding='utf-8') as arquivo_csv:
        escritor_csv = csv.writer(arquivo_csv)
        escritor_csv.writerows(dados_candidatos)
    print(f"Arquivo '{nome_arquivo_saida}' gerado com sucesso!")
    print("Verifique este arquivo na raiz do seu projeto.")
except Exception as e:
    print(f"Erro ao gerar o arquivo CSV: {e}")