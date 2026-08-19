# Local AI Lab

Environnement personnel d’expérimentation pour le développement Python, l’AI/ML engineering et les LLM exécutés localement.

## Objectifs

- Construire des projets Python propres et reproductibles
- Expérimenter avec des modèles de langage locaux via Ollama
- Pratiquer le traitement de données, le machine learning et l’engineering
- Documenter les apprentissages et les décisions techniques en Markdown

## Environnement local

- Mac mini M4
- Python
- Git et GitHub
- Ollama
- Modèles locaux stockés sur SSD externe

## Modèles disponibles

- `qwen3:8b` — assistant général et technique
- `qwen2.5-coder:7b` — développement Python, SQL, scripts et revue de code
- `gemma3:4b` — tâches rapides, synthèses et Markdown

## Structure envisagée

```text
local-ai-lab/
├── README.md
├── notebooks/       # Explorations et essais
├── src/             # Code source réutilisable
├── data/            # Données locales, non versionnées
├── docs/            # Notes et documentation
├── tests/           # Tests automatisés
└── requirements.txt # Dépendances Python
```

## Principes

- Local-first lorsque c’est pertinent
- Données sensibles conservées hors du dépôt
- Expériences documentées et reproductibles
- Dépendances isolées dans un environnement virtuel Python
