pipeline {
    agent any

    environment {
        // 🔐 Docker Hub credentials and image info
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        DOCKERHUB_USER = "vignesg043"
        BACKEND_IMAGE = "${DOCKERHUB_USER}/deepfake-backend"
        FRONTEND_IMAGE = "${DOCKERHUB_USER}/deepfake-frontend"

        // 🌩️ Azure details
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
                        echo 🔍 Extracting Azure credentials from JSON file...
                        for /f "tokens=2 delims=:,{}\"" %%i in ('findstr "clientId" %AZURE_AUTH_FILE%') do set CLIENT_ID=%%~i
                        for /f "tokens=2 delims=:,{}\"" %%i in ('findstr "clientSecret" %AZURE_AUTH_FILE%') do set CLIENT_SECRET=%%~i
                        for /f "tokens=2 delims=:,{}\"" %%i in ('findstr "tenantId" %AZURE_AUTH_FILE%') do set TENANT_ID=%%~i
                        for /f "tokens=2 delims=:,{}\"" %%i in ('findstr "subscriptionId" %AZURE_AUTH_FILE%') do set SUB_ID=%%~i

                        REM 🧹 Clean up quotes and spaces
                        set CLIENT_ID=%CLIENT_ID:"=%
                        set CLIENT_SECRET=%CLIENT_SECRET:"=%
                        set TENANT_ID=%TENANT_ID:"=%
                        set SUB_ID=%SUB_ID:"=%

                        echo 🔑 Logging into Azure...
                        az login --service-principal --username %CLIENT_ID% --password %CLIENT_SECRET% --tenant %TENANT_ID%
                        az account set --subscription %SUB_ID%

                        echo 🗑️ Removing any existing container group...
                        az container delete --resource-group ${RESOURCE_GROUP} --name deepfake-app-group --yes || echo "No old container found"

                        echo 🚀 Creating new ACI container group...
                        az container create --resource-group ${RESOURCE_GROUP} --file ${ACI_YAML}

                        echo ✅ Azure deployment completed successfully!
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
            echo "✅ CI/CD pipeline completed — Docker images pushed and deployed to Azure ACI successfully!"
        }
        failure {
            echo "❌ Pipeline failed. Check Jenkins logs for detailed errors."
        }
        always {
            cleanWs()
        }
    }
}