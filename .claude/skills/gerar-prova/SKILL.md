---
name: gerar-prova
description: Gera uma prova (e gabarito) em PDF dos Embaixadores do Rei a partir de um material de estudo já existente em estudos/. Use quando o usuário pedir "gerar prova", "criar prova" ou "PDF de prova" de uma disciplina/unidade (CGB, CGO, BJ, BWAH).
---

# Gerar prova

Parte **sempre** de um estudo existente em `estudos/<disciplina>/<unidade>.md` (não das fontes brutas). Se o estudo não existir, rode antes a skill `gerar-estudo`.

Produz `provas/<disciplina>/<unidade>.md` e, em `saida/provas/`, `<disc>_NNN_<unidade>-prova.pdf` e, em `saida/gabaritos/`, `<disc>_NNN_<unidade>-gabarito.pdf` (ex.: `cgo_001_escudeiro-prova.pdf`; NNN sequencial por unidade).

## Regras

- **A prova é sempre só de marcar: múltipla escolha com alternativas A, B, C e D.** Não gerar V/F, completar nem resposta curta.
- Toda questão deve ter resposta verificável no estudo. Não invente fatos.
- **Toda questão tem `F:` (obrigatório)**: copie a referência da pergunta correspondente no estudo (obra/capítulo/página ou livro/capítulo/versículo). O script recusa questão sem referência e **recusa referência que não exista no estudo** (campo `estudo:` do cabeçalho da prova), portanto copie o `F:` exatamente como está no estudo. No gabarito ela aparece **ao lado do enunciado** da questão (nunca na prova do aluno).
- **Sempre exatamente 20 questões** (o script recusa outra quantidade), cobrindo todas as seções do estudo proporcionalmente.
- Exatamente 4 alternativas (a–d), uma só correta. Distratores plausíveis, preferencialmente tirados de itens parecidos do mesmo estudo.
- Varie a posição da alternativa correta (distribua entre a, b, c e d).
- Alternativas curtas e de tamanho parecido, para a correta não se destacar. Evite alternativas de várias linhas: a prova precisa caber em 1 página de questões.
- Se pedirem várias provas da mesma unidade, varie as questões (arquivos `escudeiro-2.md`, etc.).

## Estrutura do PDF (automática, não precisa escrever no Markdown)

- **Cabeçalho da prova:** campos Nome, Data, Tempo e Nota (sem total de questões).
- **Prova (2 páginas, frente e verso):** página 1 = as 20 questões em 2 colunas, fonte reduzida automaticamente (de 10pt até caber); página 2 = **cartão-resposta de bolinhas** (uma coluna por letra A, B, C, D) em que o aluno marca a alternativa, sempre em uma única página e com o mesmo cabeçalho da prova (título e campos Nome, Data, Tempo, Nota).
- **Gabarito:** espelho exato da prova (mesmo layout, fonte e 2 páginas), com a alternativa correta destacada em vermelho e a referência (fonte) ao lado do enunciado e as bolinhas do cartão preenchidas.

## Formato do arquivo

Questões separadas por linha em branco. `R:` traz só a letra correta.

```
---
titulo: <título>
disciplina: <disciplina>
estudo: estudos/<disciplina>/<unidade>.md
---

[ME] Enunciado?
a) ...
b) ...
c) ...
d) ...
R: b
F: <mesma referência do estudo>
```

## Passos

1. Leia o estudo (se o `status` dele ainda for `rascunho`, avise o usuário; o script também avisa).
2. Escreva `provas/<disciplina>/<unidade>.md`.
3. Rode `python3 scripts/build_pdf.py prova provas/<disciplina>/<unidade>.md`.
4. Informe os caminhos dos PDFs e quantas questões a prova tem.

Modelo de referência: `provas/cgo/escudeiro.md`.
