# Exercice 4 — DaemonSet

## Contexte

Dans cet exercice, vous allez apprendre à utiliser la ressource **DaemonSet** sur OpenShift. Un DaemonSet garantit qu'une copie d'un Pod s'exécute sur tous les nœuds (ou certains nœuds sélectionnés) du cluster.

- **DaemonSet** : idéal pour les agents de logs, de monitoring ou les services d'infrastructure.

## Objectifs pédagogiques

- Comprendre la différence entre un Deployment et un DaemonSet.
- Déployer un DaemonSet Nginx.
- Vérifier la répartition des Pods sur les nœuds du cluster.

## Prérequis

- Avoir complété l'exercice 3.
- Être connecté au cluster OpenShift.
- Namespace : `formation-openshift`.

## Instructions

### Étape 1 — Créer le DaemonSet

- Modifier le fichier `daemonset.yaml` dans `prerequis/`.
- Changer le `kind: Deployment` par `kind: DaemonSet`.
- Retirer le champ `replicas` (un DaemonSet n'utilise pas `replicas`, il gère la réplication par nœud).
- Appliquer la configuration manuellement dans la console.

### Étape 2 — Vérifier les Pods

- Aller dans **Workloads → DaemonSets**.
- Vérifier le nombre de Pods créés.
- Aller dans **Workloads → Pods** et observer la colonne **Node**.
- Vous devriez voir un Pod par nœud (worker).

### Étape 3 — Exposer le service

- Créer un Service et une Route pour accéder à votre application (fichiers `service.yaml` et `route.yaml`).
- Vérifier l'accès via l'URL de la Route.

## Résultat attendu

- Un Pod s'exécute sur chaque nœud du cluster.
- L'application Nginx est accessible via la Route OpenShift.

## Bloqué ?

Consultez le dossier `solution/` pour voir les fichiers corrigés.
