# **Regeln der 3. Normalform (3NF)**

### **Regeln:**
1. **Eindeutige Zeilen:** Jede Zeile in der Tabelle wird durch einen **Primärschlüssel** (oder einen zusammengesetzten Primärschlüssel) eindeutig identifiziert.
2. **Nur direkte Abhängigkeiten:** Jede Spalte in der Tabelle muss **direkt vom Primärschlüssel** abhängen – und **nur vom Primärschlüssel**. Dies gilt auch für zusammengesetzte Primärschlüssel.
3. **Keine überflüssigen Verbindungen zwischen Spalten:** Es darf keine Abhängigkeiten zwischen Nicht-Schlüssel-Spalten geben.
4. **Atomarität:** Alle Werte in der Tabelle müssen **atomar** sein, das heißt, jede Zelle enthält genau **einen einzelnen Wert** und keine Listen oder Kombinationen von Werten.

---

### **Einfacher Merksatz:**
- Jede Spalte beschreibt **direkt** das, was der Primärschlüssel beschreibt, und nichts anderes.
- Jede Zelle enthält genau **einen einzelnen Wert**.

---

### **Beispiele für Regelverstöße:**

#### **Verstoß: Abhängigkeit zwischen Nicht-Schlüssel-Spalten**
**Tabelle:**

| Bestellnummer | Kundennummer | Kundenname  | Kundenadresse |
|---------------|--------------|-------------|---------------|
| 123           | K001         | Max Muster  | Musterstraße 1|

**Problem:**
- „Kundenname“ und „Kundenadresse“ hängen nicht direkt von der Bestellnummer ab, sondern nur von der Kundennummer.

**Lösung:**
- „Kundennummer“, „Kundenname“ und „Kundenadresse“ kommen in eine eigene Tabelle „Kunden“.

---

#### **Verstoß: Spalte hängt nicht direkt vom Primärschlüssel ab**
**Tabelle:**

| Artikelnummer | Lagerbestand | Lieferant      | Lieferant-Adresse |
|---------------|--------------|----------------|--------------------|
| A001          | 50           | Firma XY       | XY-Straße 10       |

**Problem:**
- „Lieferant-Adresse“ hängt nicht direkt von der Artikelnummer ab, sondern nur vom Lieferanten.

**Lösung:**
- „Lieferant“ und „Lieferant-Adresse“ kommen in eine eigene Tabelle „Lieferanten“.

---

#### **Verstoß: Verletzung der Atomarität**
**Tabelle:**

| Artikelnummer | Lagerbestand | Farben             |
|---------------|--------------|--------------------|
| A001          | 50           | rot, blau, grün    |

**Problem:**
- Die Spalte „Farben“ enthält mehrere Werte in einer Zelle.

**Lösung:**
- Eine zusätzliche Tabelle „Farben“ erstellen:

**Neue Tabellenstruktur:**

**Artikel:**

| Artikelnummer | Lagerbestand |
|---------------|--------------|
| A001          | 50           |

**Farben:**

| Artikelnummer | Farbe  |
|---------------|--------|
| A001          | rot    |
| A001          | blau   |
| A001          | grün   |

---

### **Zusammenfassung:**
Um die 3. Normalform zu erfüllen, müssen folgende Fragen beantwortet werden:
1. Gibt es Spalten, die nicht direkt vom Primärschlüssel (oder zusammengesetzten Primärschlüssel) abhängen? → **Dann auslagern.**
2. Gibt es Abhängigkeiten zwischen Nicht-Schlüssel-Spalten? → **Dann auslagern.**
3. Gibt es Zellen, die mehrere Werte enthalten? → **Aufteilen, bis jede Zelle nur einen Wert enthält.**

**Das Ziel:** Jede Tabelle enthält nur **Informationen zu einem klaren Thema**, und jede Zelle ist atomar.