#!/usr/bin/env python3
# Corre no GitHub Actions. Produz dados.json.gz = {gerado, de, ate, janela, regs:[...]}
# Fonte 1: Portal BASE/IMPIC (dados.gov.pt) — fiável, ~1 semana de atraso.
# Fonte 2: Diário da República (site) via Playwright — dias mais recentes.
import json, gzip, datetime, urllib.request, sys, os, re, asyncio

DATASET_ID = "66d72fbc58cd7a63dae28712"
JANELA_DIAS = 120
KEEP = {"Anúncio de procedimento", "Anúncio de concurso urgente"}

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

def iso2(s):  # dd-mm-aaaa -> aaaa-mm-dd
    m=re.search(r"(\d{2})-(\d{2})-(\d{4})", s or "")
    return f"{m[3]}-{m[2]}-{m[1]}" if m else ""

def categoria(tcs):
    s=" ".join(tcs or []) if isinstance(tcs,list) else str(tcs or "")
    if "Empreitada" in s: return "Obras"
    if "Concess" in s: return "Concessões"
    if "servi" in s.lower(): return "Serviços"
    if "bens" in s.lower(): return "Fornecimento de bens"
    return "Outros"

# ---------- Fonte 1: oficial ----------
def oficial(ano):
    meta=json.loads(http_get(f"https://dados.gov.pt/api/1/datasets/{DATASET_ID}/"))
    url=None
    for r in meta["resources"]:
        if r.get("format")=="json" and r.get("title","").lower()==f"anuncios{ano}.json":
            url=r.get("latest") or r["url"]; break
    if not url: return []
    raw=json.loads(http_get(url))
    out=[]
    for r in raw:
        if r.get("tipoActo") not in KEEP: continue
        dp=iso(r.get("dataPublicacao",""))
        if not dp: continue
        try: preco=float(r.get("PrecoBase")) if r.get("PrecoBase") not in (None,"") else None
        except Exception: preco=None
        out.append({"n":r.get("nAnuncio"),"data":dp,"ent":r.get("designacaoEntidade"),"nif":r.get("nifEntidade"),
            "obj":r.get("descricaoAnuncio"),"preco":preco,"cpv":r.get("CPVs"),"proc":r.get("modeloAnuncio"),
            "prazo":r.get("PrazoPropostas"),"dlim":iso(r.get("DataLimitePropostas","") or ""),
            "plat":r.get("PecasProcedimento"),"lotes":r.get("Lotes"),"amb":r.get("CriterAmbient"),
            "urg":1 if r.get("tipoActo")=="Anúncio de concurso urgente" else 0,
            "cat":categoria(r.get("tiposContrato")),"pdf":r.get("url")})
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
        "cat":categoria(tc),"pdf":"https://diariodarepublica.pt"+href}

async def dr_ao_vivo(de, ate):
    from playwright.async_api import async_playwright
    recs=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--no-sandbox"])
        ctx=await b.new_context(); pg=await ctx.new_page()
        await pg.goto("https://diariodarepublica.pt/dr/pesquisa-avancada", wait_until="domcontentloaded", timeout=60000)
        await pg.wait_for_timeout(5000)
        await pg.evaluate("()=>document.getElementById('CheckboxAtos10').click()")
        await pg.wait_for_timeout(2500)
        await pg.evaluate("""([de,ate])=>{function s(el,v){const p=Object.getPrototypeOf(el);Object.getOwnPropertyDescriptor(p,'value').set.call(el,v);el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));el.dispatchEvent(new Event('blur',{bubbles:true}));}s(document.getElementById('Input_DataDe'),de);s(document.getElementById('Input_DataAte'),ate);}""", [de, ate])
        await pg.wait_for_timeout(800)
        await pg.evaluate("()=>document.getElementById('Pesquisar').click()")
        await pg.wait_for_timeout(6000)
        # facet "Anúncio de procedimento"
        try:
            await pg.evaluate("""()=>{const t=[...document.querySelectorAll('.vscomp-toggle-button')][0];if(t)t.click();}""")
            await pg.wait_for_timeout(1200)
            await pg.evaluate("""()=>{const o=[...document.querySelectorAll('.vscomp-option')].find(o=>/Anúncio de procedimento/i.test(o.innerText));if(o)o.click();document.body.click();}""")
            await pg.wait_for_timeout(4000)
        except Exception as e: log("facet:", e)
        # paginação -> recolher hrefs
        hrefs=set()
        for pagina in range(1,40):
            got=await pg.evaluate("""(p)=>{const b=[...document.querySelectorAll('button.pagination-button')].find(x=>x.innerText.trim()===String(p));if(p>1){if(!b)return null;b.click();}return true;}""", pagina)
            if got is None: break
            await pg.wait_for_timeout(2800)
            hs=await pg.evaluate("""()=>[...document.querySelectorAll('a[href*=\"anuncio-procedimento\"]')].map(a=>a.getAttribute('href'))""")
            before=len(hrefs); hrefs.update(hs)
            if len(hrefs)==before and pagina>1: break
        hrefs=list(hrefs)
        log(f"DR: {len(hrefs)} anúncios a extrair ({de}..{ate})")
        # extrair detalhes em paralelo
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
                except Exception as e:
                    return None
                finally:
                    await pp.close()
        res=await asyncio.gather(*[um(h) for h in hrefs])
        recs=[r for r in res if r and r.get("n")]
        await b.close()
    return recs

def main():
    ano=datetime.date.today().year
    log("A obter oficial…")
    recs=oficial(ano)
    log(f"oficial: {len(recs)} anúncios")
    # DR ao vivo: do dia a seguir ao máximo oficial até hoje
    try:
        maxof=max((r["data"] for r in recs), default=None)
        hoje=datetime.date.today()
        ini=(datetime.date.fromisoformat(maxof)+datetime.timedelta(days=1)) if maxof else (hoje-datetime.timedelta(days=10))
        if ini<=hoje:
            de=ini.strftime("%Y-%m-%d"); ate=hoje.strftime("%Y-%m-%d")
            drs=asyncio.run(dr_ao_vivo(de, ate))
            log(f"DR ao vivo: {len(drs)} anúncios")
            recs+=drs
    except Exception as e:
        log("DR ao vivo indisponível:", repr(e))

    ultimo=max(r["data"] for r in recs)
    corte=(datetime.date.fromisoformat(ultimo)-datetime.timedelta(days=JANELA_DIAS)).isoformat()
    porN={}
    for r in recs:
        if r["data"]>=corte: porN[r["n"]]=r
    janela=sorted(porN.values(), key=lambda x:(x["data"], str(x["n"])))
    de=min(r["data"] for r in janela); ate=max(r["data"] for r in janela)
    obj={"gerado":datetime.date.today().isoformat(),"de":de,"ate":ate,"janela":JANELA_DIAS,"regs":janela}
    data=json.dumps(obj, ensure_ascii=False).encode("utf-8")
    with gzip.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"dados.json.gz"),"wb") as f:
        f.write(data)
    log(f"Escrito dados.json.gz: {len(janela)} anúncios, {de}..{ate}")

if __name__=="__main__":
    main()
