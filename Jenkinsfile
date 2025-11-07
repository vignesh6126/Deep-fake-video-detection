pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        DOCKERHUB_USER = "vignesg043"
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
                    bat 'npm install'
                    bat 'npm run build'
                    echo "Frontend build completed successfully."
                }
            }
        }

        stage('Backend Preparation') {
            steps {
                dir('backend') {
                    echo "Installing backend dependencies..."
                    bat '"C:\\Users\\vigne\\AppData\\Local\\Microsoft\\WindowsApps\\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\\python.exe" -m pip install -r requirements.txt'
        }
            
            }
        }

        stage('Build Docker Images') {
            steps {
                script {
                    echo "Building backend Docker image..."
                    bat "docker build -t ${BACKEND_IMAGE}:latest ./backend"

                    echo "Building frontend Docker image..."
                    bat "docker build -t ${FRONTEND_IMAGE}:latest ./frontend"
                }
            }
        }

        stage('Login to Docker Hub') {
            steps {
                echo "Logging in to Docker Hub..."
                bat """
                echo ${DOCKERHUB_CREDENTIALS_PSW} | docker login -u ${DOCKERHUB_CREDENTIALS_USR} --password-stdin
                """
            }
        }

        stage('Push Docker Images') {
            steps {
                script {
                    echo "Pushing backend image to Docker Hub..."
                    bat "docker push ${BACKEND_IMAGE}:latest"

                    echo "Pushing frontend image to Docker Hub..."
                    bat "docker push ${FRONTEND_IMAGE}:latest"
                }
            }
        }

        stage('Cleanup') {
            steps {
                echo "Cleaning up Docker images..."
                bat 'docker system prune -af || echo "Cleanup skipped"'
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
