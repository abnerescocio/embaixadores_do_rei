#!/usr/bin/env python3
"""Gera resultados/painel.html: página única (sem internet) para analisar os resultados das provas.

Uso:
    python3 scripts/painel.py        # lê resultados/alunos.csv e resultados/<sigla>/<unidade>/<NNN>.csv e escreve resultados/painel.html

Mostra, por prova (acerto por pergunta só com a 1ª tentativa de cada aluno), a nota de cada aluno e o acerto por pergunta (ID do estudo, enunciado, alternativa
mais marcada). Abaixo de MIN_RESPOSTAS respondentes a taxa é sinalizada como "poucos dados".
Os dados ficam embutidos na página (contém nomes: não publicar).
"""
import csv
import json
import re
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_pdf import RAIZ, ler_md, parse_prova  # noqa: E402

MIN_RESPOSTAS = 15


def carregar():
    arq_alunos = RAIZ / "resultados" / "alunos.csv"
    nomes = {a["id"]: a["nome"] for a in csv.DictReader(arq_alunos.open(encoding="utf-8"))} if arq_alunos.exists() else {}
    provas = []
    for arq in sorted((RAIZ / "resultados").glob("*/*/*.csv")):
        sigla, unidade, num = arq.parent.parent.name, arq.parent.name, arq.stem
        fonte = RAIZ / "provas" / sigla / unidade / f"{num}.md"
        if not fonte.exists():
            print(f"⚠ {arq.relative_to(RAIZ)}: prova {fonte.relative_to(RAIZ)} não existe; ignorado")
            continue
        _, linhas = ler_md(fonte)
        questoes = parse_prova(linhas)
        certas = [q["resposta"][:1].upper() for q in questoes]
        alunos = []
        for a in csv.DictReader(arq.open(encoding="utf-8")):
            resp = re.sub(r'\s', '', a["respostas"]).upper()
            if len(resp) != len(questoes) or set(resp) - set("ABCD-"):
                sys.exit(f"{arq.name}: respostas inválidas para {a['aluno']}: {resp!r}")
            alunos.append({"id": a["aluno"], "tent": int(a.get("tentativa") or 1), "nome": nomes.get(a["aluno"], a["aluno"]), "resp": resp})
        provas.append({
            "id": f"{sigla}/{unidade}/{num}", "sigla": sigla, "unidade": unidade, "num": num,
            "certas": certas, "alunos": alunos,
            "questoes": [{"id": q["id"], "enunciado": q["enunciado"], "fonte": q["fonte"]} for q in questoes],
        })
    return provas


