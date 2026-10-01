"""Texto de um livro com marcadores de página (docs/...) e verificação de fatos por página.

Marcadores aceitos no texto: <!-- página 11 -->, <!-- página 16 e 17 -->, <!-- página 25 a 27 -->.
Uso como biblioteca:
    livro = Livro("docs/bwah/Alvin Hatton - Sempre Embaixador - Texto Plano.md")
    livro.confere("14-15", "Powell")   # True se 'Powell' aparece no texto das páginas 14 a 15
Palavras-chave: 'a|b' = todas; 'a/b' = qualquer; sem acento/maiúscula não importa.
"""
import re
import unicodedata
from pathlib import Path


def norm(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn')


def _paginas(rotulo):
    nums = [int(n) for n in re.findall(r'\d+', rotulo)]
    if re.search(r'\ba\b', rotulo, re.I) and len(nums) == 2:
        return list(range(nums[0], nums[1] + 1))
    return nums


class Livro:
    def __init__(self, caminho):
        raiz = Path(__file__).resolve().parent.parent
        texto = (raiz / caminho).read_text(encoding='utf-8')
        self.blocos = []  # (lista de páginas, texto)
        partes = re.split(r'<!-- página ([^>]*?) -->', texto)
        for rotulo, corpo in zip(partes[1::2], partes[2::2]):
            self.blocos.append((_paginas(rotulo), corpo))

    def texto_paginas(self, spec):
        """spec: '14', '14-15', '14,16'."""
        pedidas = set()
        for item in spec.split(','):
            item = item.strip()
            if '-' in item:
                a, b = item.split('-')
                pedidas.update(range(int(a), int(b) + 1))
            elif item:
                pedidas.add(int(item))
        return ' '.join(t for ps, t in self.blocos if pedidas & set(ps))

    def confere(self, spec, kw):
        t = norm(self.texto_paginas(spec))
        return bool(t) and all(any(norm(a) in t for a in p.split('/')) for p in kw.split('|'))
