#!/usr/bin/env python3
"""Converte Markdown de estudo/prova em PDF usando Typst.

Uso:
    python3 scripts/build_pdf.py estudo estudos/cgo/escudeiro.md
    python3 scripts/build_pdf.py prova  provas/cgo/escudeiro/001.md

Saída (três pastas; o prefixo é a sigla da disciplina):
    estudo   -> saida/estudos/cgo_escudeiro.pdf              (canônico: nome fixo, sobrescrito ao regerar)
    prova    -> saida/provas/cgo_escudeiro_001.pdf
    gabarito -> saida/gabaritos/cgo_escudeiro-gabarito_001.pdf (mesmo número da prova)
Sigla, unidade e número vêm do CAMINHO do arquivo-fonte, sem contador e sem olhar a pasta saida/:
    estudos/<sigla>/<unidade>.md         -> estudo
    provas/<sigla>/<unidade>/<NNN>.md    -> prova NNN (o número é o nome do arquivo; regerar a mesma
                                            prova sobrescreve o mesmo PDF; prova nova = próximo número)
A data de geração aparece dentro do PDF; na prova também o número (subtítulo e rodapé).

Estudo: 2 colunas, fonte fixa (FONTE_ESTUDO), quantas páginas forem necessárias.
Prova e gabarito: impressão frente e verso, sempre 2 páginas em 2 colunas; o script escolhe a
maior fonte (de 10pt até FONTE_MIN) com que cabe. Sempre 20 questões; página 1 = questões,
página 2 = cartão-resposta.
A prova é validada contra o estudo: o campo 'estudo:' deve existir e cada F: da prova deve estar
no estudo. O estudo tem 'status: rascunho' ou 'status: revisado' (aviso se não estiver revisado).
Referência (F:): aparece no enunciado de cada pergunta do estudo e do gabarito; nunca na prova.

Formatos aceitos: ver .claude/skills/gerar-estudo e gerar-prova.
"""
import re
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "saida"

EMBAIXADA = "Embaixada Pastor José Saraiva"
IGREJA = "Primeira Igreja Batista em Potira I - Caucaia-CE"

QUESTOES_PROVA = 20
MAX_EM_COMUM = 5  # máximo de questões que duas provas da mesma unidade podem ter em comum
MAX_PAGINAS = 2
FONTE_ESTUDO = 11.0
# Uma cor fixa por seção (na ordem, repetindo se houver mais seções que cores). Cores escuras,
# distintas entre si e legíveis no papel; o título da seção usa a mesma cor das respostas.
CORES_SECAO = ["#1f5fbf", "#c0392b", "#1b7a3a", "#b9770e", "#7d3c98",
               "#0e7c86", "#a04000", "#c2185b", "#566573", "#6b8e23"]
FONTE_MAX = 10.0
FONTE_MIN = 6.5
COR_MARCA = 'rgb("#b00020")'
COR_TITULO = 'rgb("#1f3a6e")'


# ---------------------------------------------------------------- utilidades

def esc(texto):
    """Escapa caracteres especiais do Typst em modo markup."""
    return re.sub(r'([\\#$*_@<>`~\[\]])', r'\\\1', texto)


def marca(texto):
    """Texto destacado, usado no gabarito."""
    return f'#text(weight: "bold", fill: {COR_MARCA})[{esc(texto)}]'


def ler_md(caminho):
    """Retorna (metadados, linhas do corpo)."""
    texto = Path(caminho).read_text(encoding="utf-8")
    meta = {}
    m = re.match(r'---\n(.*?)\n---\n', texto, re.S)
    if m:
        for linha in m.group(1).splitlines():
            if ":" in linha:
                k, v = linha.split(":", 1)
                meta[k.strip()] = v.strip()
        texto = texto[m.end():]
    return meta, texto.splitlines()


def titulo_bloco(meta, subtitulo):
    """Cabeçalho visual (embaixada, igreja, título, subtítulo); repetido no cartão-resposta."""
    rotulo = meta.get('rotulo', '')
    disciplina = esc(meta.get('disciplina', ''))
    return f'''#align(center)[
  #text(size: 7.5pt, fill: gray)[{esc(EMBAIXADA)} · {esc(IGREJA)}] \\
  #text(size: 14pt, weight: "bold")[{esc(meta.get('titulo', ''))}] \\
  #text(size: 9pt, fill: gray)[{disciplina} · {subtitulo} {rotulo}]
]
#v(0.25cm)
'''


