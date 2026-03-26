from flask import Flask, render_template, jsonify
from kubernetes import client, config
import os

app = Flask(__name__)
config.load_incluster_config()
NAMESPACE = os.getenv("NAMESPACE", "formation-openshift")
MAX_MANUAL_JOBS = 3
MAX_TOTAL_JOBS = 10

# Configuration modifiable pour les Jobs manuels
MANUAL_JOB_CONFIG = {
    "image": "nginxinc/nginx-unprivileged@sha256:731f382bbad9a874f9f27db9c82d9e671e603e2210386a8e2b6da36cf336fa75",
    "command": "echo Bonjour depuis mon Job OpenShift"
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/jobs")
def get_jobs():
    core_v1 = client.CoreV1Api()
    batch_v1 = client.BatchV1Api()
    pods = core_v1.list_namespaced_pod(NAMESPACE)
    
    # On a besoin des jobs pour filtrer par type
    jobs = batch_v1.list_namespaced_job(NAMESPACE)
    job_map = {j.metadata.name: j for j in jobs.items}
    
    result = []
    for pod in pods.items:
        job_name = pod.metadata.labels.get("job-name")
        if not job_name or job_name not in job_map:
            continue
            
        job = job_map[job_name]
        owner_refs = job.metadata.owner_references or []
        is_scheduled = any(ref.kind == "CronJob" for ref in owner_refs)
        is_manual_cron = job.metadata.labels.get("type", "").startswith("cron-manual-")
        
        if is_scheduled or is_manual_cron:
            continue
            
        result.append({
            "name": pod.metadata.name,
            "job_name": job_name,
            "status": pod.status.phase,
            "start": str(pod.status.start_time) if pod.status.start_time else "N/A"
        })
    return jsonify(result)

@app.route("/api/cronjob-jobs")
def get_cronjob_jobs():
    core_v1 = client.CoreV1Api()
    batch_v1 = client.BatchV1Api()
    pods = core_v1.list_namespaced_pod(NAMESPACE)
    
    jobs = batch_v1.list_namespaced_job(NAMESPACE)
    job_map = {j.metadata.name: j for j in jobs.items}
    
    result = []
    for pod in pods.items:
        job_name = pod.metadata.labels.get("job-name")
        if not job_name or job_name not in job_map:
            continue
            
        job = job_map[job_name]
        owner_refs = job.metadata.owner_references or []
        is_scheduled = any(ref.kind == "CronJob" for ref in owner_refs)
        is_manual_cron = job.metadata.labels.get("type", "").startswith("cron-manual-")
        
        if not (is_scheduled or is_manual_cron):
            continue
            
        cron_name = "N/A"
        if is_scheduled:
            cron_name = owner_refs[0].name
        elif is_manual_cron:
            type_label = job.metadata.labels.get("type")
            cron_name = type_label.replace("cron-manual-", "") if type_label else "N/A"
            
        result.append({
            "name": pod.metadata.name,
            "job_name": job_name,
            "status": pod.status.phase,
            "start": str(pod.status.start_time) if pod.status.start_time else "N/A",
            "cronjob": cron_name
        })
    return jsonify(result)

@app.route("/api/cronjobs")
def get_cronjobs():
    batch_v1 = client.BatchV1Api()
    cronjobs = batch_v1.list_namespaced_cron_job(NAMESPACE)
    result = []
    for cj in cronjobs.items:
        result.append({
            "name": cj.metadata.name,
            "schedule": cj.spec.schedule,
            "last_schedule": str(cj.status.last_schedule_time) if cj.status.last_schedule_time else "Jamais",
            "active": len(cj.status.active) if cj.status.active else 0
        })
    return jsonify(result)

@app.route("/api/logs/<pod_name>")
def get_logs(pod_name):
    core_v1 = client.CoreV1Api()
    try:
        logs = core_v1.read_namespaced_pod_log(pod_name, NAMESPACE)
        return jsonify({"logs": logs, "pod": pod_name})
    except Exception as e:
        return jsonify({"logs": str(e)})

@app.route("/api/delete-job/<job_name>", methods=["DELETE"])
def delete_job(job_name):
    batch_v1 = client.BatchV1Api()
    batch_v1.delete_namespaced_job(
        job_name, NAMESPACE,
        body=client.V1DeleteOptions(propagation_policy="Foreground")
    )
    return jsonify({"status": "Job supprimé !"})

@app.route("/api/trigger-job", methods=["POST"])
def trigger_job():
    batch_v1 = client.BatchV1Api()

    # Vérifier limite totale
    all_jobs = batch_v1.list_namespaced_job(NAMESPACE)
    if len(all_jobs.items) >= MAX_TOTAL_JOBS:
        return jsonify({"status": "Limite totale atteinte ! Supprimez des jobs avant d'en créer de nouveaux."}), 429

    # Supprimer les anciens jobs manuels si limite atteinte
    jobs = batch_v1.list_namespaced_job(NAMESPACE, label_selector="type=manual")
    manual_jobs = sorted(jobs.items, key=lambda j: j.metadata.creation_timestamp)
    while len(manual_jobs) >= MAX_MANUAL_JOBS:
        oldest = manual_jobs.pop(0)
        batch_v1.delete_namespaced_job(
            oldest.metadata.name, NAMESPACE,
            body=client.V1DeleteOptions(propagation_policy="Foreground")
        )

    job_name = "manual-job-" + os.urandom(4).hex()
    job = client.V1Job(
        metadata=client.V1ObjectMeta(name=job_name, labels={"type": "manual"}),
        spec=client.V1JobSpec(
            ttl_seconds_after_finished=300,
            template=client.V1PodTemplateSpec(
                spec=client.V1PodSpec(
                    containers=[client.V1Container(
                        name="job",
                        image=MANUAL_JOB_CONFIG["image"],
                        command=["sh", "-c", MANUAL_JOB_CONFIG["command"]]
                    )],
                    restart_policy="Never"
                )
            )
        )
    )
    batch_v1.create_namespaced_job(NAMESPACE, job)
    return jsonify({"status": "Job déclenché !", "name": job_name})

@app.route("/api/trigger-cronjob/<cron_name>", methods=["POST"])
def trigger_cronjob(cron_name):
    batch_v1 = client.BatchV1Api()

    # Vérifier limite totale
    all_jobs = batch_v1.list_namespaced_job(NAMESPACE)
    if len(all_jobs.items) >= MAX_TOTAL_JOBS:
        return jsonify({"status": "Limite totale atteinte ! Supprimez des jobs avant d'en créer de nouveaux."}), 429

    # Supprimer les anciens jobs manuels du cronjob si limite atteinte
    jobs = batch_v1.list_namespaced_job(NAMESPACE, label_selector=f"type=cron-manual-{cron_name}")
    manual_jobs = sorted(jobs.items, key=lambda j: j.metadata.creation_timestamp)
    while len(manual_jobs) >= MAX_MANUAL_JOBS:
        oldest = manual_jobs.pop(0)
        batch_v1.delete_namespaced_job(
            oldest.metadata.name, NAMESPACE,
            body=client.V1DeleteOptions(propagation_policy="Foreground")
        )

    cron = batch_v1.read_namespaced_cron_job(cron_name, NAMESPACE)
    job_name = f"manual-{cron_name[:20]}-{os.urandom(3).hex()}"
    job = client.V1Job(
        metadata=client.V1ObjectMeta(
            name=job_name,
            labels={"type": f"cron-manual-{cron_name}"}
        ),
        spec=cron.spec.job_template.spec
    )
    batch_v1.create_namespaced_job(NAMESPACE, job)
    return jsonify({"status": f"CronJob {cron_name} déclenché !", "name": job_name})

@app.route("/api/cronjob-logs/<cron_name>")
def get_cronjob_logs(cron_name):
    batch_v1 = client.BatchV1Api()
    core_v1 = client.CoreV1Api()
    jobs = batch_v1.list_namespaced_job(NAMESPACE, label_selector=f"job-name={cron_name}")
    if not jobs.items:
        jobs = batch_v1.list_namespaced_job(NAMESPACE)
        cron_jobs = [j for j in jobs.items if cron_name in j.metadata.name]
        if not cron_jobs:
            return jsonify({"logs": "Aucun job trouvé pour ce CronJob"})
        latest = sorted(cron_jobs, key=lambda j: j.metadata.creation_timestamp)[-1]
        job_name = latest.metadata.name
    else:
        job_name = jobs.items[-1].metadata.name
    pods = core_v1.list_namespaced_pod(NAMESPACE, label_selector=f"job-name={job_name}")
    if not pods.items:
        return jsonify({"logs": "Aucun pod trouvé"})
    try:
        logs = core_v1.read_namespaced_pod_log(pods.items[0].metadata.name, NAMESPACE)
        return jsonify({"logs": logs})
    except Exception as e:
        return jsonify({"logs": str(e)})

@app.route("/api/cronjob-spec/<name>")
def get_cronjob_spec(name):
    batch_v1 = client.BatchV1Api()
    cj = batch_v1.read_namespaced_cron_job(name, NAMESPACE)
    # On renvoie juste la partie intéressante : schedule et template command
    return jsonify({
        "schedule": cj.spec.schedule,
        "command": cj.spec.job_template.spec.template.spec.containers[0].command[2] if len(cj.spec.job_template.spec.template.spec.containers[0].command) > 2 else ""
    })

@app.route("/api/update-cronjob/<name>", methods=["POST"])
def update_cronjob(name):
    from flask import request
    data = request.json
    batch_v1 = client.BatchV1Api()
    cj = batch_v1.read_namespaced_cron_job(name, NAMESPACE)
    
    if "schedule" in data:
        cj.spec.schedule = data["schedule"]
    if "command" in data:
        cj.spec.job_template.spec.template.spec.containers[0].command = ["sh", "-c", data["command"]]
        
    batch_v1.patch_namespaced_cron_job(name, NAMESPACE, cj)
    return jsonify({"status": "CronJob mis à jour !"})

@app.route("/api/manual-job-config")
def get_manual_job_config():
    return jsonify(MANUAL_JOB_CONFIG)

@app.route("/api/update-manual-job-config", methods=["POST"])
def update_manual_job_config():
    from flask import request
    data = request.json
    if "command" in data:
        MANUAL_JOB_CONFIG["command"] = data["command"]
    if "image" in data:
        MANUAL_JOB_CONFIG["image"] = data["image"]
    return jsonify({"status": "Configuration Job manuel mise à jour !"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)