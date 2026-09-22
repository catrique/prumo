# Diretrizes para agentes

Este arquivo orienta agentes de código que trabalham no repositório Prumo.

## Princípios de desenvolvimento

- Preserve a arquitetura existente e mantenha o projeto pequeno.
- Não crie abstrações sem uma necessidade real e atual.
- Mantenha responsabilidades bem separadas e o acoplamento baixo.
- Evite funções e arquivos excessivamente grandes.
- Favoreça código legível, explícito e com nomes descritivos.
- Evite dependências sem uma justificativa clara.
- Detecte ferramentas do sistema; não tente instalá-las ou alterar o ambiente.
- Execute subprocessos com argumentos separados e sem shell quando não houver
  necessidade real.
- Dependências do projeto podem ser instaladas dentro do próprio projeto.
- Escreva ou atualize testes sempre que um comportamento for alterado.
- Priorize testes de comportamentos críticos e evite testes de baixo valor.
- Execute os testes e o lint antes de considerar uma tarefa concluída.
- Verifique a segurança das alterações e nunca inclua secrets, credenciais ou
  dados específicos da máquina local.
- Não faça alterações fora do escopo solicitado.
- Nunca execute `git push` automaticamente.

## Fluxo de trabalho com Git

Depois de concluir uma tarefa solicitada:

1. Revise todas as alterações.
2. Execute os testes.
3. Execute o lint.
4. Verifique o `git diff`.
5. Crie um commit claro e objetivo.
6. Nunca execute `git push` automaticamente.
