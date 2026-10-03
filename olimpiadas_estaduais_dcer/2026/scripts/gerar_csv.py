import csv, re, datetime, collections, os
B='/Users/abnerescocio/Dev/embaixadores_do_rei/olimpiadas_estaduais_dcer/2026/'
SAIDA=B+'saida/'
REF=datetime.date(2026,10,11)  # dia anterior ao último dia do evento (art. 16, par. único)
def cat(d):
    a=REF.year-d.year-((REF.month,REF.day)<(d.month,d.day))
    return a,('Júnior' if a<=11 else 'Adolescente' if a<=14 else 'Juvenil')
def titulo(n):
    return ' '.join(w.lower() if w.lower() in('da','de','do','das','dos') else w.capitalize() for w in n.split())
BIB={'bwah':('SER','Sempre Embaixador – Biografia do WAH','escrita'),
 'montagem':('MB','Montagem Bíblica','escrita'),'bj':('BJ','Biografia de Jesus','escrita'),'biografia de jesus':('BJ','Biografia de Jesus','escrita'),
 'cgb':('CGB','Conhecimentos Gerais da Bíblia','escrita'),'cgo':('CGO','Conhecimentos Gerais da Organização ER','escrita'),
 'esgrima':('EB','Esgrima Bíblica','não escrita'),'debate':('VRB','Debate de Versículos com Referência Bíblica','não escrita'),
 'pregador':('PRE','Pregador do Evangelho','não escrita')}
SAL={'xadrez':'Xadrez','dama':'Damas','dominó':'Dominó','tênis de mesa':'Tênis de Mesa'}
NAT_ABERTA='A definir (50 m costas, 100 m livre ou revezamento 4x25 m)'
rows=[]
def add(deleg,nome,d,items,idade_inf=None,cat_inf=None):
    idade,c=cat(d) if d else (idade_inf,cat_inf)
    for t in items:
        k=t.lower().strip(); obs='';st='OK';prova='';cd=c;sg=''
        if k in BIB:
            sg,comp,tipo=BIB[k];modulo='Bíblico'
        elif k=='cgo ou cgb':
            sg='CGO ou CGB';comp='Conhecimentos Gerais (CGO ou CGB)';tipo='escrita';modulo='Bíblico';st='PENDENTE';obs='Texto original diz "Organização (CGB)": confirmar se é CGO ou CGB'
        elif k=='cj':
            sg,comp,tipo=BIB['bj'];modulo='Bíblico';obs='Texto original "Conhecimento de Jesus (CJ)"; interpretado como BJ (Biografia de Jesus)'
        elif k.startswith('dominó ou dama'):
            modulo='Esportivo';comp='Jogos de Salão';tipo='jogo de salão';prova='A definir (Dominó ou Damas)';st='PENDENTE';obs='Só 1 jogo de salão por ER (art. 13); em aberto até receber as demais delegações'
        elif k=='tênis de mesa ou dama':
            modulo='Esportivo';comp='Jogos de Salão';tipo='jogo de salão';prova='A definir (Tênis de Mesa ou Damas)';st='PENDENTE';obs='Só 1 jogo de salão por ER (art. 13); ajustar conforme a próxima delegação'
        elif k in SAL: modulo='Esportivo';comp='Jogos de Salão';tipo='jogo de salão';prova=SAL[k]
        elif k=='futsal': modulo='Esportivo';comp='Jogos Coletivos';tipo='coletiva';prova='Futsal'
        elif k=='vôlei': modulo='Esportivo';comp='Jogos Coletivos';tipo='coletiva';prova='Vôlei';cd='Única (Adolescente e Juvenil)'
        elif k=='futsal ou vôlei': modulo='Esportivo';comp='Jogos Coletivos';tipo='coletiva';prova='A definir (Futsal ou Vôlei)';st='PENDENTE';obs='Informar qual'
        elif 'revezamento' in k and 'natação' in k:
            modulo='Esportivo';comp='Natação';tipo='coletiva (revezamento)';prova='Revezamento 4x25 metros nado livre';cd='Única (Adolescente e Juvenil)'
        elif 'revezamento' in k:
            modulo='Esportivo';comp='Atletismo';tipo='coletiva (revezamento)';prova='Revezamento 4x100 metros';cd='Única (Adolescente e Juvenil)'
        elif 'atletismo' in k:
            modulo='Esportivo';comp='Atletismo';tipo='individual'
            if k=='atletismo': prova='A definir (100 m, salto em distância, 1500 m ou revezamento 4x100 m)';st='PENDENTE';obs='Prova de atletismo em aberto até receber a próxima delegação'
            elif 'salto' in k:prova='Salto em Distância'
            elif '1500' in k:prova='1500 metros';cd='Única (Adolescente e Juvenil)'
            elif '50' in k:prova='50 metros'
            else:prova='100 metros'
        elif 'natação' in k or 'nadar' in k or 'nado' in k:
            modulo='Esportivo';comp='Natação';tipo='individual'
            if c=='Júnior':prova='50 metros nado livre'
            elif 'costas' in k:prova='50 metros nado costas';cd='Única (Adolescente e Juvenil)'
            elif '50' in k and 'livre' in k:prova='A definir (50 m livre só existe no Júnior; Adolescente: 50 m costas, 100 m livre ou revezamento)';st='PENDENTE';obs='Prova informada (50 m livre) não existe para Adolescente (art. 33)';cd='Única (Adolescente e Juvenil)'
            elif 'livre' in k or '100' in k:prova='100 metros nado livre';cd='Única (Adolescente e Juvenil)'
            else:prova=NAT_ABERTA;st='PENDENTE';obs='Prova de natação não informada; em aberto até receber as demais delegações';cd='Única (Adolescente e Juvenil)'
        else: raise SystemExit('?? '+t)
        rows.append(dict(delegacao=deleg,nome=nome,nascimento=d.isoformat() if d else '',idade_em_11_10_2026=idade,categoria=c,modulo=modulo,
          competicao=comp,sigla=sg,prova=prova,tipo=tipo,categoria_disputa=cd,situacao=st,papel='Titular',dupla='',observacao=obs,sugestao='',texto_original=t))
