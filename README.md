# Tajweed — Lehrerseiten

## `teacher-reading.html` — Leseübungen

Für den Zoom-Unterricht: der Lehrer teilt den Bildschirm, der Schüler liest den
arabischen Text vor, der Lehrer korrigiert die Aussprache. Deshalb gibt es auf
der Seite keine Antwortmöglichkeiten, keine Lösungen, keine Punkte und keinen
Ton — nur den Text, groß und ruhig gesetzt.

Aufbau, Schriften, Farben, Abstände und Knöpfe sind von `teacher-exercises.html`
übernommen, damit die Seite wie eine Schwesterseite wirkt.

    links    die 40 Lektionen, nach den sieben Blöcken gruppiert
    Mitte    die Leseaufgabe, groß, mit Weiter/Zurück (Knöpfe und Pfeiltasten)
    rechts   die Liste der Leseaufgaben; ein Klick zeigt eine sofort in der Mitte

Verse stehen in der Liste auf die ersten drei Wörter gekürzt, Wörter voll.
In jeder Lektion wählt man eine Gattung: **Wörter** oder **Verse**.

Drei Schalter am linken Rand, alle im Browser gemerkt:

| Schalter                   | Wirkung                                      | Voreinstellung | localStorage              |
|----------------------------|----------------------------------------------|----------------|---------------------------|
| Tafkheem fortgeschritten   | fasst Lektion 1–7 zu einer zusammen          | an             | `tajwid.advTafkheem`      |
| Qalqalah fortgeschritten   | fasst Lektion 10–14 zu zweien zusammen       | an             | `tajwid.advQalqala`       |
| Regelstellen einfärben     | färbt `subject.spots` ein — für den Lehrer   | aus            | `tajwid.teacherSpots`     |

Die ersten zwei Schlüssel sind dieselben wie in der Übungs-App, beide Seiten
verstehen sich also. Mit beiden Schaltern hat der Lehrplan 31 Lektionen statt
40, mit einem 34 bzw. 37.

### Aufrufen

Die Seite lädt die Aufgaben zur Laufzeit und braucht deshalb einen Webserver —
als Datei geöffnet sagt sie das auch:

    python3 -m http.server 8000
    # http://localhost:8000/teacher-reading.html

Keine Bauwerkzeuge, kein Framework, kein CDN: eine HTML-Datei, die Aufgaben,
die beiden Schriften und das Logo.

## Was hier liegt

    teacher-reading.html        die neue Seite
    teacher-exercises.html      die Vorlage (gespeicherte Seite der App)
    teacher-exercises_files/    deren Beiwerk
    aufgaben/*.json             die Übungsaufgaben
    advanced.json               die zusammengefassten Lektionen
    questions.json              Fragetexte — für diese Seite nicht nötig
    fonts/                      KFGQPC HAFS und Amiri Quran (OFL)
    assets/                     Logo
    tajweed-aufgaben.zip        der Datensatz, wie er kam

`aufgaben/tafkheem-1-advanced.json`, `aufgaben/qalqala-1-advanced.json` und
`aufgaben/qalqala-2-advanced.json` liest die Seite **nicht**: sie enthalten
dieselben Aufgaben noch einmal, nur anders gebündelt — wer sie mitliest, zählt
alles doppelt. Die zusammengefassten Lektionen entstehen stattdessen aus
`advanced.json`, das die Aufgaben-IDs samt Reihenfolge nennt.

## Welcher Text wird zur Leseaufgabe

Eine Aufgabe des Datensatzes wird zu einer oder mehreren Leseaufgaben:

* `task_type: "matching"` — jedes Element aus `items` wird eine eigene.
* `task_type: "match"` — jede richtige Option (`id` steht in `answer`) wird
  eine eigene. Steht in `subject.text` ein Vorgabewort, lautet die Leseaufgabe
  `Vorgabewort + " " + Option`: die Regel entsteht erst über die Wortgrenze
  hinweg, und genau diese Verbindung soll der Schüler sprechen. Steht dort
  `اختر` („wähle"), gibt es kein Vorgabewort. Lautet die richtige Antwort
  `none` („kommt nicht vor"), werden alle arabischen Optionen genommen — auch
  diese Verbindungen gehören geübt, gerade weil dort nichts verschmilzt.
* alle übrigen Aufgabentypen — `subject.text`, genau einmal.

Danach wird innerhalb einer Lektion nach identischem Text entdoppelt.
Ist `sura` gesetzt, ist es ein **Vers**, ist `sura` gleich `null`, ein **Wort** —
nicht die Wortzahl entscheidet das.

Das ergibt über alle 40 Lektionen **1472 Wörter, 945 Verse, zusammen 2417**.

## Arabische Schrift

Der Text steht in der Uthmani-Rechtschreibung des Mushaf und wird in der
Hausschrift KFGQPC HAFS gesetzt (`fonts/hafs-uthmanic.woff2`). Die indischen
Ziffern am Versende sind die Versnummer: davor steht ein Leerzeichen und
`U+06DD`, das sie in die verzierte Kartusche setzt; die kommt aus Amiri Quran
(`fonts/amiri-quran-arabic-400-normal.woff2`, OFL — siehe
`fonts/AmiriQuran-OFL.txt`). In der Dreiwort-Vorschau der Liste bleibt die
Versnummer weg. Jedes arabische Element steht auf `direction: rtl` und
`unicode-bidi: isolate`, sonst rutschen lateinische Ziffern und Satzzeichen an
die falsche Stelle.
