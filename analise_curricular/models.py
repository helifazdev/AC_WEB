from django.db import models
from datetime import date
from django.contrib.auth import get_user_model

User = get_user_model()

class Selecao(models.Model):
    nome = models.CharField(max_length=200, unique=True, verbose_name="Nome da Seleção")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    ativa = models.BooleanField(default=True, verbose_name="Ativa para Avaliação")
    
    # Mantive exatamente como você tinha definido
    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Seleção"
        verbose_name_plural = "Seleções"
        # Adicionei ordering para padronizar a exibição
        ordering = ['nome']

class Candidato(models.Model):
    REQUISITO_OPCOES = [
        ('Sim', 'Sim'),
        ('Nao', 'Não'),
    ]
    
    AVALIACAO_OPCOES = [
        ('Graduacao', 'Graduação'),
        ('Especializacao', 'Especialização'),
        ('Mestrado', 'Mestrado'),
        ('Doutorado', 'Doutorado'),
        ('Nao possui', 'Não possui'),
    ]

    selecao = models.ForeignKey(
        Selecao,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='candidatos_da_selecao', # Mantido o nome que você escolheu
        verbose_name="Seleção"
    )
    
    # Dados Pessoais (mantidos exatamente como você definiu)
    nome = models.CharField(max_length=255, verbose_name="Nome do Candidato")
    inscricao = models.CharField(max_length=50, unique=True, verbose_name="Número de Inscrição")
    cargo = models.CharField(max_length=100, verbose_name="Cargo/Função")

    # Campos de análise (mantida sua estrutura original)
    requisito = models.CharField(
        max_length=3,
        choices=REQUISITO_OPCOES,
        blank=True,
        null=True,
        verbose_name="Possui Requisitos para o Cargo"
    )
    
    avaliacao = models.CharField(
        max_length=15,
        choices=AVALIACAO_OPCOES,
        blank=True,
        null=True,
        verbose_name="Avaliação Curricular"
    )
    
    justificativa = models.TextField( # Mudei para TextField mas mantendo sua lógica
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
    
    # Campos de controle (mantidos como você definiu)
    data_analise = models.DateField(
        auto_now_add=True,
        verbose_name="Data da Análise"
    )
    
    analisado = models.BooleanField(
        default=False,
        verbose_name="Analisado"
    )

    class Meta:
        verbose_name = "Candidato"
        verbose_name_plural = "Candidatos"
        ordering = ['nome', 'cargo'] # Mantido seu ordering original

    def __str__(self):
        return f"{self.nome} - {self.cargo} ({self.inscricao})"

    def calcular_pontuacao(self):
        """Mantido seu método original com pequena otimização"""
        pontuacoes = {
            "Graduacao": 20,
            "Especializacao": 40,
            "Mestrado": 60,
            "Doutorado": 100,
            "Nao possui": 0
        }
        self.pontuacao = pontuacoes.get(self.avaliacao, 0)
        return self.pontuacao

    def save(self, *args, **kwargs):
        """Mantida sua lógica original de save"""
        self.calcular_pontuacao()
        super().save(*args, **kwargs)

# models.py
from django.db import models

class DocumentoCandidato(models.Model):
    TIPO_CHOICES = [
        ('RG', 'Registro Geral'),
        ('CPF', 'CPF'),
        ('Diploma', 'Diploma'),
        ('Comprovante', 'Comprovante de Experiência'),
        ('Outro', 'Outro Documento'),
    ]
    
    candidato = models.ForeignKey(
        'Candidato',
        on_delete=models.CASCADE,
        related_name='documentos'
    )
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    arquivo = models.FileField(upload_to='candidatos/documentos/%Y/%m/%d/')
    data_upload = models.DateTimeField(auto_now_add=True)
    observacoes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.candidato.nome}"

    def delete(self, *args, **kwargs):
        """Deleta o arquivo físico quando o modelo é apagado"""
        self.arquivo.delete()
        super().delete(*args, **kwargs)