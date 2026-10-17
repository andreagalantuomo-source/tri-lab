# TRI LAB — 3-LAB

Sito di **3-LAB**: ingegneria, economia e AI agentica per le PMI, organizzato in tre pilastri (Piano, Execution, Bussola) con l'AI come motore.

Sito statico (HTML/CSS/JS, GSAP + Three.js da CDN), hosting GitHub Pages.

## Struttura
- `index.html` — home
- `ai/`, `case-study/` — pagine L'AI e Case study (`index.html` ciascuna); stile e JS condivisi in `assets/pilastro.css` e `assets/pilastro.js`, esempi animati in `assets/esempi.*`
- `piano/`, `execution/`, `bussola/` — non sono più pagine: solo redirect alla sezione Servizi della home (`/#servizio-business-plan`, `/#servizio-automazioni`, `/#servizio-contabilita`)
- `tre-hub/` — solo redirect dei vecchi URL: `business-hub` e `operation-hub`→`/#servizi`, `creative-hub`→`/case-study/`, `servizio.html?s=…`→servizio più vicino nella home (default `/#servizi`)
- `card/`, `privacy/` — biglietto da visita digitale e informativa dell'app
- `logo.svg` — logo (3 triangoli intrecciati)
- `Anteprime/web/` — video anteprima dei siti realizzati
- `ChiSiamo/` — foto del team
- `_riuso/` — markup, CSS e JS tolti dalla home; non fa parte del sito, `robots.txt` lo esclude dai motori di ricerca
- `sitemap.xml`, `robots.txt` — solo le 3 pagine (home, ai, case-study)

## Controllo dei contenuti
Verifica che il sito rispetti la spec del nuovo sito (termini vietati assenti, link interni non rotti, elementi obbligatori presenti). Dalla cartella del sito, nel **terminale di sistema**:

```bash
/usr/bin/python3 tools/controlla_contenuti.py      # controlla il sito
/usr/bin/python3 tools/test_controlla_contenuti.py # test del controllo stesso
```

Le regole di presenza stanno in `tools/regole.py`: ogni ticket porta `attiva=True` sulle sue righe.
