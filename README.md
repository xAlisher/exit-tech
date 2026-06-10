# exit.tech

**Exit is culture.** One line in, one exit out.

Type what you want to exit — WhatsApp, Google Photos, supermarket herbs —
and get a page with: why, how to get your stuff out first, where to go
(aggregated from credited open sources), how to burn the bridge, and a
copy-paste prompt that turns any AI agent into your personal exit guide.

## How it works

- `data/exits/<id>.yaml` — one file per exit: the dependency → exit-paths
  mapping. This is the only original dataset; everything else is aggregated
  and credited.
- `data/sources.yaml` — every external source, with license and role.
- `build.py` — validates every exit file, fetches live data (ToS;DR ratings,
  JustDeleteMe deletion links, awesome-privacy / awesome-selfhosted /
  web3privacy descriptions), caches it in `data/cache/`, renders the static
  site to `public/`.

```sh
python3 build.py            # fetch + build (needs PyYAML)
python3 build.py --offline  # build from cache only
python3 -m http.server -d public  # preview at localhost:8000
```

The merged dataset is republished openly at `/exits.json` — share-alike
honored, sources credited at `/sources.html`.

## Adding an exit

Copy `data/exits/_template.yaml` to `data/exits/<id>.yaml`, fill it in,
rebuild. The build validates every file (required fields, known categories
and path types, `recommended_by` ids must exist in `data/sources.yaml`) and
fails loudly on errors. Enrichment keys are optional — physical-world exits
work fine without them. Set `stub: true` for a page without curated routes;
it still gets a working agent prompt.

Requests land as GitHub issues: typing something unknown on the landing page
offers a prefilled `exit: <query>` issue.

## Automation

- `deploy.yml` — every push to master publishes `public/` to GitHub Pages
  (exit.tech)
- `validate.yml` — PRs and branches run the offline build as a schema check
- `refresh.yml` — weekly live rebuild (Mondays): re-fetches ratings and
  links, commits regenerated `public/` if anything changed, which triggers
  a deploy