def campos_prova():
    """Linha de preenchimento (nome, data, tempo, nota), igual na prova e no cartão-resposta."""
    return ('Nome: #box(width: 6.5cm, stroke: (bottom: 0.6pt))[] #h(1fr) '
            'Data: #box(width: 2.3cm, stroke: (bottom: 0.6pt))[] #h(1fr) '
            'Tempo: #box(width: 2.3cm, stroke: (bottom: 0.6pt))[] #h(1fr) '
            'Nota: #box(width: 1.8cm, stroke: (bottom: 0.6pt))[]\n#v(0.2cm)\n')


def cabecalho(meta, subtitulo, tam):
    """Preâmbulo Typst: página A4 com margens enxutas e cabeçalho compacto."""
    rotulo = meta.get('rotulo', '')
    disciplina = esc(meta.get('disciplina', ''))
    return f'''#set document(title: "{meta.get('titulo', '')} — {subtitulo}")
#set page(paper: "a4", margin: (x: 1.3cm, top: 1.2cm, bottom: 1.4cm),
  footer: context [#set text(size: 7pt, fill: gray)
    {esc(EMBAIXADA)} — {disciplina} · {subtitulo} {rotulo} #h(1fr) #counter(page).display()])
#set text(lang: "pt", size: {tam}pt)
#set par(justify: false, leading: 0.5em, spacing: 0.5em)
{titulo_bloco(meta, subtitulo)}'''


def ref(fonte, tam, id_estudo=""):
    """Referência em cinza, menor, para ir ao lado do enunciado (com o ID da pergunta no estudo)."""
    if id_estudo:
        fonte += f" · Estudo #{int(id_estudo) if id_estudo.isdigit() else id_estudo}"
    return f'#text(size: {tam - 1.5}pt, weight: "regular", fill: gray)[‹{esc(fonte)}›]'


def ref_curta(fonte, titulo_secao, obra):
    """No estudo, tira da referência o que já está na obra (front matter 'obra:') e no título
    da seção (ex.: 'Tarefa 2'), deixando só o que falta (ex.: 'p. 11'); se nada falta, devolve ''."""
    partes = [x.strip() for x in fonte.split(",")]
    sobra = [x for x in partes
             if x.lower() != obra.lower() and not titulo_secao.lower().startswith(x.lower())]
    return ", ".join(sobra)


def fim_com_paginas():
    """Metadado invisível que permite ao script saber quantas páginas o PDF tem."""
    return '#context [#metadata(counter(page).final().first()) <paginas>]'


# --------------------------------------------------------------------- estudo

def parse_estudo(linhas):
    """Lista de seções: (titulo, [[pergunta, resposta, fonte, id], ...])."""
    secoes, atual, alvo = [], None, None
    for linha in linhas:
        if linha.startswith("#"):
            atual = (linha.lstrip("#").strip(), [])
            secoes.append(atual)
            alvo = None
        elif linha.startswith("P:"):
            if atual is None:
                atual = ("", [])
                secoes.append(atual)
            atual[1].append([linha[2:].strip(), "", "", ""])
            alvo = 0
        elif linha.startswith("R:") and atual and atual[1]:
            atual[1][-1][1] = linha[2:].strip()
            alvo = 1
        elif linha.startswith("F:") and atual and atual[1]:
            atual[1][-1][2] = linha[2:].strip()
            alvo = 2
        elif linha.startswith("I:") and atual and atual[1]:
            atual[1][-1][3] = linha[2:].strip()
            alvo = None
        elif linha.strip() and alvo is not None:  # continuação
            atual[1][-1][alvo] += " " + linha.strip()
        else:
            alvo = None
    sem_fonte = [n for n, (_, _, f, _i) in enumerate((qa for _, qas in secoes for qa in qas), 1) if not f]
    if sem_fonte:
        sys.exit("Toda pergunta precisa de referência ('F:' com manual/capítulo/página ou "
                 f"livro/capítulo/versículo). Sem referência: {sem_fonte[:15]}")
    return secoes


