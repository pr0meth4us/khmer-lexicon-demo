# វចនានុក្រមពាក្យផ្លូវការ · Official Khmer Terminology

A searchable dictionary of Cambodian government terminology — the approved Khmer
renderings of technical, legal, economic and administrative terms. 5,929 entries
from 15 official sources, each carrying the ministry, document and year it came
from.

Until now this existed almost entirely as scanned paper. A person could look a
term up; a program could not.

## Who it's for

**An official writing a letter** — *how do I say "blockchain" officially?* Search,
copy the approved Khmer, and see which ministry approved it, because that is what
makes it safe to put in a document someone else signs.

**A student or translator reading a decree** — what a term means, in English or
French, with a citable source.

**Anyone who hits a term in the news** — plain meaning, on a phone, in ten
seconds.

## Three things it does

1. **Search**, in Khmer or English, and **spelling doesn't have to be perfect**.
   Khmer is hard to type correctly, so when nothing matches exactly we look for
   entries one syllable away and suggest those. Type `ទិន្នន័` and you still get
   `ទិន្នន័យ`.
2. **Browse by topic** — law, digital and telecom, economics, geography, and so
   on, for people who arrive without a specific query.
3. **Check a letter** — paste a draft and see the official terms you've used,
   English words that have an approved Khmer form (with a one-tap replace), and
   characters that look like Khmer but aren't and will silently break search.

The interface is Khmer-first with English alongside. It's built for a phone.
No account, no API keys, no database — the dictionary is a static file, so
nothing can fail while you're using it, and it works offline once loaded.

The engineering — single-pass matching, syllable-aware boundaries, Unicode
confusables — is explained on the **/how** page rather than shown to people
trying to look a word up. What follows is that detail.

---

## Why this is not just a dictionary lookup

**Khmer is written without spaces between words.** A dictionary scan matches
any term that happens to sit inside a longer, unrelated word. Two filters, in
order:

**Grapheme clusters.** A Khmer syllable is several code points — a base
consonant, subscript consonants introduced by COENG (U+17D2), and vowel marks.
`len("ក្រសួង")` is 6 code points but 3 clusters: `ក្រ | សួ | ង`. A match whose
offsets fall between them would highlight half a syllable. Every match is
required to start and end on a UAX #29 cluster boundary, so highlight offsets
can never split a cluster — visibly correct on coeng terms like `ស្ត្រី`, which
is 6 code points and exactly **one** cluster.

**Word boundaries.** Cluster boundaries are *not* enough, and this was measured
rather than assumed: in the source lexicon, essentially every spurious match
begins and ends on a cluster boundary. So matches must also align with token
edges from `khmer-nltk`'s CRF tokenizer. This is what removes `ប្រក` sitting
inside `ប្រកាស` ("announce"). The toggle in the UI turns it off so you can see
what it catches.

Finally, longest match wins per position, so a nested term is reported once.
The panel reconciles: **raw hits = reported + rejected + nested**.

## The algorithm choice, and the honest benchmark

Scanning 5,689 terms naively is 5,689 passes over the document — `O(|text| ×
|terms|)`. Aho-Corasick is one pass whose cost does not grow with the
dictionary — `O(|text|)`. Both are implemented; **both are timed on every
request** and displayed.

Measured here, best of 7 runs per request:

| draft | chars | Aho-Corasick | naive | CRF segmenter | speedup |
|---|---:|---:|---:|---:|---:|
| Digital policy circular | 190 | 0.028 ms | 0.669 ms | 1.447 ms | 23.9× |
| Draft with English loanwords | 223 | 0.030 ms | 0.740 ms | 1.645 ms | 24.7× |
| Contaminated draft | 140 | 0.020 ms | 0.530 ms | 1.054 ms | 26.5× |
| Boundary trap | 127 | 0.018 ms | 0.501 ms | 0.922 ms | 27.8× |
| 20× concatenated draft | 3,800 | 0.538 ms | 9.817 ms | 25.800 ms | 18.2× |

**Naive is not always worse, and the UI says so.** Below roughly 220 terms the
naive loop wins, because `str.__contains__` runs in C while a Python automaton
walk does not. Measured separately on real generated letters:

| terms | naive | Aho-Corasick |
|---:|---:|---:|
| 4 | 0.004 ms | 0.202 ms — naive **49×** faster |
| 100 | 0.120 ms | 0.282 ms — naive 2.3× faster |
| 200 | 0.258 ms | 0.291 ms — naive 1.1× faster |
| 250 | 0.327 ms | 0.265 ms — aho 1.2× faster |
| 5,780 | 7.710 ms | 0.338 ms — aho **22.8×** faster |

The crossover is 200–250 terms. The shape is the point: naive is linear in the
term count, Aho-Corasick is flat at ~0.3 ms from 250 terms to 5,780.

And the result that matters most for honesty: **matching is not the
bottleneck.** The CRF segmenter costs roughly 50× more than the match itself.
Multi-pattern matching is effectively free; the linguistics is what costs.

Both paths are checked against each other on every request and the panel says
whether they agreed.

## Running it

```bash
pip install -r requirements.txt
python3 app.py          # http://localhost:8000
```

