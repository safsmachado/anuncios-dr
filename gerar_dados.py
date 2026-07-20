#!/usr/bin/env python3
# Corre no GitHub Actions. Produz dados.json.gz = {ver, gerado, hora, de, ate, janela, regs:[...]}
# Fonte 1: Portal BASE/IMPIC (dados.gov.pt) — fiável, ~1 semana de atraso.
# Fonte 2: Diário da República (site) via Playwright — dias mais recentes.
import json, gzip, datetime, urllib.request, sys, os, re, asyncio

VERSAO = "8.1"          # versão da app/dados (aparece na página)
DATASET_ID = "66d72fbc58cd7a63dae28712"
JANELA_DIAS = 120
KEEP = {"Anúncio de procedimento", "Anúncio de concurso urgente", "Anúncio de Alteração"}

import unicodedata as _ud
GAZ={
  "abrantes":"Santarém","agueda":"Aveiro","aguiar da beira":"Guarda","alandroal":"Évora",
  "albergaria-a-velha":"Aveiro","albufeira":"Faro","alcacer do sal":"Setúbal","alcanena":"Santarém",
  "alcobaca":"Leiria","alcochete":"Setúbal","alcoutim":"Faro","alenquer":"Lisboa",
  "alfandega da fe":"Bragança","alijo":"Vila Real","aljezur":"Faro","aljustrel":"Beja","almada":"Setúbal",
  "almeida":"Guarda","almeirim":"Santarém","almodovar":"Beja","alpiarca":"Santarém",
  "alter do chao":"Portalegre","alvaiazere":"Leiria","alvito":"Beja","amadora":"Lisboa","amarante":"Porto",
  "amares":"Braga","anadia":"Aveiro","angra do heroismo":"Açores","ansiao":"Leiria",
  "arcos de valdevez":"Viana do Castelo","arganil":"Coimbra","armamar":"Viseu","arouca":"Aveiro",
  "arraiolos":"Évora","arronches":"Portalegre","arruda dos vinhos":"Lisboa","aveiro":"Aveiro",
  "avis":"Portalegre","azambuja":"Lisboa","baiao":"Porto","barcelos":"Braga","barrancos":"Beja",
  "barreiro":"Setúbal","batalha":"Leiria","beja":"Beja","belmonte":"Castelo Branco","benavente":"Santarém",
  "bombarral":"Leiria","borba":"Évora","boticas":"Vila Real","braga":"Braga","braganca":"Bragança",
  "cabeceiras de basto":"Braga","cadaval":"Lisboa","caldas da rainha":"Leiria","calheta":"Madeira",
  "calheta de sao jorge":"Açores","camara de lobos":"Madeira","caminha":"Viana do Castelo",
  "campo maior":"Portalegre","cantanhede":"Coimbra","carrazeda de ansiaes":"Bragança",
  "carregal do sal":"Viseu","cartaxo":"Santarém","cascais":"Lisboa","castanheira de pera":"Leiria",
  "castelo branco":"Castelo Branco","castelo de paiva":"Aveiro","castelo de vide":"Portalegre",
  "castro daire":"Viseu","castro marim":"Faro","castro verde":"Beja","celorico da beira":"Guarda",
  "celorico de basto":"Braga","chamusca":"Santarém","chaves":"Vila Real","cinfaes":"Viseu",
  "coimbra":"Coimbra","condeixa-a-nova":"Coimbra","constancia":"Santarém","coruche":"Santarém",
  "corvo":"Açores","covilha":"Castelo Branco","crato":"Portalegre","cuba":"Beja","elvas":"Portalegre",
  "entroncamento":"Santarém","espinho":"Aveiro","esposende":"Braga","estarreja":"Aveiro","estremoz":"Évora",
  "evora":"Évora","fafe":"Braga","faro":"Faro","felgueiras":"Porto","ferreira do alentejo":"Beja",
  "ferreira do zezere":"Santarém","figueira da foz":"Coimbra","figueira de castelo rodrigo":"Guarda",
  "figueiro dos vinhos":"Leiria","fornos de algodres":"Guarda","freixo de espada a cinta":"Bragança",
  "fronteira":"Portalegre","funchal":"Madeira","fundao":"Castelo Branco","gaviao":"Portalegre",
  "gois":"Coimbra","golega":"Santarém","gondomar":"Porto","gouveia":"Guarda","grandola":"Setúbal",
  "guarda":"Guarda","guimaraes":"Braga","horta":"Açores","idanha-a-nova":"Castelo Branco","ilhavo":"Aveiro",
  "lagoa":"Faro","lagoa (acores)":"Açores","lagos":"Faro","lajes das flores":"Açores",
  "lajes do pico":"Açores","lamego":"Viseu","leiria":"Leiria","lisboa":"Lisboa","loule":"Faro",
  "loures":"Lisboa","lourinha":"Lisboa","lousa":"Coimbra","lousada":"Porto","macao":"Santarém",
  "macedo de cavaleiros":"Bragança","machico":"Madeira","madalena":"Açores","mafra":"Lisboa","maia":"Porto",
  "mangualde":"Viseu","manteigas":"Guarda","marco de canaveses":"Porto","marinha grande":"Leiria",
  "marvao":"Portalegre","matosinhos":"Porto","mealhada":"Aveiro","meda":"Guarda","melgaco":"Viana do Castelo",
  "mertola":"Beja","mesao frio":"Vila Real","mira":"Coimbra","miranda do corvo":"Coimbra",
  "miranda do douro":"Bragança","mirandela":"Bragança","mogadouro":"Bragança","moimenta da beira":"Viseu",
  "moita":"Setúbal","moncao":"Viana do Castelo","monchique":"Faro","mondim de basto":"Vila Real",
  "monforte":"Portalegre","montalegre":"Vila Real","montemor-o-novo":"Évora","montemor-o-velho":"Coimbra",
  "montijo":"Setúbal","mora":"Évora","mortagua":"Viseu","moura":"Beja","mourao":"Évora","murca":"Vila Real",
  "murtosa":"Aveiro","nazare":"Leiria","nelas":"Viseu","nisa":"Portalegre","nordeste":"Açores",
  "obidos":"Leiria","odemira":"Beja","odivelas":"Lisboa","oeiras":"Lisboa","oleiros":"Castelo Branco",
  "olhao":"Faro","oliveira de azemeis":"Aveiro","oliveira de frades":"Viseu","oliveira do bairro":"Aveiro",
  "oliveira do hospital":"Coimbra","ourem":"Santarém","ourique":"Beja","ovar":"Aveiro",
  "pacos de ferreira":"Porto","palmela":"Setúbal","pampilhosa da serra":"Coimbra","paredes":"Porto",
  "paredes de coura":"Viana do Castelo","pedrogao grande":"Leiria","penacova":"Coimbra","penafiel":"Porto",
  "penalva do castelo":"Viseu","penamacor":"Castelo Branco","penedono":"Viseu","penela":"Coimbra",
  "peniche":"Leiria","peso da regua":"Vila Real","pinhel":"Guarda","pombal":"Leiria","ponta delgada":"Açores",
  "ponta do sol":"Madeira","ponte da barca":"Viana do Castelo","ponte de lima":"Viana do Castelo",
  "ponte de sor":"Portalegre","portalegre":"Portalegre","portel":"Évora","portimao":"Faro","porto":"Porto",
  "porto de mos":"Leiria","porto moniz":"Madeira","porto santo":"Madeira","povoa de lanhoso":"Braga",
  "povoa de varzim":"Porto","povoacao":"Açores","praia da vitoria":"Açores","proenca-a-nova":"Castelo Branco",
  "redondo":"Évora","reguengos de monsaraz":"Évora","resende":"Viseu","ribeira brava":"Madeira",
  "ribeira de pena":"Vila Real","ribeira grande":"Açores","rio maior":"Santarém","sabrosa":"Vila Real",
  "sabugal":"Guarda","salvaterra de magos":"Santarém","santa comba dao":"Viseu","santa cruz":"Madeira",
  "santa cruz da graciosa":"Açores","santa cruz das flores":"Açores","santa maria da feira":"Aveiro",
  "santa marta de penaguiao":"Vila Real","santana":"Madeira","santarem":"Santarém",
  "santiago do cacem":"Setúbal","santo tirso":"Porto","sao bras de alportel":"Faro",
  "sao joao da madeira":"Aveiro","sao joao da pesqueira":"Viseu","sao pedro do sul":"Viseu",
  "sao roque do pico":"Açores","sao vicente":"Madeira","sardoal":"Santarém","satao":"Viseu","seia":"Guarda",
  "seixal":"Setúbal","sernancelhe":"Viseu","serpa":"Beja","serta":"Castelo Branco","sesimbra":"Setúbal",
  "setubal":"Setúbal","sever do vouga":"Aveiro","silves":"Faro","sines":"Setúbal","sintra":"Lisboa",
  "sobral de monte agraco":"Lisboa","soure":"Coimbra","sousel":"Portalegre","tabua":"Coimbra",
  "tabuaco":"Viseu","tarouca":"Viseu","tavira":"Faro","terras de bouro":"Braga","tomar":"Santarém",
  "tondela":"Viseu","torre de moncorvo":"Bragança","torres novas":"Santarém","torres vedras":"Lisboa",
  "trancoso":"Guarda","trofa":"Porto","vagos":"Aveiro","vale de cambra":"Aveiro","valenca":"Viana do Castelo",
  "valongo":"Porto","valpacos":"Vila Real","velas":"Açores","vendas novas":"Évora",
  "viana do alentejo":"Évora","viana do castelo":"Viana do Castelo","vidigueira":"Beja",
  "vieira do minho":"Braga","vila de rei":"Castelo Branco","vila do bispo":"Faro","vila do conde":"Porto",
  "vila do porto":"Açores","vila flor":"Bragança","vila franca de xira":"Lisboa",
  "vila franca do campo":"Açores","vila nova da barquinha":"Santarém",
  "vila nova de cerveira":"Viana do Castelo","vila nova de famalicao":"Braga","vila nova de foz coa":"Guarda",
  "vila nova de gaia":"Porto","vila nova de paiva":"Viseu","vila nova de poiares":"Coimbra",
  "vila pouca de aguiar":"Vila Real","vila real":"Vila Real","vila real de santo antonio":"Faro",
  "vila velha de rodao":"Castelo Branco","vila verde":"Braga","vila vicosa":"Évora","vimioso":"Bragança",
  "vinhais":"Bragança","viseu":"Viseu","vizela":"Braga","vouzela":"Viseu",
}
# concelhos ordenados por comprimento (nomes longos primeiro) para casar "vila nova de gaia" antes de "gaia"
_CONC=sorted(GAZ.keys(), key=len, reverse=True)
def _na(s):
    s=_ud.normalize("NFKD", s or "").encode("ascii","ignore").decode().lower()
    return re.sub(r"\s+"," ", s).strip()
