import csv, time, requests, xml.etree.ElementTree as ET
from collections import defaultdict
from typing import List

CSV_BG_RANKS = "bg_ranks.csv"   # baixe de https://boardgamegeek.com/data_dumps/bg_ranks (logado)
API = "https://boardgamegeek.com/xmlapi2/thing"
UA = "YourApp/1.0 (contato: voce@exemplo.com)"  # use um UA amigável
DELAY_SECONDS = 5                # guideline do BGG robots.txt
BATCH_SIZE = 20                  # limite da API

def chunked(seq: List[int], n: int):
    for i in range(0, len(seq), n):
        yield seq[i:i+n]

# 1) Ler IDs do CSV oficial (colunas usuais: id,name,yearpublished,rank,bayesaverage,average,usersrated)
ids = []
seed_rank_map = {}  # rank geral do CSV (pode ajudar quando a API não retornar rank)
with open(CSV_BG_RANKS, newline="", encoding="utf-8") as f:
    r = csv.DictReader(f)
    for row in r:
        gid = row.get("id") or row.get("game_id") or row.get("objectid")
        if gid and gid.isdigit():
            gid = int(gid)
            ids.append(gid)
            # alguns CSVs trazem "rank" como texto; guardamos para fallback
            seed_rank_map[gid] = row.get("rank")

print(f"Total IDs no seed: {len(ids)}")

def fetch_things(batch_ids: List[int]) -> str:
    params = {
        "id": ",".join(str(x) for x in batch_ids),
        "type": "boardgame",
        "stats": "1",  # traz ratings + ranks + averageweight
    }
    headers = {"User-Agent": UA}
    # tentativa + backoff simples para 500/503/429
    for attempt, wait in [(1, 0), (2, DELAY_SECONDS*2), (3, DELAY_SECONDS*4)]:
        if wait:
            time.sleep(wait)
        resp = requests.get(API, params=params, headers=headers, timeout=90)
        if resp.status_code in (500, 503, 429):
            continue
        resp.raise_for_status()
        return resp.text
    # se chegou aqui, última resposta
    resp.raise_for_status()
    return resp.text

def join_list(val):
    return ", ".join(val) if isinstance(val, list) else val

