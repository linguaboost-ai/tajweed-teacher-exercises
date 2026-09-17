#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Baut aus teacher-reading.html eine einzige Datei, die ohne Netz läuft.

Wozu: wo *.vercel.app gesperrt oder unerreichbar ist, hilft keine Einstellung
am Server. Diese Datei trägt die Aufgaben, die beiden Schriften und das Logo
in sich; der Lehrer bekommt sie einmal zugeschickt und öffnet sie danach per
Doppelklick — kein Webserver, keine Verbindung, kein Nachladen.

Die Seite selbst bleibt unangetastet: nur die Ladeschicht wird ersetzt und die
Verweise auf Schriften und Logo werden zu data:-URIs. Alles andere — Lehrplan,
Ableitung der Leseaufgaben, Sprachen, Schalter — ist derselbe Quelltext.

    python3 werkzeug/einzeldatei.py
"""

import base64
import json
import os
import re
import sys

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUELLE = os.path.join(WURZEL, "teacher-reading.html")
ZIEL = os.path.join(WURZEL, "teacher-reading-offline.html")

BLOECKE = ["tafkheem", "qalqala", "idgham", "ikhfa-idgham",
           "iqlab", "madd", "waqf"]

# Die drei „*-advanced.json“ bleiben ungelesen — sie bündeln dieselben
# Aufgaben noch einmal und würden alles doppelt zählen.


def spots(liste):
    return [{"start": s["start"], "end": s["end"], "text": s["text"]}
            for s in liste or []]


def schlank(t):
    """Nur die Felder, die die Seite wirklich liest."""
    o = {"id": t["id"], "lesson": t["lesson"], "sura": t["sura"],
         "task_type": t["task_type"], "answer": t["answer"]}
    subj = t.get("subject")
    if subj:
        o["subject"] = {"text": subj.get("text")}
        if subj.get("spots"):
            o["subject"]["spots"] = spots(subj["spots"])
    if t.get("items"):
        o["items"] = []
        for i in t["items"]:
            e = {"text": i["text"]}
            if i.get("spots"):
                e["spots"] = spots(i["spots"])
            o["items"].append(e)
    if t.get("options"):
        o["options"] = []
        for x in t["options"]:
            e = {"id": x["id"], "text": x["text"]}
            if x.get("spots"):
                e["spots"] = spots(x["spots"])
            o["options"].append(e)
    return o


def daten():
    bloecke = {}
    for name in BLOECKE:
        pfad = os.path.join(WURZEL, "aufgaben", name + ".json")
        with open(pfad, encoding="utf-8") as fh:
            bloecke[name] = [schlank(t) for t in json.load(fh)]
    with open(os.path.join(WURZEL, "advanced.json"), encoding="utf-8") as fh:
        adv = json.load(fh)["lessons"]
    fort = [{"id": l["id"], "group": l["group"], "replaces": l["replaces"],
             "de": l["de"], "en": l.get("en", l["de"]), "tasks": l["tasks"]}
            for l in adv]
    return bloecke, fort


def b64(pfad, typ):
    with open(pfad, "rb") as fh:
        return "data:" + typ + ";base64," + base64.b64encode(fh.read()).decode("ascii")


def ersetze(text, alt, neu, was, mal=1):
    if text.count(alt) != mal:
        sys.exit("Abbruch: %s kommt %d mal vor, erwartet %d mal.\n  %s"
                 % (was, text.count(alt), mal, alt[:90]))
    return text.replace(alt, neu)


def main():
    with open(QUELLE, encoding="utf-8") as fh:
        html = fh.read()

    # --- Schriften und Logo hineinlegen -----------------------------------
    hafs = b64(os.path.join(WURZEL, "fonts", "hafs-uthmanic.woff2"), "font/woff2")
    amiri = b64(os.path.join(WURZEL, "fonts", "amiri-quran-arabic-400-normal.woff2"),
                "font/woff2")
    logo = b64(os.path.join(WURZEL, "assets", "gm-logo-horizontal.png"), "image/png")

    html = ersetze(html, "url('fonts/hafs-uthmanic.woff2')",
                   "url('%s')" % hafs, "Verweis auf die Hausschrift")
    html = ersetze(html, "url('fonts/amiri-quran-arabic-400-normal.woff2')",
                   "url('%s')" % amiri, "Verweis auf Amiri Quran")
    # Zweimal: einmal als Fenstersymbol, einmal als Bild im Rand.
    html = ersetze(html, "./assets/gm-logo-horizontal.png", logo,
                   "Verweis auf das Logo", mal=2)

    # --- Ladeschicht durch die eingebauten Daten ersetzen -----------------
    bloecke, fort = daten()
    anfang = html.index("/* ==========================================================================\n   Laden")
    ende = html.index("start();", anfang) + len("start();")

    eingebaut = (
        "/* ==========================================================================\n"
        "   Die Aufgaben stecken in dieser Datei\n"
        "\n"
        "   Diese Fassung lädt nichts nach: sie ist für den Fall gemacht, dass die\n"
        "   Adresse im Netz nicht erreichbar ist. Einmal speichern, danach per\n"
        "   Doppelklick öffnen — auch ganz ohne Verbindung.\n"
        "   ========================================================================== */\n"
        "const EINGEBAUT = " + json.dumps({"bloecke": bloecke, "fort": fort},
                                          ensure_ascii=False,
                                          separators=(",", ":")) + ";\n"
        "\n"
        "Object.assign(DATA, EINGEBAUT.bloecke);\n"
        "FORT = EINGEBAUT.fort;\n"
        "\n"
        "function start(){\n"
        "  drawChrome();\n"
        "  drawCtl();\n"
        "  drawRail();\n"
        "  zeigeLektion();\n"
        "}\n"
        "\n"
        "start();"
    )
    html = html[:anfang] + eingebaut + html[ende:]

    # --- Titel im Fenster kennzeichnen, damit klar ist, welche Datei es ist
    html = ersetze(html, 'title:"German Method – Leseübungen"',
                   'title:"German Method – Leseübungen (Einzeldatei)"',
                   "Fenstertitel deutsch")
    html = ersetze(html, 'title:"German Method – Reading practice"',
                   'title:"German Method – Reading practice (single file)"',
                   "Fenstertitel englisch")

    if "fonts/" in html or "aufgaben/" in html.replace("aufgaben/*.json", ""):
        rest = sorted(set(re.findall(r'(?:fonts|aufgaben|assets)/[\w.-]+', html)))
        if rest:
            sys.exit("Abbruch: es zeigt noch etwas nach draußen: %s" % rest)

    with open(ZIEL, "w", encoding="utf-8") as fh:
        fh.write(html)

    aufgaben = sum(len(v) for v in bloecke.values())
    print("%s geschrieben" % os.path.relpath(ZIEL, WURZEL))
    print("  %d Aufgaben aus %d Blöcken, %d zusammengefasste Lektionen"
          % (aufgaben, len(bloecke), len(fort)))
    print("  %.1f MB" % (os.path.getsize(ZIEL) / 1024 / 1024))


if __name__ == "__main__":
    main()
