pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        DOCKERHUB_USER = "vignesg043"
        BACKEND_IMAGE = "${DOCKERHUB_USER}/deepfake-backend"
        FRONTEND_IMAGE = "${DOCKERHUB_USER}/deepfake-frontend"
        RESOURCE_GROUP = "deepfake-rg-india"
        ACI_YAML = "deepfake-aci.yaml"
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
                        echo REACT_APP_BACKEND_URL=http://backend:8000 > .env
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

        stage('Push Docker Images') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    echo "🔐 Logging in to Docker Hub..."
                    bat 'echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin'
                    bat "docker push ${BACKEND_IMAGE}:latest"
                    bat "docker push ${FRONTEND_IMAGE}:latest"
                }
            }
        }

        stage('Deploy to Azure ACI') {
            steps {
                echo "🚀 Deploying containers to Azure Container Instances..."
                withCredentials([file(credentialsId: 'azure-auth-json', variable: 'AZURE_AUTH_FILE')]) {
                    bat """
                        az login --service-principal --username (jq -r .clientId %AZURE_AUTH_FILE%) ^
                                 --password (jq -r .clientSecret %AZURE_AUTH_FILE%) ^
                                 --tenant (jq -r .tenantId %AZURE_AUTH_FILE%)
                        az account set --subscription (jq -r .subscriptionId %AZURE_AUTH_FILE%)

                        REM Delete old container group if exists
                        az container delete --resource-group ${RESOURCE_GROUP} --name deepfake-app-group --yes || echo "No old container"

                        REM Deploy new container group
                        az container create --resource-group ${RESOURCE_GROUP} --file ${ACI_YAML}
                    """
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
            echo "✅ CI/CD pipeline completed — Docker images pushed and deployed to Azure ACI!"
        }
        failure {
            echo "❌ Pipeline failed. Check Jenkins logs for errors."
        }
        always {
            cleanWs()
        }
    }
}