# José Saraiva
D1='Embaixada Pastor José Saraiva'
for b in open(B+'entrada/delegacao_jose_saraiva.txt',encoding='utf-8').read().strip().split('\n\n'):
    ls=[l.strip() for l in b.split('\n') if l.strip()]
    m=re.match(r'(.+?)\s*-\s*(\d\d)/(\d\d)/(\d{4})\s*-\s*(\w+)',ls[0])
    nome=titulo(re.sub(r'\s+',' ',m.group(1)).strip()); d=datetime.date(int(m.group(4)),int(m.group(3)),int(m.group(2)))
    assert m.group(5).capitalize().replace('Junior','Júnior')==cat(d)[1],nome
    items=[l.lstrip('- ').strip() for l in ls[1:]]
    if nome.startswith('Pedro Luan'): items=[i for i in items if i.lower()!='debate']  # removido do Debate (limite de 2)
    if nome.startswith('Davi Lucas'): items=['dominó' if i.lower()=='dominó ou dama' else i for i in items]  # Davi fixado em Damas
    add(D1,nome,d,items)
# Waldemiro Tymchak
D2='Embaixada Waldemiro Tymchak'
add(D2,'Francisco Rai Martins da Silva',datetime.date(2013,4,17),['tênis de mesa','bj','futsal','atletismo'])
add(D2,'Francisco Rodrigo Martins da Silva',datetime.date(2014,5,28),['dominó','futsal','natação'])

