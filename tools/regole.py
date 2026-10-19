"""Regole di presenza del nuovo sito (spec .scratch/sito-value-proposition/spec.md).

Ogni regola nasce con attiva=False. Il ticket che costruisce l'elemento la porta
a True: da quel momento lo script la fa fallire se l'elemento manca.
Tipi: id (tutti gli id presenti nella pagina) · contiene (tutti i testi presenti) · ordine (testi nell'ordine dato) ·
link (la pagina ha un link a questi file) · assente (nessuno di questi testi) ·
faq-jsonld (JSON-LD FAQPage valido con queste domande, testo identico a quello visibile) ·
redirect (la pagina è solo un meta refresh verso valori[0]) ·
senza-link (nessuna pagina non-redirect linka alle cartelle in valori; pagina ignorata) ·
classi / senza-classi (tutte / nessuna delle classi CSS in valori usata nella pagina) ·
popup-fisarmoniche (ogni <dialog class="sv-dlg">: i <summary> sono i valori nell'ordine, solo il primo <details> aperto, niente <h4>).
Un tipo non elencato qui fa fallire la regola con «tipo regola sconosciuto».
"""

from controlla_contenuti import Regola

HOME, PIANO, BUSSOLA = "index.html", "piano/index.html", "bussola/index.html"
EXECUTION, AI, CASE = "execution/index.html", "ai/index.html", "case-study/index.html"

SERVIZI_SLUG = ["business-plan", "automazioni", "company-brain", "gestionali", "sito", "growth", "contabilita"]
SERVIZI_VECCHI = ["strategia", "mercato", "processi", "budget", "costi", "cruscotto"]  # slug dell'epoca degli 11 servizi
SERVIZI_TITOLI = ["Business planning", "Automazioni agentiche", "Company brain e AI operating system",
                  "Gestionali automatizzati", "Sito web", "Business development e growth", "Contabilità manageriale"]
PROGETTI = ["L&A Impianti", "OrientaCampus", "Medico Musone", "Salzillo Costruzioni", "Valentino Immobiliare"]

PRESENZA = [
    # restyling 09: Piano, Execution e Bussola non sono più pagine: restano solo i redirect dei vecchi indirizzi
    Regola("vecchio /piano: redirect a #servizio-business-plan", PIANO, "redirect", ["/#servizio-business-plan"], attiva=True),
    Regola("vecchio /execution: redirect a #servizio-automazioni", EXECUTION, "redirect", ["/#servizio-automazioni"], attiva=True),
    Regola("vecchio /bussola: redirect a #servizio-contabilita", BUSSOLA, "redirect", ["/#servizio-contabilita"], attiva=True),
    Regola("nessun link interno a piano/, execution/, bussola/", "", "senza-link",
           ["piano", "execution", "bussola"], attiva=True),
    # home: CTA
    Regola("home: CTA call conoscitiva", HOME, "contiene", ["Prenota una call conoscitiva"], attiva=True),
    # spec nuovo sito: home: come lavoriamo, AI
    Regola("home: modo di lavorare, i 6 step del framework A3 nell'ordine", HOME, "ordine",
           ["Processo", "Il nostro framework A3",
            "Il contesto", "Situazione attuale", "Cause radice", "La soluzione", "Piano d'azione",
            "Standard e crescita"], attiva=True),
    Regola("home: i 6 kicker inglesi del framework A3", HOME, "contiene",
           ["Background", "Current Situation", "Analysis", "Countermeasure", "Plan", "Standardize"], attiva=True),
    Regola("home: vecchio «Come lavoriamo» a 4 tappe assente", HOME, "assente",
           ["Come lavoriamo", "Quattro tappe, sempre nello stesso ordine"], attiva=True),
    Regola("home: Chi siamo senza il paragrafo sul dogfooding, stat a 6 step", HOME, "assente",
           ["prima su di noi", "Tappe del nostro modo di lavorare"], attiva=True),
    Regola("home: sezione AI con rimando a /ai", HOME, "link", [AI], attiva=True),
    # spec nuovo sito: home: case study, autonomia, CTA, contatti
    Regola("home: 3 progetti in evidenza", HOME, "contiene", ["3Card", "Salzillo Costruzioni", "Dott. Musone", "L&A Impianti", "Gestionale L&A", "Valentino Immobiliare", "Pivot", "OrientaCampus"], attiva=True),
    Regola("home: rimando a /case-study", HOME, "link", [CASE], attiva=True),
    Regola("home: competenze dei soci", HOME, "contiene",
           ["economisti", "ingegnere gestionale", "Step del framework A3, applicati a ogni progetto"], attiva=True),
    Regola("nuova home: sezione Autonomia vecchia assente", HOME, "assente",
           ["Ti lasciamo metodo e strumenti per andare avanti", "anche senza di noi</h2>"], attiva=True),
    Regola("home: sede nei contatti", HOME, "contiene", ["Marcianise"], attiva=True),
    Regola("home: link a 3card.3-lab.it", HOME, "contiene", ["3card.3-lab.it"], attiva=True),
    # spec nuovo sito: /ai
    Regola("/ai: attraversa i tre pilastri", AI, "contiene", ["Piano", "Execution", "Bussola"], attiva=True),
    Regola("/ai: CSS condiviso", AI, "link", ["assets/pilastro.css"], attiva=True),
    Regola("/ai: «non si compra, si implementa» con i 4 passi e il claim", AI, "contiene",
           ["L'AI non si compra", "Si implementa", "Si istruisce", "Si adatta all'ecosistema aziendale",
            "Si mette a disposizione del team", "Chi aspetta continua a spendere ore preziose"], attiva=True),
    Regola("/ai: vecchi claim assenti", AI, "assente",
           ["Si integra.", "costi e tempi che gli altri faticano a pareggiare"], attiva=True),
    Regola("/ai: agenti spiegati, company brain, CTA", AI, "contiene",
           ["Agente AI", "company brain", "AI operating system", "Prenota una call conoscitiva"], attiva=True),
    # spec nuovo sito: /case-study
    Regola("/case-study: 5 progetti", CASE, "contiene", PROGETTI, attiva=True),
    Regola("/case-study: progetti nell'ordine scelto da Andrea (19/10, Valentino sempre ultimo)", CASE, "ordine", ["OrientaCampus", "L&A Impianti", "Salzillo Costruzioni", "Medico Musone", "Valentino Immobiliare"], attiva=True),
    Regola("/case-study: CSS condiviso", CASE, "link", ["assets/pilastro.css"], attiva=True),
    Regola("/case-study: CTA call conoscitiva", CASE, "contiene", ["Prenota una call conoscitiva"], attiva=True),
]


