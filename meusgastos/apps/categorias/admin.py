from django.contrib import admin
from django import forms
from .models import Categoria


class MainCategoriaFilter(admin.SimpleListFilter):
    title = 'Categorias'
    parameter_name = 'main_categoria'

    def lookups(self, request, model_admin):
        return (
            ('main', 'Categorias Principais'),
            ('sub', 'Subcategorias'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'main':
            return queryset.filter(parent=None)
        if self.value() == 'sub':
            return queryset.filter(parent__isnull=False)
        return queryset


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['cod', 'descricao', 'tipo', 'keywords', 'is_active', 'parent']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['parent'].queryset = Categoria.objects.filter(is_active=True).order_by('parent_path')


class CategoriaAdmin(admin.ModelAdmin):
    form = CategoriaForm
    list_display = ['cod', 'descricao', 'tipo', 'get_subcategorias', 'parent', 'keywords', 'is_active']
    list_display_links = ['cod']
    list_editable = ['is_active']
    list_filter = ['tipo', 'is_active', MainCategoriaFilter]
    search_fields = ['cod__icontains', 'descricao__icontains', 'keywords__icontains']
    list_per_page = 20

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')

    def get_subcategorias(self, obj):
        subcategorias = obj.categoria_set.all()
        return ", ".join([subcategoria.cod for subcategoria in subcategorias])

    get_subcategorias.short_description = 'Sub-Categorias'


admin.site.register(Categoria, CategoriaAdmin)
