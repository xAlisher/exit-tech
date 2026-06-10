# exit.tech

**Exit as culture.** One line in, one exit out.

Type what you want to exit — WhatsApp, Google Photos, supermarket herbs —
and get a page with: why, how to get your stuff out first, where to go
(aggregated from credited open sources), how to burn the bridge, and a
copy-paste prompt that turns any AI agent into your personal exit guide.

## How it works

- `data/exits.yaml` — the dependency → exit-paths mapping. This is the only
  original dataset; everything else is aggregated and credited.
- `data/sources.yaml` — every external source, with license and role.
- `build.py` — fetches live data (ToS;DR ratings, JustDeleteMe deletion
  links, awesome-privacy / awesome-selfhosted / web3privacy descriptions),
  caches it in `data/cache/`, renders the static site to `public/`.

```sh
python3 build.py            # fetch + build (needs PyYAML)
python3 build.py --offline  # build from cache only
python3 -m http.server -d public  # preview at localhost:8000
```

The merged dataset is republished openly at `/exits.json` — share-alike
honored, sources credited at `/sources.html`.

## Adding an exit

Add an entry to `data/exits.yaml` (schema documented at the top of the
file), rebuild. Enrichment keys (`tosdr`, `justdeleteme`, `awesome_privacy`,
`awesome_selfhosted`, `web3privacy`) are optional — physical-world exits
work fine without them.
