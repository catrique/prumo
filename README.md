# Prumo

Prumo é um CLI que ajuda a criar e padronizar projetos de software. Nesta fase,
ele oferece menus interativos para configurar um projeto, validar as escolhas e
gerar aplicações React com Vite e TypeScript.

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

O comando `prumo create` usa menus navegáveis por setas e Enter, organizados
por tipo:

- Frontend: React ou Angular;
- API: FastAPI ou Express, com MySQL opcional;
- Fullstack: combinação de frontend e API, com MySQL opcional;
- Aplicação web: Flask, com MySQL opcional.

Atualmente, somente o gerador React está implementado. Ele usa Vite e
TypeScript, instala as dependências npm dentro do projeto e mantém o conteúdo
diretamente na raiz. Angular, FastAPI, Express, Flask e a configuração MySQL
estão apenas planejados; ao selecioná-los, nenhum arquivo é criado.

## Qualidade

Execute os testes e o lint com:

```bash
pytest
ruff check .
```