_CONC_RE=re.compile(r"\b(" + "|".join(re.escape(c) for c in _CONC) + r")\b")
# entidade que é autarquia (para essas, o local de execução = o próprio concelho)
_AUT_RE=re.compile(r"munic[íi]pio|c[âa]mara municipal|servi[çc]os municipaliz|freguesia|junta de freguesia", re.I)
_CUE_RE=re.compile(r"(?:concelho|munic[íi]pio|freguesia|cidade|vila)\s+d[eoa]s?\s+([a-zâãáàéêíóôõúç\- ]{3,40})", re.I)

def _conc_para_zona(nome_norm):
    m=_CONC_RE.search(nome_norm)
    if m: return m.group(1), GAZ[m.group(1)]
    return None, None

def local_execucao(ent, obj, dr_text=None):
    """Devolve (concelho, zona/distrito) do LOCAL DE EXECUÇÃO — nunca a morada da entidade.
    Prioridade: campo 'Local de execução' do DR (dias ao vivo) > autarquia dona (o concelho é o local)
    > menção explícita no objeto ('concelho de X'). Caso contrário, vazio."""
    # 1) detalhe do DR ao vivo: campo Local de execução / prestação / NUTS
    if dr_text:
        m=re.search(r"Local\s+(?:principal\s+)?d[ea]\s+(?:execu[çc][ãa]o|presta[çc][ãa]o)[^:\n]*:\s*([^\n]+)", dr_text, re.I)
        if m:
            c,z=_conc_para_zona(_na(m.group(1)))
            if z: return _titulo(c), z
    # 2) entidade autárquica → o concelho dessa autarquia é o local
    if ent and _AUT_RE.search(ent):
        c,z=_conc_para_zona(_na(ent))
        if z: return _titulo(c), z
    # 3) menção no objeto ("...no concelho de X", "município de Y")
    if obj:
        for mm in _CUE_RE.finditer(obj):
            c,z=_conc_para_zona(_na(mm.group(1)))
            if z: return _titulo(c), z
    return "", ""

