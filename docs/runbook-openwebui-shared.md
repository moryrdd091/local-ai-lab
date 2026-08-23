# Runbook – Instance Open WebUI partagée

## Objectif

Documenter l'exploitation de l'instance Open WebUI partagée : santé, accès, sauvegarde, restauration et sécurité.

## Emplacement

- Racine du projet : le dossier cloné du dépôt `local-ai-lab`
- Fichier de composition : `compose/shared.compose.yml`
- Données persistantes : `data/open-webui-shared`
- Répertoire de sauvegardes local : `backups/`
- Conteneur : `open-webui-shared`
- Interface locale : `http://localhost:3001`

> Remplace `/chemin/vers/local-ai-lab` par le chemin local du dépôt sur ta machine.

## Accès et comptes

- L'authentification Open WebUI est active (`WEBUI_AUTH: "true"`).
- Les inscriptions sont désactivées (`ENABLE_SIGNUP: "false"`).
- Les comptes sont créés manuellement par un administrateur.
- Le premier compte créé est administrateur.
- Ne jamais partager un compte administrateur avec un utilisateur standard.
- L'accès distant privé est fourni par Tailscale Serve, uniquement aux appareils autorisés du tailnet.
- Le proxy Tailscale Serve cible l'interface locale sur `http://127.0.0.1:3001`.
- Tailscale Funnel n'est pas utilisé : aucun accès Internet public n'est prévu.

## Santé de l'instance

### Vérifier que le conteneur tourne

```bash
docker ps --filter "name=open-webui-shared"
```

Le conteneur doit apparaître avec un statut `Up` et idéalement `healthy`.

### Vérifier les logs

```bash
docker logs --tail 100 open-webui-shared
docker logs -f open-webui-shared
```

Rechercher :

- erreurs répétées ;
- échecs de connexion à Ollama ;
- erreurs de base de données ;
- redémarrages répétés.

### Vérifier l'interface web

1. Depuis le Mac hôte, ouvrir `http://localhost:3001`.
2. Depuis un appareil autorisé du tailnet, ouvrir l'URL HTTPS privée configurée par Tailscale Serve.
2. Se connecter avec le compte administrateur.
3. Vérifier :
   - le chargement de la page d'accueil ;
   - la présence des modèles Ollama ;
   - l'envoi et la réception d'un message avec un modèle ;
   - l'absence d'inscription publique ;
   - la liste des utilisateurs attendus dans l'administration.

### Vérifier les ressources

```bash
docker stats open-webui-shared
```

Surveiller une consommation CPU ou mémoire anormalement élevée et les redémarrages.

## Sauvegarde

### Principe

Chaque sauvegarde contient :

- `compose/shared.compose.yml` ;
- `data/open-webui-shared/`.

Les archives sont créées dans `backups/`. Elles sont locales et ignorées par Git.

### Exécuter une sauvegarde

```bash
cd /chemin/vers/local-ai-lab
./scripts/backup-openwebui-shared.sh
```

Résultat attendu :

```text
backups/openwebui-shared-backup-YYYY-MM-DD.tar.gz
```

### Vérifier le contenu d'une archive

```bash
cd /chemin/vers/local-ai-lab
tar -tzf backups/openwebui-shared-backup-YYYY-MM-DD.tar.gz | head -30
```

L'archive doit contenir `compose/shared.compose.yml` et `data/open-webui-shared/`.

### Sauvegarde cohérente avant une opération sensible

Avant une mise à jour importante ou une restauration de référence, arrêter brièvement l'instance afin de garantir un instantané cohérent de sa base de données :

```bash
cd /chemin/vers/local-ai-lab/compose
docker compose -f shared.compose.yml stop
```

Créer ensuite la sauvegarde :

```bash
cd /chemin/vers/local-ai-lab
./scripts/backup-openwebui-shared.sh
```

Puis redémarrer le service :

```bash
cd /chemin/vers/local-ai-lab/compose
docker compose -f shared.compose.yml start
```

## Restauration

> La restauration remplace les données actuellement présentes. Créer d'abord une sauvegarde de l'état courant si celui-ci doit être conservé.

1. Arrêter l'instance :

   ```bash
   cd /chemin/vers/local-ai-lab/compose
   docker compose -f shared.compose.yml down
   ```

2. Identifier l'archive à restaurer :

   ```bash
   cd /chemin/vers/local-ai-lab
   ls -lh backups/openwebui-shared-backup-*.tar.gz
   ```

3. Extraire l'archive depuis la racine du projet :

   ```bash
   tar -xzf backups/openwebui-shared-backup-YYYY-MM-DD.tar.gz
   ```

4. Redémarrer l'instance :

   ```bash
   cd compose
   docker compose -f shared.compose.yml up -d
   ```

5. Vérifier la santé :

   ```bash
   docker ps --filter "name=open-webui-shared"
   docker logs --tail 100 open-webui-shared
   ```

6. Vérifier l'interface, le compte admin, la liste des utilisateurs et les modèles.

## Sécurité

- Ne jamais exposer directement le port Ollama `11434`.
- Le port `3001` est actuellement lié à `127.0.0.1` et n'est pas accessible depuis le réseau local ou Internet.
- Ne pas créer de compte partagé : chaque personne doit utiliser son propre compte.
- Ne pas utiliser de compte administrateur pour les usages courants.
- Ne pas committer les données `data/`, les archives `backups/`, les fichiers `.env`, mots de passe, clés API ou tokens.
- Conserver Tailscale Serve pour l'accès distant privé et ne pas ouvrir de port entrant sur le routeur.
- Ne jamais utiliser `tailscale funnel` pour cette instance.

## Évolution

- Mettre à jour ce runbook lors d'un changement d'image Open WebUI, de volume, de port, de politique de comptes ou de mode d'accès.
- Mettre à jour la documentation Tailscale à chaque changement de proxy, d'URL ou de politique d'accès.
- Tester périodiquement une restauration dans un environnement isolé.