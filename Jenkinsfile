pipeline {
    agent any

    options {
        timeout(time: 60, unit: 'MINUTES')
    }

    environment {
        // Docker Hub credentials and image info
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        DOCKERHUB_USER = "vignesg043"
        BACKEND_IMAGE = "${DOCKERHUB_USER}/deepfake-backend"
        FRONTEND_IMAGE = "${DOCKERHUB_USER}/deepfake-frontend"

        // Azure details
        RESOURCE_GROUP = "deepfake-rg-india"
        ACI_YAML = "deepfake-aci.yaml"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Checking out source code..."
                checkout scm
                echo "Repository cloned successfully."
            }
        }

        stage('Frontend Build') {
            steps {
                dir('frontend') {
                    echo "Building React frontend..."
                    bat """
                        echo REACT_APP_BACKEND_URL=http://localhost:8000 > .env
                        type .env
                        call npm install
                        call npm run build
                    """
                    echo "Frontend build completed successfully."
                }
            }
        }

        stage('Backend Preparation') {
            steps {
                dir('backend') {
                    echo "Installing backend dependencies..."
                    bat 'python --version'
                    bat 'python -m pip install --upgrade pip'
                    bat 'python -m pip install --no-cache-dir -r requirements.txt'
                    echo "Backend dependencies installed successfully."
                }
            }
        }

        stage('Verify Docker Daemon') {
            steps {
                echo "Checking if Docker is running..."
                bat 'docker version'
            }
        }

        stage('Build Docker Images') {
            steps {
                script {
                    echo "Building backend Docker image..."
                    bat "docker build -t ${BACKEND_IMAGE}:latest ./backend"

                    echo "Building frontend Docker image..."
                    bat "docker build -t ${FRONTEND_IMAGE}:latest --build-arg REACT_APP_BACKEND_URL=http://localhost:8000 ./frontend"
                }
            }
        }

        stage('Push Docker Images') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        echo "Logging in to Docker Hub..."
                        bat "echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin"
                        
                        echo "Pushing backend image..."
                        bat "docker push ${BACKEND_IMAGE}:latest"
                        
                        echo "Pushing frontend image..."
                        bat "docker push ${FRONTEND_IMAGE}:latest"
                    }
                }
            }
        }

        stage('Deploy to Azure ACI') {
            steps {
                echo "Deploying containers to Azure Container Instances..."
                withCredentials([file(credentialsId: 'azure-auth-json', variable: 'AZURE_AUTH_FILE')]) {
                    powershell """
                        Write-Host "Loading Azure credentials from JSON file..."
                        
                        # Read and parse the JSON file
                        `$authContent = Get-Content -Path '${env:AZURE_AUTH_FILE}' -Raw
                        `$authObject = `$authContent | ConvertFrom-Json
                        
                        `$clientId = `$authObject.clientId.Trim()
                        `$clientSecret = `$authObject.clientSecret.Trim()
                        `$tenantId = `$authObject.tenantId.Trim()
                        `$subscriptionId = `$authObject.subscriptionId.Trim()
                        
                        Write-Host "Logging into Azure..."
                        az login --service-principal --username `$clientId --password `$clientSecret --tenant `$tenantId
                        
                        Write-Host "Setting subscription..."
                        az account set --subscription `$subscriptionId
                        
                        Write-Host "Removing old ACI deployment..."
                        az container delete --resource-group ${env:RESOURCE_GROUP} --name deepfake-app-group --yes --no-wait
                        
                        Write-Host "Creating new ACI container group..."
                        az container create --resource-group ${env:RESOURCE_GROUP} --file ${env:ACI_YAML}
                        
                        Write-Host "Deployment completed successfully."
                    """
                }
            }
        }

        stage('Health Check') {
            steps {
                sleep time: 30, unit: 'SECONDS'
                withCredentials([file(credentialsId: 'azure-auth-json', variable: 'AZURE_AUTH_FILE')]) {
                    powershell """
                        Write-Host "Checking container status..."
                        
                        # Read and parse the JSON file
                        `$authContent = Get-Content -Path '${env:AZURE_AUTH_FILE}' -Raw
                        `$authObject = `$authContent | ConvertFrom-Json
                        
                        `$clientId = `$authObject.clientId.Trim()
                        `$clientSecret = `$authObject.clientSecret.Trim()
                        `$tenantId = `$authObject.tenantId.Trim()
                        
                        az login --service-principal --username `$clientId --password `$clientSecret --tenant `$tenantId
                        az container show --resource-group ${env:RESOURCE_GROUP} --name deepfake-app-group --query "containers[].{Name:name, State:instanceView.currentState.state}" -o table
                        
                        Write-Host "Checking frontend logs..."
                        az container logs --resource-group ${env:RESOURCE_GROUP} --name deepfake-app-group --container-name frontend --tail 10
                    """
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully. Docker images pushed and deployed to Azure ACI."
        }
        failure {
            echo "Pipeline failed. Check Jenkins logs for detailed errors."
        }
        always {
            cleanWs()
        }
    }
}