def typ_estudo(meta, secoes, tam):
    out = [cabecalho(meta, "Estudo", tam), '#set par(leading: 0.7em)',
           '#show: columns.with(2, gutter: 0.6cm)\n']
    for i, (titulo, qas) in enumerate(secoes):
        cor = f'rgb("{CORES_SECAO[i % len(CORES_SECAO)]}")'
        if titulo:
            out.append(f'#block(breakable: false, sticky: true, above: 0.8em, below: 0.4em)'
                       f'[#box(width: 0.6em, height: 0.6em, fill: {cor}, baseline: 0.5pt) #h(0.3em)'
                       f'#text(size: {tam + 1.5}pt, weight: "bold", fill: {cor})[{esc(titulo)}]'
                       f'#v(-0.35em)#line(length: 100%, stroke: 0.5pt + {cor})]\n')
        for p, r, f, n in qas:  # n = ID estável da pergunta (vira a numeração do estudo)
            n = int(n) if n.isdigit() else n
            # espaço não separável entre rótulo e número ("p. 12", "Mateus 3.4") evita quebra no meio
            fonte = re.sub(r'(\S) (\d)', '\\1\u00a0\\2', esc(ref_curta(f, titulo, meta.get("obra", ""))))
            out.append(f'#block(breakable: false, below: 1.1em)[\n'
                       f'*{n}. {esc(p)}{f" ({fonte})" if fonte else ""}* \\\n'
                       f'#text(fill: {cor})[*R:* {esc(r)}]\n]\n')
    out.append(fim_com_paginas())
    return "\n".join(out)


def contar_perguntas(secoes):
    return sum(len(qas) for _, qas in secoes)


# ---------------------------------------------------------------------- prova

def parse_prova(linhas):
    """Lista de questões de múltipla escolha: dict(enunciado, opcoes, resposta)."""
    questoes, q = [], None
    for linha in linhas:
        s = linha.strip()
        m = re.match(r'\[ME\]\s*(.*)', s)
        if m:
            q = {"enunciado": m.group(1), "opcoes": [], "resposta": "", "fonte": "", "id": ""}
            questoes.append(q)
        elif re.match(r'\[[A-Z]{2}\]', s):
            sys.exit(f"Tipo de questão não suportado (a prova é só de marcar, use [ME]): {s[:40]}")
        elif q is None or not s:
            continue
        elif s.startswith("R:"):
            q["resposta"] = s[2:].strip()
        elif s.startswith("F:"):
            q["fonte"] = s[2:].strip()
        elif s.startswith("E:"):
            q["id"] = s[2:].strip()
        elif re.match(r'[a-d]\)', s):
            q["opcoes"].append(s)
        else:
            q["enunciado"] += " " + s
    if len(questoes) != QUESTOES_PROVA:
        sys.exit(f"A prova deve ter exatamente {QUESTOES_PROVA} questões "
                 f"(encontradas {len(questoes)}).")
    for i, q in enumerate(questoes, 1):
        letras = "".join(o[0] for o in q["opcoes"])
        if letras != "abcd" or q["resposta"][:1].lower() not in tuple("abcd"):
            sys.exit(f"Questão {i}: precisa de alternativas a) b) c) d) e 'R:' com a letra correta.")
        if not q["fonte"]:
            sys.exit(f"Questão {i}: falta a referência ('F:', copiada do estudo).")
        if not q["id"]:
            sys.exit(f"Questão {i}: falta o 'E:' (ID da pergunta do estudo que originou a questão).")
    return questoes


def bolinha(letra, marcada):
    cheia = ', fill: black' if marcada else ''
    cor = ', fill: white' if marcada else ''
    return (f'#box(baseline: 30%, circle(radius: 0.29cm, inset: 0pt, stroke: 0.7pt{cheia}, '
            f'align(center + horizon, text(size: 8pt{cor})[{letra}])))')


