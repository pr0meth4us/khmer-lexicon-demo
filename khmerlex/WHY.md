# Why this package is vendored

`khmerlex` lives in `pr0meth4us/khmer-lexicon`. The clean arrangement is:

    khmerlex @ git+https://github.com/pr0meth4us/khmer-lexicon.git@main

in `requirements.txt`, so there is one implementation of the grapheme-cluster
layer, the Aho-Corasick automaton and the wrong-script tables.

That repo is currently **private**, and a git install from a private repo needs
a credential — which would mean a token in this repo, or a token in the build
environment of whatever hosts the demo. Neither is acceptable for something
meant to be publicly deployable with no secrets.

So this directory is a copy. **If the lexicon repo is made public, delete this
directory and put the git line back in `requirements.txt`** — nothing else
changes; the import path is identical.

Copied from khmer-lexicon @ cd76dfb.
