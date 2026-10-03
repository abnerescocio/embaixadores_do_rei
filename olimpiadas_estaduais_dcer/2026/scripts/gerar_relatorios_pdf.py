import csv, collections, datetime, subprocess, re, os
B='/Users/abnerescocio/Dev/embaixadores_do_rei/olimpiadas_estaduais_dcer/2026/saida/'
TMP='/private/tmp/claude-501/-Users-abnerescocio-Dev-embaixadores-do-rei/2489efff-00ee-4f39-ba6b-f99e629395da/scratchpad/typ/'
os.makedirs(TMP,exist_ok=True)
rows=list(csv.DictReader(open(B+'delegacao_departamento_oeer2026.csv',encoding='utf-8-sig')))
CATS=['Júnior','Adolescente','Juvenil']
TAG={'Embaixada Pastor José Saraiva':'JS','Embaixada Waldemiro Tymchak':'WT','Embaixada Jeff Brawner':'JB'}
EMB={'Embaixada Pastor José Saraiva':'Pastor José Saraiva','Embaixada Waldemiro Tymchak':'Waldemiro Tymchak','Embaixada Jeff Brawner':'Jeff Brawner'}
def esc(s):
    return re.sub(r'([\\#$*_`<>@\[\]~/])',r'\\\1',str(s))
PART={'da','de','do','das','dos'}
def short(n): return ' '.join([x for x in n.split() if x.lower() not in PART][:2])
def dt(iso): return '/'.join(reversed(iso.split('-')))
ER={}
for r in rows: ER.setdefault(r['nome'],[]).append(r)
def meta(n): return ER[n][0]
ORDER=sorted(ER,key=lambda n:(list(TAG).index(meta(n)['delegacao']),-CATS.index(meta(n)['categoria']),n))
def lab(r): return (r['sigla']+' · '+r['competicao']) if r['modulo']=='Bíblico' else (r['competicao']+' · '+r['prova'])
def key(r): return r['sigla'] if r['modulo']=='Bíblico' else r['competicao']+' · '+r['prova']
def col(r): return 'Única' if r['categoria_disputa'].startswith('Única') else r['categoria_disputa']
def nm(r):
    return f"{esc(short(r['nome']))}{'↑' if r['sobe_categoria'] else ''} #text(size: 6.5pt, fill: gray)[{TAG[r['delegacao']]}]"
NAMES={'CGB':'Conhecimentos Gerais da Bíblia','CGO':'Conhecimentos Gerais da Organização ER','MB':'Montagem Bíblica','SER':'Sempre Embaixador – Biografia do WAH','BJ':'Biografia de Jesus','EB':'Esgrima Bíblica','VRB':'Debate de Versículos com Referência Bíblica','PRE':'Pregador do Evangelho'}
T3=CATS
SEC=[('Módulo Bíblico',[(k,T3) for k in ['CGB','CGO','MB','SER','BJ','EB','VRB','PRE']]),
('Atletismo',[('Atletismo · 50 metros',['Júnior']),('Atletismo · Revezamento 4x50 metros',['Júnior']),('Atletismo · 100 metros',['Adolescente','Juvenil']),('Atletismo · Salto em Distância',T3),('Atletismo · 1500 metros',['Única']),('Atletismo · Revezamento 4x100 metros',['Única'])]),
('Natação',[('Natação · 50 metros nado livre',['Júnior']),('Natação · 50 metros nado costas',['Única']),('Natação · 100 metros nado livre',['Única']),('Natação · Revezamento 4x25 metros nado livre',['Única'])]),
('Jogos de Salão',[('Jogos de Salão · Xadrez',T3),('Jogos de Salão · Damas',T3),('Jogos de Salão · Dominó',T3),('Jogos de Salão · Tênis de Mesa',T3)]),
('Jogos Coletivos',[('Jogos Coletivos · Futsal',T3),('Jogos Coletivos · Vôlei',['Única'])])]
cells=collections.defaultdict(list)
for r in rows: cells[(key(r),col(r))].append(r)
def cap(k):
    if 'Dominó' in k: return 4
    if 'Revezamento' in k: return 4
    if 'Futsal' in k: return 10
    if 'Vôlei' in k: return 12
    return 2
def fl(x): return x
def tbl(cols,body,widths=None,header=True,size=8.5,hfill='luma(230)'):
    w=widths or tuple('1fr' for _ in cols)
    h=''.join(f'[*{esc(c)}*],' for c in cols) if header else ''
    return f'#table(columns: ({", ".join(w)}), inset: 4pt, stroke: 0.4pt + luma(170), fill: (x, y) => if y == 0 and {str(header).lower()} {{ {hfill} }}, align: left + top, table.header({h}), {body})\n'
