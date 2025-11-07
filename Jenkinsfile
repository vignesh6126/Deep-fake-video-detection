pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')   // Jenkins credential ID
        DOCKERHUB_USER = "vignesg043"                            // your Docker Hub username
        BACKEND_IMAGE = "${DOCKERHUB_USER}/deepfake-backend"
        FRONTEND_IMAGE = "${DOCKERHUB_USER}/deepfake-frontend"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Frontend Build') {
            steps {
                dir('frontend') {
                    echo "Building React frontend..."
                    sh 'npm install'
                    sh 'npm run build'
                    echo "Frontend build completed successfully."
                }
            }
        }

        stage('Backend Preparation') {
            steps {
                dir('backend') {
                    echo "Installing backend dependencies..."
                    sh 'pip install -r requirements.txt || echo "Skipping install in Docker build context"'
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                script {
                    echo "Building backend Docker image..."
                    sh "docker build -t ${BACKEND_IMAGE}:latest ./backend"

                    echo "Building frontend Docker image..."
                    sh "docker build -t ${FRONTEND_IMAGE}:latest ./frontend"
                }
            }
        }

        stage('Login to Docker Hub') {
            steps {
                echo "Logging in to Docker Hub..."
                sh "echo ${DOCKERHUB_CREDENTIALS_PSW} | docker login -u ${DOCKERHUB_CREDENTIALS_USR} --password-stdin"
            }
        }

        stage('Push Docker Images') {
            steps {
                script {
                    echo "Pushing backend image to Docker Hub..."
                    sh "docker push ${BACKEND_IMAGE}:latest"

                    echo "Pushing frontend image to Docker Hub..."
                    sh "docker push ${FRONTEND_IMAGE}:latest"
                }
            }
        }

        stage('Cleanup') {
            steps {
                echo "Cleaning up unused Docker images..."
                sh 'docker system prune -af || true'
            }
        }
    }

    post {
        success {
            echo "Build and push completed successfully."
        }
        failure {
            echo "Build failed. Check logs for details."
        }
        always {
            cleanWs()
        }
    }
}
