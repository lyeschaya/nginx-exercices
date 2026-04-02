# Exercice 4 — DaemonSet

## Objectif

Créer un DaemonSet nginx qui tourne sur chaque nœud du cluster.

## Contexte

Un DaemonSet garantit qu'un pod tourne sur chaque nœud du cluster.
Contrairement à un Deployment, il s'adapte automatiquement au nombre de nœuds.

## Prérequis

- Avoir complété l'exercice 3
- Être connecté au cluster OpenShift
- Namespace : `formation-openshift`

## Instructions

### Étape 1 — Compléter le fichier `daemonset.yaml`

Deux champs sont à compléter :

1. **Le nom du DaemonSet** : `nginx-daemonset`
2. **L'image** : `nginxinc/nginx-unprivileged@sha256:...`

### Étape 2 — Vérifier les pods

Aller dans **Workloads → DaemonSets**

Vérifier que le DaemonSet affiche **3 of 3 pods** en statut Running.

### Étape 3 — Supprimer un pod

Aller dans **Workloads → Pods**, supprimer un pod `nginx-daemonset-xxxx`.

Observer qu'il est automatiquement recréé.

## Résultat attendu
```
NAME              DESIRED   CURRENT   READY
nginx-daemonset   3         3         3
```

Tous les pods doivent être en statut **Running**.

## Solution

Si tu es bloqué, la solution est disponible dans le dossier `solution/`.