def cellm(content,fill=None):
    return (f'table.cell(fill: {fill})' if fill else 'table.cell()')+f'[{content}],'

PRE='''#set document(title: "__TITLE__")
#set page(paper: "a4", margin: (x: 1.5cm, top: 1.6cm, bottom: 1.8cm), numbering: "1 / 1", number-align: right,
  footer: context [#text(size: 7.5pt, fill: gray)[Delegação do Departamento · II OEER 2026 · Quixadá-CE · posição em 03/10/2026 #h(1fr) #counter(page).display("1 / 1", both: true)]])
#set text(font: ("Helvetica Neue", "Arial", "Apple Color Emoji"), size: 9pt, lang: "pt", region: "br")
#set par(justify: false, leading: 0.55em)
#show heading.where(level: 1): it => block(above: 1.1em, below: 0.6em)[#text(size: 13pt, weight: "bold", fill: rgb("#1b3a6b"))[#it.body] #v(-0.45em) #line(length: 100%, stroke: 0.8pt + rgb("#1b3a6b"))]
#show heading.where(level: 2): it => block(above: 0.9em, below: 0.4em)[#text(size: 10.5pt, weight: "bold")[#it.body]]
'''
def head(title):
    return PRE.replace('__TITLE__',title)

# ---------- cobertura ----------
sem=[];parc=[]
for sec,items in SEC:
    for k,cs in items:
        if 'Revezamento' in k or 'Dominó' in k or 'Futsal' in k or 'Vôlei' in k:
            n=sum(len(cells[(k,c)]) for c in cs)
            if n==0: sem.append((k,'todas as categorias'))
            continue
        for c in cs:
            n=len(cells[(k,c)])
            if n==0: sem.append((k,c))
            elif n==1: parc.append((k,c,cells[(k,c)][0]))
def klabel(k): return f"{k} — {NAMES[k]}" if k in NAMES else k
def cat_label(c): return c if c!='Única' else 'categoria única'


CONTATO='Abner, Coordenador de DAER: (85) 99252-8076'
def alerta(longo=True):
    box=lambda inner:f'#block(width: 100%, fill: rgb("#fdecea"), stroke: 1.6pt + rgb("#c00000"), inset: 9pt, radius: 3pt, breakable: false)[{inner}]\n#v(4pt)\n'
    red=lambda x:f'#text(fill: rgb("#c00000"), weight: "bold")[{x}]'
    if not longo:
        return box(red('ERRO NA CORREÇÃO OU NA PROVA? PROCURE O ABNER AGORA.')+f'\\ #text(fill: rgb("#8a0000"))[Se entender que houve erro na correção ou que a organização está errando na execução da prova, procure imediatamente o *Coordenador de DAER Abner: (85) 99252-8076*. O recurso só pode ser aberto em até *3 horas* (art. 46); depois disso, não há mais o que fazer.]')
    o=box(red('PREENCHA O GABARITO COM ATENÇÃO')+'\\ #text(fill: rgb("#8a0000"))[Nas provas escritas (CGB, CGO, SER e BJ), marque as 20 respostas no gabarito e confira antes de entregar. Escreva nome completo, DCER e categoria antes de começar (art. 21 I). Depois de chamar o dirigente e entregar, *não dá mais para alterar nenhuma resposta* (art. 21 VI).]')
    o+=box(red('RECURSO: O PRAZO É DE 3 HORAS')+'\\ #text(fill: rgb("#8a0000"))[Contado a partir da prova, da divulgação do resultado ou da devolução da prova corrigida (art. 46, parágrafo único). *Passou o prazo, acabou a chance.* Só o coordenador do DAER pode enviar o recurso.]')
    o+=box(red('ERROU A CORREÇÃO? A ORGANIZAÇÃO ERROU NA PROVA?')+f'\\ #text(fill: rgb("#8a0000"))[Se você ou seu líder entender que houve *erro na correção* ou que a *organização está errando na execução da prova*, procure imediatamente o *Coordenador de DAER Abner: (85) 99252-8076*. Avise antes de sair do local e anote o horário, para abrirmos o recurso dentro do prazo.]')
    return o

