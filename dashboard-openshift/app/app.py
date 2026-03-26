from flask import Flask, render_template, jsonify
from kubernetes import client, config
import os

app = Flask(__name__)
config.load_incluster_config()
NAMESPACE = os.getenv("NAMESPACE", "formation-openshift")
MAX_MANUAL_JOBS = 3
MAX_TOTAL_JOBS = 10

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/jobs")
def get_jobs():
    batch_v1 = client.BatchV1Api()
    jobs = batch_v1.list_namespaced_job(NAMESPACE)
    result = []
    for job in jobs.items:
        if job.status.succeeded:
            status = "Complete"
        elif job.status.active:
            status = "Running"
        else:
            status = "Failed"
        result.append({
            "name": job.metadata.name,
            "status": status,
            "start": str(job.status.start_time) if job.status.start_time else "N/A"
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

@app.route("/api/logs/<job_name>")
def get_logs(job_name):
    core_v1 = client.CoreV1Api()
    pods = core_v1.list_namespaced_pod(NAMESPACE, label_selector=f"job-name={job_name}")
    if not pods.items:
        return jsonify({"logs": "Aucun pod trouvé"})
    pod_name = pods.items[0].metadata.name
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
                        image="nginxinc/nginx-unprivileged@sha256:731f382bbad9a874f9f27db9c82d9e671e603e2210386a8e2b6da36cf336fa75",
                        command=["sh", "-c", "echo Bonjour depuis mon Job OpenShift"]
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)