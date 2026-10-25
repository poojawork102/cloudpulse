pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-creds')
        DOCKERHUB_REPO = 'pooja102/cloudpulse'
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build & Test') {
            steps {
                // Install deps and run pytest on the Jenkins host (fails fast, before any image is built)
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --no-cache-dir -r requirements.txt
                    python -m pytest -q
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    docker build -t ${DOCKERHUB_REPO}:${IMAGE_TAG} .
                    docker tag ${DOCKERHUB_REPO}:${IMAGE_TAG} ${DOCKERHUB_REPO}:latest
                '''
            }
        }

        stage('Push Image') {
            steps {
                sh '''
                    echo "$DOCKERHUB_CREDENTIALS_PSW" | docker login -u "$DOCKERHUB_CREDENTIALS_USR" --password-stdin
                    docker push ${DOCKERHUB_REPO}:${IMAGE_TAG}
                    docker push ${DOCKERHUB_REPO}:latest
                    docker logout
                '''
            }
        }

        stage('Minikube Deployment') {
            steps {
                sh '''
                    # Apply manifests (creates on first run, no-op afterwards)
                    kubectl apply -f k8s/
                    # Roll out this build's unique tag so every run deploys the new version
                    kubectl set image deployment/cloudpulse cloudpulse=${DOCKERHUB_REPO}:${IMAGE_TAG}
                    kubectl rollout status deployment/cloudpulse --timeout=120s
                '''
            }
        }

        stage('Verification') {
            steps {
                sh '''
                    echo "=== Pods ==="
                    kubectl get pods -l app=cloudpulse -o wide
                    echo "=== Deployment ==="
                    kubectl get deployment cloudpulse
                    echo "=== Service ==="
                    kubectl get svc cloudpulse-service
                    echo "=== Deployed image ==="
                    kubectl get deployment cloudpulse -o jsonpath='{.spec.template.spec.containers[0].image}'; echo
                    echo "=== App health check ==="
                    kubectl port-forward svc/cloudpulse-service 18080:80 >/dev/null 2>&1 &
                    PF_PID=$!
                    sleep 5
                    curl -fsS http://localhost:18080/health
                    echo
                    kill $PF_PID
                '''
            }
        }
    }

    post {
        success {
            echo "CloudPulse build #${BUILD_NUMBER} deployed successfully."
        }
        failure {
            echo 'Pipeline failed. Check the stage logs.'
        }
    }
}