```bash
docker build -t terminology-checker . && docker run -p 8000:8000 terminology-checker
```

## Deploying

The Dockerfile is the deployment unit — it reads `$PORT`, warms the CRF model
at build time, and needs no secrets.

**Hugging Face Spaces** — free, no credit card, and the fastest path to a URL:

1. Create a Space at <https://huggingface.co/new-space> → SDK **Docker** →
   Blank → public.
2. Push this repo to it, with `SPACE_README.md` renamed as the Space's
   `README.md` (its YAML front-matter is what sets `app_port: 8000`):

   ```bash
   cp SPACE_README.md README_SPACE_TMP.md
   git remote add space https://huggingface.co/spaces/<user>/<space>
   git push space main
   ```

   Or simply drag the files into the Space's web uploader. The build takes a few
   minutes, mostly `khmer-nltk`.
3. The URL is `https://<user>-<space>.hf.space`.

**Fly.io** — `fly.toml` is committed and configured (Singapore, 1 GB, health
check on `/healthz`). Needs a payment method on the account, then:

```bash
flyctl deploy
```

**Koyeb**:

1. Push this repo to GitHub.
2. Koyeb → Create Service → GitHub → pick this repo.
3. Builder: **Dockerfile**. Port: **8000**. Instance: **Small** (the automaton
   plus the CRF model need ~512 MB; Nano will OOM).
4. Deploy. No environment variables are required.

Any Docker host works the same way — Fly.io (`fly launch`), Railway, Render,
Cloud Run. Keep it to **one worker**: each gunicorn worker builds its own
automaton and loads its own copy of the CRF model.

## API

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/check` | POST `{"text": "...", "segmenter": true}` | matches, rejects with reasons, loanwords, contamination, counters |
| `/api/about` | GET | entry counts and the source manifest |
| `/healthz` | GET | liveness |

## Layout

```
app.py          Flask routes
checker.py      matching, boundary filters, counters
samples.py      the four preloaded drafts
data/           unified_lexicon.json (static, 5,929 entries)
templates/      one page, no build step, no external assets
Dockerfile      deployment
```

Khmer primitives — grapheme clusters, the Aho-Corasick automaton, wrong-script
detection — come from `khmerlex`, which lives in the (currently private)
`pr0meth4us/khmer-lexicon` repo and is **vendored** here in `khmerlex/`. A git
install would need a credential, and this repo has no secrets in it. If that
repo is made public, delete `khmerlex/` and restore the one-line git dependency
in `requirements.txt` — see `khmerlex/WHY.md`.

## About the data

5,929 entries from 15 official Cambodian government sources: NCKL bulletins
(vols. 3–10) and its political science, economics, technology and geography
glossaries; the MPTC digital lexicon (2025); Council of Ministers legal terms
(2007); Pentagonal Strategy Phase 1 (2023); Royal Academy of Cambodia new-word
lists (2018). Built by Google Cloud Vision OCR over the source PDFs, LLM parsing
into structured entries, then normalisation and merge. **None of that runs at
request time** — the demo reads a static file.

### Known limitations, stated openly

- **24** entries have no Khmer form at all.
- **1,657** entries have no English gloss — they came from Khmer-only documents
  and display as `—`.
- **21** entries have a `khmer` field containing no Khmer characters: legacy
  Limon-font OCR read as Latin, plus six French grammar terms filed into the
  wrong column. These are excluded from the automaton.
- **121** exactly duplicated Khmer forms, and **164** near-duplicates one
  grapheme cluster apart, 33 of which are explained by empirically measured
  character confusions.
- A further **26** entries carry Latin inside the Khmer field, but only 19 of
  those are defects — the other 7 are `ខ្មែរ (English)` acronym style, which is
  correct.

## What it does NOT do yet

- **It does not segment unknown Khmer text.** It finds *known* terms. It cannot
  discover a new term, or tell you that an unmatched span is a term at all.
  Contrary to the usual framing, the CRF segmenter *is* already wired in — it is
  used as a boundary filter — but only to reject bad matches, never to propose
  new ones. Out-of-vocabulary term discovery is future work.
- **No measured precision or recall.** The boundary filter demonstrably removes
  false positives, but nobody has annotated a gold set and scored it. That is
  the single most valuable next piece of work and its absence should be counted
  against the demo.
- **`MIN_TERM_CLUSTERS` and the stop-word list are hand-tuned**, not learned.
- **Coverage is terminology, not vocabulary.** `ក្រសួង` ("ministry") is not a
  lexicon entry, so it is not highlighted. That surprises people.
- **Duplicate Khmer forms across sources are shown as multiple senses**, not
  disambiguated.
- **Loanword detection is exact-match on the English side.** Inflected or
  misspelled English will be missed.
- **The lexicon itself is not normalised for input text.** Input goes through no
  mark-order normalisation before matching, so a draft typed with marks in a
  non-canonical order can fail to match a term it visually equals.

## Credits

Segmentation and POS tagging by [khmer-nltk](https://github.com/VietHoang1512/khmer-nltk).
Character-confusion and search-frequency data by
[Seanghay Yath](https://huggingface.co/seanghay) (CC-BY-SA-4.0), aggregated from
3.2M khmerdict.com searches.
