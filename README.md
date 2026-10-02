# Embaixadores do Rei — material de estudo e provas

Repositório local da **Embaixada Pastor José Saraiva** (Primeira Igreja Batista em Potira I - Caucaia-CE) para gerar **PDFs de estudo** e **PDFs de prova (com gabarito)** das disciplinas da organização Embaixadores do Rei. O conteúdo é escrito em Markdown, a partir das fontes em `docs/`, e um script converte em PDF.

## Disciplinas e siglas

A sigla é o nome da pasta de origem e o **prefixo dos PDFs**.

| Sigla | Disciplina | Fonte em `docs/` |
|---|---|---|
| `cgo` | Conhecimentos Gerais da Organização | Manuais do Escudeiro e do Arauto |
| `cgb` | Conhecimentos Gerais da Bíblia | Bíblia (10 arquivos, 66 livros) |
| `bj` | Biografia de Jesus | Os quatro Evangelhos |
| `bwah` | Biografia de William Alvin Hatton | Livro "Sempre Embaixador" |

## Estrutura de pastas

```
docs/                  fontes (texto das obras, não editar)
estudos/<sigla>/       estudos em Markdown  (a fonte da verdade do material)
provas/<sigla>/<unidade>/NNN.md   provas em Markdown (nascem do estudo; o número é o nome do arquivo)
saida/                 PDFs gerados (não editar à mão)
├── estudos/           todos os PDFs de estudo, juntos
├── provas/            todos os PDFs de prova, juntos (o que o aluno recebe)
└── gabaritos/         todos os PDFs de gabarito, juntos (só para o aplicador)
scripts/               ferramentas (build_pdf.py, biblia_fonte.py, livro_fonte.py)
.claude/skills/        skills gerar-estudo e gerar-prova
```

## Nome dos PDFs

Tudo começa pela sigla da disciplina, então a ordem alfabética agrupa por disciplina.

| Tipo | Padrão | Exemplo |
|---|---|---|
| Estudo | `saida/estudos/<sigla>_<unidade>.pdf` | `cgo_escudeiro.pdf`, `bj_03-sermao-monte-milagres.pdf` |
| Prova | `saida/provas/<sigla>_<unidade>-prova_<NNN>.pdf` | `cgo_escudeiro-prova_001.pdf` |
| Gabarito | `saida/gabaritos/<sigla>_<unidade>-gabarito_<NNN>.pdf` | `cgo_escudeiro-gabarito_001.pdf` |

- **Estudo é canônico:** não tem número; o PDF é sobrescrito sempre que o estudo é regerado. Futuramente terá versão e data de alteração dentro do material.
- **O número da prova vem do arquivo-fonte, não da pasta `saida/`:** `provas/cgo/arauto/002.md` gera `cgo_arauto-prova_002.pdf` e `cgo_arauto-gabarito_002.pdf`. Não existe contador: sigla, unidade e número são lidos do caminho do arquivo. Apagar `saida/` e regerar produz exatamente os mesmos nomes.
- **Prova nova** (questões diferentes da mesma unidade) = arquivo novo com o **próximo número livre** da pasta (`001.md`, `002.md`, `003.md`...). Regerar uma prova existente sobrescreve o PDF dela, porque o conteúdo é o mesmo.
- **Unidade** é o nome do arquivo Markdown (`escudeiro`, `arauto`, `01-nascimento-infancia`, `genesis`...).

## Como gerar

Requisito: [Typst](https://typst.app) instalado (`brew install typst`) e Python 3.

```bash
python3 scripts/build_pdf.py estudo estudos/cgo/escudeiro.md   # -> saida/estudos/cgo_escudeiro.pdf
python3 scripts/build_pdf.py prova  provas/cgo/escudeiro/001.md # -> saida/provas/cgo_escudeiro-prova_001.pdf e saida/gabaritos/cgo_escudeiro-gabarito_001.pdf
```

Também dá para pedir ao Claude com as skills `gerar-estudo` e `gerar-prova`.

## Formato do material

**Estudo** (`estudos/<sigla>/<unidade>.md`): apenas **perguntas e respostas curtas**, para decorar, agrupadas em seções.

```
---
titulo: Manual do Embaixador Escudeiro
disciplina: Conhecimentos Gerais da Organização
obra: Manual do Escudeiro
fonte: docs/cgo/...
status: rascunho
---

## Tarefa 1: Os postos

P: Quais são os postos da organização, em ordem?
R: Escudeiro, Arauto, Sênior e Emérito.
F: Manual do Escudeiro, Tarefa 1, p. 8
```

- `F:` é a **referência** (obra, capítulo/tarefa, página; ou livro bíblico, capítulo e versículo). É obrigatória.
- No PDF do estudo cada seção tem uma cor fixa e um quadradinho; a referência aparece ao lado da pergunta.

**Prova** (`provas/<sigla>/<unidade>/NNN.md`): **sempre 20 questões** de múltipla escolha com **4 alternativas (A, B, C e D)**.

```
[ME] Enunciado?
a) ...
b) ...
c) ...
d) ...
R: b
F: (a mesma referência do estudo)
```

- A prova tem **2 páginas** (frente e verso): questões em 2 colunas e o cartão-resposta de bolinhas, com o mesmo cabeçalho.
- O **gabarito** é o espelho da prova, com a alternativa correta marcada e a referência ao lado do enunciado.
- O script **recusa** a prova se alguma referência não existir no estudo indicado em `estudo:`.

## Fluxo de qualidade

1. O Claude escreve o estudo com `status: rascunho`.
2. Uma pessoa revisa fatos e referências contra a fonte e troca para `status: revisado`.
3. Provas e gabaritos nascem do estudo.
4. Os PDFs são descartáveis: para corrigir, edite o `.md` e gere de novo.

Verificadores:

```bash
python3 scripts/biblia_fonte.py estudos/bj/*.md estudos/cgb/*.md   # toda referência bíblica existe na fonte?
```

`scripts/livro_fonte.py` confere fatos de livros com marcadores de página (usado no BWAH).

## Estratégia do CGB

O material principal é a **"Visão Geral da Bíblia"** (`estudos/cgb/01` a `04`: estrutura, Antigo Testamento, Novo Testamento e grandes acontecimentos). Os panoramas por livro (modelo: `estudos/cgb/genesis.md`) são gerados **sob demanda**.

## Divergências conhecidas entre fontes

| Fato | Livro "Sempre Embaixador" (BWAH) | Manual do Arauto (CGO) |
|---|---|---|
| Nascimento de Hatton | 14/02/1921 | 10/02/1921 |
| Nomeação como missionário | 14/10/1947 | 01/10/1947 |

Cada estudo segue a sua própria fonte; a decisão sobre qual data vale nas provas está pendente.
