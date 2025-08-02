# analise_curricular/models.py

from django.db import models
from datetime import date
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
import os
from django.db.models import JSONField 

User = get_user_model()

class Selecao(models.Model):
    nome = models.CharField(max_length=200, unique=True, verbose_name="Nome da Seleção")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    ativa = models.BooleanField(default=True, verbose_name="Ativa para Avaliação")
    
    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Seleção"
        verbose_name_plural = "Seleções"
        ordering = ['nome']

class Candidato(models.Model):
    # Removidas as opções REQUISITO_OPCOES e AVALIACAO_OPCOES,
    # pois agora serão tratadas via FormQuestion
    
    # NOVAS OPÇÕES PARA DEFICIÊNCIA
    SIM_NAO_CHOICES = [
        ('Sim', 'Sim'),
        ('Nao', 'Não'),
    ]

    selecao = models.ForeignKey(
        Selecao,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='candidatos_da_selecao',
        verbose_name="Seleção"
    )
    
    # Dados Pessoais
    nome = models.CharField(max_length=255, verbose_name="Nome do Candidato")
    inscricao = models.CharField(max_length=50, unique=True, verbose_name="Número de Inscrição")
    cargo = models.CharField(max_length=100, verbose_name="Cargo/Função")

    # REMOVIDOS os campos fixos de análise (requisito, avaliacao, justificativa, observacao)
    # Eles serão agora parte das perguntas dinâmicas salvas em respostas_dinamicas
    
    pontuacao = models.IntegerField(
        default=0,
        verbose_name="Pontuação"
    )
    
    data_importacao = models.DateField(
        auto_now_add=True,
        verbose_name="Data da Importação"
    )

    data_analisado = models.DateTimeField(
        null=True, 
        blank=True
    )

    avaliador_analise = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='avaliacoes_feitas'
    )
    
    analisado = models.BooleanField(
        default=False,
        verbose_name="Analisado"
    )

    respostas_dinamicas = JSONField(default=dict, blank=True, null=True) 

    # NOVOS CAMPOS PARA DEFICIÊNCIA
    declarou_deficiencia = models.CharField(
        max_length=3,
        choices=SIM_NAO_CHOICES,
        default='Nao', # Valor padrão, pode ser ajustado
        verbose_name="Declarou que possui deficiência?"
    )
    tipo_deficiencia = models.TextField(
        blank=True,
        null=True,
        verbose_name="Tipo de Deficiência"
    )


    def save(self, *args, **kwargs):
        # A lógica de pontuação ainda pode ser baseada em 'avaliacao' ou em um campo dinâmico
        # Para calcular pontuação de campo dinâmico 'avaliacao':
        avaliacao_question = FormQuestion.objects.filter(
            selecao=self.selecao,
            question_text__icontains="Avaliação Curricular" # Ou outro nome que você usar para a pergunta de avaliação
        ).first()

        if avaliacao_question and self.respostas_dinamicas:
            avaliacao_valor_dinamico = self.respostas_dinamicas.get(str(avaliacao_question.id))
            pontuacoes = {
                "Graduacao": 20,
                "Especializacao": 40,
                "Mestrado": 60,
                "Doutorado": 100,
                "PosDoc": 120, # Adicionado PosDoc
                "Nao possui": 0
            }
            self.pontuacao = pontuacoes.get(avaliacao_valor_dinamico, 0)
        else:
            # Manter pontuação 0 se a pergunta de avaliação não for encontrada ou não houver resposta
            self.pontuacao = 0 
        
        if self.analisado and not self.data_analisado:
            self.data_analisado = timezone.now()
            if not self.avaliador_analise and 'avaliador' in kwargs: 
                self.avaliador_analise = kwargs.pop('avaliador')
            elif not self.avaliador_analise: # Garante que sempre terá um avaliador se for analisado
                self.avaliador_analise = kwargs.get('request_user') # Passar request.user aqui ou no save

        super().save(*args, **kwargs)
   
    class Meta:
        verbose_name = "Candidato"
        verbose_name_plural = "Candidatos"
        ordering = ['nome', 'cargo']

    def __str__(self):
        return f"{self.nome} - {self.cargo} ({self.inscricao})"

    # O método calcular_pontuacao foi integrado ao save() para garantir que seja chamado
    # def calcular_pontuacao(self):
    #     ... (lógica movida para save) ...


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
        self.arquivo.delete()
        super().delete(*args, **kwargs)


class FormQuestion(models.Model):
    QUESTION_TYPES = (
        ('text', 'Texto'),
        ('number', 'Número'),
        ('select', 'Seleção'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Rádio'),
        ('textarea', 'Caixa de Texto Grande'), 
    )
    
    selecao = models.ForeignKey(
        Selecao, 
        on_delete=models.CASCADE, 
        related_name='questions'
    )
    question_text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    order = models.PositiveIntegerField(default=0)
    required = models.BooleanField(default=True)
    options = JSONField(blank=True, null=True)
    conditions = JSONField(blank=True, null=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.selecao.nome} - {self.question_text}"