# Leseprotokoll: menschliche Referenzlesung für OIP-Bench

> **Abgelöst.** Diese deutsche Fassung 0.2 ist historisch. Die gültige Fassung ist `PROTOCOL.md` (englisch, 1.0, Änderungsliste gegenüber 0.1 in deren Abschnitt 9). Fassung 0.1 vom 2. November 2026 (Commit abcad9f) ist die der OSF-Registrierung https://osf.io/9rxbk angehängte Fassung.

Fassung 0.2, 4. November 2026. Entwurf für die Präregistrierung (OSF) und als Anleitung für die Leser. Fassung 0.1 vom
2. November ist die der OSF-Registrierung (https://osf.io/9rxbk) angehängte Fassung; Änderungen seither: 04.11. Abschnitt 2,
Verblindung als prozedural ausgewiesen (Paketwerte sind als Teil der offenen Daten öffentlich), Bestätigung der Leser ergänzt,
Lesebogen zeigt eine laufende Nummer statt der Item-ID. Fassung 1.0 nach Freigabe durch den Erstautor. Abschnitte 1 bis 7
sind die Messdefinitionen und der Analyseplan; sie werden vor der ersten Lesung eingefroren. Abschnitt 8 ist die Bedienung.

## 1. Ziel

Die Modellantworten in OIP-Bench wurden bisher gegen Werte aus den Paketen gewertet: die Seitenorientierung aus dem
DICOM-Header beziehungsweise der konventionellen Darstellung, CTR und Herzbreite aus einer Segmentierung (PSPNet/CheXmask,
Kontrolle CXAS). Kein Mensch hat die Bilder gelesen. Diese Studie liefert eine menschliche Referenz durch Fachärzte und
beantwortet drei Fragen:

1. Wie gut stimmen zwei Radiologen untereinander überein (Inter-Reader-Agreement)?
2. Wie gut stimmt die Segmentierung mit der menschlichen Referenz überein (Mensch gegen Modell)?
3. Ändern sich die Kernaussagen des Papers, wenn alle Modellantworten gegen die menschliche Referenz neu gewertet werden
   (Sensitivitätsanalyse)?

Außerdem ersetzt die Lesung die bisherige KI-Sichtprüfung der maskierten Bilder (Seitenmarker entfernt?) durch eine
fachärztliche Prüfung.

## 2. Leser und Verblindung

- Zwei Fachärzte für Radiologie (R1, R2), ein Facharzt für Nuklearmedizin (NM1). Bei Uneinigkeit der Radiologen entscheidet
  ein dritter Leser (R3, Adjudikation, nur die strittigen Bilder).
- Die Leser sehen ausschließlich das kanonische Rendering des Bildes ohne Annotationen, also genau das Bild, das die Modelle
  gesehen haben. Sie sehen keine Paketwerte (Pixelabstand, Orientierung, Segmentierung), keine Modellantworten und keine
  Werte des anderen Lesers.
- Die Paketwerte sind als Teil der offenen Daten öffentlich (Repository: `bench/reader/set_key.json`; Zenodo-Bündel:
  `derived/measurements.json` und `context.md` der Pakete). Die Verblindung ist deshalb prozedural: Die Leser werden weder auf
  das Repository noch auf die Schlüsseldatei oder die Zuordnung der Item-IDs hingewiesen, haben keine Rolle im Projekt und
  werden vor der Lesung gebeten, zu den gezeigten Bildern keine Werte nachzuschlagen. Der Lesebogen zeigt eine laufende
  Nummer, keine Item-ID. Jeder Leser bestätigt nach Abschluss mit einem Satz per E-Mail, dass er keine Werte nachgeschlagen
  hat; die Bestätigungen werden mit den Lesedateien abgelegt. Die Studienleitung öffnet `set_key.json` erst nach Abschluss
  der Lesung. Der Punkt wird in den Limitationen des Manuskripts genannt.
- Die Lesung findet auf einem Rechner des Erstautors statt (lokaler Lesebogen im Browser, kein Cloud-Dienst). VinDr-CXR
  wird nicht weitergegeben; die Leser erhalten Lesezugriff auf die Bilder, keine Kopien.
- Jede Antwort wird mit Zeitstempel und Revisionsnummer gespeichert. Korrekturen nimmt nur der Leser selbst vor; sie
  erzeugen eine neue Revision, nichts wird überschrieben oder nachträglich bereinigt. Fehlende Werte bleiben fehlend.

## 3. Bildmaterial und Blöcke

Alle Bilder stammen aus öffentlichen, de-identifizierten Datensätzen (VinDr-CXR, NIH ChestX-ray14, Knochenszintigramme
IICS-UNA Paraguay, CC BY 4.0). Die Reihenfolge innerhalb jedes Blocks ist zufällig (Seed 20261102) und für alle Leser gleich.
Die sha256-Prüfsumme jedes gezeigten Bildes steht in `items.json`.

| Block | Leser | Bilder | Aufgabe | Richtzeit |
|---|---|---|---|---|
| Übung | R1, R2 | 3 VinDr-Bilder außerhalb des Studiensatzes | Seite und CTR, Kalibrierung vorab gemeinsam | 15 min |
| A | R1, R2 | 150 Röntgen (100 VinDr, 50 NIH) | Seitenorientierung | 30 min |
| B | R1, R2 | 100 VinDr | CTR und Herzbreite, AP-Markierung | 3 h |
| C | R1, R2 | 82 VinDr (Conflict-Trial-Bilder), maskiertes Rendering | Seitenmarker sichtbar? | 15 min |
| D (optional) | R1, R2 | 50 NIH | CTR, nur Verhältnis | 1,5 h |
| E | NM1 | 40 Ganzkörperszintigramme (20 Patienten, anterior und posterior) | Ansicht, Seitenorientierung | 15 min |
| F | NM1 | 8 Szintigramme mit klarer Seitenasymmetrie der Zählrate | Bildhälfte mit mehr Aktivität | 5 min |

Hinweis: Die 82 Bilder in Block C (klarer kardialer Seitenhinweis, nicht von der Markerprüfung 2026-09-30 ausgeschlossen) sind
nicht dieselben 82 Bilder, die einen Pixelabstand im Header tragen; die beiden Mengen überlappen in 68 Bildern.

## 4. Messdefinitionen

### 4.1 Seitenorientierung (Blöcke A und E)

Frage: Welcher Bildrand zeigt die rechte Körperseite des Patienten? Antworten: linker Bildrand, rechter Bildrand, nicht
beurteilbar. Zusätzlich die Grundlage: Anatomie, Marker/Beschriftung, beides.

- Anatomische Kriterien beim Thoraxröntgen: Aortenknopf und Herzspitze auf der linken Patientenseite, Magenblase links,
  Leberschatten und höher stehendes Zwerchfell rechts. Die Entscheidung folgt der Anatomie, wie sie im Bild erscheint; ein
  Situs inversus oder eine Dextrokardie wird nach dem Bild beantwortet und im Kommentar vermerkt.
- Ein eingebrannter Seitenmarker (R, L, Text) darf benutzt werden. Dann ist die Grundlage "Marker/Beschriftung" oder
  "beides" anzugeben, damit die Auswertung anatomisch begründete von beschriftungsbasierten Antworten trennen kann.
- Nicht beurteilbar: weder Anatomie noch Marker erlauben eine Entscheidung, oder beide widersprechen sich ohne Auflösung.

### 4.2 CTR und Herzbreite (Blöcke B und D)

Herztransversaldurchmesser: die horizontale Distanz zwischen dem lateralsten Punkt des rechten Herzrands und dem
lateralsten Punkt des linken Herzrands der Herzsilhouette. Die beiden Punkte dürfen auf verschiedener Höhe liegen; das
Werkzeug verwendet die horizontale Komponente (das entspricht der Summe der größten Abstände beider Herzränder von der
Mittellinie). Perikardiales und epikardiales Fett zählen nicht zur Silhouette, soweit abgrenzbar; Hilusgefäße nicht.

Thoraxinnendurchmesser: die größte horizontale Innendistanz des Thorax zwischen den Innenrändern der Rippen (Pleuralinie),
meist in Höhe der rechten Zwerchfellkuppel. Auch hier wird die horizontale Komponente verwendet.

CTR = Herztransversaldurchmesser / Thoraxinnendurchmesser. Beide Längen werden in Bildpixeln des Originalrasters erfasst.
Die Herzbreite in Millimetern berechnet die Auswertung nachträglich aus den Pixeln und dem Pixelabstand des Headers,
nur für die 82 VinDr-Bilder, die einen Header-Pixelabstand tragen; die Leser sehen den Pixelabstand nicht. Es wird keine
Vergrößerungskorrektur angewendet (Detektorebene), wie bei den Paketwerten.

- AP-Projektion: ankreuzen, wenn das Bild erkennbar a.p. aufgenommen ist (Schulterblätter über den Lungenfeldern,
  Klavikulaprojektion, liegender Patient, entsprechende Beschriftung). Die Messung wird trotzdem durchgeführt; die
  Auswertung berichtet die AP-Bilder getrennt.
- Nicht beurteilbar: Herzränder oder Thoraxränder nicht abgrenzbar (Erguss, Verschattung, Abschneidung, grobe Rotation).
  Eine Teilmessung (nur Thorax oder nur Herz) wird gespeichert, geht aber nicht in die CTR ein.
- Vor Block B lesen beide Radiologen die drei Übungsbilder gemeinsam und gleichen die Punktsetzung ab (Kalibrierung).
  Die Übungsbilder gehören nicht zum Studiensatz und werden nicht ausgewertet.

### 4.3 Seitenmarker im maskierten Bild (Block C)

Die Modelle sahen in den Conflict Trials ein maskiertes Rendering: alles außerhalb eines Lungenkastens ist geschwärzt, damit
eingebrannte Seitenmarker verschwinden. Frage: Ist in diesem maskierten Bild ein Seitenmarker oder eine Seitenbeschriftung
sichtbar? Antworten: ja, nein, unsicher. Bei ja oder unsicher wird die Position angeklickt.

- Als Seitenmarker zählt jedes eingebrannte Zeichen, das eine Körperseite angibt: R, L, D, S, "rechts", "links", "re", "li",
  Pfeile mit Seitenbezug. Projektionsangaben (PA, AP), Datum, Gerätetext oder Zahlen ohne Seitenbezug zählen nicht; wenn
  unklar ist, ob ein Zeichen eine Seite bezeichnet, "unsicher" mit Kommentar.
- Symmetrische Fremdkörper (EKG-Elektroden, Clips, Knöpfe) sind keine Seitenhinweise.

### 4.4 Szintigramme (Blöcke E und F)

Gezeigt wird das kanonische Rendering (heiß = hell), invertierbar. Die Ansicht wird nicht angezeigt.

- Ansicht: anterior, posterior, unsicher. Kriterien: anterior zeigt Sternum, Gesichtsschädel, vordere Rippen, Patellae;
  posterior zeigt Wirbelsäule, Schulterblätter, Sakroiliakalgelenke, Nieren, hintere Rippen.
- Seitenorientierung: Welcher Bildrand zeigt die rechte Körperseite? Antworten wie in 4.1. Bei konventioneller Darstellung
  liegt die rechte Patientenseite in der anterioren Ansicht am linken Bildrand und in der posterioren am rechten Bildrand;
  die Entscheidung folgt aber dem Bild, nicht der Konvention.
- Aktivität (Block F): Welche Bildhälfte (links oder rechts im Bild) zeigt insgesamt mehr Aktivität, Wirbelsäule und
  Harnblase ausgenommen? Antworten: linke Bildhälfte, rechte Bildhälfte, kein klarer Unterschied, nicht beurteilbar. Die
  Antwort wird bewusst in Bildkoordinaten erfasst; die Auswertung rechnet sie mit der Orientierungsantwort des Lesers in die
  Patientenseite um.

## 5. Adjudikation (dritter Leser)

Strittig sind: unterschiedliche kategoriale Antworten (auch "nicht beurteilbar" gegen eine Antwort) in den Blöcken A und C;
in Block B ein CTR-Unterschied über 0,05 oder ein Unterschied der Herzbreite über 10 Prozent des Mittelwerts. Der dritte
Leser liest nur die strittigen Bilder, verblindet gegenüber beiden Erstlesungen. Referenz ist dann der Median der drei
Werte (kontinuierlich) beziehungsweise die Mehrheit (kategorial); bleibt keine Mehrheit, gilt das Bild als "nicht
beurteilbar". Für die Szintigramme gibt es einen Leser; Abweichungen von der Paketkonvention werden berichtet, nicht
adjudiziert.

## 6. Analyseplan

Alle Analysen laufen über die eingefrorenen CSV-Dateien (`bench/reader/readings/`), zusammengeführt mit
`bench/reader/collect.py` (letzte Revision je Leser, Bild und Aufgabe).

1. Inter-Reader-Agreement: CTR und Herzbreite ICC(2,1) (zweifaktoriell zufällig, Einzelmessung, absolute Übereinstimmung)
   mit 95-Prozent-Konfidenzintervall; Seitenorientierung, Marker und Ansicht Cohens Kappa.
2. Mensch gegen Segmentierung: Referenz ist der Mittelwert der beiden Radiologen (nach Adjudikation). Lins
   Konkordanzkorrelationskoeffizient und Bland-Altman (mittlere Differenz, 95-Prozent-Limits of Agreement) für CTR und
   Herzbreite gegen den im Paket ausgelieferten Wert (PSPNet/CheXmask); CXAS als zweite Spalte.
3. Re-Scoring: Jede Modellantwort zu `left_edge`, `ctr` und `heart_mm` wird mit der menschlichen Referenz als Wahrheit neu
   bewertet, mit denselben Toleranzen wie bisher (CTR plus/minus 0,05 absolut, Herzbreite plus/minus 10 Prozent relativ,
   `bench/tasks.py`). Bilder, die die Referenz als "nicht beurteilbar" führt, werden ausgeschlossen und gezählt. Berichtet
   werden die Modellgenauigkeiten gegen Paketwahrheit und gegen menschliche Referenz nebeneinander; kippt eine Kernaussage,
   wird das berichtet und das Framing angepasst.
4. Marker: Anteil der 82 maskierten Bilder, auf denen ein Leser einen Seitenmarker sieht; diese Bilder werden in einer
   Sensitivitätsanalyse aus den Conflict Trials entfernt.
5. Szintigramme: Übereinstimmung von Ansicht und Orientierung mit der Dateikonvention; Aktivitätsseite gegen die
   pixelbasierte Zählung (`bench/tasks_nm.py`).
6. Die Übungsbilder und alle nicht-finalen Revisionen gehen nicht in die Statistik ein. Software und Versionen werden im
   Report genannt.

## 7. Ethik und Daten

Öffentliche, de-identifizierte Datensätze; keine Patientenkontakte; keine Daten aus einer Klinik. Ob die Institution des
Erstautors für Leserstudien an öffentlichen Daten eine Bestätigung verlangt, wird vorab geklärt und im Paper angegeben.
Die Leser-CSV-Dateien werden mit Leser-Pseudonym (R1, R2, R3, NM1) veröffentlicht.

## 8. Bedienung des Lesebogens

1. Der Erstautor startet den Bogen: `python bench/reader/serve.py`, dann im Browser `http://127.0.0.1:8765/reader.html`.
   Oben rechts erscheint "Autosave in CSV aktiv". Ohne Server (Doppelklick auf `reader.html`) speichert der Bogen nur im
   Browser; dann regelmäßig "CSV exportieren".
2. Leser-ID (R1, R2, R3 oder NM1) und Rolle eintragen, den Block wählen. Beim ersten Start klappen die Kurzregeln auf.
3. Bild: Mausrad scrollt, Cmd/Strg plus Mausrad zoomt, Leertaste gedrückt halten und ziehen verschiebt. Helligkeit und
   Kontrast wirken nur auf die Anzeige. "invertiert" dreht die Grauwerte um.
4. Seitenorientierung, Marker, Ansicht, Aktivität: Antwort anklicken oder Taste 1 bis 4. "Nicht beurteilbar" (n) und
   "unsicher" (u) jederzeit. Kommentar optional.
5. CTR: "Herz messen" (h), dann zwei Klicks auf die lateralsten Punkte der Herzsilhouette; "Thorax messen" (t), dann zwei
   Klicks auf die Rippeninnenränder. Die Pixelwerte und die CTR erscheinen sofort. Ein erneuter Klick auf "Herz messen"
   verwirft die Herzpunkte und erlaubt eine neue Messung. AP-Projektion ankreuzen, wenn zutreffend.
6. Marker: bei "Ja" oder "Unsicher" einmal auf die Stelle im Bild klicken; der Kreis zeigt die gespeicherte Position.
7. Weiter mit Pfeiltaste rechts; "Nächstes offenes" springt zum nächsten unvollständigen Bild. Die Fortschrittsleiste zählt
   vollständige Bilder. Pausen sind jederzeit möglich, der Stand bleibt erhalten.
8. Am Ende jedes Blocks einmal "CSV exportieren" als zusätzliche Sicherung; der Erstautor legt die Datei zu den
   Server-Dateien in `bench/reader/readings/`.
