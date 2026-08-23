# Threat model

## Portée

Ce document décrit les risques principaux d’une plateforme LLM locale exécutée sur une machine personnelle, avec une instance Open WebUI personnelle et une instance partagée accessible uniquement via un réseau privé Tailscale.

Il ne constitue pas une certification de sécurité ni une garantie contre tous les risques. Son objectif est de rendre les compromis explicites et d’orienter les contrôles opérationnels.

## Actifs à protéger

| Actif | Risque en cas de compromission |
|---|---|
| Conversations et prompts | Divulgation de données personnelles, techniques ou sensibles |
| Comptes Open WebUI | Usurpation, accès non autorisé, élévation de privilèges |
| Fichiers importés | Fuite de documents ou de données intégrées à une conversation |
| Données persistantes | Perte, corruption ou mélange entre les deux instances |
| Secrets et paramètres | Accès non autorisé à des services ou à l’administration |
| Configuration Compose | Publication involontaire de ports, rupture de l’isolation |
| Modèles et stockage externe | Indisponibilité du service ou perte des modèles |
| Mac hôte | Accès à l’ensemble de la plateforme et des données locales |

## Hypothèses

- Les utilisateurs autorisés du tailnet sont de confiance, mais leurs appareils doivent rester protégés.
- Le Mac hôte est administré par une personne de confiance.
- Les services ne sont pas destinés à être accessibles depuis Internet.
- Les données saisies dans un LLM local doivent rester adaptées à un environnement de confiance.

## Menaces et contrôles

| Menace | Impact | Contrôles appliqués | Limites |
|---|---|---|---|
| Publication accidentelle d’un port Docker | Accès réseau non autorisé | Ports liés à `127.0.0.1`, vérification Compose | Une modification future peut réintroduire `0.0.0.0` |
| Exposition directe d’Ollama | Utilisation non autorisée, fuite via API | Ollama limité au loopback | À contrôler après toute modification de configuration |
| Accès partagé depuis Internet | Intrusion, scan automatisé, abus | Tailscale Serve uniquement, Funnel interdit | Dépend des règles et appareils du tailnet |
| Compte Open WebUI compromis | Lecture ou modification de données | Authentification active, inscriptions désactivées, comptes individuels | Mot de passe faible ou appareil compromis restent des risques |
| Mélange des données personnelles et partagées | Fuite de conversations ou fichiers | Répertoires persistants et conteneurs distincts | Une mauvaise modification de volume peut rompre l’isolation |
| Perte ou corruption de données | Indisponibilité, perte de conversations | Scripts de sauvegarde et procédures de restauration | Sauvegardes locales insuffisantes contre perte du Mac |
| Secret commité dans Git | Exposition durable dans l’historique Git | `.gitignore`, usage de fichiers non versionnés, revue avant commit | Erreur humaine possible |
| Mise à jour applicative non maîtrisée | Régression, incompatibilité, vulnérabilité | Image Docker épinglée, sauvegarde avant changement | Les mises à jour de sécurité doivent être évaluées régulièrement |
| Saturation CPU, mémoire ou stockage | Lenteur, indisponibilité | Petit groupe, modèles adaptés, vérification des ressources | Pas de scalabilité ni de haute disponibilité |
| Vol ou compromission du Mac | Accès global aux données locales | Sécurité macOS, comptes protégés, sauvegardes | Le projet dépend du niveau de sécurité de l’hôte |

## Contrôles obligatoires

- Conserver `WEBUI_AUTH=true`.
- Désactiver les inscriptions publiques après création des comptes autorisés.
- Lier les ports Open WebUI à `127.0.0.1`.
- Ne jamais exposer directement le port Ollama.
- Utiliser Tailscale Serve pour l’accès partagé et ne jamais activer Funnel.
- Garder des volumes ou répertoires de données distincts par instance.
- Ne pas commiter de données, archives, fichiers `.env`, mots de passe, clés ou jetons.
- Créer une sauvegarde avant une mise à jour, migration ou restauration.
- Vérifier les services après toute modification de Compose ou de Tailscale.

## Risques résiduels

- La plateforme reste dépendante d’une seule machine.
- Les utilisateurs du tailnet peuvent accéder à l’instance partagée s’ils sont autorisés par la politique Tailscale.
- Les sauvegardes locales ne protègent pas contre un incident affectant simultanément le Mac et les archives.
- La protection des données dépend aussi des pratiques utilisateurs : mots de passe, verrouillage des appareils, nature des prompts et des fichiers importés.
