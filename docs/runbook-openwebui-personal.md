# Runbook – Instance Open WebUI personnelle

## Objectif

Documenter l'exploitation (santé, sauvegarde, restauration) de l'instance Open WebUI personnelle.

## Emplacement

- Racine du projet : le dossier cloné du dépôt `local-ai-lab`
- Fichier de composition : `compose/personal.compose.yml`
- Données persistantes : `data/open-webui-personal`
- Répertoire de sauvegardes local : `backups/`

## Santé de l'instance

### Vérifier que le conteneur tourne

```bash
docker ps --filter "name=open-webui-personal"
```

Le conteneur doit apparaître avec un statut `Up` et idéalement `healthy`.

### Vérifier les logs

```bash
docker logs --tail 100 open-webui-personal
docker logs -f open-webui-personal
```

Rechercher :

- erreurs répétées,
- panics / crash loops,
- messages d'authentification ou de base de données anormaux.

### Vérifier l'interface web

1. Ouvrir l'interface locale de l'instance (ex. `http://localhost:3000`).
2. Se connecter avec le compte admin.
3. Vérifier :
   - chargement de la page d'accueil,
   - création d'une conversation,
   - réponse d'un modèle.
4. Dans les paramètres d'administration :
   - confirmer que l'inscription (`ENABLE_SIGNUP`) est désactivée,
   - vérifier la liste des utilisateurs.

### Vérifier les ressources (optionnel)

```bash
docker stats open-webui-personal
```

Surveiller :

- CPU : pas de 100 % continu anormal,
- Mémoire : cohérent avec l'usage attendu,
- Pas de redémarrages incessants.

## Sauvegarde

### Principe

Sauvegarder :

- le fichier de composition : `compose/personal.compose.yml`
- le dossier de données : `data/open-webui-personal`

Les archives sont stockées dans `backups/` (ignoré par Git).

### Exécuter une sauvegarde manuelle
> Remplace `/chemin/vers/local-ai-lab` par le chemin local du dépôt sur ta machine.

```bash
cd /chemin/vers/local-ai-lab
./scripts/backup-openwebui-personal.sh
```

Résultat :

- Une archive `backups/openwebui-personal-backup-YYYY-MM-DD_HH-MM-SS.tar.gz`.

### Vérifier le contenu d’une archive

```bash
cd /chemin/vers/local-ai-lab
tar -tzf backups/openwebui-personal-backup-YYYY-MM-DD_HH-MM-SS.tar.gz | head -30
```

L’archive doit contenir `compose/personal.compose.yml` et `data/open-webui-personal/`.

### Sauvegarde cohérente avant une opération sensible

Avant une mise à jour importante ou une restauration de référence, arrêter brièvement l’instance afin de garantir un instantané cohérent de sa base de données :

```bash
cd /chemin/vers/local-ai-lab/compose
docker compose -f personal.compose.yml stop
```

Créer ensuite la sauvegarde :

```bash
cd /chemin/vers/local-ai-lab
./scripts/backup-openwebui-personal.sh
```

Puis redémarrer le service :

```bash
cd /chemin/vers/local-ai-lab/compose
docker compose -f personal.compose.yml start
```

## Restauration

### Cas d'usage

- Corruption de données,
- Migration vers une nouvelle machine,
- Test de restauration.

### Procédure

1. S'assurer que l'instance est arrêtée (optionnel mais recommandé) :

   ```bash
   cd /chemin/vers/local-ai-lab/compose
   docker compose -f personal.compose.yml down
   ```

2. Identifier l'archive à restaurer dans `backups/` :

   ```bash
   ls -lh backups/openwebui-personal-backup-*.tar.gz
   ```

3. Extraire l'archive depuis la racine du projet :

   ```bash
   cd /chemin/vers/local-ai-lab
   tar -xzf backups/openwebui-personal-backup-YYYY-MM-DD.tar.gz
   ```

   Cela écrasera :
   - `compose/personal.compose.yml`
   - `data/open-webui-personal`

4. Redémarrer l'instance :

   ```bash
   cd /chemin/vers/local-ai-lab/compose
   docker compose -f personal.compose.yml up -d
   ```

5. Vérifier la santé :

   - `docker ps`, `docker logs open-webui-personal`
   - Interface web : connexion, conversations, modèles.

## Sécurité

- Inscriptions désactivées (`ENABLE_SIGNUP: "false"`).
- Port exposé uniquement en local (`127.0.0.1:3000:8080`).
- Accès admin protégé par mot de passe.
- Sauvegardes régulières et test de restauration périodique recommandé.
- Ne jamais exposer directement le port Ollama `11434`.
- Ne pas committer `data/`, `backups/`, les fichiers `.env`, mots de passe, clés API ou tokens.

## Évolution

- En cas de changement de version d'image, mettre à jour ce runbook.
- En cas d'ajout de volumes ou de services, adapter le script de sauvegarde et ce document.