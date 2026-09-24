# Benchmark local des modèles Ollama

Ce dossier contient un benchmark simple et reproductible des modèles locaux utilisés par la plateforme.

## Objectif

Comparer les modèles sur trois tâches représentatives :

- refactorisation et test Python ;
- analyse SQL PostgreSQL ;
- rédaction d’un runbook technique.

Le benchmark sert à orienter les usages sur cette machine locale. Il ne constitue pas un classement général des modèles.

## Modèles évalués

- `qwen3:8b`
- `qwen2.5-coder:7b`
- `gemma3:4b`

## Protocole

- Les prompts sont versionnés dans `prompts/`.
- Les modèles sont exécutés séquentiellement.
- Une chauffe par couple modèle-tâche est exécutée mais non incluse dans les mesures.
- Trois répétitions mesurées sont exécutées par couple modèle-tâche.
- Les paramètres de génération sont fixés : température `0`, seed `42`, limite de `1024` tokens et raisonnement Qwen désactivé.
- `keep_alive` vaut `0` afin de décharger le modèle après chaque requête et de limiter la pression mémoire sur une machine à 16 Go de mémoire unifiée.
- Les résultats bruts sont écrits dans `data/benchmarks/` et ignorés par Git.

Les mesures incluent le temps de chargement du modèle, car chaque requête le décharge ensuite. Elles reflètent donc un usage local séquentiel avec modèles non maintenus en mémoire, et non un scénario de service multi-utilisateur.

## Prérequis

- Ollama démarré localement sur `127.0.0.1:11434`.
- Les trois modèles présents dans Ollama.
- Python 3.

Vérifier les modèles disponibles :

```bash
curl -sS http://127.0.0.1:11434/api/tags | python3 -m json.tool
```

## Exécution

Depuis la racine du dépôt :

```bash
python3 benchmarks/run_benchmark.py --repetitions 3
```

Éviter les générations concurrentes dans Open WebUI ou Continue pendant l’exécution.

Pour un test rapide sans chauffe :

```bash
python3 benchmarks/run_benchmark.py --repetitions 1 --skip-warmup
```

## Résultats

Chaque exécution crée un répertoire horodaté dans :

```text
data/benchmarks/<run_id>/
```

Il contient :

- `run_config.json` : paramètres de l’exécution ;
- `results.csv` : métriques synthétiques ;
- un fichier JSON par réponse générée, avec les métriques retournées par Ollama.

Les métriques principales sont :

- `wall_seconds` : durée observée par le script ;
- `total_seconds` : durée totale rapportée par Ollama ;
- `load_seconds` : temps de chargement ;
- `eval_count` : nombre de tokens générés ;
- `tokens_per_second` : débit de génération.

Le rapport de résultats et la revue qualitative sont disponibles dans [`docs/model-benchmark.md`](../docs/model-benchmark.md).

## Limites

- Les résultats dépendent du matériel, des versions installées, de la quantification des modèles et de la configuration Ollama.
- Le protocole ne mesure ni la concurrence, ni la charge multi-utilisateur, ni la haute disponibilité.
- Les réponses de code, SQL et opérations doivent être relues avant utilisation.
- La revue qualitative porte sur un exemple par modèle et par tâche : elle est indicative et ne remplace pas des tests exhaustifs.