def _titulo(conc_norm):
    if not conc_norm: return ""
    return " ".join(w.capitalize() for w in conc_norm.replace("-"," - ").split())

def log(*a): print(*a, file=sys.stderr, flush=True)

def http_get(url, timeout=120):
    import time
    last=None
    for t in range(4):
        try:
            req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r: return r.read()
        except Exception as e:
            last=e; time.sleep(2*(t+1))
    raise last

def iso(s):
    try: return datetime.datetime.strptime(s, "%d/%m/%Y").strftime("%Y-%m-%d")
    except Exception: return None

def iso2(s):  # aceita aaaa-mm-dd (passa igual) OU dd-mm-aaaa / dd/mm/aaaa (converte)
    s=(s or "").strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s): return s
    m=re.search(r"(\d{2})[-/](\d{2})[-/](\d{4})", s)
    return f"{m[3]}-{m[2]}-{m[1]}" if m else ""

def categoria(tcs):
    s=" ".join(tcs or []) if isinstance(tcs,list) else str(tcs or "")
    if "Empreitada" in s: return "Obras"
    if "Concess" in s: return "Concessões"
    if "servi" in s.lower(): return "Serviços"
    if "bens" in s.lower(): return "Fornecimento de bens"
    return "Outros"

def is_fisc(obj, cpvs):
    if re.search(r"fiscaliza", obj or "", re.I): return True
    for c in (cpvs or []):
        c=str(c)
        if re.search(r"fiscaliza|supervis", c, re.I): return True
        code=c.split(" ")[0].split("-")[0]
        if code[:5] in ("71247","71248","71520","71521"): return True
    return False

