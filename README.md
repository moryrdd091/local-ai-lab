# Local AI Lab

Plateforme locale d’expérimentation LLM et de LLMOps, conçue sur Mac mini Apple Silicon.

Le projet vise à déployer de manière reproductible deux instances isolées d’Open WebUI, connectées à une seule installation locale d’Ollama :

- Une instance personnelle, réservée à un usage local
- Une instance partagée, réservée à un petit groupe autorisé via un accès privé sécurisé

> État : conception et préparation de l’infrastructure. Aucune instance partagée n’est encore exposée.

## Objectifs

- Exécuter des LLM open source localement avec Ollama
- Préserver le stockage interne grâce à un SSD externe dédié aux modèles
- Isoler les données, utilisateurs et paramètres entre l’usage personnel et partagé
- Mettre en pratique Docker Compose, gestion de configuration, sécurité et exploitation
- Produire une démonstration LLMOps/AI platform engineering documentée et reproductible

## Architecture cible

```text
Utilisateurs locaux
        │
        ▼
Open WebUI personnel ──────┐
                            │
                            ▼
                    Ollama natif sur macOS
                    API locale : 127.0.0.1:11434
                            │
                            ▼
                 Modèles sur SSD externe

Utilisateurs autorisés
via réseau privé sécurisé
        │
        ▼
Open WebUI partagé ─────────┘
```

## Stack technique

- macOS sur Mac mini Apple Silicon
- Ollama exécuté nativement sur macOS
- Open WebUI exécuté avec Docker Compose
- Docker Desktop
- Git et GitHub
- Tailscale prévu pour l’accès distant privé
- Markdown et scripts shell pour la documentation et l’exploitation

## Modèles locaux

Les modèles ne sont pas inclus dans ce dépôt Git. Ils sont stockés localement sur un SSD externe, configuré avec la variable `OLLAMA_MODELS`.

| Modèle | Usage principal |
|---|---|
| `qwen3:8b` | Assistant général, technique et documentation |
| `qwen2.5-coder:7b` | Python, SQL, shell, Git et revue de code |
| `gemma3:4b` | Tâches rapides, résumés et Markdown |

## Principes de sécurité

- L’API Ollama ne doit jamais être exposée directement sur Internet
- L’instance personnelle et l’instance partagée utilisent des stockages persistants distincts
- Les inscriptions publiques sont désactivées sur l’instance partagée
- Les secrets, mots de passe, tokens et fichiers `.env` ne sont jamais commités
- L’accès distant vise un réseau privé chiffré, pas une ouverture directe de ports sur Internet
- Les images Docker doivent être officielles et épinglées à une version testée
- Les sauvegardes et la restauration font partie du périmètre du projet

## Feuille de route

- [x] Préparer un environnement macOS propre et un dépôt GitHub
- [x] Installer Ollama et stocker les modèles sur SSD externe
- [x] Télécharger et vérifier les modèles locaux
- [ ] Installer et vérifier Docker Desktop
- [ ] Créer l’instance Open WebUI personnelle
- [ ] Créer l’instance Open WebUI partagée avec persistance isolée
- [ ] Mettre en place l’accès distant privé
- [ ] Ajouter sauvegardes, contrôles de santé et documentation d’exploitation
- [ ] Réaliser un benchmark reproductible des modèles locaux

## Limites connues

Cette plateforme fonctionne sur une machine personnelle avec 16 Go de mémoire unifiée. Elle n’est pas conçue pour la haute disponibilité ni pour un grand nombre d’utilisateurs simultanés. Le SSD externe doit être monté avant le démarrage d’Ollama.

## Licence

À définir avant toute réutilisation publique du code.
