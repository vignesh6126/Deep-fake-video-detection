pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        DOCKERHUB_USER = "vignesg043"
        BACKEND_IMAGE = "${DOCKERHUB_USER}/deepfake-backend"
        FRONTEND_IMAGE = "${DOCKERHUB_USER}/deepfake-frontend"
        BACKEND_URL = "http://localhost:30008"  // Kubernetes backend NodePort
        K8S_DIR = "K8s"                         // Folder containing YAML files
    }

    stages {

        stage('Checkout') {
            steps {
                echo "📦 Checking out source code..."
                checkout scm
            }
        }

        stage('Frontend Build') {
            steps {
                dir('frontend') {
                    echo "⚙️ Building React frontend..."
                    bat """
                        echo REACT_APP_BACKEND_URL=%BACKEND_URL% > .env
                        type .env
                        call npm install
                        call npm run build
                    """
                    echo "✅ Frontend build completed successfully."
                }
            }
        }

        stage('Backend Preparation') {
            steps {
                dir('backend') {
                    echo "🐍 Installing backend dependencies..."
                    bat 'python --version'
                    bat 'python -m pip install --upgrade pip'
                    bat 'python -m pip install --no-cache-dir -r requirements.txt'
                    echo "✅ Backend dependencies installed successfully."
                }
            }
        }

        stage('Verify Docker Daemon') {
            steps {
                echo "🔍 Checking if Docker is running..."
                bat 'docker version || (echo ❌ Docker is not running! && exit /b 1)'
            }
        }

        stage('Build Docker Images') {
            steps {
                script {
                    echo "🐳 Building backend Docker image..."
                    bat "docker build -t ${BACKEND_IMAGE}:latest ./backend"

                    echo "🐳 Building frontend Docker image..."
                    bat "docker build -t ${FRONTEND_IMAGE}:latest ./frontend"
                }
            }
        }

        stage('Login to Docker Hub') {
            steps {
                echo "🔐 Logging in to Docker Hub..."
                bat """
                    echo ${DOCKERHUB_CREDENTIALS_PSW} | docker login -u ${DOCKERHUB_CREDENTIALS_USR} --password-stdin
                """
            }
        }

        stage('Push Docker Images') {
            steps {
                script {
                    echo "🚀 Pushing backend image to Docker Hub..."
                    bat "docker push ${BACKEND_IMAGE}:latest"

                    echo "🚀 Pushing frontend image to Docker Hub..."
                    bat "docker push ${FRONTEND_IMAGE}:latest"
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                echo "☸️ Deploying application to Kubernetes..."
                bat """
                    kubectl set image deployment/deepfake-backend deepfake-backend=${BACKEND_IMAGE}:latest --record
                    kubectl set image deployment/deepfake-frontend deepfake-frontend=${FRONTEND_IMAGE}:latest --record

                    echo "🔄 Restarting deployments..."
                    kubectl rollout restart deployment/deepfake-backend
                    kubectl rollout restart deployment/deepfake-frontend

                    echo "✅ Waiting for pods to become ready..."
                    kubectl rollout status deployment/deepfake-backend --timeout=120s
                    kubectl rollout status deployment/deepfake-frontend --timeout=120s

                    echo "🌐 Current Kubernetes services:"
                    kubectl get svc
                """
            }
        }

        stage('Cleanup') {
            steps {
                echo "🧹 Cleaning up Docker environment..."
                bat 'docker system prune -af || echo "Cleanup skipped"'
            }
        }
    }

    post {
        success {
            echo "✅ CI/CD pipeline completed — Docker images pushed and deployed to Kubernetes!"
        }
        failure {
            echo "❌ Pipeline failed. Check Jenkins logs for errors."
        }
        always {
            cleanWs()
        }
    }
}
