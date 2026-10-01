# Embaixadores do Rei — material de estudo e provas

Repo local para gerar PDFs de estudo e de prova das disciplinas da organização Embaixadores do Rei. Idioma de tudo: português do Brasil, com acentuação correta.

Embaixada: **Embaixada Pastor José Saraiva** — Primeira Igreja Batista em Potira I - Caucaia-CE (constantes `EMBAIXADA` e `IGREJA` em `scripts/build_pdf.py`; aparecem no topo e no rodapé de todo PDF).

## Fluxo

```
docs/ (fontes)  ->  estudos/*.md  ->  saida/*-estudo.pdf
                         |
                         v
                    provas/*.md   ->  saida/*-prova.pdf + *-gabarito.pdf
```

- Skills: `gerar-estudo` e `gerar-prova` (em `.claude/skills/`). O Claude escreve o Markdown; o PDF é montado de forma determinística por `scripts/build_pdf.py` (Python 3 stdlib + Typst).
- Pré-requisito: `typst` instalado (`brew install typst`).
- A prova nasce do **estudo**, não das fontes. A prova é **sempre só de marcar (múltipla escolha A–D)** e termina com um cartão-resposta de bolinhas; o gabarito é o espelho exato da prova com as respostas marcadas.
- **Estudo:** 2 colunas, fonte 11pt, quantas páginas precisar. **Prova e gabarito:** impressão frente e verso, sempre 2 páginas em 2 colunas (fonte automática, até 10pt); sempre 20 questões; página 1 = questões, página 2 = cartão-resposta.
- **Referências obrigatórias:** toda pergunta do estudo e toda questão da prova tem `F:` (obra/capítulo/página ou livro bíblico/capítulo/versículo). Aparecem ao lado do enunciado, no estudo e no gabarito (nunca na prova do aluno).
- `saida/` é gerado; não editar à mão. Estrutura: `saida/<disciplina>/<unidade>/NNN_<unidade>-<estudo|prova|gabarito>.pdf` (NNN = próximo número livre **por tipo** na pasta; nunca sobrescreve; prova e gabarito da mesma geração dividem o número; número e data de geração também aparecem dentro do PDF).

## Fluxo de qualidade

1. O Claude escreve o estudo (`status: rascunho`).
2. Uma pessoa revisa fatos e referências contra a fonte e troca para `status: revisado`.
3. Provas e gabaritos nascem do estudo; o script valida que cada `F:` da prova existe no estudo.
4. PDFs em `saida/` são descartáveis: corrigir = editar o `.md` e regerar (a numeração NNN_ guarda as versões).

## Material de estudo

Apenas **pergunta e resposta curta**, para decorar. Nada de resumo ou resposta longa.

## Disciplinas e fontes

| Sigla | Disciplina | Fonte em `docs/` |
|---|---|---|
| `cgb` | Conhecimentos Gerais da Bíblia | `cgb/01..10-*.md` (um arquivo por grupo de livros, versão corrigida em `**N**` por versículo) |
| `cgo` | Conhecimentos Gerais da Organização | `cgo/Manual do Escudeiro…`, `cgo/Manual do Arauto…` |
| `bj` | Biografia de Jesus | `bj/06-evangelhos-…md` (Evangelhos; idêntico a `cgb/06`) |
| `bwah` | Biografia de William Alvin Hatton | `bwah/Alvin Hatton - Sempre Embaixador…md` |

Nome da unidade (arquivo em `estudos/` e `provas/`) = slug curto: `escudeiro`, `arauto`, `pentateuco`, `evangelhos`, `atos`, `sempre-embaixador`…

## Status

- Piloto pronto: CGO / Escudeiro (`estudos/cgo/escudeiro.md`, `provas/cgo/escudeiro.md`).
- BJ (Biografia de Jesus): estudos prontos em `estudos/bj/`, 8 fases cronológicas dos Evangelhos (nascimento e infância → ressurreição e ascensão); referências `F:` por livro, capítulo e versículo. Provas (20 questões ME + gabarito) geradas por fase em `provas/bj/`.
- Pendente: CGO / Arauto, BWAH, CGB (10 unidades).
