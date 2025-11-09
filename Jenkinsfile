pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        DOCKERHUB_USER = "vignesg043"
        BACKEND_IMAGE = "${DOCKERHUB_USER}/deepfake-backend"
        FRONTEND_IMAGE = "${DOCKERHUB_USER}/deepfake-frontend"
        BACKEND_URL = "http://localhost:30008" // Kubernetes NodePort for backend
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
                        echo REACT_APP_BACKEND_URL=${BACKEND_URL} > .env
                        type .env
                        npm install
                        npm run build
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
                bat 'docker version || (echo Docker is not running! && exit /b 1)'
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

        stage('Cleanup') {
            steps {
                echo "🧹 Cleaning up Docker environment..."
                bat 'docker system prune -af || echo "Cleanup skipped"'
            }
        }
    }

    post {
        success {
            echo "✅ Build and push completed successfully!"
        }
        failure {
            echo "❌ Build failed. Check Jenkins logs for details."
        }
        always {
            cleanWs()
        }
    }
}