def cartao_resposta(meta, questoes, gabarito, subtitulo):
    """Última página: mesmo cabeçalho da prova + cartão-resposta de bolinhas (colunas A–D)."""
    linhas = []
    for i, q in enumerate(questoes, 1):
        certa = q["resposta"][:1].upper() if gabarito else None
        bol = " #h(0.15cm) ".join(bolinha(l, l == certa) for l in "ABCD")
        linhas.append(f'#grid(columns: (0.9cm, auto), align: horizon, [*{i}.*], [{bol}])')
    por_coluna = max(1, -(-len(linhas) // 3))
    colunas = ["#stack(spacing: 0.55cm, " + ", ".join(
        f'[{l}]' for l in linhas[k:k + por_coluna]) + ")"
        for k in range(0, len(linhas), por_coluna)]
    out = ['#pagebreak()',
           titulo_bloco(meta, subtitulo),
           campos_prova(),
           '#v(0.3cm)',
           '#set text(size: 10.5pt)',
           '#align(center)[#text(size: 13pt, weight: "bold")[Cartão-resposta]]',
           '#align(center)[#text(size: 9pt, fill: gray)[Preencha completamente a bolinha da '
           'alternativa escolhida. Marque apenas uma alternativa por questão.]]',
           '#v(0.5cm)',
           '#grid(columns: (1fr, 1fr, 1fr), column-gutter: 0.6cm, ' +
           ", ".join(f'[{c}]' for c in colunas) + ')']
    return "\n".join(out)


def typ_prova(meta, questoes, gabarito, tam):
    """Prova; com gabarito=True é o espelho exato dela com as respostas marcadas."""
    out = [cabecalho(meta, "Gabarito" if gabarito else "Prova", tam)]
    out.append(campos_prova())
    blocos = []
    for i, q in enumerate(questoes, 1):
        certa = q["resposta"][:1].lower() if gabarito else None
        opcoes = []
        for o in q["opcoes"]:
            if o[0] == certa:
                opcoes.append(f'#h(1em)#highlight(fill: rgb("#fde3e6"))[{marca(o)}] \\')
            else:
                opcoes.append(f'#h(1em)#[{esc(o)}] \\')
        fonte = f' {ref(q["fonte"], tam, q["id"])}' if gabarito else ''
        bloco = f'*{i}. {esc(q["enunciado"])}*{fonte} \\\n' + "\n".join(opcoes) + "\n"
        blocos.append(f'#block(breakable: false, below: 0.7em)[\n{bloco}]\n')
    out.append('#columns(2, gutter: 0.7cm)[\n' + "\n".join(blocos) + ']\n')
    out.append(cartao_resposta(meta, questoes, gabarito, "Gabarito" if gabarito else "Prova"))
    out.append(fim_com_paginas())
    return "\n".join(out)


# ------------------------------------------------------------------ compilação

def ids_do_estudo(caminho):
    """Dict id -> (pergunta, fonte) das perguntas de um estudo."""
    _, linhas = ler_md(caminho)
    return {i: (p, f) for _, qas in parse_estudo(linhas) for p, r, f, i in qas if i}


def verificar_prova(meta, questoes, entrada):
    """A prova nasce do estudo: cada E: deve ser uma pergunta do estudo (com o mesmo F:), sem
    repetir pergunta dentro da prova, e a prova não pode ter mais de MAX_EM_COMUM questões em
    comum com outra prova da mesma unidade."""
    rel = meta.get("estudo")
    if not rel:
        sys.exit("A prova precisa do campo 'estudo:' no cabeçalho (caminho do estudo de origem).")
    caminho = RAIZ / rel
    if not caminho.exists():
        sys.exit(f"Estudo de origem não encontrado: {rel}")
    ids = ids_do_estudo(caminho)
    if not ids:
        sys.exit(f"O estudo {rel} ainda não tem IDs (linha 'I:'). Rode: python3 scripts/ids.py {rel}")
    erros = []
    for i, q in enumerate(questoes, 1):
        if q["id"] not in ids:
            erros.append(f"  questão {i}: E: {q['id']} não existe no estudo")
        elif ids[q["id"]][1] != q["fonte"]:
            erros.append(f"  questão {i}: F: difere do estudo (estudo: {ids[q['id']][1]!r})")
    repetidos = sorted({q["id"] for q in questoes if [x["id"] for x in questoes].count(q["id"]) > 1})
    if repetidos:
        erros.append(f"  E: repetido dentro da prova: {', '.join(repetidos)}")
    if erros:
        sys.exit(f"Problemas na prova (referência ao estudo {rel}):\n" + "\n".join(erros))
    meus = {q["id"] for q in questoes}
    for outra in sorted(entrada.parent.glob("*.md")):
        if outra.resolve() == entrada.resolve():
            continue
        comum = meus & set(re.findall(r'^E: (.*)$', outra.read_text(encoding="utf-8"), re.M))
        if len(comum) > MAX_EM_COMUM:
            sys.exit(f"Esta prova tem {len(comum)} questões em comum com {outra.stem} "
                     f"(máximo {MAX_EM_COMUM}): {', '.join(sorted(comum))}")
    estudo_meta, _ = ler_md(caminho)
    if estudo_meta.get("status") != "revisado":
        print(f"⚠ O estudo {rel} ainda não está marcado como revisado (status: {estudo_meta.get('status', 'sem status')}).")


def _typ_temp(typ):
    f = tempfile.NamedTemporaryFile("w", suffix=".typ", delete=False, encoding="utf-8")
    f.write(typ)
    f.close()
    return Path(f.name)


def contar_paginas(typ):
    tmp = _typ_temp(typ)
    try:
        r = subprocess.run(["typst", "query", str(tmp), "<paginas>", "--field", "value", "--one"],
                           capture_output=True, text=True, check=True)
        return int(r.stdout.strip())
    finally:
        tmp.unlink(missing_ok=True)


def escolher_fonte(geradores):
    """Maior fonte (10pt até FONTE_MIN, passo 0,25) com que todos os geradores cabem."""
    tam = FONTE_MAX
    while tam >= FONTE_MIN:
        if all(contar_paginas(g(tam)) <= MAX_PAGINAS for g in geradores):
            return tam
        tam -= 0.25
    sys.exit(f"Não cabe em {MAX_PAGINAS} páginas nem com fonte {FONTE_MIN}pt. "
             "Reduza o conteúdo ou divida a unidade em partes (ex.: escudeiro-1, escudeiro-2).")


def compilar(typ, destino):
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = _typ_temp(typ)
    try:
        subprocess.run(["typst", "compile", str(tmp), str(destino)], check=True)
    finally:
        tmp.unlink(missing_ok=True)
    print(f"✔ {destino.relative_to(RAIZ)}")


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("estudo", "prova"):
        sys.exit(__doc__)
    modo, entrada = sys.argv[1], Path(sys.argv[2]).resolve()
    meta, linhas = ler_md(entrada)
    if modo == "estudo":
        nome, disc = entrada.stem, entrada.parent.name          # estudos/<sigla>/<unidade>.md
    else:
        if not re.fullmatch(r'\d{3}', entrada.stem):
            sys.exit("O arquivo da prova deve se chamar NNN.md (ex.: provas/cgo/arauto/002.md).")
        num = entrada.stem                                      # provas/<sigla>/<unidade>/NNN.md
        nome, disc = entrada.parent.name, entrada.parent.parent.name
    hoje = date.today().strftime('%d/%m/%Y')
    meta["rotulo"] = hoje if modo == "estudo" else f"nº {num} · {hoje}"
    if modo == "estudo":
        if meta.get("status") != "revisado":
            print(f"⚠ Estudo ainda não revisado (status: {meta.get('status', 'sem status')}).")
        secoes = parse_estudo(linhas)
        sem_id = sum(1 for _, qas in secoes for *_, i in qas if not i)
        if sem_id:
            print(f"⚠ {sem_id} pergunta(s) sem ID (linha 'I:'). Rode: python3 scripts/ids.py {entrada.relative_to(RAIZ)}")
        typ = typ_estudo(meta, secoes, FONTE_ESTUDO)
        compilar(typ, SAIDA / "estudos" / f"{disc}_{nome}.pdf")
        print(f"  {contar_perguntas(secoes)} perguntas · {contar_paginas(typ)} páginas · "
              f"fonte {FONTE_ESTUDO}pt")
    else:
        questoes = parse_prova(linhas)
        verificar_prova(meta, questoes, entrada)
        prova = lambda t: typ_prova(meta, questoes, False, t)
        gabarito = lambda t: typ_prova(meta, questoes, True, t)
        tam = escolher_fonte([prova, gabarito])  # mesma fonte nos dois: gabarito = espelho
        compilar(prova(tam), SAIDA / "provas" / f"{disc}_{nome}_{num}.pdf")
        compilar(gabarito(tam), SAIDA / "gabaritos" / f"{disc}_{nome}-gabarito_{num}.pdf")
        print(f"  {len(questoes)} questões · fonte {tam}pt")


if __name__ == "__main__":
    main()
