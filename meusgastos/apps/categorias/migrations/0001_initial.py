from django.db import migrations, models
import django.db.models.deletion
from django.core.management import call_command


def load_fixture(apps, schema_editor):
    call_command('loaddata', 'categorias.json', app_label='categorias')


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('parent_path', models.CharField(blank=True, max_length=200, null=True, verbose_name='Caminho até a categoria pai')),
                ('cod', models.CharField(max_length=40, verbose_name='Código')),
                ('tipo', models.CharField(choices=[('E', 'Entrada'), ('S', 'Saída'), ('T', 'Todos')], default='T', help_text='Tipo de transação que a categoria se aplica. "Todos" para categorias que podem ser usadas em entradas e saídas.', max_length=1)),
                ('descricao', models.CharField(blank=True, max_length=40, null=True, verbose_name='Descrição')),
                ('keywords', models.TextField(blank=True, help_text='Palavras-chave separadas por vírgula que serão usadas para categorização automática das transações.', null=True, verbose_name='Palavras-chave')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativa')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='categorias.categoria', verbose_name='Categoria Pai')),
            ],
            options={
                'ordering': ['cod'],
                'unique_together': {('cod', 'parent')},
            },
        ),
        migrations.RunPython(load_fixture),
    ]
