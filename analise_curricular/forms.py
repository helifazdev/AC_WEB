# analise_curricular/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Candidato, Selecao, DocumentoCandidato

class CandidatoForm(forms.ModelForm):
    REQUISITO_CHOICES = [
        ('', 'Selecione uma opção'),
        ('Sim', 'Sim'),
        ('Nao', 'Nao'),
    ]
    
    AVALIACAO_CHOICES = [
        ('', 'Selecione uma opção'),
        ('Graduacao', 'Graduacao'),
        ('Especializacao', 'Especializacao'),
        ('Mestrado', 'Mestrado'),
        ('Doutorado', 'Doutorado'),
        ('Nao possui', 'Nao possui'),
    ]

    MOTIVO_NAO_POSSUI_CHOICES = [
        ('', 'Selecione o motivo'),
        ('sem_documentacao', 'Sem documentação'),
        ('documentacao_invalida', 'Documentação inválida'),
        ('documentacao_ilegivel', 'Documentação ilegível'),
        ('outros', 'Outros'),
    ]

    requisito = forms.ChoiceField(
        choices=REQUISITO_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label="Possui Requisitos para o Cargo?"
    )
    
    avaliacao = forms.ChoiceField(
        choices=AVALIACAO_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label="Avaliação Curricular"
    )

    motivo_nao_possui = forms.ChoiceField(
        choices=MOTIVO_NAO_POSSUI_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label="Motivo para 'Não possui'"
    )
    
    justificativa = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label="Justificativa"
    )

    class Meta:
        model = Candidato
        fields = [
            'nome',
            'inscricao',
            'cargo',
            'requisito',
            'avaliacao',
            'justificativa',
            'observacao'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'readonly': True}),
            'inscricao': forms.TextInput(attrs={'readonly': True}),
            'cargo': forms.TextInput(attrs={'readonly': True}),
            'observacao': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona classes CSS consistentes
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs.update({'class': 'form-radio'})

    def clean(self):
        cleaned_data = super().clean()
        avaliacao = cleaned_data.get('avaliacao')
        motivo_nao_possui = cleaned_data.get('motivo_nao_possui')
        justificativa = cleaned_data.get('justificativa')

        # Se "Nao possui" for selecionado, motivo é obrigatório
        if avaliacao == 'Nao possui' and not motivo_nao_possui:
            self.add_error('motivo_nao_possui', "Selecione o motivo para 'Não possui'.")    
        # Validação da justificativa
        if avaliacao == 'Nao possui' and not justificativa:
            self.add_error('justificativa', "Por favor, forneça uma justificativa para 'Não possui'")
        
        return cleaned_data


class AvaliadorSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class SelecaoForm(forms.Form):
    selecao_disponivel = forms.ModelChoiceField(
        queryset=Selecao.objects.filter(ativa=True).order_by('nome'),
        empty_label="Selecione uma Seleção para Avaliar",
        label="Seleção Disponível",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
class DocumentoForm(forms.ModelForm):
    class Meta:
        model = DocumentoCandidato
        fields = ['tipo', 'arquivo', 'observacoes']
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_arquivo(self):
        arquivo = self.cleaned_data.get('arquivo')
        if arquivo:
            # Limita o tamanho (5MB)
            if arquivo.size > 5*1024*1024:
                raise forms.ValidationError("Arquivo muito grande (tamanho máximo: 5MB)")
            
            # Valida extensões permitidas
            extensoes_validas = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
            if not any(arquivo.name.lower().endswith(ext) for ext in extensoes_validas):
                raise forms.ValidationError("Tipo de arquivo não suportado. Use PDF, JPG, PNG ou DOC.")
        
        return arquivo