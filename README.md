# Prumo

Prumo é um CLI que, futuramente, ajudará a criar e padronizar projetos de
software. O projeto está em sua fase inicial e oferece apenas a fundação do CLI
e a consulta de versão.

## Requisitos

- Python 3.11 ou superior

## Ambiente de desenvolvimento

Crie e ative um ambiente virtual:

```bash
python -m venv .venv
```

No Linux ou macOS:

```bash
source .venv/bin/activate
```

No PowerShell:

```powershell
.venv\Scripts\Activate.ps1
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
```

## Qualidade

Execute os testes e o lint com:

```bash
pytest
ruff check .
```
