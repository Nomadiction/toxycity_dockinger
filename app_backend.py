import os
import time
import requests
from fastapi import FastAPI
from tenacity import retry, stop_after_attempt, wait_exponential

app = FastAPI(title="MedTox Backend", description="API для токсичности лекарство–болезнь", version="0.1")

NCBI_API_KEY = os.getenv("NCBI_API_KEY")

PUBCHEM_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
PUBMED_BASE  = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# Контроль скорости для PubMed
PUBMED_MIN_INTERVAL = 0.35
_last_pubmed_call = 0.0

# Контроль скорости для PubMed
def spaced_pubmed():
    global _last_pubmed_call
    now = time.time()
    elapsed = now - _last_pubmed_call
    if elapsed < PUBMED_MIN_INTERVAL:
        time.sleep(PUBMED_MIN_INTERVAL - elapsed)
    _last_pubmed_call = time.time()

# Проверка ответа от сервера
def ok(r: requests.Response):
    if not r.ok:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
    return r

# Запросы к PubChem
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=6), reraise=True)
def pubchem_get_cid(drug: str):
    url = f"{PUBCHEM_BASE}/compound/name/{requests.utils.quote(drug)}/cids/JSON"
    r = ok(requests.get(url, timeout=20))
    data = r.json()
    return data.get("IdentifierList", {}).get("CID", [None])[0]

# Создание запроса для PubMed
def make_pubmed_term(drug: str, disease: str) -> str:
    return f"({drug}[Title/Abstract]) AND toxicity[Subheading] AND ({disease}[Title/Abstract])"

# Поиск в PubMed
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=6), reraise=True)
def pubmed_search(term: str, retmax: int = 10):
    spaced_pubmed()
    url = f"{PUBMED_BASE}/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": term,
        "retmax": retmax,
        "retmode": "json"
    }
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY
    r = ok(requests.get(url, params=params, timeout=30))
    return r.json().get("esearchresult", {}).get("idlist", [])

# Сводка из PubMed
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=6), reraise=True)
def pubmed_summary(pmids):
    if not pmids:
        return []
    spaced_pubmed()
    url = f"{PUBMED_BASE}/esummary.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "json"
    }
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY
    r = ok(requests.get(url, params=params, timeout=40))
    data = r.json().get("result", {})
    out = []
    for pmid in data.get("uids", []):
        it = data.get(pmid, {})
        out.append({
            "pmid": pmid,
            "title": it.get("title"),
            "journal": it.get("fulljournalname"),
            "pubdate": it.get("pubdate")
        })
    return out

# Endpoint для получения токсичности
@app.get("/toxicity")
def get_toxicity(drug: str, disease: str, retmax: int = 10):
    """
    Например: /toxicity?drug=Aspirin&disease=Peptic+ulcer+disease
    """
    cid = pubchem_get_cid(drug)
    term = make_pubmed_term(drug, disease)
    pmids = pubmed_search(term, retmax=retmax)
    summaries = pubmed_summary(pmids)
    return {
        "drug": drug,
        "disease": disease,
        "pubchem_cid": cid,
        "pubmed_term": term,
        "results": summaries
    }
