# Architecture

## Vue d’ensemble

Local AI Lab est une plateforme locale d’expérimentation LLM et de pratiques LLMOps légères. Elle sépare deux instances Open WebUI tout en mutualisant une seule installation native d’Ollama.

```text
Usage personnel local
        │
        ▼
Open WebUI personnel
127.0.0.1:<personal-port>
        │
        ├────────────────────────────────────┐
        │                                    │
        ▼                                    ▼
Docker Desktop                    Ollama natif sur macOS
                                              │
Usage partagé privé                         127.0.0.1:11434
via appareils autorisés                         │
du tailnet                                      ▼
        │                              Modèles sur stockage externe
        ▼
Tailscale Serve (HTTPS, tailnet only)
        │
        ▼
Open WebUI partagé
127.0.0.1:<shared-port>
```

## Composants

| Composant | Rôle | Exposition |
|---|---|---|
| Ollama natif | Exécute les modèles LLM locaux | Loopback uniquement |
| Open WebUI personnel | Interface réservée à l’utilisateur local | Loopback uniquement |
| Open WebUI partagé | Interface d’un petit groupe autorisé | Loopback, relayée par Tailscale Serve |
| Docker Compose | Définit et orchestre les instances Open WebUI | Local au Mac |
| Tailscale Serve | Termine HTTPS et relaye l’interface partagée au tailnet | Appareils autorisés du tailnet |
| Stockage externe | Conserve les modèles Ollama | Local au Mac |
| Stockage persistant Open WebUI | Conserve comptes, conversations, fichiers et réglages | Répertoires distincts, hors Git |

## Frontières de confiance

Le modèle privilégie la réduction de surface d’exposition :

- Ollama écoute uniquement sur `127.0.0.1:11434` et n’est jamais exposé directement.
- Les ports Open WebUI sont liés à `127.0.0.1`, pas à `0.0.0.0`.
- L’instance personnelle ne sort pas du Mac.
- L’instance partagée reste locale côté Docker, puis est publiée au tailnet par Tailscale Serve.
- Tailscale Funnel n’est pas utilisé : aucune publication directe sur Internet n’est prévue.
- Open WebUI conserve une authentification applicative active, même derrière le réseau privé Tailscale.

## Isolation des instances

Les instances personnelle et partagée disposent chacune de leur propre :

- fichier Compose ;
- conteneur ;
- port local ;
- répertoire persistant ;
- comptes utilisateurs ;
- conversations ;
- paramètres ;
- fichiers importés.

Elles partagent uniquement le service Ollama local et les modèles. Ce choix évite la duplication des modèles tout en empêchant un mélange des données applicatives.

## Flux réseau

### Instance personnelle

```text
Navigateur local
    │ HTTP local
    ▼
Open WebUI personnel : 127.0.0.1:<personal-port>
    │ réseau Docker vers l’hôte
    ▼
Ollama : host.docker.internal:11434
```

### Instance partagée

```text
Navigateur sur appareil autorisé
    │ HTTPS chiffré dans le tailnet
    ▼
Tailscale Serve
    │ proxy HTTP local
    ▼
Open WebUI partagé : 127.0.0.1:<shared-port>
    │ réseau Docker vers l’hôte
    ▼
Ollama : host.docker.internal:11434
```

## Persistance et sauvegardes

Les données d’Open WebUI sont montées depuis des répertoires hôtes distincts. Elles ne sont pas commitées dans Git.

Les scripts de sauvegarde archivent pour chaque instance :

- le fichier Compose correspondant ;
- le répertoire de données persistant ;
- une archive horodatée dans le répertoire local de sauvegardes.

Les modèles Ollama sont stockés séparément sur le stockage externe et ne font pas partie des archives Open WebUI.

## Limites

- Plateforme mono-machine, sans haute disponibilité.
- Ressources limitées par la mémoire unifiée et la capacité de calcul du Mac.
- Une interruption d’Ollama, Docker Desktop, du stockage externe ou du Mac rend les services indisponibles.
- Les sauvegardes locales ne remplacent pas une stratégie de sauvegarde hors machine.
- Le projet vise un petit groupe de confiance, pas un service Internet public à grande échelle.