D3='Embaixada Jeff Brawner'
J=[('Davi da Silva',17,'Juvenil',['cgb','esgrima','natação 100 metros nado livre','natação revezamento 4x25','dama','futsal','vôlei']),
('Josué Barbosa Ferreira',16,'Juvenil',['cgo ou cgb','esgrima','dama','dominó','tênis de mesa','vôlei']),
('Bruno Cezar Dias Silva',15,'Juvenil',['cgo','pregador','dama','dominó','tênis de mesa','futsal','vôlei']),
('Guilherme da Silva de Paiva',15,'Juvenil',['cgb','esgrima','atletismo 100 metros','natação 100 metros livre','tênis de mesa','vôlei','futsal']),
('Josue Kaleby da Silva Cruz',14,'Adolescente',['bj','esgrima','atletismo 100 metros','natação 100 metros nado livre','tênis de mesa','dama','futsal']),
('Antônio Gabriel Oliveira Magalhães',14,'Adolescente',['cgo','esgrima','atletismo 100 metros','natação 50 metros livre','dominó','dama','futsal']),
('Afonso Daniel de Lima Alves',11,'Júnior',['bj','esgrima','atletismo 50 metros','natação 50 metros nado livre','dama','dominó','futsal']),
('João Miguel Barbosa Ferreira',10,'Júnior',['cj','esgrima','atletismo 50 metros','natação 50 metros nado livre','dama','dominó','futsal']),
('Davi Barroso de Sousa Melo',10,'Júnior',['cgb','pregador','dama','dominó','futsal'])]
_dts=[datetime.date(int(y),int(m),int(d)) for d,m,y in re.findall(r'^\s*(\d\d)/(\d\d)/(\d{4})\s*$',open(B+'entrada/delegacao_jeff_brawner.txt',encoding='utf-8').read(),re.M)]
assert len(_dts)==len(J)
DN={n:d for (n,_,_,_),d in zip(J,_dts)}
DIV=[]
for n,i,c,it in J:
    a,cc_=cat(DN[n])
    if a!=i or cc_!=c: DIV.append((n,i,c,DN[n],a,cc_))
    add(D3,n,DN[n],it)
print('DIVERGENCIAS',DIV)
for n,i,it in [('Josué Barbosa Ferreira',16,'atletismo salto'),('Josué Barbosa Ferreira',16,'montagem'),('Guilherme da Silva de Paiva',15,'bwah'),('Afonso Daniel de Lima Alves',11,'cgo'),('Antônio Gabriel Oliveira Magalhães',14,'debate'),('Josue Kaleby da Silva Cruz',14,'cgb'),('João Miguel Barbosa Ferreira',10,'montagem'),('Afonso Daniel de Lima Alves',11,'debate'),('João Miguel Barbosa Ferreira',10,'atletismo salto'),('Afonso Daniel de Lima Alves',11,'atletismo salto'),('Davi Barroso de Sousa Melo',10,'atletismo 50 metros'),('Guilherme da Silva de Paiva',15,'natação revezamento 4x25'),('Josue Kaleby da Silva Cruz',14,'natação revezamento 4x25'),('Bruno Cezar Dias Silva',15,'natação revezamento 4x25'),('Davi da Silva',17,'natação costas'),('João Miguel Barbosa Ferreira',10,'tênis de mesa'),('Josue Kaleby da Silva Cruz',14,'atletismo salto'),('Bruno Cezar Dias Silva',15,'atletismo salto'),('Davi da Silva',17,'atletismo 1500 metros')]:
    add(D3,n,DN[n.replace('Josue Kaleby da Silva Cruz','Josue Kaleby da Silva Cruz')],[it]); rows[-1].update(texto_original='',observacao='Inscrição nova, não constava na lista original (proposta da poda)')


for _it in ['bwah','debate']:
    add(D2,'Francisco Rai Martins da Silva',datetime.date(2013,4,17),[_it]); rows[-1].update(texto_original='',observacao='Inscrição nova, não constava na lista original')
# ---- 1ª poda (prioridade: José Saraiva > Waldemiro > Jeff Brawner; Jeff Brawner como suplentes) ----
def f(nome,key):
    return [r for r in rows if r['nome'].startswith(nome) and (key in (r['sigla'],r['prova']) or (key.startswith('A definir') and r['prova'].startswith(key)))]
def papel(nome,key,p,sug=''):
    rs=f(nome,key); assert len(rs)==1,(nome,key,len(rs))
    r=rs[0]; r['papel']=p
    if sug: r['sugestao']=sug
