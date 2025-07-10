# analise_curricular/forms.py

from django import forms
from .models import Candidato, Selecao
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm # <--- Adicione esta linha

REQUISITO_CHOICES = [
    ('', 'Selecione uma opção'), # Opção vazia para validação de "não marcado"
    ('Sim', 'Sim'),
    ('Nao', 'Não'), # Use 'Nao' para consistência, se não for um Booleano
]

AVALIACAO_CHOICES = [
    ('', 'Selecione uma opção'), # Opção vazia para validação de "não marcado"
    ('Graduação', 'Graduacao'),
    ('Especialização', 'Especializacao'),
    ('Mestrado', 'Mestrado'),
    ('Doutorado', 'Doutorado'),
    ('Nao possui', 'Não possui'),
    # Adicione outras opções de avaliação se existirem
]


class CandidatoForm(forms.ModelForm):
    # Definindo os campos com as choices se não estiverem no modelo
    requisito = forms.ChoiceField(
        choices=REQUISITO_CHOICES,
        widget=forms.RadioSelect,
        required=True # Marca como obrigatório para validação HTML5 e Django
    )
    avaliacao = forms.ChoiceField(
        choices=AVALIACAO_CHOICES,
        widget=forms.RadioSelect,
        required=True # Marca como obrigatório
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
            'observacao': forms.Textarea(attrs={'rows': 4}),
            # Campos readonly já estão aqui
            'nome': forms.TextInput(attrs={'readonly': 'readonly'}),
            'inscricao': forms.TextInput(attrs={'readonly': 'readonly'}),
            'cargo': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.Select, forms.Textarea)):
                field.widget.attrs.update({'class': 'form-control'})
            # Não é necessário adicionar classe para RadioSelect aqui, o CSS já lida.

        # Lógica para justificativa baseada no instance.
        # Isso garante que se o formulário for carregado com 'Não possui', a justificativa apareça.
        # Se for outra opção, ela não é obrigatória no back-end.
        if self.instance and self.instance.avaliacao and self.instance.avaliacao != 'Nao possui':
            self.fields['justificativa'].required = False
            # Não vamos usar HiddenInput aqui, pois o JS do front-end fará isso.
            # Ocultar com JS é mais flexível para o usuário interagir.
        else:
            # Garante que se 'Nao possui' for a avaliação inicial, a justificativa seja obrigatória.
            self.fields['justificativa'].required = True


    def clean(self):
        cleaned_data = super().clean()
        requisito = cleaned_data.get('requisito')
        avaliacao = cleaned_data.get('avaliacao')
        justificativa = cleaned_data.get('justificativa')

        # Validação para campos não marcados (se você não usar required=True ou se o cliente desabilitar JS)
        if not requisito:
            self.add_error('requisito', "Por favor, selecione uma opção para 'Requisitos para o Cargo'.")
        if not avaliacao:
            self.add_error('avaliacao', "Por favor, selecione uma opção para 'Avaliação Curricular'.")

        # Validação da justificativa
        if avaliacao == 'Nao possui' and not justificativa:
            self.add_error('justificativa', "Por favor, forneça uma justificativa para a avaliação 'Não possui'.")
        elif avaliacao != 'Nao possui': # Se a avaliação não for 'Não possui', a justificativa não é necessária
             cleaned_data['justificativa'] = '' # Limpa o campo se não for necessário para evitar dados indesejados

        return cleaned_data
    
    # NOVO: Formulário de Cadastro para Avaliadores
class AvaliadorSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',) # Opcional: Adicionar campo de email
        # Se quiser adicionar outros campos personalizados ao seu usuário,
        # você precisaria criar um Custom User Model. Por enquanto, focaremos no básico.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

# NOVO FORMULÁRIO: SelecaoForm
class SelecaoForm(forms.Form):
    selecao_disponivel = forms.ModelChoiceField(
        queryset=Selecao.objects.filter(ativa=True).order_by('nome'),
        empty_label="Selecione uma Seleção para Avaliar",
        label="Seleção Disponível",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )