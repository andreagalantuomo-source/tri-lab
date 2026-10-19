#!/usr/bin/env python3
"""Test del checker di contenuti — mini-siti in cartelle temporanee.

    /usr/bin/python3 tools/test_controlla_contenuti.py
"""

import tempfile
import unittest
from pathlib import Path

import controlla_contenuti as cc

PAGINA_OK = """<!doctype html><html><head><title>3-LAB</title>
<meta name="description" content="Consulenza per aziende"></head><body>
<header class="hero"><h1>Scala senza caos</h1></header>
<main id="top"><a href="#top">su</a><a href="piano/">piano</a>
<a href="https://esempio.it/">fuori</a><a href="mailto:a@b.it">mail</a></main>
<footer>Sede: Marcianise</footer></body></html>"""


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.radice = Path(self.tmp.name)
        self.scrivi("index.html", PAGINA_OK)
        self.scrivi("piano/index.html", "<html><body><h1>Piano</h1></body></html>")

    def tearDown(self):
        self.tmp.cleanup()

    def scrivi(self, nome, testo):
        p = self.radice / nome
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(testo, encoding="utf-8")

    def esiti(self, presenza=None):
        return cc.controlla(self.radice, presenza=presenza if presenza is not None else [])

    def fallite(self, presenza=None):
        return [e for e in self.esiti(presenza) if e.stato == "fallita"]


