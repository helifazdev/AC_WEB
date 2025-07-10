from django.db import models
from datetime import date # Importar para data_analise default

class Candidato(models.Model):
    
    selecao = models.ForeignKey(
        'Selecao', # Use 'Selecao' como string se Selecao for definido depois de Candidato
        on_delete=models.SET_NULL,
        null=True,     # Permite valores nulos no banco de dados
        blank=True,    # Permite campos vazios no formulário
        related_name='candidatos_da_selecao',
        verbose_name="Seleção"
    )
    # Dados Pessoais do Candidato
    nome = models.CharField(max_length=255, verbose_name="Nome do Candidato")
    inscricao = models.CharField(max_length=50, unique=True, verbose_name="Número de Inscrição")
    cargo = models.CharField(max_length=100, verbose_name="Cargo/Função")

    # Dados da Análise Curricular
    # Opções para o campo 'requisito'
    REQUISITO_OPCOES = [
        ('Sim', 'Sim'),
        ('Nao', 'Não'),
    ]
    requisito = models.CharField(
        max_length=3,
        choices=REQUISITO_OPCOES,
        blank=True,
        null=True,
        verbose_name="Possui Requisitos para o Cargo"
    )

    # Opções para o campo 'avaliacao'
    AVALIACAO_OPCOES = [
        ('Especializacao', 'Especialização'),
        ('Mestrado', 'Mestrado'),
        ('Doutorado', 'Doutorado'),
        ('Nao possui', 'Não possui'),
    ]
    avaliacao = models.CharField(
        max_length=15,
        choices=AVALIACAO_OPCOES,
        blank=True,
        null=True,
        verbose_name="Avaliação Curricular"
    )

    justificativa = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Justificativa (se 'Não possui')"
    )
    observacao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações Adicionais"
    )
    pontuacao = models.IntegerField(
        default=0,
        verbose_name="Pontuação"
    )

    # Campos de controle/metadados (opcional, mas boa prática)
    data_analise = models.DateField(
        auto_now_add=True, # Define a data automaticamente na criação
        verbose_name="Data da Análise"
    )
    analisado = models.BooleanField(
        default=False, # Indica se o candidato já foi analisado
        verbose_name="Analisado"
    )

    class Meta:
        verbose_name = "Candidato"
        verbose_name_plural = "Candidatos"
        ordering = ['nome', 'cargo'] # Ordena os candidatos por nome e cargo, como você fazia

    def __str__(self):
        return f"{self.nome} - {self.cargo} ({self.inscricao})"

    def calcular_pontuacao(self):
        pontuacoes_map = {
            "Especializacao": 40,
            "Mestrado": 60,
            "Doutorado": 100, # Adaptei para 100, você tinha 10 no seu código, que pareceu baixo para doutorado
            "Nao possui": 0
        }
        self.pontuacao = pontuacoes_map.get(self.avaliacao, 0)
        return self.pontuacao

    def save(self, *args, **kwargs):
        # Atualiza a pontuação antes de salvar o objeto
        self.calcular_pontuacao()
        super().save(*args, **kwargs)
        
# MODELO: Selecao
class Selecao(models.Model):
    nome = models.CharField(max_length=200, unique=True, verbose_name="Nome da Seleção")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    ativa = models.BooleanField(default=True, verbose_name="Ativa para Avaliação")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Seleção"
        verbose_name_plural = "Seleções"

