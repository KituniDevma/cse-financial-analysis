import re
import unicodedata
import pdfplumber
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Tuple, Dict
from tqdm import tqdm
import csv

# ----------------- CONFIG -----------------
ROOT = Path("data/raw_files")
OUT  = Path("data/processed/financial_data.csv")
USE_OCR = False
# ------------------------------------------

try:
    import pytesseract
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

MONTHS = {
    "JANUARY":1,"FEBRUARY":2,"MARCH":3,"APRIL":4,"MAY":5,"JUNE":6,
    "JULY":7,"AUGUST":8,"SEPTEMBER":9,"SEPT":9,"OCTOBER":10,"NOVEMBER":11,"DECEMBER":12
}

def _normalize(s: str | None) -> str:
    s = unicodedata.normalize("NFKC", s or "")
    s = s.replace("\xa0", " ")
    return re.sub(r"\s+", " ", s).strip()

def _strip_ordinal(day_text: str) -> str:
    return re.sub(r"(?i)(ST|ND|RD|TH)$", "", day_text)

def _parse_long_date(text: str) -> Optional[datetime.date]:
    parts = _normalize(text).upper().split()
    if len(parts) < 3: return None
    day = _strip_ordinal(parts[0])
    mon = MONTHS.get(parts[1].upper())
    yr  = parts[-1]
    if not (day.isdigit() and mon and yr.isdigit()): return None
    return datetime(int(yr), mon, int(day)).date()

def _parse_numeric_date(text: str) -> Optional[datetime.date]:
    m = re.fullmatch(r"(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})", _normalize(text))
    if not m: return None
    d, mth, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if y < 100: y += 2000 if y < 50 else 1900
    return datetime(y, mth, d).date()

def _extract_first_page_text_pdfplumber(pdf_path: Path) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        if not pdf.pages: return ""
        p1 = pdf.pages[0]
        txt = _normalize(p1.extract_text() or "")
        if txt: return txt
        words = p1.extract_words() or []
        return _normalize(" ".join(w["text"] for w in words)) if words else ""

PAT_HEADLINE_ANY   = re.compile(r"INTERIM\s+REPORT\s+FOR\s+THE\s+(QUARTER|YEAR)\s+ENDED", re.I)
PAT_AFTER_ENDED_TX = re.compile(r"\bENDED\b[\s:,-]*(\d{1,2}(?:ST|ND|RD|TH)?\s+[A-Z]{3,}\s+\d{4})", re.I)
PAT_AFTER_ENDED_NUM= re.compile(r"\bENDED\b[\s:,-]*(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})", re.I)
PAT_LONG_DATE      = re.compile(
    r"(\d{1,2}(?:ST|ND|RD|TH)?\s+(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|"
    r"JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\s+\d{4})", re.I
)

@dataclass
class ExtractionResult:
    file: str
    headline_kind: Optional[str]
    raw: Optional[str]
    iso_date: Optional[str]
    method: str
    note: str

def _try_find_in_text_first_page(text: str, ended_window: int = 80):
    m = PAT_AFTER_ENDED_TX.search(text)
    if m:
        raw = m.group(1).strip()
        return raw, _parse_long_date(raw), "text-direct"
    m = PAT_AFTER_ENDED_NUM.search(text)
    if m:
        raw = m.group(1).strip()
        return raw, _parse_numeric_date(raw), "text-numeric"
    for dm in PAT_LONG_DATE.finditer(text):
        start = dm.start(1)
        window = text[max(0, start - ended_window):start].upper()
        if "ENDED" in window:
            raw = dm.group(1).strip()
            return raw, _parse_long_date(raw), "text-proximity"
    return None, None, "no-match"

