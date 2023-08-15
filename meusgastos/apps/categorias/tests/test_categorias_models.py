import pytest
from django.core.exceptions import ValidationError
from meusgastos.apps.categorias.models import Categoria


@pytest.mark.django_db
def test_categoria_creation():
    # Cria uma categoria
    categoria = Categoria.objects.create(
        cod='ALIM',
        tipo='S',
        descricao='Alimentação'
    )

    assert str(categoria) == categoria.parent_path
    assert categoria.parent_path == 'Alimentação'


@pytest.mark.django_db
def test_subcategoria_tipo_valid():
    # Cria uma categoria pai
    categoria_pai = Categoria.objects.create(
        cod='PAI',
        tipo='T',
        descricao='Categoria Pai'
    )

    # Cria uma subcategoria
    subcategoria = Categoria.objects.create(
        cod='SUB',
        tipo='S',
        descricao='Subcategoria',
        parent=categoria_pai
    )

    assert str(subcategoria) == 'Categoria Pai > Subcategoria'

    # Garante que não é possível criar outra subcategoria com o mesmo código e pai
    with pytest.raises(ValidationError):
        Categoria.objects.create(
            cod='SUB',
            tipo='E',  # Tipo compatível com o pai
            descricao='Outra Subcategoria',
            parent=categoria_pai
        )


@pytest.mark.django_db
def test_subcategoria_tipo_invalid():
    # Cria uma categoria pai
    categoria_pai = Categoria.objects.create(
        cod='PAI',
        tipo='E',
        descricao='Categoria Pai'
    )

    # Tenta criar uma subcategoria com tipo incompatível
    with pytest.raises(ValidationError):
        Categoria.objects.create(
            cod='SUB',
            tipo='S',
            descricao='Subcategoria',
            parent=categoria_pai
        )
