# Architecture cible

## Décision principale

Ollama est exécuté directement sur macOS afin d’utiliser les modèles stockés sur le SSD externe. Open WebUI est exécuté dans des conteneurs Docker distincts.

## Séparation des responsabilités

| Composant | Rôle | Exposition prévue |
|---|---|---|
| Ollama | Inférence des modèles locaux | Localhost uniquement |
| Open WebUI personnel | Interface personnelle | Localhost uniquement |
| Open WebUI partagé | Interface pour un petit groupe | Réseau privé sécurisé |
| SSD externe | Stockage des modèles Ollama | Local au Mac |
| Docker Compose | Orchestration des interfaces | Local au Mac |

## Isolation des données

Les deux instances Open WebUI devront avoir des répertoires ou volumes persistants séparés. Elles ne partageront ni comptes, ni conversations, ni paramètres, ni fichiers importés.

## Justification

Cette séparation réduit le risque de mélange entre données personnelles et données d’utilisateurs partagés, tout en évitant de dupliquer les modèles et le serveur Ollama.
