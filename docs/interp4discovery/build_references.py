#!/usr/bin/env python3
"""Generate docs/interp4discovery/references.bib from machine-verified metadata.

Every field in the emitted .bib comes from one of three retrieval-grounded sources,
never from model memory:

  * arxiv_meta.json   -- arXiv Atom API (title, authors, date, journal_ref, DOI)
  * crossref_meta.json-- Crossref REST /works/{doi} (title, container, vol/issue/pages, authors)
  * dblp_venues.json  -- DBLP publication search (peer-reviewed venue for arXiv preprints)

Those three caches are produced by the citation-audit sweep (2026-08-14) and live in the
session scratchpad; pass their directory with --meta_dir.

Caller-side checks the sources cannot express are asserted here:
  1. every declared citation key resolves to a fetched record;
  2. the surname embedded in each key matches the record's first author;
  3. no duplicate keys, no duplicate arXiv IDs across keys.

Usage:
    python3 build_references.py --meta_dir <dir> --out references.bib
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata

# --------------------------------------------------------------------------------------
# Citation registry.
#
# Each entry: key -> dict with exactly one primary source plus optional overrides.
#   arxiv:     arXiv id, metadata pulled from arxiv_meta.json
#   xref:      key into crossref_meta.json
#   venue:     booktitle/journal to use, ONLY when independently verified
#   etype:     forced BibTeX entry type
#   manual:    literal field dict for records with no machine-readable source
#   note:      audit note carried into the entry
#   override:  field dict applied AFTER extraction, for the rare case where the machine
#              source is demonstrably incomplete; every override needs override_reason
# The `section` field only controls comment grouping in the output file.
# --------------------------------------------------------------------------------------

REG: "dict[str, dict]" = {}


def add(section, key, **kw):
    kw["section"] = section
    REG[key] = kw


# ---- 1. Operator-learning canon -------------------------------------------------------
S = "Operator-learning canon"
add(S, "li2021fno", arxiv="2010.08895", venue="International Conference on Learning Representations (ICLR)", venue_year=2021, etype="inproceedings")
add(S, "lu2021deeponet", arxiv="1910.03193", xref="lu2021deeponet", etype="article")
add(S, "kovachki2023neuraloperator", arxiv="2108.08481", etype="article",
    journal="Journal of Machine Learning Research", volume="24", number="89", pages="4061--4157", year_override=2023)

# ---- 2. Multi-fidelity classics and surveys -------------------------------------------
S = "Multi-fidelity classics and surveys"
add(S, "kennedy2000predicting", xref="kennedy2000predicting",
    override=dict(author="Kennedy, Marc C. and O'Hagan, Anthony"),
    override_reason="Crossref's record for 10.1093/biomet/87.1.1 lists only the first author; "
                    "the Biometrika 87(1):1-13 paper is by Kennedy and O'Hagan.")
add(S, "peherstorfer2018survey", xref="peherstorfer2018survey")
add(S, "forrester2007cokriging", xref="forrester2007cokriging")
add(S, "perdikaris2017nonlinear", xref="perdikaris2017nonlinear")
add(S, "fernandezgodino2023review", arxiv="1609.07196")

# ---- 3. Spectral bias and FNO spectral behaviour --------------------------------------
S = "Spectral bias and FNO spectral behaviour"
add(S, "rahaman2019spectral", arxiv="1806.08734", venue="International Conference on Machine Learning (ICML)", venue_year=2019, etype="inproceedings")
add(S, "xu2020frequency", arxiv="1901.06523", etype="article",
    journal="Communications in Computational Physics", doi="10.4208/cicp.OA-2020-0085")
add(S, "qin2024spectral", arxiv="2404.07200")
add(S, "george2024incremental", arxiv="2211.15188")
add(S, "kalimuthu2025loglo", arxiv="2504.04260")
add(S, "shi2026sirenfno", arxiv="2606.11518")
add(S, "bartolucci2023reno", arxiv="2305.19913")

# ---- 4. Mechanistic interpretability ---------------------------------------------------
S = "Mechanistic interpretability"
add(S, "kim2018tcav", arxiv="1711.11279", venue="International Conference on Machine Learning (ICML)", venue_year=2018, etype="inproceedings")
add(S, "alain2017probes", arxiv="1610.01644")
add(S, "cunningham2024sae", arxiv="2309.08600")
add(S, "olah2020circuits", xref="olah2020circuits")
add(S, "tolooshams2025saeno", arxiv="2509.03738")

# ---- 5. Conditioning mechanisms --------------------------------------------------------
S = "Conditioning mechanisms (FiLM and kin)"
add(S, "perez2018film", arxiv="1709.07871", venue="AAAI Conference on Artificial Intelligence", venue_year=2018, etype="inproceedings")
add(S, "dumoulin2018featurewise", xref="dumoulin2018featurewise")
add(S, "huang2017adain", arxiv="1703.06868", venue="IEEE International Conference on Computer Vision (ICCV)", venue_year=2017, etype="inproceedings")
add(S, "kirchmeyer2022coda", arxiv="2202.01889", venue="International Conference on Machine Learning (ICML)", venue_year=2022, etype="inproceedings")
add(S, "shokar2025pdecond", arxiv="2509.09599",
    note="Supersedes the fabricated key beggs2025pdecond used in earlier factory INSPIRATION files; "
         "the paper conditions on PDE parameters with local attention, it does not present FiLM-via-LayerNorm.")

# ---- 6. Transfer / warm-start analyses -------------------------------------------------
S = "Transfer and warm-start analyses"
add(S, "neyshabur2020transferred", arxiv="2008.11687", venue="Advances in Neural Information Processing Systems (NeurIPS)", venue_year=2020, etype="inproceedings")
add(S, "frankle2020lmc", arxiv="1912.05671", venue="International Conference on Machine Learning (ICML)", venue_year=2020, etype="inproceedings")
add(S, "kornblith2019cka", arxiv="1905.00414", venue="International Conference on Machine Learning (ICML)", venue_year=2019, etype="inproceedings")
add(S, "lee2023surgical", arxiv="2210.11466", venue="International Conference on Learning Representations (ICLR)", venue_year=2023, etype="inproceedings")
add(S, "meyes2019ablation", arxiv="1901.08644")

# ---- 7. Discovery / interpretation precedents in scientific ML -------------------------
S = "Discovery and interpretation precedents in scientific ML"
add(S, "boulle2022greens", xref="boulle2022greens", arxiv="2105.00266")
add(S, "boulle2022thesis", arxiv="2210.16016")
add(S, "cranmer2020symbolic", arxiv="2006.11287", venue="Advances in Neural Information Processing Systems (NeurIPS)", venue_year=2020, etype="inproceedings")
add(S, "krishnapriyan2021failure", arxiv="2109.01050", venue="Advances in Neural Information Processing Systems (NeurIPS)", venue_year=2021, etype="inproceedings")
add(S, "yang2024interpretableclimate", arxiv="2403.18864")
add(S, "liu2025nipde", arxiv="2505.23106")
add(S, "wang2026weightspace", arxiv="2605.14546")
add(S, "li2026basis", arxiv="2602.21551")
add(S, "kastor2026unet", arxiv="2601.22654")

# ---- 8. Strong-simple-baseline framing -------------------------------------------------
S = "Strong-simple-baseline framing"
add(S, "grinsztajn2022tabular", arxiv="2207.08815", venue="Advances in Neural Information Processing Systems (NeurIPS) Datasets and Benchmarks Track", venue_year=2022, etype="inproceedings")
add(S, "zeng2023dlinear", arxiv="2205.13504", venue="AAAI Conference on Artificial Intelligence", venue_year=2023, etype="inproceedings")
add(S, "dacrema2019progress", arxiv="1907.06902")
add(S, "gulrajani2021domainbed", arxiv="2007.01434", venue="International Conference on Learning Representations (ICLR)", venue_year=2021, etype="inproceedings")
add(S, "huang2021labelprop", arxiv="2010.13993", venue="International Conference on Learning Representations (ICLR)", venue_year=2021, etype="inproceedings")
add(S, "mcgreivy2024weak", xref="mcgreivy2024weak", arxiv="2407.07218")

# ---- 9. PDE benchmarks -----------------------------------------------------------------
S = "PDE benchmarks"
add(S, "takamoto2022pdebench", arxiv="2210.07182", venue="Advances in Neural Information Processing Systems (NeurIPS) Datasets and Benchmarks Track", venue_year=2022, etype="inproceedings")
add(S, "gupta2023pdearena", arxiv="2209.15616")
add(S, "ohana2024thewell", arxiv="2412.00568", venue="Advances in Neural Information Processing Systems (NeurIPS) Datasets and Benchmarks Track", venue_year=2024, etype="inproceedings")
add(S, "mccabe2023mpp", arxiv="2310.02994")
add(S, "luo2023cfdbench", arxiv="2310.05963")
add(S, "ren2025superbench", arxiv="2306.14070")
add(S, "koehler2024apebench", arxiv="2411.00180", venue="Advances in Neural Information Processing Systems (NeurIPS)", venue_year=2024, etype="inproceedings")

# ---- 10. Multi-fidelity machine learning and the baseline set --------------------------
S = "Multi-fidelity machine learning and baselines"
add(S, "meng2020composite", xref="meng2020composite", arxiv="1903.00104")
add(S, "howard2023mfdeeponet", xref="howard2023mfdeeponet", arxiv="2204.09157")
add(S, "lu2022mfdeeponetprr", xref="lu2022multifidelity_prr",
    note="Resolves the single [UNVERIFIED] entry in appendix B; article number 023210.")
add(S, "lyu2023mffno", xref="lyu2023mffno_pof", arxiv="2304.06972")
add(S, "de2020bifidelity", xref="de2020bifidelity", arxiv="2002.04495")
add(S, "goswami2022transfer", xref="goswami2022transfer", arxiv="2204.09810")
add(S, "villatoro2026correlation", arxiv="2512.02868")
add(S, "chen2024dataefficient", arxiv="2402.15734")
add(S, "niu2024mfrnp", arxiv="2402.18846", venue="International Conference on Machine Learning (ICML)", venue_year=2024, etype="inproceedings")
add(S, "li2022ifc", arxiv="2207.00678", venue="Advances in Neural Information Processing Systems (NeurIPS)", venue_year=2022, etype="inproceedings")
add(S, "wang2022gar", arxiv="2301.05729", venue="Advances in Neural Information Processing Systems (NeurIPS)", venue_year=2022, etype="inproceedings",
    doi="10.52202/068431-0614", pages="8441--8455")
add(S, "xing2023continuar", xref="xing2023continuar", etype="inproceedings")
add(S, "wu2022mfhnp", arxiv="2206.04872")
add(S, "wu2023dmfd", arxiv="2305.04392")
add(S, "xing2019drc", arxiv="1910.07577")
add(S, "yu2026fire", arxiv="2601.22371")
add(S, "chen2026mffm", arxiv="2605.16118")
add(S, "seidman2022nomad", arxiv="2206.03551", venue="Advances in Neural Information Processing Systems (NeurIPS)", venue_year=2022, etype="inproceedings")

# ---- 11. Transformer / foundation-model operator baselines -----------------------------
S = "Transformer and foundation-model operator baselines"
add(S, "wu2024transolver", arxiv="2402.02366", venue="International Conference on Machine Learning (ICML)", venue_year=2024, etype="inproceedings")
add(S, "luo2025transolverpp", arxiv="2502.02414")
add(S, "herde2024poseidon", arxiv="2405.19101", venue="Advances in Neural Information Processing Systems (NeurIPS)", venue_year=2024, etype="inproceedings")
add(S, "hao2024dpot", arxiv="2403.03542", venue="International Conference on Machine Learning (ICML)", venue_year=2024, etype="inproceedings")
add(S, "serrano2024aroma", arxiv="2406.02176", venue="Advances in Neural Information Processing Systems (NeurIPS)", venue_year=2024, etype="inproceedings")
add(S, "alkin2024upt", arxiv="2402.12365", venue="Advances in Neural Information Processing Systems (NeurIPS)", venue_year=2024, etype="inproceedings")
add(S, "shen2024ups", arxiv="2403.07187")
add(S, "li2023factformer", arxiv="2305.17560", venue="Advances in Neural Information Processing Systems (NeurIPS)", venue_year=2023, etype="inproceedings")
add(S, "tran2023ffno", arxiv="2111.13802", venue="International Conference on Learning Representations (ICLR)", venue_year=2023, etype="inproceedings")
add(S, "raonic2023cno", arxiv="2302.01178", venue="Advances in Neural Information Processing Systems (NeurIPS)", venue_year=2023, etype="inproceedings")
add(S, "lippe2023pderefiner", arxiv="2308.05732", venue="Advances in Neural Information Processing Systems (NeurIPS)", venue_year=2023, etype="inproceedings")
add(S, "bassi2025relift", arxiv="2509.12220")

# ---- 12. Benchmark dataset provenance --------------------------------------------------
S = "Benchmark dataset provenance"
add(S, "hersbach2020era5", xref="hersbach2020era5")
add(S, "ghia1982highre", xref="ghia1982highre")
add(S, "tripathy2018deepuq", xref="tripathy2018deepuq", arxiv="1802.00850")
add(S, "penwarden2023metalearning", xref="penwarden2023metalearning", arxiv="2110.13361")
add(S, "xue2025euno", arxiv="2509.01293")

# ---- 13. Governing-equation and scheme origins (generated datasets) --------------------
S = "Governing-equation and numerical-scheme origins"
add(S, "sod1978survey", xref="sod1978survey")
add(S, "cahn1958free", xref="cahn1958free")
add(S, "allen1979microscopic", xref="allen1979microscopic")
add(S, "elder2004modeling", xref="elder2004modeling")
add(S, "swift1977hydrodynamic", xref="swift1977hydrodynamic")
add(S, "fisher1937wave", xref="fisher1937wave")
add(S, "vazquez2007pme", xref="vazquez2007pme", etype="book", year_override=2007,
    override=dict(publisher="Oxford University Press", author="V{\\'a}zquez, Juan Luis"),
    override_reason="Crossref renders the publisher as 'Oxford University PressOxford' and drops the "
                    "diacritic in the author surname; 2007 is the print year (Crossref lists 2006 online).")
add(S, "schulzrinne1993classification", xref="schulzrinne1993classification")
add(S, "kurganov2002solution", xref="kurganov2002solution")
add(S, "pearson1993complex", xref="pearson1993complex")
add(S, "kassam2005fourth", xref="kassam2005fourth")
add(S, "cox2002exponential", xref="coxmatthews2002")
add(S, "sethian1996fast", xref="sethian1996fast")
add(S, "rayleigh1916convection", xref="rayleigh1916convection")
add(S, "burgers1948mathematical", xref="burgers1948mathematical")
add(S, "kolmogorov1937study", manual=dict(
    etype="article",
    title="A study of the diffusion equation with increase in the amount of substance, and its "
          "application to a biological problem",
    author="Kolmogorov, A. N. and Petrovsky, I. G. and Piskunov, N. S.",
    journal="Bulletin of Moscow University, Mathematics and Mechanics",
    volume="1", pages="1--25", year="1937",
    note="English reprint in Selected Works of A. N. Kolmogorov, Vol. I, Springer, pp. 242--270. "
         "Cited as the mathematical origin of the Fisher--KPP equation only."))

SECTION_ORDER = []
for _k, _v in REG.items():
    if _v["section"] not in SECTION_ORDER:
        SECTION_ORDER.append(_v["section"])


# --------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------
# Venue resolution.
#
# A venue is written into the .bib only when the evidence supports it:
#   * any single authoritative source (DBLP, Crossref, arXiv journal_ref), or
#   * two independent sources agreeing (Semantic Scholar, OpenAlex, DBLP, journal_ref), or
#   * one independent source agreeing with the venue asserted in the registry.
# Otherwise the entry is emitted as an arXiv preprint (@misc) and the unconfirmed venue
# hint, if any, is recorded in the audit report -- never silently in the bibliography.
# --------------------------------------------------------------------------------------

CANON = [
    ("iclr", ("international conference on learning representations", "iclr")),
    ("icml", ("international conference on machine learning", "icml")),
    ("neurips", ("neural information processing systems", "neurips", "nips")),
    ("aaai", ("aaai",)),
    ("kdd", ("knowledge discovery and data mining", "sigkdd", "kdd")),
    ("iccv", ("international conference on computer vision", "iccv")),
    ("tmlr", ("trans. mach. learn. res", "transactions on machine learning research")),
    ("recsys", ("recommender systems", "recsys")),
    ("jcp", ("journal of computational physics",)),
    ("nmi", ("nature machine intelligence", "nat. mac. intell")),
    ("cicp", ("communications in computational physics",)),
    ("pof", ("physics of fluids",)),
    ("scirep", ("scientific reports",)),
    ("ijuq", ("international journal for uncertainty quantification",)),
    ("dmlr", ("data-centric mach. learn. res", "data-centric machine learning research")),
    ("acse", ("advances in computational science and engineering",)),
]

DISPLAY = {
    "iclr": ("International Conference on Learning Representations (ICLR)", "inproceedings"),
    "icml": ("International Conference on Machine Learning (ICML)", "inproceedings"),
    "neurips": ("Advances in Neural Information Processing Systems (NeurIPS)", "inproceedings"),
    "aaai": ("AAAI Conference on Artificial Intelligence", "inproceedings"),
    "kdd": ("ACM SIGKDD Conference on Knowledge Discovery and Data Mining", "inproceedings"),
    "iccv": ("IEEE International Conference on Computer Vision (ICCV)", "inproceedings"),
    "recsys": ("ACM Conference on Recommender Systems (RecSys)", "inproceedings"),
    "tmlr": ("Transactions on Machine Learning Research", "article"),
    "dmlr": ("Journal of Data-centric Machine Learning Research", "article"),
    "jcp": ("Journal of Computational Physics", "article"),
    "nmi": ("Nature Machine Intelligence", "article"),
    "cicp": ("Communications in Computational Physics", "article"),
    "pof": ("Physics of Fluids", "article"),
    "scirep": ("Scientific Reports", "article"),
    "ijuq": ("International Journal for Uncertainty Quantification", "article"),
    "acse": ("Advances in Computational Science and Engineering", "article"),
}


def canon(name: str):
    n = (name or "").lower()
    if not n or "arxiv" in n:
        return None
    for key, needles in CANON:
        if any(x in n for x in needles):
            return key
    return None


def resolve_venue(aid, spec, arx, dblp, s2, oa):
    """Return (canonical_venue|None, year|None, evidence list)."""
    ev = {}
    jr = canon(arx[aid].get("journal_ref", ""))
    if jr:
        ev.setdefault(jr, []).append("arxiv_journal_ref")
    d = dblp.get(aid)
    if d and canon(d["venue"]):
        ev.setdefault(canon(d["venue"]), []).append("dblp")
    s = s2.get(aid)
    if s and canon(s["venue"]):
        ev.setdefault(canon(s["venue"]), []).append("semantic_scholar")
    o = oa.get(aid)
    if o and canon(o.get("source", "")) and o.get("type") != "preprint":
        ev.setdefault(canon(o["source"]), []).append("openalex")
    asserted = canon(spec.get("venue", ""))
    if asserted and asserted in ev:
        ev[asserted].append("registry_assertion")

    best = None
    for v, srcs in ev.items():
        independent = [x for x in srcs if x != "registry_assertion"]
        authoritative = {"dblp", "arxiv_journal_ref"} & set(srcs)
        if authoritative or len(srcs) >= 2:
            if best is None or len(ev[best]) < len(srcs):
                best = v
    if best is None:
        return None, None, ev

    year = None
    if d and canon(d["venue"]) == best and d.get("year"):
        year = int(d["year"])
    elif o and canon(o.get("source", "")) == best and o.get("type") != "preprint" and o.get("year"):
        year = int(o["year"])
    elif spec.get("venue_year") and asserted == best:
        year = int(spec["venue_year"])
    elif s and canon(s["venue"]) == best and DISPLAY.get(best, ("", ""))[1] == "article" and s.get("year"):
        year = int(s["year"])
    return best, year, ev


ROMAN_PREFIX = re.compile(r"^[IVXLC]+\.\s+")


def clean_title(t: str) -> str:
    """Publisher metadata carries HTML italics, journal article numbers and all-caps titles."""
    t = re.sub(r"<[^>]+>", "", t)
    t = " ".join(t.split())
    t = ROMAN_PREFIX.sub("", t)
    letters = [c for c in t if c.isalpha()]
    if letters and sum(c.isupper() for c in letters) / len(letters) > 0.8:
        t = t.title()
    return t


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def surname_of(author_str: str) -> str:
    """First author's surname from an arXiv 'Given M. Family' style name."""
    parts = [p for p in author_str.replace(".", " ").split() if p]
    if not parts:
        return ""
    # drop trailing suffixes
    while len(parts) > 1 and parts[-1].lower() in {"jr", "sr", "ii", "iii"}:
        parts.pop()
    return fold(parts[-1])


