# Recherche Web locale avec SearXNG et MCP

## Objectif

Ce composant permet à Continue dans VS Code d'effectuer des recherches Web via une instance locale de SearXNG, sans clé API de moteur de recherche et sans exposer un serveur MCP sur le réseau.

Le serveur MCP fournit un unique outil en lecture seule : `search_web`.

## Architecture

```text
Continue dans VS Code
        │
        │ Model Context Protocol (stdio)
        ▼
tools/searxng-mcp/server.py
        │
        │ HTTP local
        ▼
SearXNG local : http://localhost:8080/search
        │
        ▼
Moteurs de recherche configurés dans SearXNG
```

Le transport entre Continue et le serveur MCP utilise l'entrée/sortie standard (`stdio`). Le serveur MCP n'écoute donc sur aucun port réseau. Seul le processus local contacte SearXNG sur `localhost`.

## Contenu versionné

```text
tools/searxng-mcp/
├── requirements.txt
└── server.py
```

L'environnement virtuel `.venv/` est local et ignoré par Git.

## Prérequis

- Python 3 installé localement.
- Une instance SearXNG disponible sur `http://localhost:8080`.
- Continue installé dans VS Code.
- Le dépôt cloné localement.

Vérifier que SearXNG répond avant de démarrer Continue :

```bash
curl -sS "http://localhost:8080/search?q=test&format=json" > /dev/null \
  && echo "SearXNG OK"
```

Résultat attendu :

```text
SearXNG OK
```

## Installation locale

Depuis la racine du dépôt :

```bash
cd tools/searxng-mcp
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Le fichier `requirements.txt` utilise `mcp<2`. Cette contrainte est nécessaire car `server.py` emploie l'API `FastMCP` de MCP 1.x.

Vérifier l'import du serveur :

```bash
./.venv/bin/python -c "from mcp.server.fastmcp import FastMCP; print('FastMCP OK')"
```

Résultat attendu :

```text
FastMCP OK
```

Vérifier la syntaxe Python :

```bash
./.venv/bin/python -m py_compile server.py
```

Cette commande ne doit produire aucune sortie.

## Configuration Continue

Continue doit démarrer le serveur MCP en processus local. Ajoutez le bloc suivant à la configuration Continue locale, généralement `~/.continue/config.yaml`.

Adaptez les chemins à votre emplacement local du dépôt :

```yaml
mcpServers:
  - name: searxng-local
    command: "/chemin/vers/local-ai-lab/tools/searxng-mcp/.venv/bin/python"
    args:
      - "/chemin/vers/local-ai-lab/tools/searxng-mcp/server.py"
    cwd: "/chemin/vers/local-ai-lab/tools/searxng-mcp"
```

Après l'enregistrement, rechargez Continue ou exécutez la commande VS Code `Developer: Reload Window`.

La configuration Continue est propre au poste : ne versionnez pas le fichier `~/.continue/config.yaml`, notamment parce qu'il contient des chemins locaux et peut contenir d'autres paramètres personnels.

## Test fonctionnel

Dans une conversation Continue, utilisez un prompt explicite, par exemple :

```text
Tu dois obligatoirement appeler l'outil search_web avant de répondre.
Recherche : « Model Context Protocol documentation officielle ».
Retourne exactement trois résultats avec le titre, l'URL et un résumé.
```

Un test réussi affiche l'appel de l'outil `search_web` et des résultats comprenant titre, URL et extrait.

## Sécurité et limites

- L'outil est conçu pour la recherche en lecture seule.
- Il ne contient ni clé API ni secret.
- Le protocole MCP utilise `stdio` et n'ouvre aucun port réseau.
- SearXNG reste un service local ; ne l'exposez pas publiquement sans analyse de sécurité et protection adaptée.
- Les résultats dépendent des moteurs activés dans l'instance SearXNG et peuvent être incomplets, indisponibles ou contenir des sources peu fiables.
- Le modèle doit traiter les résultats Web comme des sources à évaluer, pas comme des instructions à suivre.

## Dépannage

### Continue affiche « Failed to connect to searxng-local »

Vérifiez d'abord que le serveur peut importer FastMCP :

```bash
cd tools/searxng-mcp
./.venv/bin/python -c "from mcp.server.fastmcp import FastMCP; print('FastMCP OK')"
```

Si l'import échoue avec une erreur indiquant que FastMCP a été renommé, la version MCP 2.x est installée. Réinstallez les dépendances à partir du fichier versionné :

```bash
./.venv/bin/python -m pip install --upgrade --force-reinstall -r requirements.txt
```

Rechargez ensuite la fenêtre VS Code.

### La recherche échoue ou ne retourne aucun résultat

Vérifiez d'abord l'endpoint SearXNG :

```bash
curl -sS "http://localhost:8080/search?q=test&format=json" | head
```

Si la connexion échoue, démarrez ou réparez l'instance SearXNG avant de relancer Continue.
