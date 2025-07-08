# analise_curricular/management/commands/import_candidatos.py

import csv
import os
from django.core.management.base import BaseCommand, CommandError
from analise_curricular.models import Candidato

class Command(BaseCommand):
    help = 'Importa dados de candidatos de um arquivo CSV.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='O caminho para o arquivo CSV de candidatos.')

    def handle(self, *args, **options):
        file_path = options['csv_file']

        if not os.path.exists(file_path):
            raise CommandError(f'O arquivo CSV não foi encontrado no caminho: {file_path}')

        self.stdout.write(self.style.SUCCESS(f'Iniciando a importação de dados do arquivo: {file_path}'))

        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader, None)  # Lê a primeira linha como cabeçalho

                if header is None:
                    raise CommandError("O arquivo CSV está vazio ou não possui cabeçalho.")

                # Mapeia os índices das colunas para os nomes dos campos do modelo
                try:
                    nome_idx = header.index('Nome do Candidato')
                    inscricao_idx = header.index('Numero de Inscricao')
                    cargo_idx = header.index('Cargo/Funcao')
                except ValueError as e:
                    raise CommandError(f"Cabeçalho CSV inválido. Certifique-se de ter as colunas 'Nome do Candidato', 'Numero de Inscricao', 'Cargo/Funcao'. Erro: {e}")


                imported_count = 0
                for row in reader:
                    if len(row) < 3: # Garante que a linha tem pelo menos 3 colunas esperadas
                        self.stdout.write(self.style.WARNING(f'Pulando linha inválida (menos de 3 colunas): {row}'))
                        continue

                    nome = row[nome_idx]
                    inscricao = row[inscricao_idx]
                    cargo = row[cargo_idx]

                    try:
                        # Verifica se o candidato já existe para evitar duplicatas (usando inscricao como unique)
                        candidato, created = Candidato.objects.update_or_create(
                            inscricao=inscricao,
                            defaults={
                                'nome': nome,
                                'cargo': cargo
                            }
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Candidato "{nome}" ({inscricao}) importado com sucesso.'))
                            imported_count += 1
                        else:
                            self.stdout.write(self.style.WARNING(f'Candidato "{nome}" ({inscricao}) já existe. Informações atualizadas.'))

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Erro ao importar candidato "{nome}" ({inscricao}): {e}'))

            self.stdout.write(self.style.SUCCESS(f'Importação concluída. Total de {imported_count} novos candidatos importados/atualizados.'))

        except FileNotFoundError:
            raise CommandError(f'O arquivo CSV não foi encontrado no caminho: {file_path}')
        except Exception as e:
            raise CommandError(f'Ocorreu um erro durante a importação: {e}')