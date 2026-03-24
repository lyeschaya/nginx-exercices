# Exercice 1 — Déploiement nginx simple

## Contexte
Dans cet exercice, vous allez déployer une application nginx sur OpenShift
en utilisant les ressources de base : Deployment, Service et Route.

## Objectifs pédagogiques
- Comprendre la structure d'un Deployment OpenShift
- Créer et exposer un Service
- Accéder à l'application via une Route

## Prérequis
- Accès au cluster OpenShift
- CLI `oc` installé et configuré
- Connecté en tant que `kubeadmin`

## Instructions

### Étape 1 — Créer le namespace
```bash
oc new-project exercice-nginx-1
```

### Étape 2 — Créer le Deployment
Créez un fichier `deployment.yaml` avec les caractéristiques suivantes :
- **Image** : `nginxinc/nginx-unprivileged`
- **Replicas** : 3
- **Port** : 8080

### Étape 3 — Créer le Service
Créez un fichier `service.yaml` qui expose le port 8080.

### Étape 4 — Créer la Route
Créez un fichier `route.yaml` pour exposer l'application.

### Étape 5 — Appliquer les fichiers
```bash
oc apply -f deployment.yaml -n exercice-nginx-1
oc apply -f service.yaml -n exercice-nginx-1
oc apply -f route.yaml -n exercice-nginx-1
```

### Étape 6 — Vérifier
```bash
oc get pods -n exercice-nginx-1
oc get route -n exercice-nginx-1
```

## Résultat attendu
- 3 pods en status `Running`
- Une route accessible dans le navigateur

## Vous bloquez ?
Consultez le dossier `solution/` ou l'application ArgoCD `nginx-exercice-1`
qui déploie automatiquement la solution complète.# Exercice 1 — Déploiement nginx simple

## Objectif
Déployer nginx sur OpenShift manuellement.

## Ce que tu dois faire

1. Créer un Deployment nginx-unprivileged
   - Image : nginxinc/nginx-unprivileged
   - Replicas : 3
   - Port : 8080

2. Créer un Service
   - Port : 8080

3. Créer une Route OpenShift

4. Namespace : exercice-nginx-1

## Commandes utiles
```bash
# Créer le namespace
oc new-project exercice-nginx-1

# Appliquer les fichiers
oc apply -f deployment.yaml
oc apply -f service.yaml
oc apply -f route.yaml

# Vérifier
oc get pods -n exercice-nginx-1
oc get route -n exercice-nginx-1
```

## Si tu bloques
Regarde le dossier `solution/` ou ArgoCD app `nginx-exercice-1-solution`