class Assenza(Base):
    def test_sito_conforme_non_ha_fallimenti(self):
        self.assertEqual(self.fallite(), [])

    def test_termine_vietato_fallisce_e_dice_dove(self):
        self.scrivi("index.html", PAGINA_OK.replace("Sede:", "Prenota una demo. Sede:"))
        f = [e for e in self.fallite() if "Prenota una demo" in e.regola]
        self.assertEqual(len(f), 1)
        self.assertIn("index.html", f[0].dettaglio)

    def test_hub_e_a3_vietati_ma_non_dentro_altre_parole(self):
        self.scrivi("index.html", PAGINA_OK.replace("Scala", "Creative Hub e Metodo A3"))
        regole = " ".join(e.regola for e in self.fallite())
        self.assertIn("Hub", regole)
        self.assertIn("A3", regole)
        self.scrivi("index.html", PAGINA_OK.replace("Scala", "hubris A30 chubby"))
        self.assertEqual(self.fallite(), [])

    def test_framework_a3_ammesso_ma_non_nell_hero(self):
        # Andrea (16/10): «Framework A3» è il nome del metodo e si può scrivere; «Metodo A3» e A3 nudo restano vietati.
        self.scrivi("index.html", PAGINA_OK.replace("</main>", "<p>Il Framework A3 in 6 step, framework A3</p></main>"))
        self.assertEqual([e for e in self.fallite() if "A3" in e.regola], [])
        self.scrivi("index.html", PAGINA_OK.replace("</main>", "<p>Il Metodo A3 e basta A3</p></main>"))
        self.assertEqual(len([e for e in self.fallite() if e.regola == "assenza: «A3»"]), 1)
        self.scrivi("index.html", PAGINA_OK.replace("<h1>", "<h1>Framework A3 "))
        self.assertEqual(len([e for e in self.fallite() if "hero" in e.regola and "Marcianise" not in e.regola]), 1)

    def test_script_e_style_ignorati(self):
        self.scrivi("index.html", PAGINA_OK.replace(
            "</body>", "<style>/* Hub A3 */</style><script>var s='Prenota una demo'</script></body>"))
        self.assertEqual(self.fallite(), [])

    def test_aria_label_e_title_contano_come_testo(self):
        self.scrivi("index.html", PAGINA_OK.replace("<h1>", '<h1 aria-label="Video Ads">'))
        self.assertEqual(len(self.fallite()), 1)

    def test_marcianise_vietata_nell_hero_ma_ammessa_nel_footer(self):
        self.assertEqual(self.fallite(), [])
        self.scrivi("index.html", PAGINA_OK.replace(
            "<h1>", '<h1><span class="sr-only">PMI a Marcianise</span>'))
        f = [e for e in self.fallite() if "hero" in e.regola]
        self.assertEqual(len(f), 1)

    def test_hero_senza_hub_a3_demo(self):
        for sporco in ("Esplora i 3 Hub", "Metodo A3", "Guarda la demo"):
            with self.subTest(sporco=sporco):
                self.scrivi("index.html", PAGINA_OK.replace("<h1>", "<h1>" + sporco + " "))
                hero = [e for e in self.fallite() if "hero" in e.regola and "Marcianise" not in e.regola]
                self.assertEqual(len(hero), 1)
        self.scrivi("index.html", PAGINA_OK.replace("</header>", "</header><p>Metodo A3 fuori dall'hero</p>"))
        self.assertEqual([e for e in self.fallite() if "hero" in e.regola], [])

    def test_home_senza_demo_in_nessun_punto(self):
        self.scrivi("index.html", PAGINA_OK.replace("</main>", "<p>La demo è gratis</p></main>"))
        f = [e for e in self.fallite() if "demo" in e.regola]
        self.assertEqual(len(f), 1)
        self.assertIn("index.html", f[0].dettaglio)
        self.scrivi("piano/index.html", "<html><body><p>una demo</p></body></html>")
        self.scrivi("index.html", PAGINA_OK)
        self.assertEqual([e for e in self.fallite() if "demo" in e.regola], [])  # solo la home

    def test_marcianise_in_home_solo_in_footer_o_contatti(self):
        self.assertEqual(self.fallite(), [])  # footer
        self.scrivi("index.html", PAGINA_OK.replace("</main>", '<section id="contact">Marcianise</section></main>'))
        self.assertEqual(self.fallite(), [])
        self.scrivi("index.html", PAGINA_OK.replace("</main>", "<p>Siamo a Marcianise</p></main>"))
        f = [e for e in self.fallite() if "fuori" in e.regola]
        self.assertEqual(len(f), 1)

    def test_marcianise_fuori_da_footer_dopo_un_footer_chiuso(self):
        self.scrivi("index.html", PAGINA_OK.replace("</footer>", "</footer><p>Marcianise</p>"))
        self.assertEqual(len([e for e in self.fallite() if "fuori" in e.regola]), 1)

    def test_marcianise_vietata_nei_meta(self):
        self.scrivi("index.html", PAGINA_OK.replace("Consulenza per", "Consulenza a Marcianise per"))
        self.assertEqual(len(self.fallite()), 1)

    def test_blocco_chatcms_e_tricard_vietati_in_home(self):
        self.scrivi("index.html", PAGINA_OK.replace("<main", '<section id="tricard"></section><main'))
        self.assertEqual(len(self.fallite()), 1)

    def test_pagina_siti_web_vietata(self):
        self.scrivi("siti-web/index.html", "<html><body>x</body></html>")
        self.assertEqual(len(self.fallite()), 1)

    def test_tre_hub_con_contenuto_fallisce_ma_redirect_passa(self):
        self.scrivi("tre-hub/x.html", "<html><body>Pagina vecchia</body></html>")
        self.assertEqual(len(self.fallite()), 1)
        self.scrivi("tre-hub/x.html",
                    '<html><head><meta http-equiv="refresh" content="0; url=/piano/"></head>'
                    "<body>Business Hub si e spostato</body></html>")
        self.assertEqual(self.fallite(), [])

    def test_cartelle_di_servizio_ignorate(self):
        for d in ("_riuso", "tools", ".git"):
            self.scrivi(f"{d}/a.html", "<html><body>Prenota una demo</body></html>")
        self.assertEqual(self.fallite(), [])


class Link(Base):
    def test_link_rotto_fallisce(self):
        self.scrivi("index.html", PAGINA_OK.replace("piano/", "nonesiste/"))
        f = self.fallite()
        self.assertEqual(len(f), 1)
        self.assertIn("nonesiste", f[0].dettaglio)

    def test_ancora_mancante_fallisce(self):
        self.scrivi("index.html", PAGINA_OK.replace('href="#top"', 'href="#manca"'))
        self.assertEqual(len(self.fallite()), 1)

    def test_link_assoluto_alla_radice_e_con_ancora_ok(self):
        self.scrivi("piano/index.html", '<html><body><h1 id="x">Piano</h1></body></html>')
        self.scrivi("index.html", PAGINA_OK.replace('href="piano/"', 'href="/piano/#x"'))
        self.assertEqual(self.fallite(), [])


