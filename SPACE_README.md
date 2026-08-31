---
title: Official Terminology Checker
emoji: 🇰🇭
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8000
pinned: false
license: cc-by-sa-4.0
---

# Official Terminology Checker

Scans a Khmer government draft against 5,689 official terms in a single pass
(Aho-Corasick), on grapheme clusters rather than code points, and shows the work
done — matches, rejects with reasons, loanword suggestions, script
contamination, and both the single-pass and naive timings.

Full documentation, benchmarks and limitations: see `README.md` in the repo.