def extract_date_from_pdf_first_page(pdf_path: Path, use_ocr: bool = False) -> ExtractionResult:
    text = _extract_first_page_text_pdfplumber(pdf_path)
    headline_kind = None
    m_head = PAT_HEADLINE_ANY.search(text)
    if m_head:
        headline_kind = m_head.group(1).upper()
    if text:
        raw, parsed, method = _try_find_in_text_first_page(text)
        if raw:
            return ExtractionResult(str(pdf_path), headline_kind, raw, parsed.isoformat() if parsed else None, method, "pdfplumber")
    return ExtractionResult(str(pdf_path), headline_kind, None, None, "no-match", "no date on page 1")

# ---------- helpers ----------
AMOUNT_TOKEN = re.compile(r"\(?\d{1,3}(?:,\d{3})+(?:\.\d+)?\)?")
def _parse_amount_token(tok: str) -> Optional[int]:
    tok = tok.strip()
    neg = tok.startswith("(") and tok.endswith(")")
    if neg: tok = tok[1:-1]
    tok = tok.replace(",", "")
    try: return -int(round(float(tok))) if neg else int(round(float(tok)))
    except: return None

def _nth_amount_after(label_regex: re.Pattern, text_block: str, n: int) -> Optional[int]:
    m = label_regex.search(text_block)
    if not m: return None
    tail = text_block[m.end():]
    idx = 0
    for m2 in AMOUNT_TOKEN.finditer(tail):
        idx += 1
        if idx == n:
            return _parse_amount_token(m2.group(0))
    return None

# ---------- DIPD ----------
DIPD_LABELS = {
    "Revenue": re.compile(r"Revenue\s+from\s+contracts\s+with\s+customers", re.I|re.S),
    "Revenue": re.compile(r"customers", re.I|re.S),
    "COGS": re.compile(r"Cost\s+of\s+sales", re.I),
    "GrossProfit": re.compile(r"Gross\s+profit", re.I),
    "DistributionCosts": re.compile(r"Distribution\s+costs", re.I),
    "AdministrativeExpenses": re.compile(r"Administrative\s+expenses", re.I),
    "OtherIncomeAndGains": re.compile(r"Other\s+income\s+and\s+gains|Other\s+income", re.I),
    "NetIncome": re.compile(r"(Profit\s+for\s+the\s+period|Profit\s*/\s*\(loss\)\s+for\s+the\s+period)", re.I),
   # "NetIncome": re.compile(r"Profit\s+/\s+(loss)\s+for\s+the\s+period", re.I),
}
PL_START_RX = re.compile(r"STATEMENT\s+OF\s+PROFIT\s+OR\s+LOSS", re.I)
PL_END_RX   = re.compile(r"STATEMENT\S*\s+OF\s+FINANCIAL\s+POSITION", re.I)

def extract_dipd_metrics_from_pdf(pdf_path: Path, nth_after: int = 1):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = "\n".join(p.extract_text() or "" for p in pdf.pages)
    m_start = PL_START_RX.search(full_text)
    if not m_start: return {}
    m_end = PL_END_RX.search(full_text, pos=m_start.end())
    block = full_text[m_start.end(): m_end.start()] if m_end else full_text[m_start.end():]
    block = block.replace("\xa0", " ")
    block = re.sub(r"[ \t]+", " ", block)
    def grab(k): return _nth_amount_after(DIPD_LABELS[k], block, nth_after)
    revenue = grab("Revenue"); cogs = grab("COGS"); gross = grab("GrossProfit")
    dist = grab("DistributionCosts") or 0; admin = grab("AdministrativeExpenses") or 0
    other = grab("OtherIncomeAndGains") or 0; net = grab("NetIncome")
    opex = dist+admin; opinc = (gross or 0)+(other or 0)-opex if gross is not None else None
    return {"Revenue": revenue,"COGS": cogs,"GrossProfit": gross,
            "AdministrativeExpenses": admin or None,"DistributionCosts": dist or None,
            "OtherIncomeAndGains": other or None,"OperatingExpenses": opex,
            "OperatingIncome": opinc,"NetIncome": net}