class Presenza(Base):
    def regola(self, **kw):
        base = dict(nome="r", pagina="index.html", tipo="contiene", valori=["Scala senza caos"], attiva=True)
        base.update(kw)
        return [cc.Regola(**base)]

    def stato(self, regola):
        e = [x for x in self.esiti(regola) if x.regola == "r"]
        self.assertEqual(len(e), 1)
        return e[0].stato

    def test_regola_non_attiva_non_fallisce(self):
        self.assertEqual(self.stato(self.regola(attiva=False, valori=["assente"])), "non attiva")

    def test_contiene_ok_e_fallita_case_insensitive(self):
        self.assertEqual(self.stato(self.regola(valori=["scala SENZA caos"])), "ok")
        self.assertEqual(self.stato(self.regola(valori=["altro"])), "fallita")

    def test_apostrofo_tipografico_equivale_al_dritto(self):
        self.scrivi("index.html", PAGINA_OK.replace("Scala", "C’è sotto"))
        self.assertEqual(self.stato(self.regola(valori=["C'è sotto"])), "ok")

    def test_parole_in_tag_diversi_prima_di_una_virgola(self):
        # titolo con parole chiave in <span>: il testo visibile è «Scala, senza caos», senza spazio prima della virgola
        self.scrivi("index.html", PAGINA_OK.replace("<h1>Scala senza caos</h1>",
                    "<h1><span>Scala</span>, <span>senza</span> caos</h1>"))
        self.assertEqual(self.stato(self.regola(valori=["Scala, senza caos"])), "ok")

    def test_pagina_mancante_con_regola_attiva_fallisce(self):
        self.assertEqual(self.stato(self.regola(pagina="bussola/index.html")), "fallita")

    def test_pagina_mancante_con_regola_non_attiva_e_non_attiva(self):
        self.assertEqual(self.stato(self.regola(pagina="bussola/index.html", attiva=False)), "non attiva")

    def test_ordine(self):
        self.scrivi("index.html", PAGINA_OK.replace("Scala", "Alfa poi Beta"))
        self.assertEqual(self.stato(self.regola(tipo="ordine", valori=["Alfa", "Beta"])), "ok")
        self.assertEqual(self.stato(self.regola(tipo="ordine", valori=["Beta", "Alfa"])), "fallita")

    def test_ordine_vale_come_sequenza_anche_con_voci_ripetute(self):
        self.scrivi("index.html", PAGINA_OK.replace("Scala", "Beta menu. Alfa. Beta. Gamma"))
        self.assertEqual(self.stato(self.regola(tipo="ordine", valori=["Alfa", "Beta", "Gamma"])), "ok")
        self.assertEqual(self.stato(self.regola(tipo="ordine", valori=["Gamma", "Alfa"])), "fallita")

    def test_link_a_pagina(self):
        self.assertEqual(self.stato(self.regola(tipo="link", valori=["piano/index.html"])), "ok")
        self.assertEqual(self.stato(self.regola(tipo="link", valori=["bussola/index.html"])), "fallita")

    def test_id_presenti_nella_pagina(self):
        self.assertEqual(self.stato(self.regola(tipo="id", valori=["top"])), "ok")
        self.assertEqual(self.stato(self.regola(tipo="id", valori=["top", "servizio-x"])), "fallita")

    def test_assente_ok_se_il_testo_manca_fallita_se_c_e(self):
        self.assertEqual(self.stato(self.regola(tipo="assente", valori=["testo vecchio"])), "ok")
        self.assertEqual(self.stato(self.regola(tipo="assente", valori=["scala senza caos"])), "fallita")

    def test_assente_non_attiva_non_fallisce(self):
        self.assertEqual(self.stato(self.regola(tipo="assente", attiva=False)), "non attiva")

    def test_redirect_verso_il_bersaglio_indicato(self):
        self.scrivi("vecchia/index.html", '<html><head><meta http-equiv="refresh" content="0; url=/#servizi">'
                    "</head><body>spostata</body></html>")
        self.assertEqual(self.stato(self.regola(pagina="vecchia/index.html", tipo="redirect", valori=["/#servizi"])), "ok")
        self.assertEqual(self.stato(self.regola(pagina="vecchia/index.html", tipo="redirect", valori=["/#altro"])), "fallita")

    def test_redirect_fallisce_se_la_pagina_ha_contenuto_o_manca(self):
        self.assertEqual(self.stato(self.regola(pagina="piano/index.html", tipo="redirect", valori=["/#servizi"])), "fallita")
        self.assertEqual(self.stato(self.regola(pagina="manca/index.html", tipo="redirect", valori=["/#servizi"])), "fallita")

    def test_senza_link_a_cartelle_eliminate(self):
        # nel mini-sito la home linka piano/ (pagina con contenuto): la regola lo segnala e dice da dove
        r = self.regola(pagina="", tipo="senza-link", valori=["piano"])
        self.assertEqual(self.stato(r), "fallita")
        self.scrivi("index.html", PAGINA_OK.replace('<a href="piano/">piano</a>', ""))
        self.assertEqual(self.stato(r), "ok")

    def test_senza_link_ignora_le_pagine_redirect(self):
        self.scrivi("index.html", PAGINA_OK.replace('<a href="piano/">piano</a>', ""))
        self.scrivi("piano/index.html", '<html><head><meta http-equiv="refresh" content="0; url=/#servizi">'
                    '</head><body><a href="../piano/">noi</a></body></html>')
        self.assertEqual(self.stato(self.regola(pagina="", tipo="senza-link", valori=["piano"])), "ok")

    def test_ogni_regola_produce_una_riga_con_nome(self):
        e = self.esiti(self.regola())
        self.assertIn("r", [x.regola for x in e])