def is_proj(obj, cpvs, cat_base):
    """Serviços de elaboração/revisão de projeto (arquitetura/engenharia).
    CPVs: 71240xx-71246xx (serviços de arquitetura/engenharia e planeamento, exceto 71247/71248=fiscalização)
    e 7132xxx (serviços de conceção técnica). Por texto, só quando o contrato é de Serviços."""
    for c in (cpvs or []):
        code=str(c).split(" ")[0].split("-")[0]
        if code[:5] in ("71240","71241","71242","71243","71244","71245","71246"): return True
        if code[:4]=="7132": return True
    if cat_base=="Serviços" and re.search(
        r"(elabora\w+|revis\w+|conce\w+|execu[çc]\w+)\s+d[eoa]s?\s+projec?to|projec?to\s+de\s+execu[çc]|estudo\s+pr[ée]vio", obj or "", re.I):
        return True
    return False

# ---------- Fonte 1: oficial ----------
def oficial(ano):
    meta=json.loads(http_get(f"https://dados.gov.pt/api/1/datasets/{DATASET_ID}/"))
    url=None
    for r in meta["resources"]:
        if r.get("format")=="json" and r.get("title","").lower()==f"anuncios{ano}.json":
            url=r.get("latest") or r["url"]; break
    if not url:
        log(f"oficial: ficheiro anuncios{ano}.json não encontrado")
        return []
    raw=json.loads(http_get(url))
    out=[]
    for r in raw:
        if r.get("tipoActo") not in KEEP: continue
        dp=iso(r.get("dataPublicacao",""))
        if not dp: continue
        try: preco=float(r.get("PrecoBase")) if r.get("PrecoBase") not in (None,"") else None
        except Exception: preco=None
        ta=r.get("tipoActo")
        cat_base=categoria(r.get("tiposContrato"))
        if ta=="Anúncio de Alteração":
            cat="Alterações de procedimento"
        elif is_fisc(r.get("descricaoAnuncio"), r.get("CPVs")):
            cat="Serviços de fiscalização"
        elif is_proj(r.get("descricaoAnuncio"), r.get("CPVs"), cat_base):
            cat="Serviços de projeto"
        else:
            cat=cat_base
        loc,dist=local_execucao(r.get("designacaoEntidade"), r.get("descricaoAnuncio"))
        out.append({"n":r.get("nAnuncio"),"data":dp,"ent":r.get("designacaoEntidade"),"nif":r.get("nifEntidade"),
            "obj":r.get("descricaoAnuncio"),"preco":preco,"cpv":r.get("CPVs"),"proc":r.get("modeloAnuncio"),
            "prazo":r.get("PrazoPropostas"),"dlim":iso(r.get("DataLimitePropostas","") or ""),
            "plat":r.get("PecasProcedimento"),"lotes":r.get("Lotes"),"amb":r.get("CriterAmbient"),
            "urg":1 if ta=="Anúncio de concurso urgente" else 0, "alt":1 if ta=="Anúncio de Alteração" else 0,
            "cat":cat,"local":loc,"dist":dist,"pdf":r.get("url")})
    return out

