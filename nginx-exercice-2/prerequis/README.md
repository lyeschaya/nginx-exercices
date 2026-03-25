# # Exercice 2 — ConfigMap et Secret

## Contexte
Dans cet exercice, vous allez apprendre à gérer la configuration d'une application nginx sur OpenShift en utilisant deux ressources Kubernetes :
- **ConfigMap** : pour stocker des données de configuration non sensibles
- **Secret** : pour stocker des données sensibles (mots de passe, tokens)

## Objectifs pédagogiques
- Comprendre la différence entre ConfigMap et Secret
- Créer et injecter des variables d'environnement dans un pod
- Vérifier que les variables sont bien accessibles dans le conteneur

## Prérequis
- Avoir complété l'exercice 1
- Être connecté au cluster OpenShift
- Namespace : `formation-openshift`

## Instructions

### Étape 1 — Créer le ConfigMap
```bash
oc create configmap nginx-config-2 --from-literal=APP_MESSAGE="Bienvenue dans NGINX avec ConfigMap" -n formation-openshift
```

### Étape 2 — Créer le Secret
```bash
oc create secret generic nginx-secret-2 --from-literal=USERNAME=admin --from-literal=PASSWORD=admin123 -n formation-openshift
```

### Étape 3 — Compléter le deployment.yaml
Ouvrez le fichier `deployment.yaml` et complétez la section `env` :
```yaml
env:
  - name: APP_MESSAGE
    valueFrom:
      configMapKeyRef:
        name: nginx-config-2
        key: APP_MESSAGE
  - name: USERNAME
    valueFrom:
      secretKeyRef:
        name: nginx-secret-2
        key: USERNAME
  - name: PASSWORD
    valueFrom:
      secretKeyRef:
        name: nginx-secret-2
        key: PASSWORD
```

### Étape 4 — Appliquer
```bash
oc apply -f deployment.yaml -f service.yaml -f route.yaml -n formation-openshift
```

### Étape 5 — Vérifier les pods
```bash
oc get pods -n formation-openshift
```

### Étape 6 — Tester le ConfigMap et le Secret
Entrez dans le pod et vérifiez les variables :
```bash
oc exec -it <pod> -n formation-openshift -- env | grep -E "APP_MESSAGE|USERNAME|PASSWORD"
```

Résultat attendu :
```
APP_MESSAGE=Bienvenue dans NGINX avec ConfigMap
USERNAME=admin
PASSWORD=admin123
```

Ou testez variable par variable :
```bash
oc exec -it <pod> -n formation-openshift -- sh -c 'echo $APP_MESSAGE'
oc exec -it <pod> -n formation-openshift -- sh -c 'echo $USERNAME'
oc exec -it <pod> -n formation-openshift -- sh -c 'echo $PASSWORD'
```

### Étape 7 — Tester depuis la console OpenShift
1. Allez dans **Workloads** → **Pods**
2. Cliquez sur un pod → onglet **Terminal**
3. Tapez :
```bash
echo $APP_MESSAGE
echo $USERNAME
echo $PASSWORD
```

## Bloqué ?
Consultez le dossier `solution/` ou l'app ArgoCD `formation-exercice-2`.Exercice 2 — ConfigMap et Secret

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
