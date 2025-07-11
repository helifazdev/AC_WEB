# analise_curricular/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Candidato, Selecao

class CandidatoForm(forms.ModelForm):
    REQUISITO_CHOICES = [
        ('', 'Selecione uma opção'),
        ('Sim', 'Sim'),
        ('Nao', 'Não'),
    ]
    
    AVALIACAO_CHOICES = [
        ('', 'Selecione uma opção'),
        ('Graduacao', 'Graduação'),
        ('Especializacao', 'Especialização'),
        ('Mestrado', 'Mestrado'),
        ('Doutorado', 'Doutorado'),
        ('Nao possui', 'Não possui'),
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
        justificativa = cleaned_data.get('justificativa')

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