SUP=[('Matheus','Damas'),('Bruno','CGO'),('Josue Kaleby','BJ'),
('Davi da Silva','EB'),('Josué Barbosa','EB'),('Guilherme','EB'),
('Davi da Silva','100 metros nado livre'),('Guilherme','100 metros nado livre'),
('Josue Kaleby','100 metros nado livre'),('Antônio Gabriel','A definir (50 m livre'),
('Josué Barbosa','Damas'),('Josué Barbosa','Tênis de Mesa'),
('Bruno','Damas'),('Bruno','Tênis de Mesa')]
SUP+=[('Francisco Levy','PRE'),('Samuel','50 metros nado livre')]
for n,k in SUP: papel(n,k,'Suplente')
for n,k in [('João Miguel','Dominó'),('Josue Kaleby','Damas')]: papel(n,k,'Descartado')
papel('Samuel','Vôlei','Removido')
for n,k in [('Guilherme','CGB'),('Josué Barbosa','CGO ou CGB'),('Afonso','BJ'),('Antônio Gabriel','EB'),('Josue Kaleby','BJ'),('João Miguel','BJ'),('Afonso','EB'),('João Miguel','50 metros'),('Afonso','50 metros'),('Josue Kaleby','100 metros'),('Josué Barbosa','Salto em Distância'),('Francisco Rai','BJ'),('Samuel','50 metros nado livre'),('João Victor',NAT_ABERTA),('Guilherme','100 metros nado livre'),('Josue Kaleby','100 metros nado livre'),('Davi da Silva','100 metros nado livre'),('Francisco Rodrigo',NAT_ABERTA),('João Miguel','Damas'),('João Miguel','Dominó'),('Davi Barroso','Damas'),('Afonso','Dominó'),('Josue Kaleby','Damas'),('Antônio Gabriel','Dominó'),('Francisco Levy','Tênis de Mesa'),('Josué Barbosa','Tênis de Mesa'),('Bruno','Tênis de Mesa'),('Josué Barbosa','Damas'),('Bruno','Damas'),('Matheus','Damas'),('Davi da Silva','Revezamento 4x25 metros nado livre')]: papel(n,k,'Excluir')
rows[:]=[r for r in rows if r['papel']!='Excluir']
SUG={
}
for (n,k),v in SUG.items(): f(n,k)[0]['sugestao']=v
# itens em aberto de José Saraiva / Waldemiro com proposta
OPEN=[]
for n,k,v in OPEN: papel(n,k,'Em aberto',v)
f('Samuel','A definir (Dominó ou Damas)')[0].update(prova='Dominó',situacao='OK',observacao='',sugestao='',papel='Titular')
_r=f('Antônio Gabriel','A definir (50 m livre')[0]
_r.update(prova='50 metros nado costas',categoria_disputa='Única (Adolescente e Juvenil)',situacao='OK',observacao='',sugestao='',papel='Titular')
for n in ('Antônio Márcio',):
    _r=f(n,NAT_ABERTA)[0]
    _r.update(prova='Revezamento 4x25 metros nado livre',tipo='coletiva (revezamento)',categoria_disputa='Única (Adolescente e Juvenil)',situacao='OK',observacao='',sugestao='',papel='Titular')
_r=f('Francisco Rai','A definir (100 m, salto em distância, 1500 m ou revezamento 4x100 m)')[0]
_r.update(prova='Salto em Distância',situacao='OK',observacao='',sugestao='',papel='Titular')
rows[:]=[r for r in rows if r['papel'] not in ('Suplente','Removido','Descartado')]  # suplentes encerrados: titulares definidos
# Samuel (Júnior) sobe para a categoria Adolescente no Pregador (art. 19)
_r=f('Samuel','PRE')[0]; _r['categoria_disputa']='Adolescente'; _r['observacao']=(_r['observacao']+'; ' if _r['observacao'] else '')+'Júnior competindo na categoria Adolescente (art. 19)'
for r in rows:
    if r['papel'] in('Suplente','Descartado','Removido'): r['situacao']=r['papel'].upper()
ACT=lambda r:r['papel'] in('Titular','Em aberto')

DUPLAS={'Juvenil · Dupla 1':['João Victor','Pedro Luan'],'Juvenil · Dupla 2':['Josué Barbosa','Bruno'],'Adolescente · Dupla 1':['Davi Lucas','Francisco Rodrigo'],'Júnior · Dupla 1':['Samuel','Davi Barroso']}
for _d,_ns in DUPLAS.items():
    for _n in _ns: f(_n,'Dominó')[0]['dupla']=_d
def tag(r,msg,st='ATENÇÃO'):
    r['observacao']=(r['observacao']+'; ' if r['observacao'] else '')+msg
    if r['situacao']=='OK':r['situacao']=st
