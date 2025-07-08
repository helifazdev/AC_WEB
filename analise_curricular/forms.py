# analise_curricular/forms.py

from django import forms
from .models import Candidato

class CandidatoForm(forms.ModelForm):
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
            # Adiciona o atributo readonly para os campos de dados básicos
            'nome': forms.TextInput(attrs={'readonly': 'readonly'}),
            'inscricao': forms.TextInput(attrs={'readonly': 'readonly'}),
            'cargo': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.Select, forms.Textarea)):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.RadioSelect):
                # Para radio buttons, a classe precisa ser aplicada ao input individualmente,
                # ou o CSS deve ser mais genérico para inputs[type="radio"]
                # Vamos remover o attrs.update aqui e confiar no CSS direto no template
                pass # Não adiciona classe aqui para RadioSelect, pois pode causar problemas com o render padrão do Django

        if self.instance and self.instance.avaliacao != 'Nao possui':
            self.fields['justificativa'].required = False
            self.fields['justificativa'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        avaliacao = cleaned_data.get('avaliacao')
        justificativa = cleaned_data.get('justificativa')

        if avaliacao == 'Nao possui' and not justificativa:
            self.add_error('justificativa', "Por favor, forneça uma justificativa para a avaliação 'Não possui'.")

        return cleaned_data