# ---------- Fonte 2: DR ao vivo (Playwright) ----------
def extrair(t, href):
    g=lambda re_: (re.search(re_,t,re.I).group(1).strip() if re.search(re_,t,re.I) else "")
    numM=re.search(r"n\.?[ºo]\s*(\d+)\s*/\s*(\d{4})", t)
    vs=g(r"Valor do pre[çc]o base do procedimento:\s*([\d.,]+)\s*EUR")
    try: preco=float(vs.replace(".","").replace(",",".")) if vs else None
    except Exception: preco=None
    tc=g(r"Tipo de [Cc]ontrato[^:\n]*:\s*([^\n]+)")
    obj=g(r"SUM[ÁA]RIO\s*([\s\S]+?)\s*TEXTO")
    return {"n":(numM[1]+"/"+numM[2]) if numM else "","data":iso2(g(r"Data de Publica[çc][ãa]o:\s*([\d-]+)")),
        "ent":g(r"Designa[çc][ãa]o da entidade adjudicante:\s*([^\n]+)"),"nif":g(r"NIPC:\s*(\d+)"),
        "obj":re.sub(r"\s+"," ",obj)[:300],"preco":preco,
        "cpv":[g(r"Vocabul[áa]rio [Pp]rincipal:\s*([^\n]+)")] if g(r"Vocabul[áa]rio [Pp]rincipal:\s*([^\n]+)") else [],
        "proc":g(r"Tipo de [Pp]rocedimento:\s*([^\n]+)"),"prazo":"",
        "dlim":iso2(g(r"Prazo para apresenta[çc][ãa]o das propostas:\s*([\d\-/]+)")),
        "plat":g(r"Plataforma eletr[óo]nica[^:\n]*:\s*([^\n]+)"),
        "lotes":["Sim"] if re.search(r"Procedimento com lotes\s*\?\s*Sim",t,re.I) else None,"amb":"",
        "urg":1 if re.search(r"concurso p[úu]blico urgente",t,re.I) else 0,
        "cat":_cat_dr(obj, [g(r"Vocabul[áa]rio [Pp]rincipal:\s*([^\n]+)")], tc),
        "local":_loc_dr(t,obj)[0],"dist":_loc_dr(t,obj)[1],
        "pdf":"https://diariodarepublica.pt"+href}

