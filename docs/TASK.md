# Coding Challenge 1 — Catalog Transformation

## Task description

You will process a shoe supplier catalog delivered as two files: `pricat.csv` and `mappings.csv`. The goal is to transform the supplier’s *flat* price catalog into a more structured format using the mapping configuration. 

---

## Input files

### `pricat.csv`

* A “price catalog” in a **flat format** where **every possible configuration** of a shoe is represented by **a single line**. 
* Uses **semicolon (`;`)** as column separator. 
* The **first line is the header** (column names), and **the header can differ for every pricat received**. 

**Example (conceptual):**
If article `15189-02-001` is available in sizes 36/37/38 and colors black/white (but size 37 only in white), it becomes 5 records: 

* `15189-02-001;36;white`
* `15189-02-001;37;white`
* `15189-02-001;38;white`
* `15189-02-001;36;black`
* `15189-02-001;38;black`

---

### `mappings.csv`

* Also a **semicolon-separated** file with **header in the first line**. 
* Each line defines a mapping from a **source field/value** to a **destination type/value**. Example: map `season=winter` → `type=season, value=Winter` (and similarly for summer). 
* Supports **multi-field mappings** where multiple source values must be combined to determine the destination value (e.g., `size_group_code` + `size_code` → `type=size, value=European size 36`). 
* **Not all columns are mapped**. Any **non-empty** column not covered by mappings should be **copied to the same type in the result** (example: `brand`). 

---

## Grouping and structure

`pricat.csv` is flat; the desired output should be structured as:

**Catalog → Article → Variation** 

Rules:

* Create **one Catalog** containing multiple **Articles**. 
* Each **Article** is defined by a **unique article number** and contains multiple **Variations**. 
* After grouping variations into articles by article number, **move attributes common to all children up to the parent**, both:

  * **Variation → Article**
  * **Article → Catalog** 

Hints:

* `brand` is the same in each row → belongs to **Catalog**
* `ean` is different per variation → stays at **Variation** 

---

## Output requirements

* Output the **entire structured Catalog** (including all Articles and Variations) in **JSON**. 
* You may choose the exact JSON shape, but it should be something an **API could return**. 
* Focus is on the **algorithm**; no need to build a web framework or UI—prioritize requirements, clean code, and tests. 

---

## Bonus points

* Add a **configurable option** to combine multiple fields into a new field, e.g. combine `price_buy_net` + `currency` → `price_buy_net_currency` producing `58.5 EUR`. 
* Write **unit and/or integration tests**. 

---

## Constraints

* If using Python: **do not use `pandas`**. 

---

## Submission (as stated in the document)

Share your GitHub repo with the coding challenge and/or email it as a ZIP archive to `reviewer@fashion.cloud`. 