key=lambda r:r['sigla'] or r['prova']
cd_=lambda r:r['categoria_disputa'] if not r['categoria_disputa'].startswith('Única') else r['categoria']
cnt=collections.Counter((r['sigla'],cd_(r)) for r in rows if r['sigla'] and ACT(r))
for r in rows:
    if not ACT(r): continue
    if r['sigla'] and cnt[(r['sigla'],cd_(r))]>2:
        tag(r,f"{cnt[(r['sigla'],cd_(r))]} representantes na categoria {cd_(r)} (limite 2, art. 13 §1º)")
    if r['prova']=='Vôlei' and r['categoria']=='Júnior': r['observacao']='Júnior joga em categoria única Adolescente/Juvenil (arts. 19 e 31)'
    if r['competicao']=='Natação' and r['prova']=='A definir'[:0]+NAT_ABERTA:
        tag(r,'100 m livre é categoria única (art. 33 III): limite de 2 no total, já ocupado por Davi e Pedro','PENDENTE')
fut=collections.Counter(r['categoria'] for r in rows if r['prova']=='Futsal' and ACT(r))
vol=sum(1 for r in rows if r['prova']=='Vôlei' and ACT(r))
LIM=('100 metros','50 metros','Salto em Distância','1500 metros','100 metros nado livre','50 metros nado livre','Damas','Tênis de Mesa','Xadrez')
def kk(r): return (r['prova'], r['categoria_disputa'] if r['categoria_disputa'].startswith('Única') else r['categoria'])
dom=collections.Counter(r['categoria'] for r in rows if r['prova']=='Dominó' and ACT(r))
pc=collections.Counter(kk(r) for r in rows if r['prova'] in LIM and ACT(r))
for r in rows:
    if not ACT(r): continue
    if r['prova']=='Futsal' and not 5<=fut[r['categoria']]<=10:
        tag(r,f"Futsal {r['categoria']}: {fut[r['categoria']]} ER (exige 5 a 10, art. 40 §1º)")
    if r['prova']=='Vôlei' and not 6<=vol<=12:
        tag(r,f"Vôlei: {vol} ER declarados (exige 6 a 12, art. 41 §1º)")
    if r['prova'] in LIM and pc[kk(r)]>2:
        tag(r,f"{pc[kk(r)]} ER declarados em {r['prova']} ({kk(r)[1]}); limite 2 (art. 13 §1º)")
for n in set(r['nome'] for r in rows):
    rs=[r for r in rows if r['nome']==n and ACT(r)]
    sal=[r for r in rs if r['tipo']=='jogo de salão']
    if len(sal)>1:
        for r in sal: tag(r,f"ER com {len(sal)} jogos de salão ({', '.join(x['prova'] for x in sal)}); art. 13 permite só 1")
    esc=[r for r in rs if r['tipo']=='escrita']
    if len(esc)>1:
        for r in esc: tag(r,f"ER com {len(esc)} provas escritas; art. 13 permite só 1")
    if len(rs)>7:
        for r in rs: tag(r,'ER com mais de 7 modalidades (art. 13)')
_ix=['Júnior','Adolescente','Juvenil']
for r in rows:
    d=r['categoria_disputa']
    up=(r['categoria']=='Júnior') if d.startswith('Única') else _ix.index(d)>_ix.index(r['categoria'])
    r['sobe_categoria']='Sim' if up else ''
    if up: r['observacao']='Compete acima da própria categoria (arts. 19 e 31)'
os.makedirs(SAIDA,exist_ok=True)
cols=list(rows[0].keys())
def save(path,rs):
    with open(path,'w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rs)
save(SAIDA+'delegacao_jose_saraiva_oeer2026.csv',[r for r in rows if r['delegacao']==D1])
save(SAIDA+'delegacao_waldemiro_tymchak_oeer2026.csv',[r for r in rows if r['delegacao']==D2])
save(SAIDA+'delegacao_jeff_brawner_oeer2026.csv',[r for r in rows if r['delegacao']==D3])
save(SAIDA+'delegacao_daer_litoral_oeer2026.csv',rows)
print(len(rows),dict(fut),vol)
for kx,v in sorted(pc.items()):
    if v>2:print('LIM',kx,v)
cc=collections.Counter((r['sigla'],cd_(r)) for r in rows if r['sigla'] and ACT(r))
for kx,v in sorted(cc.items()):print('BIB',kx,v)
for r in rows:
    if r['situacao']!='OK':print(r['situacao'],r['papel'],r['delegacao'][-8:],r['nome'],'|',r['prova'] or r['competicao'],'|',r['observacao'])
fut=collections.Counter(r['categoria'] for r in rows if r['prova'] in('Futsal','A definir (Futsal ou Vôlei)'));print('futsal(inclui ou)',fut)