def _loc_dr(t, obj):
    ent=re.search(r"Designa[çc][ãa]o da entidade adjudicante:\s*([^\n]+)", t, re.I)
    return local_execucao(ent.group(1) if ent else "", obj, dr_text=t)

def _cat_dr(obj, cpvs, tc):
    base=categoria(tc)
    if is_fisc(obj, cpvs): return "Serviços de fiscalização"
    if is_proj(obj, cpvs, base): return "Serviços de projeto"
    return base

async def _recolher_dia(pg, dia, hrefs):
    """Pesquisa um único dia e recolhe os hrefs de todas as páginas (robusto à paginação com janela)."""
    await pg.goto("https://diariodarepublica.pt/dr/pesquisa-avancada", wait_until="domcontentloaded", timeout=60000)
    # espera a SPA renderizar o formulário (em vez de esperar um tempo fixo)
    await pg.wait_for_selector("#CheckboxAtos10", timeout=45000)
    await pg.wait_for_timeout(2500)
    # liga a 2.ª série e espera os campos de data aparecerem.
    # IMPORTANTE: a SPA às vezes ANULA o 1.º clique (re-render) — verificar e insistir.
    ok=False
    for tent in range(4):
        marcado=await pg.evaluate("()=>{const c=document.getElementById('CheckboxAtos10');return c?c.checked:null;}")
        if marcado is not True:
            await pg.evaluate("()=>{const c=document.getElementById('CheckboxAtos10');if(c)c.click();}")
        for _ in range(12):
            await pg.wait_for_timeout(800)
            if await pg.evaluate("()=>!!(document.getElementById('Input_DataDe')&&document.getElementById('Input_DataAte'))"):
                ok=True; break
        if ok: break
        log(f"DR {dia}: campos de data ainda não apareceram (tentativa {tent+1})")
    if not ok:
        raise RuntimeError(f"DR {dia}: campos de data não apareceram")
    # põe as datas e CONFIRMA que ficaram lá (senão repete)
    for tent in range(3):
        await pg.evaluate("""(dia)=>{function s(el,v){const p=Object.getPrototypeOf(el);Object.getOwnPropertyDescriptor(p,'value').set.call(el,v);el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));el.dispatchEvent(new Event('blur',{bubbles:true}));}s(document.getElementById('Input_DataDe'),dia);s(document.getElementById('Input_DataAte'),dia);}""", dia)
        await pg.wait_for_timeout(900)
        v=await pg.evaluate("()=>[document.getElementById('Input_DataDe').value,document.getElementById('Input_DataAte').value]")
        if v==[dia,dia]: break
    await pg.evaluate("()=>document.getElementById('Pesquisar').click()")
    # espera os resultados de verdade: o menu «Refinar Pesquisa» (vscomp) só existe na página de resultados
    for _ in range(30):
        await pg.wait_for_timeout(1000)
        if await pg.evaluate("()=>document.querySelectorAll('.vscomp-toggle-button').length>0"): break
    # facet "Anúncio de procedimento" (lê também o total anunciado pelo site, para autocontrolo)
    esperado=None
    try:
        await pg.evaluate("""()=>{const t=[...document.querySelectorAll('.vscomp-toggle-button')][0];if(t)t.click();}""")
        await pg.wait_for_timeout(1200)
        txt=await pg.evaluate("""()=>{const o=[...document.querySelectorAll('.vscomp-option')].find(o=>/Anúncio de procedimento/i.test(o.innerText));return o?o.innerText:'';}""")
        m=re.search(r"(\d+)\s*$", (txt or "").strip())
        esperado=int(m[1]) if m else None
        await pg.evaluate("""()=>{const o=[...document.querySelectorAll('.vscomp-option')].find(o=>/Anúncio de procedimento/i.test(o.innerText));if(o)o.click();document.body.click();}""")
        await pg.wait_for_timeout(4000)
    except Exception as e:
        log("facet:", e)
    antes_dia=len(hrefs)
    # Percorre TODAS as páginas. Validado ao vivo em 2026-07-10 (688/688 anúncios em 06–10/07):
    # a página ativa tem a classe "is--active" (ou aria-current="true"); só termina na última página;
    # a paginação some durante o carregamento, por isso espera-se que reapareça e que o nº ativo mude.
    for _ in range(60):
        for _t in range(10):   # espera a paginação renderizar (nos dias com ≤25 resultados não existe)
            n_btns=await pg.evaluate("()=>document.querySelectorAll('button.pagination-button').length")
            if n_btns: break
            await pg.wait_for_timeout(700)
        est=await pg.evaluate("""()=>{
          const btns=[...document.querySelectorAll('button.pagination-button')];
          const act=btns.find(b=>b.classList.contains('is--active')||b.classList.contains('is--act')||b.getAttribute('aria-current')==='true');
          const nums=btns.map(b=>parseInt(b.innerText)).filter(n=>!isNaN(n));
          return {cur: act?parseInt(act.innerText):1, ult: nums.length?Math.max(...nums):1};
        }""")
        hs=await pg.evaluate("""()=>[...document.querySelectorAll('a[href*=\"anuncio-procedimento\"]')].map(a=>a.getAttribute('href'))""")
        hrefs.update(hs)
        if est["cur"]>=est["ult"]: break     # última página: fim verdadeiro
        clicked=await pg.evaluate("""(cur)=>{
          const btns=[...document.querySelectorAll('button.pagination-button')];
          let nb=btns.find(b=>parseInt(b.innerText)===cur+1);
          if(!nb) nb=btns.find(b=>/seguinte|next|pr[oó]xim/i.test(b.getAttribute('aria-label')||''));
          if(!nb) return false;
          nb.click(); return true;
        }""", est["cur"])
        if not clicked: break
        for _t in range(24):   # espera a página ativa mudar de número (máx 12 s)
            await pg.wait_for_timeout(500)
            cur2=await pg.evaluate("""()=>{const act=[...document.querySelectorAll('button.pagination-button')].find(b=>b.classList.contains('is--active')||b.getAttribute('aria-current')==='true');return act?parseInt(act.innerText):0;}""")
            if cur2 and cur2!=est["cur"]: break
        await pg.wait_for_timeout(900)       # deixar os 25 links renderizar
    rec=len(hrefs)-antes_dia
    log(f"DR {dia}: +{rec} hrefs" + (f" (site diz {esperado})" if esperado is not None else ""))
    if esperado is not None and rec<esperado:
        log(f"AVISO: DR {dia} pode estar incompleto ({rec}<{esperado})")

