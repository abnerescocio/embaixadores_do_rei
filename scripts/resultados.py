#!/usr/bin/env python3
"""Corrige os cartões-resposta registrados e mostra notas e acerto por pergunta.

Uso:
    python3 scripts/resultados.py provas/cgb/01-estrutura-da-biblia/001.md

Lê resultados/<sigla>/<unidade>/<NNN>.csv, com uma linha por aluno:
    aluno,foto,respostas,tentativa   (tentativa 1 por padrão; 2, 3... se o aluno refez a prova; aluno = ID de resultados/alunos.csv; respostas = 20 letras, '-' se em branco)
    A01,A01.jpg,CBDAAACBCBCBABCBDBDB,1

Compara com o gabarito da prova e mostra a nota de cada aluno e, por pergunta (pelo ID do estudo),
quantos acertaram (só a 1ª tentativa de cada aluno entra no acerto por pergunta). Abaixo de MIN_RESPOSTAS respondentes, a taxa é mostrada como "poucos dados".
"""
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_pdf import RAIZ, ler_md, parse_prova, QUESTOES_PROVA  # noqa: E402

MIN_RESPOSTAS = 15


def nomes_alunos():
    """id -> nome, de resultados/alunos.csv."""
    arq = RAIZ / "resultados" / "alunos.csv"
    return {a["id"]: a["nome"] for a in csv.DictReader(arq.open(encoding="utf-8"))} if arq.exists() else {}


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    prova = Path(sys.argv[1]).resolve()
    rel = prova.relative_to(RAIZ)
    sigla, unidade, num = rel.parts[1], rel.parts[2], prova.stem
    arq = RAIZ / "resultados" / sigla / unidade / f"{num}.csv"
    if not arq.exists():
        sys.exit(f"Sem resultados em {arq.relative_to(RAIZ)}")
    _, linhas = ler_md(prova)
    questoes = parse_prova(linhas)
    certas = [q["resposta"][:1].upper() for q in questoes]
    nomes = nomes_alunos()
    alunos = list(csv.DictReader(arq.open(encoding="utf-8")))
    acertos = [0] * QUESTOES_PROVA
    n = len({a["aluno"] for a in alunos})
    print(f"{rel}: {n} aluno(s), {len(alunos)} cartão(ões)\n")
    for a in alunos:
        resp = re.sub(r'\s', '', a["respostas"]).upper()
        if len(resp) != QUESTOES_PROVA or set(resp) - set("ABCD-"):
            sys.exit(f"{a['aluno']}: 'respostas' deve ter {QUESTOES_PROVA} letras A-D (ou '-'): {resp!r}")
        nota = sum(r == c for r, c in zip(resp, certas))
        tent = int(a.get("tentativa") or 1)
        if tent == 1:
            for i, (r, c) in enumerate(zip(resp, certas)):
                acertos[i] += r == c
        erradas = ", ".join(str(i) for i, (r, c) in enumerate(zip(resp, certas), 1) if r != c)
        print(f"  {a['aluno']} {nomes.get(a['aluno'], '?')}{f' (tentativa {tent})' if tent > 1 else ''}: {nota}/{QUESTOES_PROVA}  (erradas: {erradas or '—'})")
    print(f"\nPor pergunta (E = ID no estudo){'' if n >= MIN_RESPOSTAS else f' — poucos dados (<{MIN_RESPOSTAS})'}:")
    for i, q in enumerate(questoes):
        taxa = f"{acertos[i]}/{n}" + (f" ({100 * acertos[i] // n}%)" if n >= MIN_RESPOSTAS else "")
        print(f"  {i + 1:>2}. E {q['id']}  {taxa:<12} {q['enunciado'][:60]}")


if __name__ == "__main__":
    main()
