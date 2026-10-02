#!/usr/bin/env python3
"""Relatório de cobertura: quais perguntas do estudo já caíram em provas.

Uso:
    python3 scripts/cobertura.py estudos/cgo/arauto.md          # resumo + por seção
    python3 scripts/cobertura.py estudos/cgo/arauto.md --livres # lista as perguntas nunca usadas
    python3 scripts/cobertura.py estudos/cgo/arauto.md --usos   # lista pergunta a pergunta com nº de usos

Lê as provas em provas/<sigla>/<unidade>/NNN.md (linhas 'E:') e cruza com os IDs 'I:' do estudo.
Ao montar uma prova nova, priorize as perguntas com menos usos e distribua pelas seções.
"""
import re
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_pdf import RAIZ, ler_md, parse_estudo, MAX_EM_COMUM  # noqa: E402


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    estudo = Path(args[0]).resolve()
    rel = estudo.relative_to(RAIZ)
    pasta = RAIZ / "provas" / rel.parent.name / rel.stem
    _, linhas = ler_md(estudo)
    secoes = parse_estudo(linhas)
    provas = {p.stem: set(re.findall(r'^E: (.*)$', p.read_text(encoding="utf-8"), re.M))
              for p in sorted(pasta.glob("*.md"))} if pasta.exists() else {}
    usos = {i: sum(i in ids for ids in provas.values()) for _, qas in secoes for *_, i in qas if i}
    total = len(usos)
    nunca = sum(1 for n in usos.values() if n == 0)
    uma = sum(1 for n in usos.values() if n == 1)
    varias = sum(1 for n in usos.values() if n > 1)
    print(f"{rel}: {total} perguntas, {len(provas)} prova(s)")
    print(f"  nunca usadas: {nunca}  |  usadas 1 vez: {uma}  |  usadas 2+ vezes: {varias}")
    if len(provas) > 1:
        print("\nQuestões em comum entre provas (máx. %d):" % MAX_EM_COMUM)
        for a, b in combinations(provas, 2):
            n = len(provas[a] & provas[b])
            print(f"  {a} × {b}: {n}" + ("  ⚠ acima do limite" if n > MAX_EM_COMUM else ""))
    print("\nPor seção (nunca usadas / total):")
    for titulo, qas in secoes:
        ids = [i for *_, i in qas if i]
        livres = sum(1 for i in ids if usos[i] == 0)
        print(f"  {livres:>3} / {len(ids):<3} {titulo}")
    if "--livres" in sys.argv or "--usos" in sys.argv:
        print()
        for titulo, qas in secoes:
            print(f"## {titulo}")
            for p, r, f, i in qas:
                if "--usos" in sys.argv or usos[i] == 0:
                    print(f"  {i} [{usos[i]}x] {p}")


if __name__ == "__main__":
    main()