async def dr_ao_vivo(dias):
    from playwright.async_api import async_playwright
    recs=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--no-sandbox"])
        ctx=await b.new_context(); pg=await ctx.new_page()
        hrefs=set()
        falhados=[]
        for dia in dias:
            try: await _recolher_dia(pg, dia, hrefs)
            except Exception as e: log("dia", dia, "falhou:", repr(e)); falhados.append(dia)
        # 2.ª volta para os dias que falharam (página nova, do zero)
        for dia in falhados:
            try:
                await pg.close(); pg=await ctx.new_page()
                await _recolher_dia(pg, dia, hrefs)
            except Exception as e: log("dia", dia, "falhou 2x:", repr(e))
        hrefs=list(hrefs)
        log(f"DR: {len(hrefs)} anúncios a extrair ({len(dias)} dias)")
        sem=asyncio.Semaphore(6)
        async def um(href):
            async with sem:
                pp=await ctx.new_page()
                try:
                    await pp.goto("https://diariodarepublica.pt"+href, wait_until="domcontentloaded", timeout=45000)
                    t=""
                    for _ in range(16):
                        await pp.wait_for_timeout(800)
                        t=await pp.evaluate("()=>document.body.innerText")
                        if "ENTIDADE ADJUDICANTE" in t: break
                    return extrair(t, href)
                except Exception:
                    return None
                finally:
                    await pp.close()
        res=await asyncio.gather(*[um(h) for h in hrefs])
        recs=[r for r in res if r and r.get("n")]
        await b.close()
    return recs

