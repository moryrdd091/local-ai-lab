# Benchmark local des modèles Ollama

## Résumé

Ce benchmark compare trois modèles locaux utilisés par la plateforme sur des tâches de Python, SQL PostgreSQL et documentation technique.

Il vise à orienter les usages sur cette machine. Il ne constitue pas un classement général des modèles ni une évaluation de production exhaustive.

Résultat principal : `gemma3:4b` est le plus rapide, tandis que `qwen3:8b` a fourni les sorties techniques les plus cohérentes dans cette série limitée. Les trois modèles nécessitent une relecture humaine avant usage pour du code, SQL ou des actions opérationnelles.

## Environnement et protocole

- Machine : Mac mini Apple Silicon avec 16 Go de mémoire unifiée.
- Inférence : Ollama natif sur macOS, API locale sur `127.0.0.1:11434`.
- Stockage des modèles : SSD externe.
- Modèles : `qwen3:8b`, `qwen2.5-coder:7b` et `gemma3:4b`.
- Quantification installée : Q4_K_M pour les trois modèles lors du run analysé.
- Tâches : refactorisation Python, analyse SQL PostgreSQL et rédaction d’un runbook.
- Prompts : versionnés dans [`benchmarks/prompts/`](../benchmarks/prompts/).
- Paramètres : température `0`, seed `42`, limite de `1024` tokens, `think: false` et `keep_alive: 0`.
- Exécution : une chauffe non mesurée puis trois répétitions mesurées par couple modèle-tâche, séquentiellement.
- Run analysé : `20260924T090345Z`.

`keep_alive: 0` décharge le modèle après chaque requête. Les temps mesurés incluent donc le chargement du modèle et reflètent un usage local séquentiel avec modèles non conservés en mémoire.

Voir les instructions de reproduction dans [`benchmarks/README.md`](../benchmarks/README.md).

## Résultats de performance

Moyennes des trois répétitions. Le débit correspond aux tokens générés par seconde.

| Modèle | Python | SQL | Documentation | Interprétation |
|---|---:|---:|---:|---|
| `gemma3:4b` | 13,52 s / 36,60 tok/s | 18,18 s / 36,28 tok/s | 21,00 s / 36,14 tok/s | Le plus rapide sur les trois tâches |
| `qwen2.5-coder:7b` | 18,99 s / 22,25 tok/s | 27,69 s / 22,05 tok/s | 25,83 s / 21,98 tok/s | Compromis intermédiaire de vitesse |
| `qwen3:8b` | 20,96 s / 19,98 tok/s | 33,91 s / 19,83 tok/s | 25,74 s / 19,99 tok/s | Le plus lent dans ce protocole |

Les 27 requêtes mesurées se sont terminées avec `done_reason: stop`. Les neuf couples modèle-tâche ont produit des résultats stables entre les répétitions.

La vitesse ne suffit pas à déterminer le meilleur choix : les modèles ne produisent pas le même volume de texte et la qualité varie selon la tâche.

## Revue qualitative

La revue porte sur une réponse par modèle et par tâche. Elle vise à relever les erreurs ou corrections nécessaires, sans prétendre fournir une évaluation exhaustive.

| Modèle | Python | SQL | Documentation |
|---|---|---|---|
| `qwen3:8b` | Utilisable avec corrections mineures | Utilisable avec corrections mineures | Utilisable avec corrections mineures |
| `qwen2.5-coder:7b` | Utilisable avec corrections mineures | À éviter sans réécriture | À éviter sans forte adaptation |
| `gemma3:4b` | À éviter sans reprise | À éviter sans reprise | À éviter sans reprise |

### Qwen 3 8B

- Python : identifie les défauts essentiels et propose une implémentation cohérente. La réponse suppose implicitement que les types non numériques autres que `None` sont ignorés. Le test utilise `pytest.raises` sans `import pytest` et ne démontre pas explicitement l’échec de l’implémentation d’origine.
- SQL : bonne structure avec agrégation, tentative de série mensuelle, `LEFT JOIN` et `COALESCE`. La génération des mois dépend toutefois de `CURRENT_DATE` au lieu de fixer 2025. Le calcul de croissance teste le revenu courant au lieu du revenu précédent et doit protéger le dénominateur avec `NULLIF`.
- Documentation : structure complète, diagnostic globalement sûr et avertissement sécurité correct. Le test proposé avec `docker run --network host` n’est pas adapté à Docker Desktop sur macOS. `host.docker.internal` est le nom utilisé depuis le conteneur pour joindre l’hôte, pas une adresse sur laquelle Ollama doit écouter.

### Qwen 2.5 Coder 7B

- Python : implémentation raisonnable et test avec `import pytest`, mais conserve le paramètre mutable `values=[]`. Le diagnostic est partiellement confus et le test ne couvre pas suffisamment zéro, `None` mélangé à des nombres ni le calcul de la moyenne.
- SQL : ne génère pas les douze mois de 2025 et omet donc les mois sans commande payée. L’explication affirme une propriété que la requête ne satisfait pas.
- Documentation : garde-fous sécurité corrects, mais plusieurs commandes sont orientées Linux plutôt que macOS, notamment `sudo systemctl restart docker` et `./ollama start`. Le lien interne Open WebUI vers Ollama ne dépend pas de Tailscale.

### Gemma 3 4B

- Python : la sortie contient une contradiction sur le traitement des booléens et une explication erronée du paramètre mutable. Le test ne couvre pas les comportements demandés (`None`, booléens, zéro et `ValueError`).
- SQL : la requête omet `paid_order_count`, ne génère pas les mois vides, ne transforme pas les revenus absents en zéro et ne protège pas correctement la croissance contre un revenu précédent nul.
- Documentation : la réponse confond l’architecture en traitant Ollama comme un conteneur Docker. Certaines commandes sont inadaptées, telles que `ping 11434`, `docker restart <ollama_container_id>` et l’ouverture du port 11434 dans le pare-feu.

## Recommandations d’usage

- `gemma3:4b` : privilégier les brouillons, résumés, notes Markdown et tâches rapides à faible risque. Vérifier attentivement les sorties techniques.
- `qwen2.5-coder:7b` : utiliser comme assistant pour code et scripts avec revue humaine. Ne pas généraliser son orientation code à toutes les tâches SQL ou opérationnelles à partir de ce seul test.
- `qwen3:8b` : utiliser comme modèle généraliste par défaut pour les demandes techniques mixtes, la documentation et le SQL complexe, avec relecture systématique des dates, jointures, calculs et commandes d’exploitation.

## Limites

- Les résultats dépendent de cette machine, des versions des modèles, de leur quantification et de la configuration Ollama installée.
- Le benchmark mesure un usage séquentiel local, sans concurrence ni charge multi-utilisateur.
- Les temps incluent le chargement des modèles car ils sont déchargés après chaque requête.
- Trois répétitions sur un prompt par tâche ne suffisent pas pour établir une robustesse générale.
- La revue qualitative est manuelle et indicative.
- Les réponses générées restent des propositions : elles doivent être relues, testées et adaptées avant utilisation dans la plateforme.
