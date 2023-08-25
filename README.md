# meus-gastos
Projeto Django para controle financeiro dos gastos, com extração das transações de arquivos ofx e categorização automática dos gastos.

Esse projeto começou com uma necessidade pessoal de controlar os gastos e ter uma visão geral de onde o dinheiro estava sendo gasto. A ideia é que o sistema seja capaz de ler os arquivos ofx disponibilizados pelo banco e categorizar automaticamente os gastos.

Como o projeto foi iniciado para uso pessoal, a princípio não há planos de torná-lo preparado para multi usuários. Se você se interessou pelo projeto, fique à vontade para usá-lo e contribuir com melhorias.

## Instalação
Criar um ambiente virtual e instalar as dependências:

Linux:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Windows:
```
python3 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Configuração

### Dados iniciais
Migrações:
```
python manage.py migrate
```

Para criar um usuário administrador, execute o comando:
```
python manage.py createsuperuser
```

Criar as categorias de gastos:
```
python manage.py loaddata categorias.json
```

### Extração de dados de extratos em arquivos ofx
Para extrair os dados dos arquivos ofx, execute o comando:
```
python manage.py importar_extrato <caminho do arquivo ofx>
```
Lembrando que o script de extração de dados foi desenvolvido para extratos do banco Bradesco. Se você usa outro banco, provavelmente será necessário fazer algumas adaptações no script.

Foi detectado que o arquivo ofx do Bradesco possui um erro de formatação que impede a extração dos dados. Para corrigir esse erro, faça o seguinte:
1. Abra o arquivo ofx no editor de texto de sua preferência
2. Procure pela linha que contém a string `<DTSERVER>00000000000000`
3. Copie a data presente na linha <DTSTART> e cole na linha <DTSERVER>

Exemplo:
```
<OFX>
    <SIGNONMSGSRSV1>
        <SONRS>
            <STATUS>
                <CODE>0
                <SEVERITY>INFO
            </STATUS>
            <DTSERVER>00000000000000
            <LANGUAGE>POR
        </SONRS>
        <BANKMSGSRSV1>
            <STMTTRNRS>
		...
		          <BANKTRANLIST>
		              <DTSTART>20230801000000
```
Ficará assim:
```
<OFX>
    <SIGNONMSGSRSV1>
        <SONRS>
            <STATUS>
                <CODE>0
                <SEVERITY>INFO
            </STATUS>
            <DTSERVER>20230801000000
            <LANGUAGE>POR
        </SONRS>
        <BANKMSGSRSV1>
            <STMTTRNRS>
		...
		          <BANKTRANLIST>
		              <DTSTART>20230801000000
```

### Extração de dados de faturas de cartão de crédito em arquivos txt