from django.db import models
from django.db.models import JSONField  # Usando o JSONField nativo do Django (versão >= 3.1)

class FormSelection(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return self.name

class FormQuestion(models.Model):
    QUESTION_TYPES = (
        ('text', 'Texto'),
        ('number', 'Número'),
        ('select', 'Seleção'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Rádio'),
    )
    
    form_selection = models.ForeignKey(FormSelection, on_delete=models.CASCADE, related_name='questions')
    question_text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    order = models.PositiveIntegerField(default=0)
    required = models.BooleanField(default=True)
    # Configurações específicas por tipo de pergunta
    options = JSONField(blank=True, null=True)  # Para perguntas de seleção, checkbox, etc.
    conditions = JSONField(blank=True, null=True)  # Para lógicas condicionais
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.form_selection.name} - {self.question_text}"