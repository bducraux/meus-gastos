# coding: utf-8
from django.db import models
from django.core.exceptions import ValidationError


class Categoria(models.Model):
    TIPOS = (
        ('E', 'Entrada'),
        ('S', 'Saída'),
        ('T', 'Todos')
    )

    id = models.BigAutoField(primary_key=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Categoria Pai')
    parent_path = models.CharField(max_length=200, null=True, blank=True, verbose_name='Caminho até a categoria pai')
    cod = models.CharField(max_length=40, verbose_name='Código')
    tipo = models.CharField(choices=TIPOS,
                            default='T',
                            max_length=1,
                            help_text='Tipo de transação que a categoria se aplica. '
                                      '"Todos" para categorias que podem ser usadas em entradas e saídas.')
    descricao = models.CharField(max_length=40, verbose_name='Descrição', null=True, blank=True)
    keywords = models.TextField(
        verbose_name='Palavras-chave',
        blank=True,
        null=True,
        help_text='Palavras-chave separadas por vírgula que serão usadas para categorização automática das transações.'
    )
    is_active = models.BooleanField(default=True, verbose_name='Ativa')

    class Meta:
        ordering = ['cod']
        unique_together = [['cod', 'parent']]

    def __str__(self):
        return self.parent_path if self.parent_path else self.cod

    def _get_category_path(self, category):
        if category.parent:
            return f"{self._get_category_path(category.parent)} > {category.descricao}"
        else:
            return category.descricao

    def save(self, *args, **kwargs):
        self.cod = self.cod.upper()
        self.parent_path = self._get_category_path(self)
        self.full_clean()
        super(Categoria, self).save(*args, **kwargs)

    def clean(self):
        if self.parent and self.parent.tipo != 'T':
            if self.parent.tipo != self.tipo:
                raise ValidationError("Subcategoria precisa ser do mesmo 'tipo' que a categoria pai.")