# ---------- relatório da delegação ----------
def relatorio():
    t=head('Delegação do Departamento — II OEER 2026')
    n=len(ER); porcat=collections.Counter(meta(x)['categoria'] for x in ER); pordel=collections.Counter(meta(x)['delegacao'] for x in ER)
    t+=f'''#align(center)[#text(size: 9pt, fill: gray)[II Olimpíada Estadual de Embaixadores do Rei · Quixadá-CE · 10 a 12 de outubro de 2026]
#v(2pt) #text(size: 20pt, weight: "bold")[Delegação do Departamento]
#v(2pt) #text(size: 11pt)[Relatório para os líderes da delegação · posição em 03/10/2026]]
#v(6pt)
= Resumo
'''
    t+=f'''*{n} Embaixadores do Rei* inscritos: {pordel['Embaixada Pastor José Saraiva']} da Embaixada Pastor José Saraiva (JS), {pordel['Embaixada Waldemiro Tymchak']} da Embaixada Waldemiro Tymchak (WT) e {pordel['Embaixada Jeff Brawner']} da Embaixada Jeff Brawner (JB). Por categoria: {porcat['Júnior']} Júnior (9 a 11 anos), {porcat['Adolescente']} Adolescente (12 a 14) e {porcat['Juvenil']} Juvenil (15 a 17). Total de {len(rows)} inscrições em modalidades; cada Embaixador do Rei disputa no máximo 7.

'''
    fut=collections.Counter(r['categoria'] for r in rows if r['prova']=='Futsal'); vol=sum(1 for r in rows if r['prova']=='Vôlei')
    # prazos
    t+='= Prazos e documentos\n'
    pr=[('Pagamento da inscrição','R$ 140 até 15/09 às 18h; R$ 160 até 02/10 às 18h (prazo final já encerrado). Sem devolução em caso de desistência (art. 7).'),
        ('Formulário online com os participantes por modalidade','até 04/10/2026. Depois dessa data não há alteração, em nenhuma hipótese (art. 15). Competir sem constar na relação custa 1.000 pontos (art. 49 II b).'),
        ('Necessidade especial / adaptação de prova','informar ao Comitê Organizador até 05/10/2026 (art. 11 §2).'),
        ('Documento de identificação','O art. 12 exige a carteira de Embaixador do Rei, mas ela não é necessária nesta edição. Cada participante leva um documento oficial com foto.'),
        ('Hospedagem','a inscrição inclui hospedagem econômica, alimentação e premiação. Cada um leva colchonete e roupa de cama (art. 7 §3 e §4). Aspectos físicos e médicos são responsabilidade da delegação (art. 14).'),
        ('Chegada às provas escritas','20 minutos antes do horário, com documento com foto e caneta azul (art. 20, sem a carteira de ER nesta edição). O Quadro de Horários será divulgado pelo Comitê (art. 13 §2).')]
    t+=tbl(['Item','Detalhe'],''.join(cellm('*'+esc(a)+'*')+cellm(esc(b)) for a,b in pr),widths=('5cm','1fr'))
    # participantes
    t+='#pagebreak()\n= Participantes\n'
    body=''
    for i,x in enumerate(ORDER,1):
        m=meta(x); nmod=len(ER[x]); up=any(r['sobe_categoria'] for r in ER[x])
        body+=cellm(str(i))+cellm('*'+esc(x)+'*')+cellm(dt(m['nascimento']))+cellm(f"{m['idade_em_11_10_2026']}")+cellm(esc(m['categoria'])+(' ↑' if up else ''))+cellm(esc(EMB[m['delegacao']]))+cellm(str(nmod))
    t+=tbl(['Nº','Nome completo','Nascimento','Idade','Categoria','Embaixada','Modal.'],body,widths=('0.8cm','6.6cm','2.2cm','1.1cm','2.3cm','1fr','1.2cm'))
    t+='\n_Idade em 11/10/2026, conforme o art. 16. "Modal." = número de modalidades. ↑ = compete acima da própria categoria._\n'
    # quadro por competição
    t+='#pagebreak()\n= Quadro por competição\n'
    t+='_Legenda: JS = José Saraiva · WT = Waldemiro Tymchak · JB = Jeff Brawner · ↑ compete acima da própria categoria (arts. 19 e 31)._\n'
    for sec,items in SEC:
        if sec=='Jogos Coletivos': continue
        t+=f'== {esc(sec)}\n'
        body=''
        for k,cs in items:
            nome=f"*{esc(k.split(' · ',1)[-1])}*"+(f"\\ #text(size: 7.5pt, fill: gray)[{esc(NAMES[k])}]" if k in NAMES else '')
            body+=cellm(nome)
            for c in ['Júnior','Adolescente','Juvenil','Única']:
                if c not in cs: body+=cellm('#text(fill: luma(140))[—]','luma(228)'); continue
                it=cells[(k,c)]
                if not it: body+=cellm('#text(fill: rgb("#a00000"))[sem competidor]','rgb("#fff0f0")'); continue
                if 'Dominó' in k:
                    ds=collections.OrderedDict()
                    for r in it: ds.setdefault(r['dupla'],[]).append(r)
                    txt=' \\ '.join('('+' + '.join(nm(r) for r in v)+')' for v in ds.values())
                else: txt=' \\ '.join(nm(r) for r in it)
                lim=cap(k)
                tail='' if len(it)>=lim else f' \\ #text(size: 7.5pt, fill: gray)[{lim-len(it)} vaga(s) livre(s)]'
                body+=cellm(txt+tail)
        t+=tbl(['Prova','Júnior','Adolescente','Juvenil','Única'],body,widths=('4.2cm','1fr','1fr','1fr','1fr'))
    t+='== Futsal e Vôlei (equipes)\n'
    body=''
    for c in CATS:
        it=cells[('Jogos Coletivos · Futsal',c)]
        body+=cellm(f'*Futsal {c}*\\ {len(it)} Embaixadores do Rei'+(' (mínimo 5)' if len(it)<5 else ''))+cellm(', '.join(nm(r) for r in it) if it else '—')
    it=cells[('Jogos Coletivos · Vôlei','Única')]
    body+=cellm(f'*Vôlei*\\ {len(it)} Embaixadores do Rei')+cellm(', '.join(nm(r) for r in it))
    for k,lab_ in [('Atletismo · Revezamento 4x100 metros','Revezamento 4x100 m (atletismo)'),('Natação · Revezamento 4x25 metros nado livre','Revezamento 4x25 m (natação)')]:
        it=cells[(k,'Única')]; body+=cellm(f'*{lab_}*\\ {len(it)} Embaixadores do Rei')+cellm(', '.join(nm(r) for r in it))
    t+=tbl(['Equipe','Atletas'],body,widths=('4.6cm','1fr'))
    # cobertura
    t+='= Cobertura da delegação\n'
    t+='Modalidades e categorias *sem nenhum competidor* da nossa delegação:\n\n'
    t+=''.join(f'- {esc(klabel(k))} — {esc(cat_label(c))}\n' for k,c in sem)
    t+='\nCategorias com *apenas 1 competidor* (resta 1 vaga pelo limite do art. 13 §1º):\n\n'
    t+=''.join(f'- {esc(klabel(k))} — {esc(cat_label(c))}: {esc(short(r["nome"]))}\n' for k,c,r in parc)
    t+='\n_As vagas livres só podem ser ocupadas por Embaixadores do Rei que ainda tenham espaço no limite de 7 modalidades e que respeitem a regra de uma prova por tipo (art. 13). Nenhuma inscrição pode ser incluída depois de 04/10 (art. 15)._\n'
    # pontos de atenção
    t+='= Pontos de atenção\n'
    ups=[r for r in rows if r['sobe_categoria']]
    t+='- *Futsal Júnior:* 4 Embaixadores do Rei, e o mínimo é 5 (art. 40 §1º). A delegação negocia com o Comitê Organizador. Sem solução, a equipe Júnior não se forma.\n'
    for r in ups: t+=f'- *{esc(short(r["nome"]))}* ({esc(r["categoria"])}) compete acima da própria categoria no {esc(r["competicao"])}, categoria {esc(r["categoria_disputa"])} (arts. 19 e 31).\n'
    # interpretações
    t+='== Interpretações adotadas (confirmar com o Comitê)\n'
    for s in ['Revezamento não conta entre as 2 provas coletivas por Embaixador do Rei do art. 13; ocupa a vaga de atletismo ou de natação.','Dominó permite 2 duplas por categoria (4 Embaixadores do Rei).','O limite de 2 representantes por competição (art. 13 §1º) vale por categoria. Nas provas de categoria única (100 m livre, 50 m costas, 1500 m), vale 2 no total.','A carteira de Embaixador do Rei (art. 12) não é exigida nesta edição; vale um documento com foto.','Esgrima Bíblica: 2 por categoria, apesar do texto do art. 27 II ("um por embaixada"), que se entende como erro de redação.']:
        t+=f'- {esc(s)}\n'
    # regulamento
    t+='#pagebreak()\n= Regulamento — o que os líderes precisam saber\n'
    t+=alerta(True)
    t+=regulamento()
    open(TMP+'relatorio.typ','w',encoding='utf-8').write(t)

