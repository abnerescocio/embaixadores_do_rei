---
name: gerar-estudo
description: Gera o material de estudo (perguntas e respostas curtas, para decorar) de uma disciplina dos Embaixadores do Rei a partir das fontes em docs/ e o converte em PDF. Use quando o usuário pedir "gerar estudo", "material de estudo" ou "PDF de estudo" de CGB, CGO, BJ ou BWAH, ou de um manual/livro/seção específica.
---

# Gerar estudo

Produz `estudos/<disciplina>/<unidade>.md` e o PDF em `saida/<disciplina>/<unidade>/NNN_<unidade>-estudo.pdf`.

## Entrada

Disciplina (`cgb`, `cgo`, `bj`, `bwah`) e a unidade (ver tabela em `CLAUDE.md`). Se a unidade não for informada, pergunte qual, pois as fontes são grandes.

## Regras de conteúdo (do usuário, inegociáveis)

- **Só pergunta e resposta curta**, focadas em memorização. Nada de resumo, texto corrido ou resposta descritiva longa.
- Uma pergunta = um fato. Respostas de preferência com até uma linha (nomes, datas, números, ordens, referências bíblicas, definições curtas).
- Exceção: textos que devem ser decorados literalmente (compromissos, versículos-chave) entram na resposta inteiros.
- Seja fiel à fonte: não acrescente fatos de fora. Se a fonte tiver erro evidente (data impossível, referência errada), registre a versão do manual ou corrija e **avise o usuário no final**.
- O PDF do estudo sai em 2 colunas, fonte 11pt (constante `FONTE_ESTUDO` em `scripts/build_pdf.py`), com quantas páginas forem necessárias. Não há limite de perguntas por arquivo, mas unidades muito grandes (como livros inteiros da Bíblia) ficam melhores divididas em partes (`pentateuco-1.md`…).
- **Toda pergunta tem referência (`F:`), obrigatória** (o script recusa o estudo se faltar alguma). Ela aparece **ao lado do enunciado da pergunta** no PDF. No estudo o script omite o que já está no `obra:` do cabeçalho e no título da seção (ex.: `Manual do Escudeiro, Tarefa 2, p. 11` vira `p. 11` sob `## Tarefa 2: …`), então escreva a referência sempre completa e comece cada seção com o mesmo rótulo usado em `F:` (`Tarefa N`, `Capítulo N`). No gabarito ela aparece completa. Coloque toda a referência possível, sempre a mais precisa que a fonte permitir:
  - Manuais e livros: obra, capítulo/tarefa/seção e **página** (use os marcadores `<!-- página NN -->` da fonte; a página é a do marcador que vem *antes* do trecho). Várias páginas: `pp. 42, 44 e 46` ou `pp. 51-52`.
  - Bíblia (CGB e BJ): livro, capítulo e versículo(s), p. ex. `Atos 2.1-4` (nos arquivos de `docs/cgb` e `docs/bj` o capítulo vem no título `# Livro Cap NN` e o versículo em `**N**`).
  - Se a resposta cita versículo(s) que a fonte indica (como "Efésios 6.16"), mantenha na resposta e, se útil, repita em `F:`.
- Cubra a fonte inteira, na ordem em que aparece, uma seção `##` por capítulo/tarefa.
- Perguntas de lacuna ("Complete: ... ___") são bem-vindas para versículos.

## Formato do arquivo

```
---
titulo: <título da unidade>
disciplina: <nome completo da disciplina>
obra: <nome curto da obra, igual ao 1º item das referências F:>
status: rascunho
fonte: <caminho em docs/>
---

## <Seção>

P: <pergunta>
R: <resposta curta>
F: <referência: obra, capítulo/tarefa, página — ou livro bíblico, capítulo, versículo>
```

## Revisão (status)

Todo estudo nasce com `status: rascunho`. Só uma pessoa troca para `status: revisado`, depois de conferir os fatos e as referências contra o manual ou a Bíblia. O Claude nunca marca como revisado. Enquanto for rascunho, o script avisa ao gerar PDFs. Depois de revisado, mudar o estudo é correção deliberada: regerar as provas que dependem dele.

## Passos

1. Leia a fonte em `docs/` (arquivos grandes: leia em blocos por `offset`/`limit`; no CGB cada capítulo é um `# Livro Cap NN` com versículos em `**N**`).
2. Escreva `estudos/<disciplina>/<unidade>.md` no formato acima.
3. Rode `python3 scripts/build_pdf.py estudo estudos/<disciplina>/<unidade>.md`.
4. Informe o caminho do PDF, a quantidade de perguntas e qualquer inconsistência encontrada na fonte.

Modelo de referência: `estudos/cgo/escudeiro.md`.