def parse_thing_xml(xml_text: str):
    root = ET.fromstring(xml_text)
    rows = []
    for item in root.findall("item"):
        d = defaultdict(list)
        d["id"] = item.attrib.get("id")
        d["type"] = item.attrib.get("type")

        # nomes
        primary_name = None
        alt_names = []
        for name in item.findall("name"):
            if name.attrib.get("type") == "primary":
                primary_name = name.attrib.get("value")
            else:
                v = name.attrib.get("value")
                if v: alt_names.append(v)
        d["name"] = primary_name or ""
        d["alt_names"] = alt_names

        # básicos
        for tag, key in [
            ("yearpublished", "yearpublished"),
            ("image", "image"),
            ("thumbnail", "thumbnail"),
            ("minplayers", "minplayers"),
            ("maxplayers", "maxplayers"),
            ("playingtime", "playingtime"),
            ("minplaytime", "minplaytime"),
            ("maxplaytime", "maxplaytime"),
            ("minage", "minage"),
        ]:
            el = item.find(tag)
            if el is not None:
                # na API alguns desses vêm como atributo "value"
                val = el.attrib.get("value") if "value" in (el.attrib or {}) else el.text
                if val: d[key] = val

        desc = item.find("description")
        if desc is not None and desc.text:
            d["description"] = desc.text.strip()

        # links (publisher, designer, artist, category, mechanic, family, expansion)
        link_map = {
            "boardgamepublisher": "publishers",
            "boardgamedesigner": "designers",
            "boardgameartist": "artists",
            "boardgamecategory": "categories",
            "boardgamemechanic": "mechanics",
            "boardgamefamily": "families",
            "boardgameexpansion": "expansions",
        }
        for link in item.findall("link"):
            ltype = link.attrib.get("type", "")
            value = link.attrib.get("value")
            if not value:
                continue
            key = link_map.get(ltype)
            if key:
                d[key].append(value)

        # polls úteis (num jogadores, idade sugerida, dependência de idioma)
        polls = item.findall("poll")
        for poll in polls:
            pname = poll.attrib.get("name")
            if pname == "suggested_numplayers":
                # colapsar opções em um resumo "N: (Best/Vote counts)"
                opts = []
                for results in poll.findall("results"):
                    num = results.attrib.get("numplayers")
                    counts = {r.attrib.get("value"): int(r.attrib.get("numvotes", "0"))
                              for r in results.findall("result")}
                    best = max(counts, key=counts.get) if counts else ""
                    opts.append(f"{num}:{best}({counts.get(best,0)})")
                d["poll_suggested_numplayers"] = "; ".join(opts)
            elif pname == "suggested_playerage":
                totals = []
                for results in poll.findall("results"):
                    for r in results.findall("result"):
                        age = r.attrib.get("value")
                        votes = r.attrib.get("numvotes")
                        totals.append(f"{age}:{votes}")
                d["poll_playerage"] = "; ".join(totals)
            elif pname == "language_dependence":
                # guarda a opção com mais votos
                best = ""
                best_votes = -1
                for results in poll.findall("results"):
                    for r in results.findall("result"):
                        v = int(r.attrib.get("numvotes", "0"))
                        if v > best_votes:
                            best_votes = v
                            best = r.attrib.get("value")
                if best:
                    d["poll_language_dependence"] = best

        # stats/ratings (inclui averageweight e ranks)
        stats = item.find("statistics")
        if stats is not None:
            ratings = stats.find("ratings")
            if ratings is not None:
                for tag, key in [
                    ("usersrated", "usersrated"),
                    ("average", "average"),
                    ("bayesaverage", "bayesaverage"),
                    ("stddev", "stddev"),
                    ("median", "median"),
                    ("owned", "owned"),
                    ("trading", "trading"),
                    ("wanting", "wanting"),
                    ("wishing", "wishing"),
                    ("numweights", "numweights"),
                    ("averageweight", "averageweight"),  # “peso/complexidade”
                ]:
                    el = ratings.find(tag)
                    if el is not None:
                        d[key] = el.attrib.get("value")

                # ranks (pega o “boardgame” geral e também captura outros)
                ranks = ratings.find("ranks")
                if ranks is not None:
                    other_ranks = []
                    for rk in ranks.findall("rank"):
                        name = rk.attrib.get("name")
                        val = rk.attrib.get("value")
                        friendly = rk.attrib.get("friendlyname")
                        if name == "boardgame":
                            d["rank_boardgame"] = val  # principal
                        else:
                            other_ranks.append(f"{friendly or name}:{val}")
                    if other_ranks:
                        d["ranks_other"] = "; ".join(other_ranks)

        # transformar listas em string
        rows.append({k: (join_list(v) if isinstance(v, list) else v) for k, v in d.items()})
    return rows

all_rows = []
for batch in chunked(ids, BATCH_SIZE):
    xml = fetch_things(batch)
    all_rows.extend(parse_thing_xml(xml))
    time.sleep(DELAY_SECONDS) 
    print(f"Fetched {len(all_rows)} registers") # respeita o guideline do BGG

print(f"Coletados {len(all_rows)} registros (via API).")

# 5) Ordenar pelo rank geral do BGG (boardgame). Não ranqueados vão ao fim.
def parse_rank(val):
    # valores podem vir como "Not Ranked" ou "0"; empurre para o fim
    if val is None:
        return float('inf')
    s = str(val).strip()
    if not s or s.lower().startswith("not"):
        return float('inf')
    try:
        v = int(float(s))
        if v <= 0:
            return float('inf')
        return v
    except:
        return float('inf')

# Fallback: se não veio da API, tenta do seed CSV
for row in all_rows:
    if not row.get("rank_boardgame"):
        try:
            rid = int(row.get("id"))
            row["rank_boardgame"] = seed_rank_map.get(rid)
        except:
            pass

all_rows.sort(key=lambda r: parse_rank(r.get("rank_boardgame")))

# 6) Salvar CSV final
out_cols = [
    "id","type","name","alt_names","yearpublished","description",
    "image","thumbnail",
    "minplayers","maxplayers","playingtime","minplaytime","maxplaytime","minage",
    "publishers","designers","artists","categories","mechanics","families","expansions",
    "poll_suggested_numplayers","poll_playerage","poll_language_dependence",
    "usersrated","average","bayesaverage","stddev","median",
    "owned","trading","wanting","wishing",
    "numweights","averageweight",
    "rank_boardgame","ranks_other"
]

with open("bgg_boardgames_full_sorted.csv","w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=out_cols, extrasaction="ignore")
    w.writeheader()
    for row in all_rows:
        w.writerow({k: row.get(k,"") for k in out_cols})

print("CSV final: bgg_boardgames_full_sorted.csv")