def regulamento():
    s=''
    def sec(title,items):
        o=f'== {esc(title)}\n'
        for a,b in items: o+=f'- *{esc(a)}* {esc(b)}\n'
        return o+'\n'
    s+=sec('Geral',[('Identificação (art. 12):','o regulamento pede a carteira de ER, mas nesta edição ela não é necessária. Levar um documento oficial com foto.'),('Categorias (art. 16):','Júnior 9 a 11 anos, Adolescente 12 a 14, Juvenil 15 a 17. Quem completa 12, 15 ou 18 anos a partir de 12/10/2026 fica na categoria que tinha no dia anterior ao evento.'),
      ('Categoria acima (arts. 19 e 31):','o ER de categoria inferior pode competir em categoria de maior idade; o contrário não é permitido.'),
      ('Limites por ER (art. 13):','até 7 modalidades: 1 prova bíblica escrita, 1 não escrita, 1 jogo de salão, 2 individuais (atletismo e natação) e 2 coletivas. Até 2 representantes por competição individual.'),
      ('Inscrição (arts. 6 e 15):','feita pelo coordenador do DAER; o formulário por modalidade não pode ser alterado depois do prazo.'),
      ('Bíblia (art. 17 §2):','João Ferreira de Almeida, Revista e Atualizada, edição 1995, salvo regra específica.')])
    s+=sec('Módulo Bíblico',[('Provas escritas (CGB, CGO, SER, BJ):','20 questões de múltipla escolha, até 20 minutos (art. 21). Escrever nome completo, DCER e categoria antes de começar. Quem termina levanta a prova e diz "terminei"; depois disso não pode alterar respostas. Classificação por acertos; empate pelo menor tempo; novo empate, nova prova.'),
      ('Pontuação mínima (art. 18):','quem não acertar pelo menos 50% não pontua, mesmo entre os 3 primeiros.'),
      ('CGO (art. 22):','Júnior: Novo Manual do Escudeiro. Adolescente: Escudeiro e Arauto. Juvenil: Escudeiro, Arauto e Sênior.'),
      ('SER (art. 25):','livro "Sempre Embaixador", versão de fevereiro de 2010 (site www.denaer.org.br).'),
      ('BJ (art. 26):','ministério de Jesus nos Evangelhos de Mateus, Marcos, Lucas e João.'),
      ('Montagem Bíblica (art. 24 e Anexo I):','prova escrita sem consulta. Júnior: montagem completa (grande divisão, livros e capítulos). Adolescente e Juvenil: super completa (inclui subdivisões). São erros: livro, capítulo ou divisão omitidos ou fora de ordem, erro ortográfico, livro com inicial minúscula, número cardinal em vez de romano ("II Samuel"). Classificação: menos erros, depois menor tempo. Letra legível.'),
      ('Esgrima Bíblica (art. 27):','Bíblia fornecida pelo DCER. Na posição de "espada" com o braço levantado; ao comando "CARREGAR", localizar e ler o versículo. Quem lê primeiro marca ponto; 5 pontos vencem. Segurar errado ou "queimar" gera advertência; na segunda, fica fora da rodada.'),
      ('Debate de Versículos (art. 28):','citar livro, capítulo e versículo e recitar de cor. Bíblia impressa própria (digital não vale). 60 segundos para começar. Eliminação por erro. Salmos 133.1 com "Oh!". Versículo repetido em várias referências só pode ser usado uma vez.'),
      ('Pregador do Evangelho (art. 29):','sermão de até 10 minutos (cada minuto a mais tira 1 ponto). Notas de 1 a 10 em postura, noções de homilética, destreza com a Bíblia e conteúdo. Esboço em papel permitido; equipamentos eletrônicos não.')])
    s+=sec('Módulo Esportivo',[('Geral (arts. 30 a 33):','regras oficiais de cada modalidade, com adaptações. Tolerância de 10 minutos após a chamada para se apresentar; passado esse prazo, a pessoa ou equipe é considerada ausente.'),
      ('Atletismo (art. 32):','tênis obrigatório. 50 m e revezamento 4x50 m: Júnior. 100 m: Adolescente e Juvenil. Salto em distância: as três categorias. Revezamento 4x100 m e 1500 m: categoria única Adolescente/Juvenil. Revezamento exige 4 ER na chamada.'),
      ('Natação (art. 33):','50 m livre: Júnior. 50 m costas, 100 m livre e revezamento 4x25 m: categoria única Adolescente/Juvenil. Roupa própria de natação, senão há eliminação. Não precisa de virada olímpica; pode ficar em pé, mas não andar nem se impulsionar no fundo.'),
      ('Xadrez (art. 35):','15 minutos por jogador no relógio; vitória 2 pontos, empate 1. Lance irregular desconta 1 minuto; 3 lances irregulares derrotam.'),
      ('Damas (art. 36):','tabuleiro de 64 casas, sem relógio. Vitória 2 pontos, empate 1.'),
      ('Dominó (art. 37):','em duplas; partida de até 3 jogos; vence a dupla que chegar a 3 pontos. Batida de 1 a 3 pontos conforme a pedra. Comunicação irregular desclassifica a dupla.'),
      ('Tênis de Mesa (art. 38):','até 3 sets de 11 pontos; vence quem ganha 2 sets. Levar a própria raquete. Vitória vale 2 pontos.'),
      ('Futsal (art. 40):','5 a 10 ER por categoria. Jogo de 20 minutos (2 tempos de 10). Entrar em quadra uniformizado e relacionado na súmula em até 10 minutos, ou é WO. Cinco faltas individuais tiram o jogador. Mínimo de 4 em quadra. Vitória vale 3 pontos, empate 1.'),
      ('Vôlei (art. 41):','6 a 12 ER, categoria única Adolescente/Juvenil. Até 3 sets; vence quem ganha 2. Uniformizado e na súmula em até 10 minutos, ou é WO. Mínimo de 4 em quadra. Rodízio só no saque.')])
    s+=sec('Pontuação e premiação (arts. 42 a 45)',[('Módulo Bíblico:','1º lugar 500 pontos, 2º 300, 3º 100.'),('Módulo Esportivo:','1º lugar 250 pontos, 2º 150, 3º 50.'),('Medalhas:','até o 3º lugar em todas as competições; nas coletivas, só campeão e vice. Troféu itinerante para o DAER campeão geral 2026–2028.'),('Desempate geral:','maior pontuação bíblica, depois esportivo coletivo, esportivo individual, e por fim quantidade de medalhas de ouro, prata e bronze.')])
    s+=sec('Recursos e penalidades (arts. 46 a 49)',[('Recurso:','o coordenador do DAER envia narrativa dos fatos para dcercearense@hotmail.com, com um telefone para a resposta, em até 3 horas após a prova, o resultado ou a devolução da prova corrigida.'),('Perda de 2.000 pontos:','ER, líder ou conselheiro participar sem inscrição; desrespeito claro ao Comitê; má-fé clara em competição.'),('Perda de 1.000 pontos:','ER competir sem estar na relação de participantes do art. 15; desrespeito amplo a conselheiro ou ao Comitê.'),('Outras:','de 100 a 2.000 pontos em casos não previstos, proibição de competir, desclassificação do DCER de uma competição.')])
    return s

