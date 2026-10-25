
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
                sh '''
                    docker build -t ${DOCKERHUB_REPO}:${IMAGE_TAG} .
                    docker run --rm \
                      --entrypoint python \
                      ${DOCKERHUB_REPO}:${IMAGE_TAG} \
                      -m pytest -q
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                sh '''
                    echo "$DOCKERHUB_CREDENTIALS_PSW" | docker login -u "$DOCKERHUB_CREDENTIALS_USR" --password-stdin
                    docker tag ${DOCKERHUB_REPO}:${IMAGE_TAG} ${DOCKERHUB_REPO}:latest
                    docker push ${DOCKERHUB_REPO}:${IMAGE_TAG}
                    docker push ${DOCKERHUB_REPO}:latest
                    docker logout
                '''
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    kubectl set image deployment/cloudpulse cloudpulse=${DOCKERHUB_REPO}:${IMAGE_TAG} || \
                    kubectl apply -f k8s/
                    kubectl rollout status deployment/cloudpulse --timeout=60s
                '''
            }
        }

        stage('Verify') {
            steps {
                sh '''
                    echo "=== Pods ==="
                    kubectl get pods -l app=cloudpulse
                    echo "=== Deployment ==="
                    kubectl get deployment cloudpulse
                    echo "=== Service ==="
                    kubectl get svc cloudpulse-service
                '''
            }
        }
    }

    post {
        success {
            echo 'CloudPulse pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed. Check the stage logs.'
        }
    }
}
