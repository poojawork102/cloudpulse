
pipeline {
    agent any

    environment {
        IMAGE_NAME = 'cloudpulse'
        CONTAINER_NAME = 'cloudpulse'
        APP_PORT = '5000'
    }

    stages {
        stage('Clone') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                sh 'docker build -t cloudpulse:${BUILD_NUMBER} .'
            }
        }

        stage('Test') {
            steps {
                sh '''
                    docker run --rm \
                      --entrypoint python \
                      cloudpulse:${BUILD_NUMBER} \
                      -m pytest -q
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker stop cloudpulse || true
                    docker rm cloudpulse || true

                    docker run -d \
                      --restart unless-stopped \
                      --name cloudpulse \
                      -p 5000:5000 \
                      cloudpulse:${BUILD_NUMBER}
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