# ---------- fichas ----------
RULES={'CGB':'Prova escrita: 20 questões de múltipla escolha, até 20 minutos. Chegar 20 min antes, com documento com foto e caneta azul. Escrever nome completo, DCER e categoria antes de começar. Abaixo de 50% de acertos não pontua.',
'CGO':'Prova escrita (mesmas regras do CGB). Conteúdo: Júnior = Manual do Escudeiro; Adolescente = Escudeiro e Arauto; Juvenil = Escudeiro, Arauto e Sênior.',
'MB':'Prova escrita sem consulta, com folha pautada do DCER. Júnior: completa. Adolescente e Juvenil: super completa (com subdivisões). Atenção: II Samuel (romano), letra maiúscula, ordem e número de capítulos.',
'SER':'Prova escrita (mesmas regras do CGB) sobre o livro "Sempre Embaixador", versão de fevereiro de 2010.',
'BJ':'Prova escrita (mesmas regras do CGB) sobre o ministério de Jesus nos 4 Evangelhos.',
'EB':'Bíblia fornecida pelo DCER. Braço levantado até o comando "CARREGAR"; não baixar antes (advertência). Quem ler o versículo primeiro marca ponto; 5 pontos vencem.',
'VRB':'Citar livro, capítulo e versículo e recitar de cor. Levar Bíblia impressa (não vale digital). 60 s para começar; errou, está eliminado. Salmos 133.1 com "Oh!".',
'PRE':'Sermão de até 10 minutos (−1 ponto por minuto excedido). Pode levar esboço em papel; eletrônicos não. Levar Bíblia impressa.',
'Atletismo · 50 metros':'Tênis obrigatório. Estar no local em até 10 min da chamada. Classificação por tempo.',
'Atletismo · 100 metros':'Tênis obrigatório. Estar no local em até 10 min da chamada. Classificação por tempo.',
'Atletismo · Salto em Distância':'Tênis obrigatório. Estar no local em até 10 min da chamada.',
'Atletismo · 1500 metros':'Categoria única Adolescente/Juvenil. Tênis obrigatório. Chegar em até 10 min da chamada.',
'Atletismo · Revezamento 4x100 metros':'Equipe de exatamente 4 ER na chamada, senão a equipe não corre. Tênis obrigatório.',
'Natação · 50 metros nado livre':'Roupa própria de natação (senão eliminado). Chegar em até 10 min da chamada. Basta tocar a borda; pode ficar em pé, mas sem andar nem tomar impulso no fundo.',
'Natação · 50 metros nado costas':'Roupa própria de natação. Chegar em até 10 min da chamada. Categoria única Adolescente/Juvenil.',
'Natação · 100 metros nado livre':'Roupa própria de natação. Chegar em até 10 min da chamada. Categoria única Adolescente/Juvenil.',
'Natação · Revezamento 4x25 metros nado livre':'Equipe de 4. Roupa própria de natação. Chegar em até 10 min da chamada.',
'Jogos de Salão · Xadrez':'15 minutos por jogador no relógio. Vitória 2 pontos, empate 1. Lance irregular desconta 1 minuto.',
'Jogos de Salão · Damas':'Tabuleiro de 64 casas, sem relógio. Vitória 2 pontos, empate 1.',
'Jogos de Salão · Dominó':'Em dupla. Partida de até 3 jogos; vence a dupla que chegar a 3 pontos. Comunicação irregular desclassifica a dupla.',
'Jogos de Salão · Tênis de Mesa':'Levar a própria raquete. Até 3 sets de 11 pontos; vence quem ganha 2 sets. Vitória vale 2 pontos.',
'Jogos Coletivos · Futsal':'Jogo de 20 min (2 tempos de 10). Entrar em quadra uniformizado e na súmula em até 10 min, senão WO. Cinco faltas tiram o jogador.',
'Jogos Coletivos · Vôlei':'Até 3 sets; vence quem ganha 2. Uniformizado e na súmula em até 10 min, senão WO. Rodízio só no saque.'}
def ficha():
    t=head('Fichas dos Embaixadores do Rei — II OEER 2026')
    for i,x in enumerate(ORDER):
        m=meta(x); rs=ER[x]
        if i: t+='#pagebreak()\n'
        t+=f'''#text(size: 8.5pt, fill: gray)[II OEER 2026 · Quixadá-CE · 10 a 12 de outubro]
#v(2pt) #text(size: 18pt, weight: "bold")[{esc(x)}]
#v(4pt)
'''
        t+=tbl(['Embaixada','Nascimento','Idade','Categoria','Modalidades'],cellm(esc(EMB[m['delegacao']]))+cellm(dt(m['nascimento']))+cellm(f"{m['idade_em_11_10_2026']} anos")+cellm(esc(m['categoria']))+cellm(str(len(rs))),widths=('1fr','2.4cm','1.8cm','2.4cm','2.2cm'),size=9)
        t+='\n= Modalidades\n'
        order={'Bíblico':0,'Jogos de Salão':2,'Atletismo':1,'Natação':1,'Jogos Coletivos':3}
        rs2=sorted(rs,key=lambda r:(order[r['competicao'] if r['competicao'] in order else 'Bíblico'] if r['modulo']!='Bíblico' else 0,lab(r)))
        body=''
        extra=set()
        for r in rs2:
            k=key(r); txt=RULES[k]
            cd=col(r)
            if r['sigla']=='CGO': txt=txt
            nome=f"*{esc(lab(r))}*"
            if r['dupla']:
                par=[y for y in rows if y['dupla']==r['dupla'] and y['nome']!=x]
                nome+=f"\\ Dupla: {esc(', '.join(short(p['nome']) for p in par))}"
            if r['sobe_categoria']: nome+=f"\\ #text(fill: rgb(\"#6b3fb5\"))[↑ compete na categoria {esc(r['categoria_disputa'])}]"
            if 'Revezamento' in r['prova']:
                par=[short(y['nome']) for y in rows if y['prova']==r['prova'] and y['nome']!=x]
                nome+=f"\\ Equipe: {esc(', '.join(par))}"
            body+=cellm(nome)+cellm(esc(cd.replace('Única','Única Adol./Juvenil')))+cellm(esc(txt))
        t+=tbl(['Modalidade','Categoria','Regras principais'],body,widths=('5.2cm','2.4cm','1fr'))
        ks=list(rs)
        has=lambda f:any(f(r) for r in ks)
        docs=[('🪪','Documento oficial com foto (RG ou outro)'),('💊','Medicamentos de uso pessoal e cartão do plano de saúde, se tiver')]
        dorm=[('🛏️','Colchonete'),('🛌','Lençol, cobertor e travesseiro'),('🎒','Mochila ou mala identificada com o nome')]
        roup=[('👕','Camisas e bermudas para os 3 dias'),('👖','Calça e roupa para o culto'),('🧦','Meias e roupa íntima'),('🧥','Agasalho'),('🩴','Chinelo'),('🚿','Toalha de banho'),('🪥','Escova, pasta, sabonete e desodorante'),('🧴','Protetor solar')]
        prov=[('📖','Bíblia, de preferência Almeida Revista e Atualizada (1995)')] if True else []
        if has(lambda r:r['tipo']=='escrita'): prov.append(('🖊️','Caneta azul (leve duas) e chegue 20 min antes'))
        if has(lambda r:r['sigla']=='PRE'): prov.append(('📝','Esboço do sermão em papel (sem celular)'))
        if has(lambda r:r['sigla']=='VRB'): prov.append(('📚','Bíblia impressa para conferência (não vale digital)'))
        if has(lambda r:r['competicao']=='Atletismo'): prov.append(('👟','Tênis (sem tênis não corre)'))
        if has(lambda r:r['competicao']=='Natação'): prov.append(('🩳','Roupa própria de natação (senão é eliminado)'));prov.append(('🧖','Toalha extra para a piscina'))
        if has(lambda r:r['prova']=='Tênis de Mesa'): prov.append(('🏓','Raquete de tênis de mesa'))
        if has(lambda r:r['prova']=='Futsal'): prov.append(('⚽','Uniforme de futsal e tênis de quadra'))
        if has(lambda r:r['prova']=='Vôlei'): prov.append(('🏐','Uniforme de vôlei e tênis de quadra'))
        if has(lambda r:r['prova']=='Xadrez'): prov.append(('♟️','Disposição para o relógio de 15 minutos (tabuleiro é do evento)'))
        extra=[('💧','Garrafa de água'),('🍪','Lanche leve para os intervalos'),('🔌','Carregador do celular')]
        def blk(titulo,items):
            g=''.join(f'[#box(width: 10pt, height: 10pt, stroke: 0.8pt + luma(80), baseline: 2pt) #h(6pt) #text(size: 13pt)[{e}] #h(4pt) {esc(tx)}],' for e,tx in items)
            return f'#v(4pt)\n== {esc(titulo)}\n#set text(size: 10pt)\n#grid(columns: (1fr, 1fr), column-gutter: 12pt, row-gutter: 9pt, {g})\n'
        t+='\n= Lembretes\n'+'- Chegar ao local de cada prova antes da chamada: a tolerância é de 10 minutos.\n- O Quadro de Horários é divulgado pelo Comitê Organizador; confira se duas provas coincidem.\n- A carteira de Embaixador do Rei não é necessária nesta edição, mas o documento com foto é.\n- Recursos: o coordenador do DAER tem 3 horas após a prova para enviar (dcercearense\\@hotmail.com).\n- No verso desta folha está o checklist da sua bagagem.\n'
        t+='#v(6pt)\n'+alerta(False)
        t+='#pagebreak()\n'+f'#text(size: 8.5pt, fill: gray)[II OEER 2026 · Quixadá-CE · 10 a 12 de outubro]\n#v(2pt) #text(size: 18pt, weight: "bold")[Checklist da bagagem]\n#v(1pt) #text(size: 11pt)[{esc(x)} · {esc(EMB[m["delegacao"]])}]\n#v(4pt)\n'
        t+=blk('Documentos e saúde',docs)+blk('Para dormir',dorm)+blk('Roupas e higiene',roup)+blk('Para as suas provas',prov)+blk('No dia a dia',extra)
    open(TMP+'fichas.typ','w',encoding='utf-8').write(t)

relatorio(); ficha()
for n,out in [('relatorio','oeer2026_relatorio_delegacao.pdf'),('fichas','oeer2026_fichas_embaixadores.pdf')]:
    r=subprocess.run(['typst','compile','--root','/',TMP+n+'.typ',B+out],capture_output=True,text=True)
    print(n,r.returncode,r.stderr[:1500])
