create-categoria-fixture:
	python manage.py dumpdata --indent 4 categorias.Categoria > meusgastos/apps/categorias/fixtures/categorias.json

load-categoria-fixture:
	python manage.py loaddata categorias.json