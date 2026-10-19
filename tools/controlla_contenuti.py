#!/usr/bin/env python3
"""Controllo dei contenuti di sito-3lab contro la spec del nuovo sito.

    /usr/bin/python3 tools/controlla_contenuti.py [cartella-del-sito]

Legge l'HTML finale (mai il codice sorgente di un framework): termini vietati
assenti, link interni non rotti, e le regole di presenza di `regole.py`.
Una riga per regola: [ok] / [FALLITA] / [non attiva]. Exit 1 se una regola
attiva fallisce.
"""

import json
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path


CARTELLE_IGNORATE = {"_riuso", "tools", ".git", "node_modules", ".well-known"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
SALTA = {"script", "style", "noscript"}
ATTR_TESTO = ("aria-label", "alt", "title")
SCHEMA = re.compile(r"^[a-z][a-z0-9+.\-]*:", re.I)

# (nome, regex, flag): «Hub» e «A3» a parola intera, il resto come frase.
TERMINI = [
    ("Hub", r"\bhub\b", re.I),
    ("A3", r"(?<!ramework )\bA3\b", 0),  # «Framework A3» è ammesso (16/10): è il nome del metodo, A3 nudo no
    ("Prenota una demo", r"prenota una demo", re.I),
    ("Video Ads", r"video ads", re.I),
    ("Piano di marketing", r"piano di marketing", re.I),
    ("AI Stack", r"ai stack", re.I),
    ("Geologo Musone", r"geologo musone", re.I),
    ("Si vede (etichetta interna)", r"\bsi vede\b", re.I),
    ("C'è sotto (etichetta interna)", r"c['’]è sotto", re.I),
]

# Nell'hero, oltre a «Marcianise», non devono tornare hub, A3 e demo (pulsanti e metriche vecchi).
HERO_VIETATI = [("Hub", r"\bhub\b"), ("A3", r"\bA3\b"), ("demo", r"\bdemo\b")]


@dataclass
class Esito:
    regola: str
    stato: str  # ok | fallita | non attiva
    dettaglio: str = ""


@dataclass
class Regola:
    nome: str
    pagina: str
    tipo: str  # contiene | ordine | link | assente | redirect | senza-link | classi | senza-classi | popup-fisarmoniche
    valori: list
    attiva: bool = False


def norm(t):
    t = t.replace("’", "'").replace("‘", "'")
    t = re.sub(r"\s+", " ", t).strip().lower()
    return re.sub(r" ([,.;:!?])", r"\1", t)  # «<span>a</span>, b» si legge «a, b»


class Pagina(HTMLParser):
    def __init__(self, testo_html):
        super().__init__(convert_charrefs=True)
        self.testo, self.hero, self.meta, self.corpo = [], [], [], []  # corpo: fuori da footer e #contact
        self.ids, self.link, self.redirect = set(), [], False
        self.classi = set()  # tutte le classi CSS usate nella pagina
        self.popup, self._dlg, self._sum = [], None, False  # popup: un dict per <dialog class="sv-dlg">
        self.refresh = ""  # destinazione del meta refresh
        self.jsonld, self._in_ld = [], False  # testi grezzi degli <script type=ld+json>
        self._pila, self._salta, self._in_title = [], 0, False
        self.feed(testo_html)

    def _hero(self):
        return any(h for _, h, _ in self._pila)

    def _aggiungi(self, t):
        self.testo.append(t)
        if not any(c for _, _, c in self._pila):
            self.corpo.append(t)
        if self._hero():
            self.hero.append(t)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for k in ("id", "name"):
            if a.get(k):
                self.ids.add(a[k])
        self.classi.update((a.get("class") or "").split())
        if tag == "dialog" and "sv-dlg" in (a.get("class") or "").split():
            self._dlg = {"summary": [], "aperte": [], "h4": 0}
            self.popup.append(self._dlg)
        elif self._dlg is not None:
            if tag == "summary":
                self._dlg["summary"].append("")
                self._sum = True
            elif tag == "details":
                self._dlg["aperte"].append("open" in a)
            elif tag == "h4":
                self._dlg["h4"] += 1
            elif tag == "li" and "a3-i" in (a.get("class") or "").split():  # popup a due colonne: sezione del componente A3
                self._dlg["aperte"].append("is-open" in (a.get("class") or "").split())
            elif tag == "span" and "a3-t" in (a.get("class") or "").split():
                self._dlg["summary"].append("")
                self._sum = True
        if tag == "meta":
            if (a.get("http-equiv") or "").lower() == "refresh":
                self.redirect = True
                self.refresh = re.sub(r"^\s*\d+\s*;\s*url=", "", a.get("content") or "", flags=re.I).strip()
            if a.get("name") == "description" or a.get("property") == "og:title":
                self.meta.append(a.get("content") or "")
        if tag in ("a", "link") and a.get("href") is not None:
            self.link.append(a["href"])
        if tag == "title":
            self._in_title = True
        if not self._salta:
            for k in ATTR_TESTO:
                if a.get(k):
                    self._aggiungi(a[k])
        if tag in VOID:
            return
        self._pila.append((tag, "hero" in (a.get("class") or "").split(),
                           tag == "footer" or a.get("id") == "contact"))
        if tag in SALTA:
            self._salta += 1
        if tag == "script" and (a.get("type") or "").lower() == "application/ld+json":
            self._in_ld = True
            self.jsonld.append("")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag == "script":
            self._in_ld = False
        if tag in ("summary", "span"):
            self._sum = False
        if tag == "dialog":
            self._dlg = None
        for i in range(len(self._pila) - 1, -1, -1):
            if self._pila[i][0] == tag:
                for t, _, _ in self._pila[i:]:
                    if t in SALTA:
                        self._salta -= 1
                del self._pila[i:]
                break

    def handle_data(self, data):
        if self._sum:
            self._dlg["summary"][-1] += data
        if self._in_ld:
            self.jsonld[-1] += data
        elif self._in_title:
            self.meta.append(data)
        elif not self._salta and data.strip():
            self._aggiungi(data)


class Sito:
    def __init__(self, radice):
        self.radice = Path(radice).resolve()
        self._cache = {}
        self.file = sorted(
            p for p in self.radice.rglob("*.html")
            if not CARTELLE_IGNORATE & set(p.relative_to(self.radice).parts[:-1])
        )

    def pagina(self, p):
        if p not in self._cache:
            self._cache[p] = Pagina(p.read_text(encoding="utf-8", errors="replace"))
        return self._cache[p]

    def rel(self, p):
        return str(p.relative_to(self.radice))

    def risolvi(self, da, href):
        """Path di destinazione di un link interno, None se esterno/ignorabile,
        False se non esiste. Ritorna (path, frammento)."""
        if not href.strip() or SCHEMA.match(href) or href.startswith("//"):
            return None, ""
        percorso, _, frammento = href.partition("#")
        percorso = percorso.partition("?")[0]
        if not percorso:
            return da, frammento
        base = self.radice if percorso.startswith("/") else da.parent
        p = (base / percorso.lstrip("/")).resolve()
        for cand in (p, p / "index.html", p.with_name(p.name + ".html")):
            if cand.is_file():
                return cand, frammento
        return False, frammento


def controlla(radice, presenza=None):
    sito = Sito(radice)
    if presenza is None:
        import regole  # import tardivo: regole.py importa Regola da qui
        presenza = regole.PRESENZA
    return assenze(sito) + link(sito) + presenze(sito, presenza)


def assenze(sito):
    pagine = [(p, sito.pagina(p)) for p in sito.file]
    attive = [(p, pg) for p, pg in pagine if not pg.redirect]
    esiti = []
    for nome, rx, flag in TERMINI:
        dove = []
        for p, pg in attive:
            n = len(re.findall(rx, " ".join(pg.testo + pg.meta), flag))
            if n:
                dove.append("%s (%d)" % (sito.rel(p), n))
        esiti.append(esito("assenza: «%s»" % nome, dove))
    dove = []
    for p, pg in attive:
        if re.search("marcianise", " ".join(pg.hero), re.I):
            dove.append(sito.rel(p))
    esiti.append(esito("assenza: «Marcianise» nell'hero", dove))
    dove = []
    for p, pg in attive:
        testo_hero = " ".join(pg.hero)
        for nome, rx in HERO_VIETATI:
            if re.search(rx, testo_hero, re.I):
                dove.append("%s: %s" % (sito.rel(p), nome))
    esiti.append(esito("assenza: Hub, A3, demo nell'hero", dove))
    home = sito.radice / "index.html"
    pg = sito.pagina(home) if home.is_file() else None
    esiti.append(esito("assenza: «demo» nella homepage",
                       ["index.html"] if pg and re.search(r"\bdemo\b", " ".join(pg.testo), re.I) else []))
    esiti.append(esito("assenza: «Marcianise» in homepage fuori da contatti e footer",
                       ["index.html"] if pg and re.search("marcianise", " ".join(pg.corpo), re.I) else []))
    dove = [sito.rel(p) for p, pg in attive if re.search("marcianise", " ".join(pg.meta), re.I)]
    esiti.append(esito("assenza: «Marcianise» in title/description", dove))

    dove = []
    home = sito.radice / "index.html"
    if home in sito._cache or home.is_file():
        pg = sito.pagina(home)
        dove += ["#" + i for i in ("chatcms", "tricard") if i in pg.ids]
        dove += [h for h in pg.link if h in ("#chatcms", "#tricard")]
    esiti.append(esito("assenza: Chat-to-CMS e 3Card in homepage e menu", dove))

    dove = [d for d in ("siti-web", "siti-web.html") if (sito.radice / d).exists()]
    esiti.append(esito("assenza: pagina /siti-web", dove))
    dove = [sito.rel(p) for p, pg in pagine
            if p.relative_to(sito.radice).parts[0] == "tre-hub" and not pg.redirect]
    esiti.append(esito("assenza: pagine tre-hub/* (non redirect)", dove))
    return esiti


def esito(nome, dove):
    if dove:
        return Esito(nome, "fallita", "; ".join(dove))
    return Esito(nome, "ok")


def link(sito):
    rotti = []
    for p in sito.file:
        pg = sito.pagina(p)
        for href in pg.link:
            dest, fr = sito.risolvi(p, href)
            if dest is None:
                continue
            if dest is False:
                rotti.append("%s → %s" % (sito.rel(p), href))
            elif fr and fr != "top" and dest.suffix == ".html" and fr not in sito.pagina(dest).ids:
                rotti.append("%s → %s (ancora mancante)" % (sito.rel(p), href))
    return [esito("link interni non rotti", rotti)]


def presenze(sito, elenco):
    esiti = []
    for r in elenco:
        if not r.attiva:
            esiti.append(Esito(r.nome, "non attiva"))
            continue
        if r.tipo == "senza-link":  # r.valori: cartelle a cui nessuna pagina (non redirect) deve linkare
            manca = []
            for q in sito.file:
                if sito.pagina(q).redirect:
                    continue
                for h in sito.pagina(q).link:
                    dest = sito.risolvi(q, h)[0]
                    if dest and dest.relative_to(sito.radice).parts[0] in r.valori:
                        manca.append("%s → %s" % (sito.rel(q), h))
            esiti.append(Esito(r.nome, "fallita", "; ".join(manca)) if manca else Esito(r.nome, "ok"))
            continue
        p = sito.radice / r.pagina
        if not p.is_file():
            esiti.append(Esito(r.nome, "fallita", "pagina assente: " + r.pagina))
            continue
        pg = sito.pagina(p)
        testo = norm(" ".join(pg.testo))
        if r.tipo == "redirect":  # la pagina è solo un redirect verso r.valori[0]
            manca = [] if pg.redirect and pg.refresh == r.valori[0] else \
                ["non è un redirect verso " + r.valori[0] + " (trovato: %s)" % (pg.refresh or "nessuno")]
        elif r.tipo == "contiene":
            manca = [v for v in r.valori if norm(v) not in testo]
        elif r.tipo == "assente":
            manca = ["testo vecchio ancora presente: " + v for v in r.valori if norm(v) in testo]
        elif r.tipo == "ordine":
            manca, da = [], 0  # ogni voce si cerca dopo la precedente: le ripetizioni (menu) non contano
            for v in r.valori:
                i = testo.find(norm(v), da)
                if i < 0:
                    manca = ["ordine sbagliato o voce assente: " + " < ".join(r.valori)]
                    break
                da = i + len(norm(v))
        elif r.tipo == "faq-jsonld":
            manca = faq_jsonld(pg, testo, r.valori)
        elif r.tipo == "classi":  # tutte le classi in r.valori sono usate nella pagina
            manca = [v for v in r.valori if v not in pg.classi]
        elif r.tipo == "senza-classi":
            manca = ["classe vecchia ancora usata: " + v for v in r.valori if v in pg.classi]
        elif r.tipo == "popup-fisarmoniche":  # ogni popup: i <summary> = r.valori, solo il primo <details> aperto, niente h4
            manca = [] if pg.popup else ["nessun popup sv-dlg"]
            for i, d in enumerate(pg.popup, 1):
                if [norm(x) for x in d["summary"]] != [norm(v) for v in r.valori]:
                    manca.append("popup %d: summary diversi da %s" % (i, r.valori))
                if d["aperte"] != [True] + [False] * (len(r.valori) - 1):
                    manca.append("popup %d: deve aprirsi con la sola prima sezione aperta" % i)
                if d["h4"]:
                    manca.append("popup %d: ci sono ancora degli h4" % i)
        elif r.tipo == "id":
            manca = [v for v in r.valori if v not in pg.ids]
        elif r.tipo == "link":
            raggiunti = {sito.risolvi(p, h)[0] for h in pg.link}
            manca = [v for v in r.valori if (sito.radice / v).resolve() not in raggiunti]
        else:
            manca = ["tipo regola sconosciuto: " + r.tipo]
        esiti.append(Esito(r.nome, "fallita", "%s: manca %s" % (r.pagina, "; ".join(manca))) if manca
                     else Esito(r.nome, "ok"))
    return esiti


def faq_jsonld(pg, testo, domande):
    """JSON-LD FAQPage valido: ogni domanda attesa c'è e domanda e risposta sono identiche al testo visibile."""
    qa = []
    for grezzo in pg.jsonld:
        try:
            dati = json.loads(grezzo)
        except ValueError as e:
            return ["JSON-LD non valido: %s" % e]
        nodi = dati.get("@graph", [dati]) if isinstance(dati, dict) else dati
        for n in nodi:
            if isinstance(n, dict) and n.get("@type") == "FAQPage":
                for q in n.get("mainEntity", []):
                    qa.append((q.get("name", ""), (q.get("acceptedAnswer") or {}).get("text", "")))
    if not qa:
        return ["nessun JSON-LD FAQPage"]
    nomi = [norm(q) for q, _ in qa]
    manca = ["domanda assente nel JSON-LD: " + d for d in domande if norm(d) not in nomi]
    manca += ["testo JSON-LD diverso dalla pagina: " + q for q, a in qa
              if not a.strip() or norm(q) not in testo or norm(a) not in testo]
    return manca


def main(argv, presenza=None):
    radice = Path(argv[0]) if argv else Path(__file__).resolve().parent.parent
    esiti = controlla(radice, presenza=presenza)
    etichetta = {"ok": "[ok]", "fallita": "[FALLITA]", "non attiva": "[non attiva]"}
    for e in esiti:
        print(etichetta[e.stato], e.regola + (" — " + e.dettaglio if e.dettaglio else ""))
    n = {s: sum(e.stato == s for e in esiti) for s in etichetta}
    print("\n%d ok · %d fallite · %d non attive" % (n["ok"], n["fallita"], n["non attiva"]))
    return 1 if n["fallita"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
