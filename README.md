# Prumo

Prumo é um CLI que ajuda a criar e padronizar projetos de software. Nesta fase,
ele permite configurar interativamente um projeto, validar as escolhas e criar
somente a estrutura inicial de diretórios planejada.

## Requisitos

- Python 3.11 ou superior

## Ambiente de desenvolvimento

Crie e ative um ambiente virtual:

```bash
python -m venv .venv
```

No PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

No Linux ou macOS:

```bash
source .venv/bin/activate
```

Instale as dependências e o Prumo em modo editável:

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Uso

```bash
prumo --help
prumo version
prumo create
```

O comando `prumo create` solicita o nome e as tecnologias do projeto,
apresenta um resumo para confirmação e cria os diretórios necessários. React,
Angular, Flask e MySQL ainda não são instalados nem configurados nesta versão.

## Qualidade

Execute os testes e o lint com:

```bash
pytest
ruff check .
```
