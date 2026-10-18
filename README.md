# api-keeper

Finds deprecated API and model names in your code (and soon opens a PR with the fix).

## Run
    python scanner.py /path/to/your/repo

## Add a rule
Edit `rules.json`: vendor, old name, new name, link to the vendor's official deprecation page.

## Roadmap
- [x] Scanner
- [ ] Fixer: replace string, branch, commit, open PR
- [ ] GitHub Action
- [ ] More vendors
