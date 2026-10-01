"""Texto bíblico da fonte (docs/cgb) e verificação de referências.

Uso:
    python3 scripts/biblia_fonte.py estudos/bj/01-nascimento-infancia.md [...]
Confere se cada referência bíblica (F:) dos estudos existe na fonte (livro, capítulo, versículo).
Referências que não são bíblicas (manuais, 'Estrutura da Bíblia', etc.) são ignoradas.
Como biblioteca: texto(ref) devolve o texto; verificar(refs, palavras_chave) confere palavras no texto.
"""
import re, glob, unicodedata
from pathlib import Path
R=str(Path(__file__).resolve().parent.parent/'docs'/'cgb')+'/'
FONTE={ "Deuteronômio":"Deuteronomio","Jeremias":"Jeremías","1 Samuel":"1Samuel","1 Tessalonicenses":"1 Tessalonisences",
        "2 Tessalonicenses":"2 Tessalonisences","Filemom":"Filemon","Cantares":"Cantares de Salomão","Atos":"Atos dos Apóstolos"}
data={}; capitulos={}
for f in sorted(glob.glob(R+'*.md')):
    livro=cap=None
    for l in open(f,encoding='utf-8').read().split('\n'):
        m=re.match(r'# (.+?) Cap (\d+)',l)
        if m:
            livro,cap=m.group(1),int(m.group(2)); capitulos[livro]=max(capitulos.get(livro,0),cap); continue
        m=re.match(r'\*\*(\d+)\*\*\s*(.*)',l)
        if m and livro: data[(livro,cap,int(m.group(1)))]=m.group(2).strip()
def norm(s): return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn')
def nome_fonte(n): return FONTE.get(n,n)
def n_capitulos(livro): return capitulos[nome_fonte(livro)]
def texto(ref):
    """ref: 'Livro c.v1-v2' | 'Livro c.v' | 'Livro c1-c2' | 'Livro c'. Devolve o texto (ou None se ref inválida)."""
    m=re.match(r'(.+) (\d+)(?:\.(\d+)(?:-(\d+))?|-(\d+))?$',ref.strip())
    if not m: return None
    livro,c,v1,v2,c2=m.groups(); livro=nome_fonte(livro); c=int(c)
    if c2: caps=[(k,1,999) for k in range(c,int(c2)+1)]
    elif v1: caps=[(c,int(v1),int(v2 or v1))]
    else: caps=[(c,1,999)]
    out=[]
    for k,a,b in caps:
        out+= [t for (lv,cc,vv),t in data.items() if lv==livro and cc==k and a<=vv<=b]
    return ' '.join(out) if out else None
def verificar(refs, kw):
    """True se todas as palavras-chave (separadas por '|', alternativas por '/') aparecem no texto das refs."""
    if not kw: return True
    t=norm(' '.join(texto(r) or '' for r in refs.split('; ')))
    return all(any(norm(a) in t for a in p.split('/')) for p in kw.split('|'))


LIVROS_BJ={"Mateus","Marcos","Lucas","João"}  # já constam nos arquivos de docs/cgb

def referencias_invalidas(caminho):
    """Lista (ref, motivo) das referências bíblicas inexistentes em um estudo."""
    ruins=[]
    for f in re.findall(r'^F: (.*)$', Path(caminho).read_text(encoding='utf-8'), re.M):
        for parte in f.split('; '):
            m=re.match(r'(.+?) (\d+(?:[.\-]\d+)*(?:, ?\d+(?:[.\-]\d+)*)*)$', parte.strip())
            if not m or nome_fonte(m.group(1)) not in capitulos:
                continue  # não é referência bíblica
            livro, resto = m.group(1), m.group(2)
            cap_atual=None
            for item in [x.strip() for x in resto.split(',')]:
                ref=f"{livro} {item}"
                if '.' in item: cap_atual=item.split('.')[0]
                elif cap_atual and '-' not in item or (cap_atual and re.fullmatch(r'\d+-\d+', item) and f"{livro} {cap_atual}.{item}" and texto(f"{livro} {cap_atual}.{item}")):
                    ref=f"{livro} {cap_atual}.{item}"
                if texto(ref) is None:
                    ruins.append((f"{livro} {resto}", f"não existe: {ref}"))
                    break
    return ruins

if __name__ == "__main__":
    import sys
    total=0
    for arq in sys.argv[1:]:
        for ref,motivo in referencias_invalidas(arq):
            print(f"{arq}: {ref} -> {motivo}"); total+=1
    print(f"{total} referência(s) inválida(s)")
    sys.exit(1 if total else 0)
