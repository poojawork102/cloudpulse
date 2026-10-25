![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Docker](https://img.shields.io/badge/docker-containerized-2496ED)
![Kubernetes](https://img.shields.io/badge/kubernetes-minikube-326CE5)

# CloudPulse — Deployment Monitor

A Flask-based deployment monitor that tracks application health, version and uptime. Built as a CI/CD pipeline demonstration for CCA 2 (Cloud Computing and DevOps).

The app exposes three endpoints:

| Endpoint | Purpose |
|----------|---------|
| `/` | Dashboard UI — shows pipeline stages, health status, version and activity log |
| `/health` | Returns JSON with status, version and start time |
| `/api/status` | Detailed JSON status including environment info |

All three endpoints are covered by pytest (see `tests/test_app.py`).

## Repository Structure

```
cloudpulse/
├── app.py                  # Flask application
├── templates/
│   └── index.html          # Dashboard UI
├── tests/
│   └── test_app.py         # 3 pytest tests
├── Dockerfile              # Python 3.12-slim image
├── Jenkinsfile             # 6-stage declarative pipeline
├── k8s/
│   ├── deployment.yaml     # 2-replica Deployment
│   └── service.yaml        # NodePort Service (30080)
└── requirements.txt        # Flask + pytest
```

## Pipeline Stages

The Jenkinsfile defines a declarative pipeline with six stages:

| # | Stage | What it does |
|---|-------|-------------|
| 1 | **Checkout** | Pulls the latest code from this GitHub repo using Pipeline SCM |
| 2 | **Build & Test** | Builds the Docker image and runs `pytest -q` inside the container to verify all 3 tests pass |
| 3 | **Docker Build** | Tags the image with the Jenkins build number for versioning |
| 4 | **Push Image** | Logs into Docker Hub using the `dockerhub-creds` credential and pushes both `:BUILD_NUMBER` and `:latest` tags |
| 5 | **Minikube Deployment** | Runs `kubectl apply -f k8s/` to create or update the Deployment and Service on Minikube, then waits for rollout to complete |
| 6 | **Verification** | Prints running pods, deployment status and service details to confirm everything is healthy |

Credentials are stored in Jenkins (Manage Jenkins → Credentials) and never in the repo.

## AWS EC2 Setup

Jenkins runs on an EC2 instance in **ap-south-1 (Mumbai)**:

- **Instance type**: m7i-flex.large (2 vCPU, 8 GB RAM)
- **OS**: Ubuntu 22.04 LTS
- **Installed tools**: Jenkins 2.580.1, Docker 29.1.3, Minikube 1.39.0, kubectl 1.37.1

### What was configured

1. Installed Java 21, Jenkins, Docker, Minikube and kubectl on the EC2 instance
2. Added the `jenkins` user to the `docker` group so Jenkins can build images
3. Started Minikube with `--driver=docker` under the jenkins user
4. Copied the kubeconfig to `/var/lib/jenkins/.kube/config` so Jenkins stages can run kubectl
5. In Jenkins, created a **Username with password** credential (ID: `dockerhub-creds`) storing the Docker Hub PAT for `pooja102`
6. Created a Pipeline job pointing to this repo with **Pipeline script from SCM**
7. Opened ports 8080 (Jenkins), 5000 (app) and 30000-32767 (NodePort range) in the EC2 security group

## Docker Hub

Images are pushed automatically to **pooja102/cloudpulse** on every successful build.

Each build pushes two tags:
- `:BUILD_NUMBER` (e.g. `:3`, `:4`) — immutable version tag
- `:latest` — always points to the most recent build

Image size is around 47 MB (based on python:3.12-slim).

## Kubernetes Deployment

The app runs on Minikube with the Docker driver:

- **Deployment**: 2 replicas of the CloudPulse container, with readiness and liveness probes hitting `/health`
- **Service**: NodePort type, maps port 80 → container port 5000, exposed on node port 30080
- **Access**: Used `kubectl port-forward --address 0.0.0.0 svc/cloudpulse-service 8081:80` to make the app reachable at `http://<EC2-IP>:8081`

After deployment, `kubectl get pods` shows both replicas Running and `kubectl get svc` confirms the NodePort mapping.

## Second Pipeline Run (Version Bump)

To demonstrate a code change flowing through the pipeline:

1. Changed `VERSION` in `app.py` from `"1.0.0"` to `"1.1.0"`
2. Committed and pushed to GitHub
3. Triggered **Build #4** in Jenkins
4. All 6 stages passed again (56 seconds total)
5. Docker Hub received the new `:4` tag
6. Kubernetes rolled out the updated pods
7. Hitting `/health` returned `"version": "1.1.0"` — confirming the change went end-to-end

## Running Locally

```bash
pip install -r requirements.txt
python app.py
# Visit http://localhost:5000
```

To run tests:
```bash
pytest -q
```

## Tools Used

| Tool | Role |
|------|------|
| GitHub | Source code, Jenkinsfile, Dockerfile, K8s manifests |
| AWS EC2 | Hosts Jenkins, Docker and Minikube |
| Jenkins | Runs the 6-stage pipeline automatically |
| Docker | Packages the app into an image |
| Docker Hub | Stores images so Kubernetes can pull them |
| Minikube + kubectl | Runs the local K8s cluster and manages deployments |
