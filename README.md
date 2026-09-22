# Prumo

Prumo é um CLI que ajuda a criar e padronizar projetos de software. Nesta fase,
ele permite configurar interativamente um projeto, validar as escolhas e gerar
aplicações React com Vite e TypeScript. As demais tecnologias ainda têm apenas
sua estrutura inicial planejada.

## Requisitos

- Python 3.11 ou superior
- Node.js 20.19+ ou 22.12+
- npm

O Prumo detecta Node.js e npm, mas não instala nem altera essas ferramentas no
sistema.

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

O comando `prumo create` solicita o nome e as tecnologias do projeto e
apresenta um resumo para confirmação. Projetos React são gerados com Vite e
TypeScript, e suas dependências npm são instaladas dentro do projeto.

Em projetos somente React, o conteúdo fica diretamente na raiz. Em uma
configuração React + Flask, o React fica em `frontend/` e `backend/` é
reservado para a implementação futura do Flask. Angular, Flask e MySQL ainda
não são gerados ou configurados.

## Qualidade

Execute os testes e o lint com:

```bash
pytest
ruff check .
```
