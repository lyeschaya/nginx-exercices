# Formation OpenShift - Chapitre 2

Exercices de déploiement nginx sur OpenShift via ArgoCD.

## Description

Ce dépôt contient les exercices pratiques du chapitre 2 de la formation OpenShift.
Chaque exercice est déployé automatiquement via ArgoCD dans un namespace dédié.

## Exercices

### nginx-exercice-1 — Déploiement nginx simple
- Déploiement de nginx-unprivileged
- Service et Route OpenShift
- Namespace : `exercice-nginx-1`

### nginx-exercice-2 — ConfigMap et Secret
- Déploiement nginx avec variables d'environnement
- ConfigMap : `nginx-config` (APP_MESSAGE)
- Secret : `nginx-secret` (USERNAME, PASSWORD)
- Page HTML personnalisée avec branding Neutron IT
- Namespace : `exercice-nginx-2`

### nginx-exercice-3 — Job et CronJob
- Job : exécution unique d'une commande echo
- CronJob : exécution toutes les minutes
- Déploiement nginx avec Service et Route
- Namespace : `exercice-nginx-3`

## Stack technique

- OpenShift Single Node (SNO)
- ArgoCD (GitOps)
- Kustomize
- nginx-unprivileged

## Auteur

Lyes Chaya — Neutron IT 2026
