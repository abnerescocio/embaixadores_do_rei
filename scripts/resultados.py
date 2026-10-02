#!/usr/bin/env python3
"""Corrige os cartões-resposta registrados e mostra notas e acerto por pergunta.

Uso:
    python3 scripts/resultados.py provas/cgb/01-estrutura-da-biblia/001.md

Lê resultados/<sigla>/<unidade>/<NNN>.csv, com uma linha por aluno:
    aluno,foto,respostas        (respostas = 20 letras, na ordem; '-' se em branco)
    Fulano de Tal,fulano.jpg,CBDAAACBCBCBABCBDBDB

Compara com o gabarito da prova e mostra a nota de cada aluno e, por pergunta (pelo ID do estudo),
quantos acertaram. Abaixo de MIN_RESPOSTAS respondentes, a taxa é mostrada como "poucos dados".
"""
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_pdf import RAIZ, ler_md, parse_prova, QUESTOES_PROVA  # noqa: E402

MIN_RESPOSTAS = 15


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
    alunos = list(csv.DictReader(arq.open(encoding="utf-8")))
    acertos = [0] * QUESTOES_PROVA
    print(f"{rel}: {len(alunos)} aluno(s)\n")
    for a in alunos:
        resp = re.sub(r'\s', '', a["respostas"]).upper()
        if len(resp) != QUESTOES_PROVA or set(resp) - set("ABCD-"):
            sys.exit(f"{a['aluno']}: 'respostas' deve ter {QUESTOES_PROVA} letras A-D (ou '-'): {resp!r}")
        nota = sum(r == c for r, c in zip(resp, certas))
        for i, (r, c) in enumerate(zip(resp, certas)):
            acertos[i] += r == c
        erradas = ", ".join(str(i) for i, (r, c) in enumerate(zip(resp, certas), 1) if r != c)
        print(f"  {a['aluno']}: {nota}/{QUESTOES_PROVA}  (erradas: {erradas or '—'})")
    n = len(alunos)
    print(f"\nPor pergunta (E = ID no estudo){'' if n >= MIN_RESPOSTAS else f' — poucos dados (<{MIN_RESPOSTAS})'}:")
    for i, q in enumerate(questoes):
        taxa = f"{acertos[i]}/{n}" + (f" ({100 * acertos[i] // n}%)" if n >= MIN_RESPOSTAS else "")
        print(f"  {i + 1:>2}. E {q['id']}  {taxa:<12} {q['enunciado'][:60]}")


if __name__ == "__main__":
    main()
