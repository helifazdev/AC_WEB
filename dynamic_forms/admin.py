from django.contrib import admin
from .models import FormSelection, FormQuestion

class FormQuestionInline(admin.TabularInline):
    model = FormQuestion
    extra = 1
    fields = ('question_text', 'question_type', 'order', 'required', 'options', 'conditions')

@admin.register(FormSelection)
class FormSelectionAdmin(admin.ModelAdmin):
    inlines = [FormQuestionInline]
    list_display = ('name', 'description')

@admin.register(FormQuestion)
class FormQuestionAdmin(admin.ModelAdmin):
    list_display = ('form_selection', 'question_text', 'question_type', 'order')
    list_filter = ('form_selection', 'question_type')
    ordering = ('form_selection', 'order')