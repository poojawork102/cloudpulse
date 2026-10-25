# CloudPulse – CI/CD Pipeline on Jenkins, Docker Hub and Minikube

CCA 2 – Cloud Computing and DevOps (TYCSE, MIT-WPU)

CloudPulse is a small Flask status dashboard (`/`, `/health`, `/api/status`). The project is an existing academic project; this repo adds a fully automated CI/CD pipeline around it.

## Repository layout

| Path | Purpose |
|---|---|
| `app.py`, `templates/` | Flask application |
| `tests/test_app.py` | pytest tests (dashboard, `/health`, `/api/status`) |
| `Dockerfile` | Image build (python:3.12-slim, gunicorn, non-root user) |
| `Jenkinsfile` | Declarative pipeline |
| `k8s/deployment.yaml` | Deployment, 2 replicas, readiness and liveness probes on `/health` |
| `k8s/service.yaml` | NodePort Service (80 → 5000, nodePort 30080) |

## Pipeline stages

| # | Stage | What it does |
|---|---|---|
| 1 | Checkout | Jenkins pulls the latest code from GitHub (`checkout scm`) |
| 2 | Build & Test | Creates a venv, installs `requirements.txt`, runs `pytest` |
| 3 | Docker Build | Builds `pooja102/cloudpulse:<BUILD_NUMBER>` and tags it `latest` |
| 4 | Push Image | Logs in to Docker Hub with Jenkins credentials (`dockerhub-creds`) and pushes both tags |
| 5 | Minikube Deployment | `kubectl apply -f k8s/`, then `kubectl set image` to this build's tag, then waits for rollout |
| 6 | Verification | Lists pods, deployment, service, deployed image, and curls `/health` via port-forward |

Credentials are stored in Jenkins (Manage Jenkins → Credentials) and never in the repo.

## Jenkins on AWS – setup summary

1. Launch an EC2 instance (Ubuntu, t3.medium or larger, 20 GB disk). Security group: SSH (22) and Jenkins (8080) from my IP, NodePort range if needed.
2. Install Java 17, Jenkins, Docker, kubectl, Minikube, Python 3 + venv.
3. Add the `jenkins` user to the `docker` group and restart Jenkins.
4. Start Minikube (docker driver) and make the kubeconfig available to the `jenkins` user (`/var/lib/jenkins/.kube/config`).
5. In Jenkins: install the Git, Pipeline, Credentials Binding plugins; add Docker Hub username/password as credential ID `dockerhub-creds`.
6. Create a Pipeline job → "Pipeline script from SCM" → this GitHub repo, branch `main`, script path `Jenkinsfile`.

## Deploying and accessing the app

After a successful build:

```bash
kubectl get pods -l app=cloudpulse
kubectl get svc cloudpulse-service
minikube service cloudpulse-service --url
```

Open the printed URL in a browser (or `curl <url>/health`).

## Second run – source-code change

Change made: _(fill in, e.g. bumped `VERSION` in `app.py` from `1.0.0` to `1.1.0` and updated the dashboard text)_.

The tests compare against `app.VERSION`, so a version bump does not break the test stage. After `git push`, the pipeline was triggered again, a new image tag (`<BUILD_NUMBER>`) was pushed, Kubernetes rolled out the new pods, and the dashboard showed the new version.

## Screenshots

Stored in `screenshots/`: Jenkins pipeline stage view, Docker Hub repo tags, `kubectl get pods/deploy/svc`, running app (v1 and v2).