FAQ_QA = [(q, "Risposta a: " + q) for q in (
    "Cosa succede nella call conoscitiva?", "A che tipo di azienda siete adatti?",
    "Quanto dura un lavoro e come si svolge?", "Devo cambiare gli strumenti che uso oggi?",
    "Cosa significa che l'AI è il vostro motore?", "Cosa fate con i miei dati?", "Quanto costa?",
    "Posso prendere solo una parte?", "E se dopo il lavoro non ho una persona che gestisce gli strumenti?")]


def jsonld_faq(qa):
    import json
    ent = [{"@type": "Question", "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]
    return '<script type="application/ld+json">%s</script>' % json.dumps(
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": ent}, ensure_ascii=False)


SEZIONI = [  # nuova home, in ordine di pagina
    ("hero", "Ingegneria, economia ed AI agentica per scalare senza caos. Uniamo ingegneria, rigore economico e "
             "AI agentica per costruire le proporzioni strutturali perfette con cui scalare. "
             "Arriviamo. Discutiamo. Automatizziamo. Voi vincete. Il metodo delle grandi aziende, alla portata di una PMI. Prenota una call conoscitiva"),
    ("cosa", "Cosa facciamo. 01 Analizziamo i tuoi dati. 02 Ti aiutiamo a decidere dove portare la tua azienda. "
             "03 Costruiamo con te il sistema per arrivarci. "
             "04 Ti forniamo la bussola per accorgerti subito quando stai deviando. "
             "Dove vado? Come ci arrivo? Sto deviando?"),
    ("servizi", "Cuciti su misura. Business planning pianificazione. Automazioni agentiche esecuzione. Company brain e AI operating "
                "system. Gestionali automatizzati. Sito web. Business development e growth. "
                "Contabilità manageriale controllo. Cos'è. A cosa serve. Come lo facciamo. Cosa ricevi. Per chi è. "
                "Controllo: a ogni passo misuriamo il risultato e correggiamo la rotta. Non sai da dove partire? "
                "Pianificazione strategica e organizzazione. Analisi di mercato e posizionamento. "
                "Business model design. Piano economico-finanziario. "
                "Costi reali per prodotto e cliente. Budget. Scostamenti"),
    ("come", "Il nostro framework A3"),
    ("ai", "Qual è il ruolo dell'AI? AI agentica: esegue compiti, non solo risponde. Si istruisce. "
           "Si adatta all'ecosistema aziendale. Si mette a disposizione del team. "
           "Si usa come strumento di collaborazione avanzato. Chi aspetta continua a spendere ore preziose. "
           "Scopri come lavora l'AI"),
    ("case", "Il nostro portfolio. Valentino Immobiliare"),
    ("chi", "economisti ingegnere gestionale"),
    ("faq", "Hai ancora domande? Scrivici. " + " ".join(q + " " + a for q, a in FAQ_QA)),
    ("call", "gratuita 30 minuti"),
]


class NuovaHome(Base):
    def regole_nuova_home(self):
        import dataclasses
        import regole
        return [dataclasses.replace(r, attiva=True) for r in regole.PRESENZA if r.nome.startswith("nuova home:")]

    def home(self, sezioni):
        import regole
        ids = " ".join('<i id="servizio-%s"></i>' % x for x in regole.SERVIZI_SLUG)
        extra = {"servizi": ids + '<i class="sv-bg"></i><ul><li class="sv-card glass">c</li></ul>' + popup()}
        corpo = "".join('<section id="%s"><p>%s</p>%s</section>' % (k, t, extra.get(k, ""))
                        for k, t in sezioni)
        self.scrivi("index.html", "<html><body>%s%s</body></html>" % (corpo, jsonld_faq(FAQ_QA)))

    def fallite_nuova_home(self):
        regole = self.regole_nuova_home()
        nomi = {r.nome for r in regole}
        return [e for e in self.esiti(regole) if e.stato == "fallita" and e.regola in nomi]

    def test_le_regole_nuova_home_esistono(self):
        import regole
        nuove = [r for r in regole.PRESENZA if r.nome.startswith("nuova home:")]
        self.assertGreaterEqual(len(nuove), 8)

    def test_regole_dell_hero_attive(self):
        import regole
        hero = [r for r in regole.PRESENZA if r.nome.startswith("nuova home:") and "hero" in r.nome]
        self.assertGreaterEqual(len(hero), 3)
        self.assertEqual([r.nome for r in hero if not r.attiva], [])

    def test_regole_dei_servizi_attive_con_ancore(self):
        import regole
        sv = [r for r in regole.PRESENZA if r.nome.startswith("nuova home:") and "servizi" in r.nome]
        self.assertGreaterEqual(len(sv), 3)
        self.assertEqual([r.nome for r in sv if not r.attiva], [])
        self.assertTrue(any(r.tipo == "id" and len(r.valori) == 8 for r in sv))

    def test_regola_ordine_sezioni_attiva(self):
        import regole
        o = [r for r in regole.PRESENZA if r.nome == "nuova home: ordine delle sezioni"]
        self.assertEqual([r.attiva for r in o], [True])

    def test_home_conforme_passa_tutte(self):
        self.home(SEZIONI)
        self.assertEqual(self.fallite_nuova_home(), [])

    def test_sezioni_in_ordine_sbagliato_falliscono(self):
        s = list(SEZIONI)
        s[2], s[3] = s[3], s[2]  # A3 prima dei servizi
        self.home(s)
        self.assertTrue(any("ordine" in e.regola for e in self.fallite_nuova_home()))

    def test_sezione_mancante_fallisce(self):
        for chiave in ("faq", "servizi", "come", "cosa", "ai"):
            with self.subTest(chiave=chiave):
                self.home([x for x in SEZIONI if x[0] != chiave])
                self.assertTrue(self.fallite_nuova_home())

    def test_testi_vecchi_fanno_fallire(self):
        for vecchio in ("L'AI è il motore, non un'app", "Dove la geometria incontra il business",
                       "Servizi su misura, uno alla volta", "Sistemi che lavorano per loro",
                       "Ti lasciamo metodo e strumenti per andare avanti"):
            with self.subTest(vecchio=vecchio):
                self.home(SEZIONI + [("vecchio", vecchio)])
                self.assertTrue(any("vecchi" in e.regola for e in self.fallite_nuova_home()))


TITOLI_POPUP = ["Cos'è", "A cosa serve", "Come lo facciamo", "Cosa ricevi", "Per chi è"]


def popup(titoli=TITOLI_POPUP, aperto=0, h4=False):
    det = "".join('<details class="sv-acc"%s><summary>%s</summary><p>x</p></details>' %
                  (" open" if i == aperto else "", t) for i, t in enumerate(titoli))
    return '<dialog class="sv-dlg" id="servizio-x"><div class="sv-corpo">%s%s</div></dialog>' % (
        det, "<h4>Cos'è</h4>" if h4 else "")


class PopupFisarmoniche(Base):
    def stato(self, html):
        self.scrivi("index.html", "<html><body>%s</body></html>" % html)
        return self.esiti([cc.Regola("p", "index.html", "popup-fisarmoniche", TITOLI_POPUP, attiva=True)])[-1].stato

    def test_popup_a_due_colonne_con_componente_a3_passa(self):
        voci = "".join('<li class="a3-i%s"><button class="a3-b"><span class="a3-n">0%d</span><span class="a3-t">%s</span></button></li>'
                       % (" is-open" if n == 0 else "", n + 1, t) for n, t in enumerate(TITOLI_POPUP))
        self.assertEqual(self.stato('<dialog class="sv-dlg"><ol class="a3 a3-v">%s</ol></dialog>' % voci), "ok")

    def test_cinque_summary_prima_aperta_passa(self):
        self.assertEqual(self.stato(popup()), "ok")

    def test_nessun_popup_fallisce(self):
        self.assertEqual(self.stato("<p>niente</p>"), "fallita")

    def test_h4_al_posto_dei_summary_fallisce(self):
        self.assertEqual(self.stato(popup(h4=True)), "fallita")

    def test_titolo_mancante_o_fuori_ordine_fallisce(self):
        self.assertEqual(self.stato(popup(TITOLI_POPUP[:4])), "fallita")
        self.assertEqual(self.stato(popup(TITOLI_POPUP[::-1])), "fallita")

    def test_prima_sezione_chiusa_fallisce(self):
        self.assertEqual(self.stato(popup(aperto=2)), "fallita")

    def test_piu_sezioni_aperte_di_default_falliscono(self):
        self.assertEqual(self.stato(popup().replace("<details class=\"sv-acc\">", "<details class=\"sv-acc\" open>", 1)), "fallita")


class Classi(Base):
    def stato(self, tipo, valori, body):
        self.scrivi("index.html", "<html><body>%s</body></html>" % body)
        return self.esiti([cc.Regola("c", "index.html", tipo, valori, attiva=True)])[-1].stato

    def test_senza_classi(self):
        self.assertEqual(self.stato("senza-classi", ["pn-wide"], '<li class="pn card pn-wide">x</li>'), "fallita")
        self.assertEqual(self.stato("senza-classi", ["pn-wide"], '<li class="pn-card">x</li>'), "ok")

    def test_classi_presenti(self):
        self.assertEqual(self.stato("classi", ["sec-head--sm"], '<header class="sec-head sec-head--sm">x</header>'), "ok")
        self.assertEqual(self.stato("classi", ["sec-head--sm"], '<header class="sec-head">x</header>'), "fallita")


class TipoSconosciuto(Base):
    def test_tipo_di_regola_sconosciuto_fallisce_con_messaggio_chiaro(self):
        r = cc.Regola("regola con refuso", "index.html", "contienee", ["x"], attiva=True)
        f = self.fallite([r])
        self.assertEqual(len(f), 1)
        self.assertIn("tipo regola sconosciuto: contienee", f[0].dettaglio)


class FaqJsonLd(Base):
    def esito(self, html_extra, qa=FAQ_QA):
        visibile = "".join("<h3>%s</h3><p>%s</p>" % qa_ for qa_ in FAQ_QA)
        self.scrivi("index.html", "<html><body>%s%s</body></html>" % (visibile, html_extra))
        r = cc.Regola("faq", "index.html", "faq-jsonld", [q for q, _ in FAQ_QA], attiva=True)
        return self.esiti([r])[-1]

    def test_jsonld_coerente_passa(self):
        self.assertEqual(self.esito(jsonld_faq(FAQ_QA)).stato, "ok")

    def test_jsonld_assente_fallisce(self):
        self.assertEqual(self.esito("").stato, "fallita")

    def test_jsonld_non_valido_fallisce(self):
        self.assertEqual(self.esito('<script type="application/ld+json">{rotto</script>').stato, "fallita")

    def test_risposta_diversa_dal_testo_visibile_fallisce(self):
        qa = [(q, a + " in piu") for q, a in FAQ_QA]
        self.assertEqual(self.esito(jsonld_faq(qa)).stato, "fallita")

    def test_domanda_mancante_nel_jsonld_fallisce(self):
        self.assertEqual(self.esito(jsonld_faq(FAQ_QA[:-1])).stato, "fallita")


class Cli(Base):
    def test_exit_zero_se_pulito_uno_se_fallisce(self):
        self.assertEqual(cc.main([str(self.radice)], presenza=[]), 0)
        self.scrivi("index.html", PAGINA_OK.replace("Scala", "Prenota una demo"))
        self.assertEqual(cc.main([str(self.radice)], presenza=[]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
