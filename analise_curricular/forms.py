# analise_curricular/forms.py (Versão corrigida e com novo formulário para o Admin)

import os
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Candidato, Selecao, FormQuestion 

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

# NOVO FORMULÁRIO: CandidatoAdminForm (para uso exclusivo no Django Admin)
class CandidatoAdminForm(forms.ModelForm):
    class Meta:
        model = Candidato
        # Liste AQUI todos os campos do modelo Candidato que você quer editar no Admin.
        # Inclua todos os campos fixos, e também 'respostas_dinamicas' se quiser visualizá-lo.
        fields = [
            'selecao', 
            'nome', 
            'inscricao', 
            'cargo', 
            'declarou_deficiencia', 
            'tipo_deficiencia', 
            'pontuacao', 
            'analisado', 
            'data_analisado', 
            'avaliador_analise',
            'respostas_dinamicas', # Para poder ver o JSON no Admin
        ]
        widgets = {
            'respostas_dinamicas': forms.Textarea(attrs={'rows': 5, 'readonly': True}), # Opcional: mostrar como readonly
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Você pode aplicar estilos aqui para o Admin, se quiser
        # Exemplo: self.fields['nome'].widget.attrs.update({'class': 'vTextField'})


# DynamicCandidatoForm (este será o formulário usado pelos avaliadores, permanece como está)
class DynamicCandidatoForm(forms.ModelForm):
    # Campos de Deficiência como READONLY neste formulário
    DECLAROU_DEFICIENCIA_CHOICES = [
        ('Sim', 'Sim'),
        ('Nao', 'Não'),
    ]

    class Meta:
        model = Candidato
        fields = [
            'nome', 
            'inscricao', 
            'cargo', 
            'declarou_deficiencia', # Agora é somente leitura
            'tipo_deficiencia',     # Agora é somente leitura
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'readonly': True, 'class': 'form-control'}),
            'inscricao': forms.TextInput(attrs={'readonly': True, 'class': 'form-control'}),
            'cargo': forms.TextInput(attrs={'readonly': True, 'class': 'form-control'}),
            
            # Campos de Deficiência como READONLY/DISABLED para o AVALIADOR
            'declarou_deficiencia': forms.RadioSelect(attrs={'disabled': True}),
            'tipo_deficiencia': forms.Textarea(attrs={'readonly': True, 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        selecao_id = kwargs.pop('selecao_id', None)
        super().__init__(*args, **kwargs)
        
        if 'declarou_deficiencia' in self.fields:
            self.fields['declarou_deficiencia'].choices = Candidato.SIM_NAO_CHOICES
        
        for field_name, field in self.fields.items():
            # Aplica classes para campos que não são nome, inscricao, cargo, deficiência
            if field_name not in ['nome', 'inscricao', 'cargo', 'declarou_deficiencia', 'tipo_deficiencia']:
                if isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.Select)):
                    field.widget.attrs.update({'class': 'form-control'})
                elif isinstance(field.widget, forms.RadioSelect):
                    field.widget.attrs.update({'class': 'form-radio'})
            
            # Re-garante que campos de deficiência são desabilitados/somente leitura para o avaliador
            if field_name in ['declarou_deficiencia', 'tipo_deficiencia']:
                 self.fields[field_name].widget.attrs['readonly'] = True
                 self.fields[field_name].widget.attrs['disabled'] = True
                 self.fields[field_name].required = False # Campos disabled não podem ser required


        if selecao_id:
            questions = FormQuestion.objects.filter(selecao_id=selecao_id).order_by('order')
            instance_respostas = self.instance.respostas_dinamicas if self.instance and self.instance.pk else {}

            for question in questions:
                field_name = f'question_{question.id}'
                initial_value = instance_respostas.get(str(question.id))

                if question.question_type == 'text':
                    self.fields[field_name] = forms.CharField(
                        label=question.question_text,
                        required=question.required,
                        initial=initial_value,
                        widget=forms.TextInput(attrs={'class': 'form-control'})
                    )
                elif question.question_type == 'number':
                    self.fields[field_name] = forms.IntegerField(
                        label=question.question_text,
                        required=question.required,
                        initial=initial_value,
                        widget=forms.NumberInput(attrs={'class': 'form-control'})
                    )
                elif question.question_type == 'textarea':
                    self.fields[field_name] = forms.CharField(
                        label=question.question_text,
                        required=question.required,
                        initial=initial_value,
                        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
                    )
                elif question.question_type == 'select':
                    choices = []
                    if not question.required:
                        choices.append(('', '---------'))
                    choices.extend([(opt['value'], opt['text']) for opt in question.options])
                    self.fields[field_name] = forms.ChoiceField(
                        label=question.question_text,
                        choices=choices,
                        required=question.required,
                        initial=initial_value,
                        widget=forms.Select(attrs={'class': 'form-control'})
                    )
                elif question.question_type == 'checkbox':
                    choices = [(opt['value'], opt['text']) for opt in question.options]
                    self.fields[field_name] = forms.MultipleChoiceField(
                        label=question.question_text,
                        choices=choices,
                        required=question.required,
                        initial=initial_value,
                        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
                    )
                elif question.question_type == 'radio':
                    choices = [(opt['value'], opt['text']) for opt in question.options]
                    self.fields[field_name] = forms.ChoiceField(
                        label=question.question_text,
                        choices=choices,
                        required=question.required,
                        initial=initial_value,
                        widget=forms.RadioSelect(attrs={'class': 'form-radio'})
                    )
                
                if isinstance(self.fields[field_name].widget, forms.RadioSelect):
                    self.fields[field_name].widget.attrs.update({'class': 'form-radio'})


    def clean(self):
        cleaned_data = super().clean()
        
        # A validação de declarou_deficiencia e tipo_deficiencia agora deve ser feita no CandidatoAdminForm
        # ou diretamente no modelo Candidato se precisar ser mais abrangente,
        # pois esses campos não são editáveis (e portanto não estão em cleaned_data) aqui.

        dynamic_responses = {}
        selecao_id_for_questions = self.instance.selecao.id if self.instance and self.instance.selecao else None

        for name, value in cleaned_data.items():
            if name.startswith('question_'):
                question_id = name.replace('question_', '')
                dynamic_responses[question_id] = value
        
        self.instance.respostas_dinamicas = dynamic_responses 

        if selecao_id_for_questions: 
            avaliacao_question = FormQuestion.objects.filter(
                selecao_id=selecao_id_for_questions,
                question_text__icontains="Avaliação Curricular"
            ).first()

            motivo_nao_possui_question = FormQuestion.objects.filter(
                selecao_id=selecao_id_for_questions,
                question_text__icontains="Motivo para 'Não possui'"
            ).first()

            justificativa_question = FormQuestion.objects.filter(
                selecao_id=selecao_id_for_questions,
                question_text__icontains="Justificativa"
            ).first()

            if avaliacao_question:
                avaliacao_valor_dinamico = dynamic_responses.get(str(avaliacao_question.id))
                if avaliacao_valor_dinamico == 'Nao possui':
                    if motivo_nao_possui_question:
                        motivo_valor_dinamico = dynamic_responses.get(str(motivo_nao_possui_question.id))
                        if not motivo_valor_dinamico:
                            self.add_error(f'question_{motivo_nao_possui_question.id}', "Selecione o motivo para 'Não possui'.")
                        elif motivo_valor_dinamico == 'outros':
                            if justificativa_question:
                                justificativa_valor_dinamica = dynamic_responses.get(str(justificativa_question.id))
                                if not justificativa_valor_dinamica:
                                    self.add_error(f'question_{justificativa_question.id}', "Por favor, forneça uma justificativa para 'Não possui' quando o motivo for 'Outros'.")

        return cleaned_data