# ---------- REXP ----------
REXP_LABELS = {
    "Revenue": re.compile(r"^Revenue\b", re.I|re.M),
    "COGS": re.compile(r"^\s*Cost\b", re.I | re.M),
    "GrossProfit": re.compile(r"Gross\s+profit", re.I),
    "DistributionCosts": re.compile(r"Distribution\s+Costs", re.I),
    "AdministrativeExpenses": re.compile(r"Administrative\s+Expenses", re.I),
    "OtherOperatingCosts": re.compile(r"Other\s+operating\s+(costs|expenses)", re.I),
    "OtherOperatingIncome": re.compile(r"Other\s+operating\s+income", re.I),
    "NetIncome": re.compile(r"(Profit\s+for\s+the\s+period|Profit\s+/(loss)\s+for\s+the\s+period|Profit\s+/(Loss)\s+for\s+the\s+period)", re.I),
}
REXP_PL_START = re.compile(r"CONSOLIDATED\s+INCOME\s+STATEMENT", re.I)
REXP_PL_END = re.compile(r"STATEMENT\S*\s+OF\s+FINANCIAL\s+POSITION", re.I)

def extract_rexp_metrics_from_pdf(pdf_path: Path, nth_after: int = 1):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = "\n".join(p.extract_text() or "" for p in pdf.pages)
    m_start = REXP_PL_START.search(full_text)
    if not m_start: return {}
    m_end = REXP_PL_END.search(full_text, pos=m_start.end())
    block = full_text[m_start.end(): m_end.start()] if m_end else full_text[m_start.end():]
    block = block.replace("\xa0", " "); block = re.sub(r"[ \t]+", " ", block)
    def grab(k): return _nth_amount_after(REXP_LABELS[k], block, nth_after)
    revenue = grab("Revenue"); cogs = grab("COGS"); gross = grab("GrossProfit")
    dist = grab("DistributionCosts") or 0; admin = grab("AdministrativeExpenses") or 0
    other_costs = grab("OtherOperatingCosts") or 0; other_inc = grab("OtherOperatingIncome") or 0
    net = grab("NetIncome")
    opex = dist+admin+other_costs; opinc = (gross or 0)+(other_inc or 0)-opex if gross is not None else None
    return {"Revenue": revenue,"COGS": cogs,"GrossProfit": gross,
            "AdministrativeExpenses": admin or None,"DistributionCosts": dist or None,
            "OtherIncomeAndGains": other_inc or None,"OperatingExpenses": opex,
            "OperatingIncome": opinc,"NetIncome": net}


# ---------- Batch ----------
def run(root: Path, out_csv: Path, use_ocr: bool = False):
    pdfs = sorted(root.rglob("*.pdf"))
    results = []
    for pdf in tqdm(pdfs, desc="Processing PDFs"):
        date_res = extract_date_from_pdf_first_page(pdf, use_ocr=use_ocr)
        row = {"file_name": pdf.name,"file_path": str(pdf),
               "headline_kind": date_res.headline_kind,
               "quarter_end_raw": date_res.raw,"quarter_end": date_res.iso_date}
        up = str(pdf).upper()
        try:
            if "DIPD" in up:
                nth = 1 if date_res.headline_kind == "QUARTER" else 3
                row.update(extract_dipd_metrics_from_pdf(pdf, nth_after=nth))
            elif "REXP" in up:
                nth = 1 
                row.update(extract_rexp_metrics_from_pdf(pdf, nth_after=nth))
            else:
                row["note"] = "P&L skipped (non-DIPD/REXP)"
        except Exception as e:
            row["error"] = f"P&L parse error: {type(e).__name__}: {e}"
        results.append(row)

        out_csv.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = ["file_name","file_path","headline_kind","quarter_end_raw","quarter_end",
                      "Revenue","COGS","GrossProfit","OperatingExpenses","OperatingIncome","NetIncome",
                      "AdministrativeExpenses","DistributionCosts","OtherIncomeAndGains","note","error"]
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in results:
                w.writerow({k: r.get(k) for k in fieldnames})
    return results

if __name__ == "__main__":
    results = run(ROOT, OUT, use_ocr=USE_OCR)
    print(f"CSV: {OUT.resolve()}")
    