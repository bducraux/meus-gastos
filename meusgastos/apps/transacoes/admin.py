from django.contrib import admin
from django.forms import inlineformset_factory
from django import forms
import os

from .models import Transacao, TransacaoItem, Planejamento
from meusgastos.apps.categorias.models import Categoria


class TransacaoItemForm(forms.ModelForm):
    class Meta:
        model = TransacaoItem
        fields = ['descricao', 'valor', 'categoria']


TransacaoItemFormSet = inlineformset_factory(Transacao,
                                             TransacaoItem,
                                             form=TransacaoItemForm,
                                             fields=('descricao', 'valor', 'categoria'),
                                             extra=1, can_delete=True, can_delete_extra=True)


class TransacaoItemInline(admin.TabularInline):
    model = TransacaoItem
    formset = TransacaoItemFormSet
    form = TransacaoItemForm  # Usar o formulário personalizado
    extra = 1
    verbose_name = 'Items da Transação'
    verbose_name_plural = 'Items da Transação'


class TransacaoForm(forms.ModelForm):
    class Meta:
        model = Transacao
        fields = ['identificacao', 'memo', 'observacao', 'valor', 'data', 'tipo', 'categoria', 'efetivado', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['categoria'].queryset = Categoria.objects.filter(is_active=True).order_by('parent_path')


class FilledCategoriaFilter(admin.SimpleListFilter):
    title = 'Categorias'
    parameter_name = 'filled_categoria'

    def lookups(self, request, model_admin):
        return (
            ('categorized', 'Categorizados'),
            ('not_categorized', 'Não Categorizados'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'categorized':
            return queryset.filter(categoria__isnull=False)
        if self.value() == 'not_categorized':
            return queryset.filter(categoria__isnull=True)
        return queryset


class TransacaoAdmin(admin.ModelAdmin):
    form = TransacaoForm
    list_display = ['data', 'memo', 'valor', 'tipo', 'categoria', 'efetivado', 'status']
    list_display_links = ['memo']
    list_filter = ['data', 'tipo', 'efetivado', 'status', FilledCategoriaFilter]
    search_fields = ['memo__icontains', 'observacao__icontains', 'categoria__descricao', 'valor', 'data']
    list_per_page = 20
    inlines = [TransacaoItemInline]

    def get_inline_instances(self, request, obj=None):
        """Show inline form only on update form."""
        inline_instances = []
        if obj:
            inline_instances = super().get_inline_instances(request, obj)
        return inline_instances

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.update_valor()


class TransacaoItemAdmin(admin.ModelAdmin):
    list_display = ['transacao', 'descricao', 'valor', 'categoria']
    list_display_links = ['descricao']
    list_filter = ['categoria']
    search_fields = ['descricao__icontains', 'valor', 'categoria__descricao']
    list_per_page = 20


class PlanejamentoAdmin(admin.ModelAdmin):
    list_display = ['categoria', 'valor', 'mes', 'repeticoes_display']
    list_display_links = ['categoria']
    list_filter = ['mes', 'categoria']
    search_fields = ['categoria__descricao', 'valor', 'med']
    list_per_page = 20

    def repeticoes_display(self, obj):
        if obj.repeticoes == 0:
            return 'Mensalmente'
        if obj.repeticoes == 1:
            return 'Um mês'
        return f"{obj.repeticoes} meses"

    repeticoes_display.short_description = 'Repetições'


admin.site.register(Transacao, TransacaoAdmin)
admin.site.register(TransacaoItem, TransacaoItemAdmin)
admin.site.register(Planejamento, PlanejamentoAdmin)