HTML = r"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Painel de resultados</title>
<style>
:root{--bg:#f6f5f2;--card:#fff;--tx:#1c1c1a;--mut:#6b6b66;--bd:#e2e0da;--ok:#2e7d4f;--no:#c0392b;--ac:#4a3b8f}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--card:#1f1f1d;--tx:#ecebe6;--mut:#9a9890;--bd:#33322e;--ok:#5fbf86;--no:#e8776a;--ac:#a99bf0}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--tx);font:15px/1.45 system-ui,sans-serif}
main{max-width:1000px;margin:0 auto;padding:20px 16px 48px}
h1{font-size:1.3rem;margin:0 0 4px}h2{font-size:1.05rem;margin:28px 0 10px}
.sub{color:var(--mut);margin:0 0 16px}
select{font:inherit;padding:8px 10px;border:1px solid var(--bd);border-radius:8px;background:var(--card);color:var(--tx);max-width:100%}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:16px 0}
.card{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:12px 14px}
.card b{display:block;font-size:1.5rem}.card span{color:var(--mut);font-size:.85rem}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--bd);border-radius:10px;overflow:hidden}
th,td{padding:8px 10px;text-align:left;border-bottom:1px solid var(--bd);vertical-align:middle}
th{font-size:.8rem;color:var(--mut);font-weight:600;cursor:pointer;user-select:none;white-space:nowrap}
tr:last-child td{border-bottom:0}.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.bar{height:8px;border-radius:4px;background:var(--bd);min-width:80px;overflow:hidden}.bar i{display:block;height:100%;background:var(--ok)}
.bar.low i{background:var(--no)}.mut{color:var(--mut)}.aviso{color:var(--mut);font-size:.85rem}
.wrap{overflow-x:auto}.chip{display:inline-block;padding:1px 7px;border-radius:99px;border:1px solid var(--bd);font-size:.8rem}
.er{color:var(--no)}.ac{color:var(--ok)}code{font-size:.85em}
</style></head><body><main>
<h1>Painel de resultados</h1>
<p class="sub">Embaixada Pastor José Saraiva · acertos por aluno e por pergunta</p>
<label>Prova: <select id="sel"></select></label>
<div id="app"></div>
</main>
<script>
const DADOS = __DADOS__, MIN = __MIN__;
const sel = document.getElementById('sel'), app = document.getElementById('app');
DADOS.forEach((p, i) => sel.add(new Option(`${p.sigla.toUpperCase()} · ${p.unidade} · nº ${p.num} (${new Set(p.alunos.map(a=>a.id)).size} aluno${new Set(p.alunos.map(a=>a.id)).size==1?'':'s'})`, i)));
const esc = s => s.replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
let ordemQ = 'n', ordemA = 'nota';
function render() {
  const p = DADOS[sel.value]; if (!p) { app.innerHTML = '<p>Nenhum resultado em resultados/.</p>'; return; }
  const n = new Set(p.alunos.map(a => a.id)).size, nq = p.questoes.length, prim = p.alunos.filter(a => a.tent == 1), np = prim.length;
  const notas = p.alunos.map(a => ({tent: a.tent, nome: a.nome + (a.tent > 1 ? ` (tentativa ${a.tent})` : ''), nota: a.resp.split('').filter((r, i) => r === p.certas[i]).length, resp: a.resp}));
  const media = notas.filter(a => a.tent == 1).reduce((s, a) => s + a.nota, 0) / np;
  const qs = p.questoes.map((q, i) => {
    const cont = {A:0,B:0,C:0,D:0,'-':0}; prim.forEach(a => cont[a.resp[i]]++);
    const ac = cont[p.certas[i]];
    const top = Object.entries(cont).filter(([l]) => l != p.certas[i] && l != '-').sort((a, b) => b[1] - a[1])[0];
    return {n: i + 1, ...q, ac, taxa: ac / np, certa: p.certas[i], errMais: top && top[1] ? `${top[0]} (${top[1]})` : '—'};
  });
  const poucos = np < MIN;
  const dif = [...qs].sort((a, b) => a.taxa - b.taxa)[0];
  qs.sort((a, b) => ordemQ == 'taxa' ? a.taxa - b.taxa || a.n - b.n : a.n - b.n);
  notas.sort((a, b) => ordemA == 'nome' ? a.nome.localeCompare(b.nome) : b.nota - a.nota);
  app.innerHTML = `
  <div class="cards">
    <div class="card"><b>${n}</b><span>aluno${n==1?'':'s'}</span></div>
    <div class="card"><b>${media.toFixed(1)}/${nq}</b><span>média da turma (1ª tentativa)</span></div>
    <div class="card"><b>${Math.max(...notas.map(a=>a.nota))}/${nq}</b><span>maior nota</span></div>
    <div class="card"><b>${Math.min(...notas.map(a=>a.nota))}/${nq}</b><span>menor nota</span></div>
  </div>
  ${poucos ? `<p class="aviso">⚠ Poucos dados (menos de ${MIN} alunos): as porcentagens por pergunta ainda não são confiáveis; veja os acertos absolutos.</p>` : ''}
  <h2>Alunos</h2>
  <div class="wrap"><table><tr><th data-a="nome">Aluno</th><th data-a="nota" class="num">Nota</th><th>Erradas</th></tr>
  ${notas.map(a => `<tr><td>${esc(a.nome)}</td><td class="num"><b>${a.nota}</b>/${nq}</td><td class="er">${
     a.resp.split('').map((r, i) => r !== p.certas[i] ? i + 1 : '').filter(Boolean).join(', ') || '<span class="ac">—</span>'}</td></tr>`).join('')}</table></div>
  <h2>Perguntas ${poucos ? '' : '(da mais difícil para a mais fácil: clique em “Acerto”)'}</h2>
  <div class="wrap"><table><tr><th data-q="n">#</th><th>ID</th><th>Pergunta</th><th>Certa</th><th data-q="taxa" class="num">Acerto</th><th>Mais marcada errada</th></tr>
  ${qs.map(q => `<tr><td class="num">${q.n}</td><td class="num mut">${q.id}</td><td>${esc(q.enunciado)}<div class="mut"><small>${esc(q.fonte)}</small></div></td>
   <td><span class="chip">${q.certa}</span></td>
   <td class="num">${q.ac}/${np}${poucos ? '' : ' · ' + Math.round(q.taxa * 100) + '%'}<div class="bar ${q.taxa < .5 ? 'low' : ''}"><i style="width:${q.taxa * 100}%"></i></div></td>
   <td class="mut">${q.errMais}</td></tr>`).join('')}</table></div>`;
  app.querySelectorAll('th[data-q]').forEach(t => t.onclick = () => { ordemQ = t.dataset.q; render(); });
  app.querySelectorAll('th[data-a]').forEach(t => t.onclick = () => { ordemA = t.dataset.a; render(); });
}
sel.onchange = render; render();
</script></body></html>
"""


def main():
    provas = carregar()
    if not provas:
        sys.exit("Nenhum CSV em resultados/<sigla>/<unidade>/<NNN>.csv")
    saida = RAIZ / "resultados" / "painel.html"
    dados = json.dumps(provas, ensure_ascii=False).replace("</", "<\\/")
    saida.write_text(HTML.replace("__DADOS__", dados).replace("__MIN__", str(MIN_RESPOSTAS)), encoding="utf-8")
    print(f"✔ {saida.relative_to(RAIZ)}  ({len(provas)} prova(s))")


if __name__ == "__main__":
    main()