def hora_lisboa():
    try:
        from zoneinfo import ZoneInfo
        return datetime.datetime.now(ZoneInfo("Europe/Lisbon")).strftime("%H:%M")
    except Exception:
        return datetime.datetime.utcnow().strftime("%H:%M")

def main():
    hoje=datetime.date.today()
    # No início do ano a janela de 120 dias apanha o ano anterior — vai buscar os dois ficheiros
    anos=sorted({(hoje-datetime.timedelta(days=JANELA_DIAS+14)).year, hoje.year})
    recs=[]
    for ano in anos:
        log(f"A obter oficial {ano}…")
        try:
            parte=oficial(ano)
            log(f"oficial {ano}: {len(parte)} anúncios")
            recs+=parte
        except Exception as e:
            log(f"oficial {ano} falhou:", repr(e))
    # DR ao vivo: dias úteis desde o último dia de PROCEDIMENTOS no oficial até hoje (dia a dia, robusto)
    try:
        proc_dates=[r["data"] for r in recs if not r.get("alt")]
        maxof=max(proc_dates) if proc_dates else None
        ini=(datetime.date.fromisoformat(maxof)+datetime.timedelta(days=1)) if maxof else (hoje-datetime.timedelta(days=10))
        todos=[]; d=ini
        while d<=hoje:
            if d.weekday()<5: todos.append(d.strftime("%Y-%m-%d"))
            d+=datetime.timedelta(days=1)
        dias=todos[-12:]   # no máximo os 12 dias úteis mais recentes
        if dias:
            drs=asyncio.run(dr_ao_vivo(dias))
            log(f"DR ao vivo: {len(drs)} anúncios em {len(dias)} dias")
            recs+=drs
    except Exception as e:
        log("DR ao vivo indisponível:", repr(e))

    if not recs:
        log("ERRO: nenhum anúncio obtido (oficial e DR falharam). Não escrevo dados para não estragar o site.")
        sys.exit(1)

    ultimo=max(r["data"] for r in recs)
    corte=(datetime.date.fromisoformat(ultimo)-datetime.timedelta(days=JANELA_DIAS)).isoformat()
    porN={}
    for r in recs:               # o oficial vem primeiro na lista ⇒ fica com prioridade
        if r["data"]>=corte: porN.setdefault(r["n"], r)
    janela=sorted(porN.values(), key=lambda x:(x["data"], str(x["n"])))
    de=min(r["data"] for r in janela); ate=max(r["data"] for r in janela)
    obj={"ver":VERSAO,"gerado":hoje.isoformat(),"hora":hora_lisboa(),"de":de,"ate":ate,"janela":JANELA_DIAS,"regs":janela}
    data=json.dumps(obj, ensure_ascii=False).encode("utf-8")
    with gzip.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"dados.json.gz"),"wb") as f:
        f.write(data)
    log(f"Escrito dados.json.gz: {len(janela)} anúncios, {de}..{ate}")

if __name__=="__main__":
    main()
