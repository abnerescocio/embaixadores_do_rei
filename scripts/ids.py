#!/usr/bin/env python3
"""Atribui um ID estável (linha 'I: NNN') a cada pergunta de um estudo que ainda não tem.

Uso:
    python3 scripts/ids.py estudos/cgo/arauto.md [outros.md ...]

O ID é sequencial dentro do estudo (continua do maior já existente) e nunca muda depois de
atribuído, mesmo que o texto da pergunta seja editado. As provas citam esse ID na linha 'E:'.
"""
import re
import sys
from pathlib import Path


def atribuir(caminho):
    linhas = Path(caminho).read_text(encoding="utf-8").split("\n")
    maior = max((int(m.group(1)) for l in linhas if (m := re.match(r'I: (\d+)\s*$', l))), default=0)
    saida, novos = [], 0
    for i, linha in enumerate(linhas):
        saida.append(linha)
        if linha.startswith("F:"):
            seguinte = linhas[i + 1] if i + 1 < len(linhas) else ""
            if not seguinte.startswith("I:"):
                maior += 1
                novos += 1
                saida.append(f"I: {maior:03d}")
    Path(caminho).write_text("\n".join(saida), encoding="utf-8")
    return novos, maior


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for arq in sys.argv[1:]:
        novos, total = atribuir(arq)
        print(f"{arq}: {novos} ID(s) novo(s); último ID {total:03d}")
