# Embaixadores do Rei — material de estudo e provas

Repo local para gerar PDFs de estudo e de prova das disciplinas da organização Embaixadores do Rei. Idioma de tudo: português do Brasil, com acentuação correta.

Embaixada: **Embaixada Pastor José Saraiva** — Primeira Igreja Batista em Potira I - Caucaia-CE (constantes `EMBAIXADA` e `IGREJA` em `scripts/build_pdf.py`; aparecem no topo e no rodapé de todo PDF).

## Fluxo

```
docs/ (fontes)  ->  estudos/*.md  ->  saida/estudos/<disc>_<unidade>.pdf
                         |
                         v
                    provas/<disc>/<unidade>/NNN.md ->  saida/provas/<disc>_<unidade>_NNN.pdf
                                    saida/gabaritos/<disc>_<unidade>-gabarito_NNN.pdf
```

- Skills: `gerar-estudo` e `gerar-prova` (em `.claude/skills/`). O Claude escreve o Markdown; o PDF é montado de forma determinística por `scripts/build_pdf.py` (Python 3 stdlib + Typst).
- Pré-requisito: `typst` instalado (`brew install typst`).
- A prova nasce do **estudo**, não das fontes. A prova é **sempre só de marcar (múltipla escolha A–D)** e termina com um cartão-resposta de bolinhas; o gabarito é o espelho exato da prova com as respostas marcadas.
- **Estudo:** 2 colunas, fonte 11pt, quantas páginas precisar. **Prova e gabarito:** impressão frente e verso, sempre 2 páginas em 2 colunas (fonte automática, até 10pt); sempre 20 questões; página 1 = questões, página 2 = cartão-resposta.
- **Referências obrigatórias:** toda pergunta do estudo e toda questão da prova tem `F:` (obra/capítulo/página ou livro bíblico/capítulo/versículo). Aparecem ao lado do enunciado, no estudo e no gabarito (nunca na prova do aluno).
- `saida/` é gerado; não editar à mão. Três pastas (`estudos`, `provas`, `gabaritos`), com os PDFs de cada tipo juntos e a sigla da disciplina como prefixo: `saida/estudos/<disc>_<unidade>.pdf` (estudo canônico, nome fixo, sobrescrito ao regerar) `saida/provas/<disc>_<unidade>_NNN.pdf` e `saida/gabaritos/<disc>_<unidade>-gabarito_NNN.pdf` (NNN = nome do arquivo-fonte `provas/<disc>/<unidade>/NNN.md`; sem contador e sem olhar `saida/`; prova nova = próximo número livre da pasta). Detalhes no `README.md`.

## Fluxo de qualidade

1. O Claude escreve o estudo (`status: rascunho`).
2. Uma pessoa revisa fatos e referências contra a fonte e troca para `status: revisado`.
3. Provas e gabaritos nascem do estudo; cada questão tem `E:` (ID `I:` da pergunta de origem) e o script valida o ID, o `F:` e o limite de 5 questões em comum entre provas da mesma unidade.
3b. Controle de uso: `python3 scripts/ids.py <estudo.md>` numera perguntas novas (`I: NNN`, nunca renumerar; o ID é o número exibido no PDF do estudo e aparece como `Estudo #NN` no gabarito, nunca na prova do aluno); `python3 scripts/cobertura.py <estudo.md> [--livres|--usos]` mostra o que já caiu em provas. Ao montar prova nova, priorizar as perguntas nunca usadas e distribuir por seção. Níveis (essencial/normal/detalhe) e dificuldade por resultado de alunos são etapas futuras.
4. PDFs em `saida/` são descartáveis: corrigir = editar o `.md` e regerar (o PDF do estudo é sobrescrito; regerar uma prova sobrescreve o PDF dela; o número vem do nome do arquivo-fonte).

## Material de estudo

Apenas **pergunta e resposta curta**, para decorar. Nada de resumo ou resposta longa.

## Disciplinas e fontes

| Sigla | Disciplina | Fonte em `docs/` |
|---|---|---|
| `cgb` | Conhecimentos Gerais da Bíblia | `cgb/01..10-*.md` (um arquivo por grupo de livros, versão corrigida em `**N**` por versículo) |
| `cgo` | Conhecimentos Gerais da Organização | `cgo/Manual do Escudeiro…`, `cgo/Manual do Arauto…` |
| `bj` | Biografia de Jesus | `bj/06-evangelhos-…md` (Evangelhos; idêntico a `cgb/06`) |
| `bwah` | Biografia de William Alvin Hatton | `bwah/Alvin Hatton - Sempre Embaixador…md` |

Nome da unidade (arquivo em `estudos/<sigla>/` e pasta em `provas/<sigla>/`) = slug curto: `escudeiro`, `arauto`, `pentateuco`, `evangelhos`, `atos`, `sempre-embaixador`…

## Status

- CGO: Escudeiro e Arauto prontos (`estudos/cgo/`, `provas/cgo/`). No Arauto, a fonte não marca página nas Tarefas 1 e 2 e na Introdução, então essas referências ficam sem página.
- BJ (Biografia de Jesus): estudos prontos em `estudos/bj/`, 8 fases cronológicas dos Evangelhos (nascimento e infância → ressurreição e ascensão); referências `F:` por livro, capítulo e versículo. Provas (20 questões ME + gabarito) geradas por fase em `provas/bj/`.
- CGB: estratégia decidida em dois níveis. **Material principal = "Visão Geral da Bíblia"** em 4 partes (`estudos/cgb/01-estrutura-da-biblia`, `02-antigo-testamento`, `03-novo-testamento`, `04-grandes-acontecimentos`; 383 perguntas) com 4 provas de 20 questões (`provas/cgb/`). **Panoramas por livro sob demanda** (modelo: `estudos/cgb/genesis.md`, com prova), gerados só quando pedidos.
- Qualidade de referências bíblicas: `python3 scripts/biblia_fonte.py estudos/<disc>/<unidade>.md` confere se cada `F:` bíblica existe na fonte (livro, capítulo e versículo); rodar sempre após escrever um estudo de CGB ou BJ. Ao escrever fatos bíblicos, confira também que a palavra-chave aparece no versículo (`biblia_fonte.verificar`).
- Referência externa (regulamento de competições do DCER Mineiro, 2026, não oficial para esta embaixada): CGB = 20 perguntas, 5 alternativas, 20 minutos, 1 ponto cada; estuda-se "a estrutura da Bíblia, fatos históricos e acontecimentos importantes". Prova ELB (um livro específico, em 2026 Daniel) e Montagem Bíblica (ordem e divisões dos livros, número de capítulos) são provas à parte.
- BWAH (Biografia de Alvin Hatton): estudos em 4 partes por capítulo do livro "Sempre Embaixador" (`estudos/bwah/01..04`; 331 perguntas, referência por capítulo e página) e 4 provas de 20 questões (`provas/bwah/`). Cada fato foi conferido por palavra-chave no texto da página citada (`scripts/livro_fonte.py`).
- **Divergências entre o livro e o Manual do Arauto (CGO)**: nascimento de Hatton, livro 14/02/1921 × manual 10/02/1921; nomeação como missionário, livro 14/10/1947 × manual 01/10/1947. O estudo de BWAH segue o livro; o de CGO / Arauto segue o manual. Decidir qual valer nas provas.
- Pendente: panoramas por livro do CGB sob demanda.