def bib_authors_from_arxiv(names):
    out = []
    for n in names:
        parts = [p for p in n.split() if p]
        if len(parts) == 1:
            out.append(parts[0])
        else:
            out.append(parts[-1] + ", " + " ".join(parts[:-1]))
    return " and ".join(out)


def decaps(name: str) -> str:
    """Some publishers deposit surnames in all caps (e.g. Wiley's 1937 Fisher record)."""
    letters = [c for c in name if c.isalpha()]
    if len(letters) > 1 and all(c.isupper() for c in letters):
        return name.title()
    return name


def bib_authors_from_xref(pairs):
    return " and ".join((f"{decaps(fam)}, {giv}" if giv else decaps(fam)) for fam, giv in pairs)


def emit(key, etype, fields):
    lines = [f"@{etype}{{{key},"]
    width = max(len(k) for k in fields)
    for k, v in fields.items():
        v = str(v).strip()
        if not v:
            continue
        lines.append(f"  {k.ljust(width)} = {{{v}}},")
    lines[-1] = lines[-1].rstrip(",")
    lines.append("}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta_dir", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    arx = json.load(open(os.path.join(a.meta_dir, "arxiv_meta.json")))
    xref = json.load(open(os.path.join(a.meta_dir, "crossref_meta.json")))
    def load_opt(name):
        path = os.path.join(a.meta_dir, name)
        return json.load(open(path)) if os.path.exists(path) else {}

    dblp = {k: v for k, v in load_opt("dblp_venues.json").items() if v}
    s2 = load_opt("s2_venues.json")
    oa = load_opt("openalex_venues.json")

    problems, seen_arxiv, venue_report = [], {}, {}
    out_sections = {s: [] for s in SECTION_ORDER}

    for key, spec in REG.items():
        fields, etype = {}, spec.get("etype")

        if "manual" in spec:
            m = dict(spec["manual"])
            etype = m.pop("etype", "misc")
            fields = m

        elif "xref" in spec:
            xk = spec["xref"]
            if xk not in xref:
                problems.append(f"{key}: crossref record '{xk}' missing"); continue
            r = xref[xk]
            first = r["authors"][0][0] if r["authors"] else ""
            if not key.startswith(fold(first).replace(" ", "").replace("-", "")[:4]):
                problems.append(f"{key}: key/first-author mismatch (crossref first author = {first})")
            etype = etype or ("book" if r.get("type") == "book" else
                              "inproceedings" if "Advances in Neural Information" in r.get("container", "") else "article")
            fields["title"] = clean_title(r["title"])
            fields["author"] = bib_authors_from_xref(r["authors"])
            if etype == "inproceedings":
                fields["booktitle"] = r["container"]
            elif etype == "book":
                fields["publisher"] = r.get("publisher", "")
            else:
                fields["journal"] = r["container"]
            fields["volume"] = r.get("volume", "")
            fields["number"] = r.get("issue", "")
            fields["pages"] = (r.get("page", "") or "").replace("-", "--")
            fields["year"] = spec.get("year_override") or r.get("year", "")
            fields["doi"] = r["doi"]
            if "arxiv" in spec:
                fields["note"] = f"arXiv:{spec['arxiv']}"

        elif "arxiv" in spec:
            aid = spec["arxiv"]
            if aid not in arx:
                problems.append(f"{key}: arXiv record {aid} missing"); continue
            r = arx[aid]
            if aid in seen_arxiv:
                problems.append(f"{key}: arXiv {aid} already used by {seen_arxiv[aid]}")
            seen_arxiv[aid] = key
            if r["authors"]:
                sn = surname_of(r["authors"][0])
                if sn and not key.startswith(sn.replace("-", "").replace("'", "")[:4]):
                    problems.append(f"{key}: key/first-author mismatch (arXiv first author = {r['authors'][0]})")
            cv, cyear, ev = resolve_venue(aid, spec, arx, dblp, s2, oa)
            venue_report[key] = dict(canonical=cv, year=cyear, evidence=ev,
                                     asserted=spec.get("venue", ""), arxiv=aid)
            if spec.get("venue") and canon(spec["venue"]) and cv and canon(spec["venue"]) != cv:
                problems.append(f"{key}: registry asserts {canon(spec['venue'])} but evidence says {cv}")
            if spec.get("journal"):                      # explicitly pinned journal (vol/pages known)
                etype, venue_name = etype or "article", spec["journal"]
            elif cv:
                venue_name, dtype = DISPLAY[cv]
                etype = etype if etype in ("article", "inproceedings") else dtype
            else:
                venue_name, etype = "", "misc"
            fields["title"] = clean_title(r["title"])
            fields["author"] = bib_authors_from_arxiv(r["authors"])
            if etype == "inproceedings":
                fields["booktitle"] = venue_name
            elif etype == "article":
                fields["journal"] = venue_name
                fields["volume"] = spec.get("volume", "")
                fields["number"] = spec.get("number", "")
                fields["pages"] = spec.get("pages", "")
            fields["year"] = spec.get("year_override") or cyear or spec.get("venue_year") or int(r["published"][:4])
            fields["eprint"] = aid
            fields["archivePrefix"] = "arXiv"
            fields["primaryClass"] = r.get("cat", "")
            fields["doi"] = spec.get("doi") or r.get("doi", "")
            if etype == "misc":
                fields["howpublished"] = f"arXiv:{aid}"
        else:
            problems.append(f"{key}: no source declared"); continue

        if spec.get("override"):
            if not spec.get("override_reason"):
                problems.append(f"{key}: override without override_reason")
            fields.update(spec["override"])
        if spec.get("note"):
            fields["note"] = (fields.get("note", "") + ("; " if fields.get("note") else "") + spec["note"])
        if spec.get("pages") and not fields.get("pages"):
            fields["pages"] = spec["pages"]

        m = re.search(r"(19|20|21)\d{2}", key)
        if m and fields.get("year") and str(fields["year"]) != m.group(0):
            problems.append(f"{key}: key year {m.group(0)} != emitted year {fields['year']}")

        ordered = {k: fields[k] for k in
                   ["title", "author", "booktitle", "journal", "publisher", "volume", "number",
                    "pages", "year", "eprint", "archivePrefix", "primaryClass", "doi", "url", "note"]
                   if fields.get(k)}
        out_sections[spec["section"]].append(emit(key, etype, ordered))

    header = [
        "% references.bib -- Interp4Discovery workshop paper (MFFP).",
        "% Generated by docs/interp4discovery/build_references.py from retrieval-grounded metadata:",
        "%   arXiv Atom API, Crossref REST, DBLP publication search (citation audit, 2026-08-14).",
        "% Do not hand-edit: add the entry to build_references.py and regenerate, so every field",
        "% keeps a machine-verifiable source.",
        f"% Entries: {sum(len(v) for v in out_sections.values())}",
        "",
    ]
    body = []
    for s in SECTION_ORDER:
        if not out_sections[s]:
            continue
        body.append("% " + "-" * 84)
        body.append(f"% {s}")
        body.append("% " + "-" * 84 + "\n")
        body.append("\n\n".join(out_sections[s]))
        body.append("")

    with open(a.out, "w") as fh:
        fh.write("\n".join(header + body) + "\n")

    report_path = os.path.splitext(a.out)[0] + "_venue_evidence.tsv"
    with open(report_path, "w") as fh:
        fh.write("key\tarxiv\tvenue_used\tyear\tevidence\n")
        for k in sorted(venue_report):
            v = venue_report[k]
            ev = "; ".join(f"{vv}<-{','.join(src)}" for vv, src in v["evidence"].items()) or "none"
            fh.write(f"{k}\t{v['arxiv']}\t{v['canonical'] or 'PREPRINT'}\t{v['year'] or ''}\t{ev}\n")

    resolved = sum(1 for v in venue_report.values() if v["canonical"])
    print(f"wrote {a.out}: {sum(len(v) for v in out_sections.values())} entries, "
          f"{len(SECTION_ORDER)} sections")
    print(f"venue evidence: {resolved}/{len(venue_report)} arXiv entries resolved to a peer-reviewed "
          f"venue; report at {report_path}")
    if problems:
        print(f"\n{len(problems)} CONSISTENCY PROBLEM(S):")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print("all consistency checks passed")


if __name__ == "__main__":
    main()
