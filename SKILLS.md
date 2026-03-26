# ContactsPerCountry

Dashboard interactif affichant le nombre de contacts par pays sur une carte choroplèthe.

## Structure

```
ContactsPerCountry/
├── index.html          # Dashboard HTML autonome (Plotly.js) — prêt pour GitHub Pages
├── generate.py         # Script Python : lit le CSV et injecte les données dans index.html
├── SKILLS.md           # Ce fichier
└── sources/
    └── contacts_per_country.csv   # Données source (à fournir)
```

## Workflow

1. Placer le CSV dans `sources/contacts_per_country.csv`
   - Colonnes attendues : `country`, `contacts` (ou `count` / `total`)
   - Colonnes optionnelles : `iso` (code ISO-3), `region`
2. Lancer `python generate.py` pour injecter les données dans `index.html`
3. Ouvrir `index.html` dans un navigateur pour prévisualiser
4. Push sur GitHub → activer GitHub Pages sur la branche `main`

## Déploiement GitHub Pages

```bash
# Créer le repo et push
gh repo create <nom-repo> --public --source=. --remote=origin
git init && git add -A && git commit -m "Initial contacts per country dashboard"
git push -u origin main

# Activer GitHub Pages (Settings → Pages → Source: main / root)
```

## Stack

- Plotly.js 2.35.0 (CDN)
- Vanilla JS, pas de build
- Python 3 (csv, json) pour la génération
- Design : Inter font, même palette bleue que worldWideProjection