# Restyling landing (spec .scratch/sito-landing-restyling/spec.md). Tutte attive dal ticket 10;
# ogni ticket ha attivato le sue (attiva=True) quando ha costruito l'elemento.
NUOVA_HOME = [
    # ticket 03 — hero
    Regola("nuova home: hero, sottotitolo e slogan", HOME, "contiene",
           ["Ingegneria, economia ed AI agentica per scalare senza caos",
            "Uniamo ingegneria, rigore economico e AI agentica per costruire le proporzioni strutturali perfette con cui scalare",
            "Arriviamo. Discutiamo. Automatizziamo. Voi vincete."], attiva=True),
    Regola("nuova home: sottotitolo hero vecchio assente", HOME, "assente",
           ["Dove la geometria incontra il business"], attiva=True),
    Regola("nuova home: secondo bottone hero verso Cosa facciamo, «Il nostro processo» non esiste più", HOME, "assente",
           ["Il nostro processo"], attiva=True),
    # ticket 13 — ritocchi copy
    Regola("nuova home: cosa facciamo, 4 righe nell'ordine con «Analizziamo i tuoi dati» al numero 01", HOME, "ordine",
           ["Cosa facciamo", "01 Analizziamo i tuoi dati", "02 Ti aiutiamo a decidere dove portare la tua azienda",
            "03 Costruiamo con te il sistema per arrivarci",
            "04 Ti forniamo la bussola per accorgerti subito quando stai deviando"], attiva=True),
    Regola("nuova home: titolo Servizi «Cuciti su misura»", HOME, "contiene", ["Cuciti su misura"], attiva=True),
    Regola("nuova home: titolo Servizi vecchio assente", HOME, "assente", ["Servizi su misura, uno alla volta"], attiva=True),
    Regola("nuova home: titolo case study «Il nostro portfolio»", HOME, "contiene", ["Il nostro portfolio"], attiva=True),
    Regola("nuova home: titolo case study vecchio assente", HOME, "assente", ["Sistemi che lavorano per loro"], attiva=True),
    # ticket 04 — cosa facciamo
    Regola("nuova home: cosa facciamo in tre mosse", HOME, "contiene",
           ["Analizziamo i tuoi dati", "ti aiutiamo a decidere dove portare la tua azienda",
            "costruiamo con te il sistema per arrivarci",
            "ti forniamo la bussola per accorgerti subito quando stai deviando"], attiva=True),
    # ticket 05 — processo
    Regola("nuova home: cosa facciamo assorbe il processo (Piano, Execution, Bussola)", HOME, "contiene",
           ["Dove vado?", "Come ci arrivo?", "Sto deviando?"], attiva=True),
    Regola("nuova home: sezione processo a schede separata assente", HOME, "assente",
           ["Tutto ciò che ti serve per pianificare, creare, scalare e misurare"], attiva=True),
    # ticket 06 — servizi
    Regola("nuova home: 7 servizi", HOME, "contiene", SERVIZI_TITOLI, attiva=True),
    Regola("nuova home: servizi vecchi assenti (11 → 7)", HOME, "assente",
           ["Cruscotto e report", "Processi e operations", "Strategia e organizzazione", "Budget e scostamenti",
            "Growth e business development", *["servizio-" + x for x in SERVIZI_VECCHI], "Undici servizi"], attiva=True),
    Regola("nuova home: ogni popup ha la stessa struttura", HOME, "contiene",
           ["Cos'è", "A cosa serve", "Come lo facciamo", "Cosa ricevi", "Per chi è",
            "Controllo: a ogni passo misuriamo il risultato e correggiamo la rotta",
            "Non sai da dove partire?"], attiva=True),
    Regola("nuova home: popup = 5 fisarmoniche <summary> nell'ordine, la prima aperta, niente h4", HOME,
           "popup-fisarmoniche", ["Cos'è", "A cosa serve", "Come lo facciamo", "Cosa ricevi", "Per chi è"], attiva=True),
    Regola("nuova home: Business planning con le 4 componenti", HOME, "contiene",
           ["Pianificazione strategica e organizzazione", "Analisi di mercato e posizionamento",
            "Business model design", "Piano economico-finanziario"], attiva=True),
    Regola("nuova home: Contabilità manageriale con le 3 componenti", HOME, "contiene",
           ["Costi reali per prodotto e cliente", "Budget", "Scostamenti"], attiva=True),
    Regola("nuova home: etichette di fase sui servizi", HOME, "contiene",
           ["pianificazione", "esecuzione", "controllo"], attiva=True),
    Regola("nuova home: servizi con ancora diretta #servizio-*", HOME, "id",
           ["servizi"] + ["servizio-" + x for x in SERVIZI_SLUG], attiva=True),
    # ticket 14 — card servizi in vetro, «Il metodo resta a te» come intestazione (non più card)
    Regola("nuova home: card servizi in liquid glass con sfondo di forme", HOME, "classi",
           ["sv-card", "glass", "sv-bg"], attiva=True),
    Regola("nuova home: sezione Perché noi eliminata", HOME, "assente",
           ["Perché noi", "Competenze complementari", "Tre teste diverse"], attiva=True),
    Regola("nuova home: .pn-wide (box vecchio) assente", HOME, "senza-classi", ["pn-wide"], attiva=True),
    Regola("nuova home: popup senza i vecchi blocchi sv-blk", HOME, "senza-classi", ["sv-blk"], attiva=True),
    Regola("nuova home: vecchi claim sull'AI assenti", HOME, "assente",
           ["il motore operativo di 3-Lab", "più veloce, costa meno", "Nel Piano", "Nell'Execution"], attiva=True),
    Regola("nuova home: sezione Qual è il ruolo dell'AI con i 4 passi e il claim", HOME, "contiene",
           ["Qual è il ruolo dell'AI?", "AI agentica", "non solo risponde", "Si istruisce",
            "Si adatta all'ecosistema aziendale", "Si mette a disposizione del team",
            "strumento di collaborazione avanzato", "Chi aspetta continua a spendere ore preziose"], attiva=True),
    Regola("nuova home: titolo AI vecchio assente", HOME, "assente", ["L'AI è il motore, non un'app"], attiva=True),
    # ticket 08 — FAQ
    Regola("nuova home: FAQ con le 9 domande e la card Hai ancora domande", HOME, "contiene",
           ["Hai ancora domande?", "Scrivici", "Cosa succede nella call conoscitiva?",
            "A che tipo di azienda siete adatti?", "Quanto dura un lavoro e come si svolge?",
            "Devo cambiare gli strumenti che uso oggi?", "Cosa significa che l'AI è il vostro motore?",
            "Cosa fate con i miei dati?", "Quanto costa?", "Posso prendere solo una parte?",
            "E se dopo il lavoro non ho una persona che gestisce gli strumenti?"], attiva=True),
    Regola("nuova home: FAQ nei dati strutturati JSON-LD, identica al testo visibile", HOME, "faq-jsonld",
           ["Cosa succede nella call conoscitiva?", "A che tipo di azienda siete adatti?",
            "Quanto dura un lavoro e come si svolge?", "Devo cambiare gli strumenti che uso oggi?",
            "Cosa significa che l'AI è il vostro motore?", "Cosa fate con i miei dati?", "Quanto costa?",
            "Posso prendere solo una parte?",
            "E se dopo il lavoro non ho una persona che gestisce gli strumenti?"], attiva=True),
    # ticket 10 — ordine complessivo delle sezioni
    Regola("nuova home: ordine delle sezioni", HOME, "ordine",
           ["Ingegneria, economia ed AI agentica", "Analizziamo i tuoi dati",
            "Automazioni agentiche", "Il nostro framework A3", "Qual è il ruolo dell'AI?", "Valentino Immobiliare",
            "ingegnere gestionale", "Hai ancora domande?", "30 minuti"], attiva=True),
]

PRESENZA += NUOVA_HOME
