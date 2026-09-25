# Operations runbook

## Objectif

Ce runbook décrit les opérations communes aux deux instances Open WebUI. Les procédures propres à chaque instance sont documentées dans les runbooks dédiés.

Les ports et chemins indiqués sous la forme `<...>` sont des placeholders. Consulter les runbooks dédiés pour les valeurs propres à chaque instance.

## Prérequis de démarrage

Avant de démarrer les services :

- Vérifier que Docker Desktop fonctionne.
- Vérifier que le stockage contenant les modèles Ollama est monté.
- Vérifier que les fichiers Compose sont valides.
- Vérifier qu’aucun changement de configuration non relu n’est en attente.

```bash
docker info >/dev/null
docker compose -f compose/personal.compose.yml config --quiet
docker compose -f compose/shared.compose.yml config --quiet
git status --short
```

## Démarrage

### 1. Démarrer Ollama

Démarrer Ollama sur l’hôte avec la variable qui pointe vers le stockage des modèles :

```bash
export OLLAMA_MODELS="<external-models-path>"
ollama serve
```

Dans un autre terminal :

```bash
ollama list
```

### 2. Démarrer les interfaces Open WebUI

```bash
docker compose -f compose/personal.compose.yml up -d
docker compose -f compose/shared.compose.yml up -d
```

### 3. Vérifier l’état

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
```

Tester les interfaces locales :

```bash
curl -I http://127.0.0.1:<personal-port>/
curl -I http://127.0.0.1:<shared-port>/
```

### 4. Vérifier le proxy privé

```bash
tailscale serve status
```

Le service partagé doit être affiché avec l’état `tailnet only`.

## Arrêt

Arrêter l’instance personnelle :

```bash
docker compose -f compose/personal.compose.yml down
```

Arrêter l’instance partagée :

```bash
docker compose -f compose/shared.compose.yml down
```

Puis arrêter Ollama dans le terminal où il est exécuté :

```text
Ctrl + C
```

Ne pas utiliser `docker compose down -v` sans sauvegarde validée : cette commande peut supprimer des volumes Docker gérés.

## Santé et diagnostic

### État des conteneurs

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
```

### Journaux

```bash
docker logs --tail 100 open-webui-personal
docker logs --tail 100 open-webui-shared
```

Suivre les logs en direct :

```bash
docker logs -f open-webui-personal
docker logs -f open-webui-shared
```

### Ressources

```bash
docker stats
```

### Vérifier Ollama

```bash
ollama list
curl -sS http://127.0.0.1:11434/api/tags | python3 -m json.tool
```

### Vérifier Tailscale

```bash
tailscale status
tailscale serve status
```

## Sauvegarde

Créer une sauvegarde personnelle :

```bash
./scripts/backup-openwebui-personal.sh
```

Créer une sauvegarde partagée :

```bash
./scripts/backup-openwebui-shared.sh
```

Vérifier le contenu d’une archive sans la restaurer :

```bash
tar -tzf backups/<backup-file>.tar.gz | head -30
```

Avant une mise à jour importante, arrêter brièvement l’instance concernée, créer une sauvegarde, puis la redémarrer.

Les scripts sauvegardent la configuration et les données Open WebUI, mais pas les modèles Ollama stockés sur le SSD externe. Après une perte du stockage externe, les modèles doivent être retéléchargés avec Ollama.

## Mise à jour contrôlée

1. Lire les notes de version de l’image ciblée.
2. Créer une sauvegarde de l’instance concernée.
3. Mettre à jour explicitement le tag dans le fichier Compose.
4. Valider le rendu Compose avec `docker compose config --quiet`.
5. Redémarrer uniquement l’instance concernée.
6. Vérifier l’interface, l’authentification, les modèles, les logs et les données.
7. Prévoir un retour au tag précédent si la validation échoue.

## Restauration

La restauration remplace les données de l’instance concernée.

1. Créer une sauvegarde de l’état actuel si nécessaire.
2. Arrêter l’instance.
3. Identifier l’archive de restauration.
4. Extraire l’archive depuis la racine du projet.
5. Redémarrer l’instance.
6. Vérifier les conteneurs, les logs, l’interface, les comptes et les modèles.

Consulter les runbooks dédiés pour les commandes précises propres à chaque instance.

## Règles d’exploitation

- Ne pas publier les ports Docker sur toutes les interfaces réseau.
- Ne pas exposer Ollama directement.
- Ne pas utiliser Tailscale Funnel.
- Ne pas partager de compte Open WebUI.
- Ne pas utiliser un compte administrateur pour les usages ordinaires.
- Ne pas commiter les données persistantes, les sauvegardes ou les secrets.
- Vérifier `git diff --check` et `git status` avant tout commit.
