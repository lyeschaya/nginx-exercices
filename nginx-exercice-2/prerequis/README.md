# Exercice 2 — ConfigMap et Secret

## Objectif
Injecter des variables de configuration dans nginx via ConfigMap et Secret.

## Prérequis
- Avoir complété l'exercice 1
- Namespace : `formation-openshift`

## Ce que tu dois faire

### Étape 1 — Créer le ConfigMap
```bash
oc create configmap nginx-config-2 \
  --from-literal=APP_MESSAGE="Bienvenue dans NGINX avec ConfigMap" \
  -n formation-openshift
```

### Étape 2 — Créer le Secret
```bash
oc create secret generic nginx-secret-2 \
  --from-literal=USERNAME=admin \
  --from-literal=PASSWORD=admin123 \
  -n formation-openshift
```

### Étape 3 — Compléter le deployment.yaml
Ouvre le fichier `deployment.yaml` et ajoute les variables d'environnement manquantes.

### Étape 4 — Appliquer
```bash
oc apply -f deployment.yaml -n formation-openshift
oc apply -f service.yaml -n formation-openshift
oc apply -f route.yaml -n formation-openshift
```

### Étape 5 — Vérifier
```bash
oc get pods -n formation-openshift
oc exec -it <pod> -n formation-openshift -- env | grep -E "APP_MESSAGE|USERNAME|PASSWORD"
```

## Vous bloquez ?
Consultez le dossier `solution/` ou l'application ArgoCD `formation-exercice-2`
