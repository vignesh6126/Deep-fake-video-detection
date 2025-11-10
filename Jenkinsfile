pipeline {
    agent any

    options {
        timeout(time: 60, unit: 'MINUTES')
    }

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        DOCKERHUB_USER = "vignesg043"
        BACKEND_IMAGE = "${DOCKERHUB_USER}/deepfake-backend"
        FRONTEND_IMAGE = "${DOCKERHUB_USER}/deepfake-frontend"
        RESOURCE_GROUP = "deepfake-rg-india"
        ACI_YAML = "deepfake-aci.yaml"
    }

    stages {
        stage('Checkout Source Code') {
            steps {
                echo "Checking out latest code from GitHub..."
                checkout scm
                echo "Repository cloned successfully."
            }
        }

        stage('Build Frontend (React)') {
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

        stage('Prepare Backend (Python)') {
            steps {
                dir('backend') {
                    echo "Installing backend dependencies..."
                    bat """
                        python --version
                        python -m pip install --upgrade pip
                        python -m pip install --no-cache-dir -r requirements.txt
                    """
                    echo "Backend dependencies installed successfully."
                }
            }
        }

        stage('Verify Docker Daemon') {
            steps {
                echo "Checking Docker service..."
                bat 'docker version || (echo Docker is not running! && exit /b 1)'
                echo "Docker is active."
            }
        }

        stage('Build Docker Images') {
            steps {
                script {
                    echo "Building backend image..."
                    bat "docker build -t ${BACKEND_IMAGE}:latest ./backend"

                    echo "Building frontend image..."
                    bat "docker build -t ${FRONTEND_IMAGE}:latest --build-arg REACT_APP_BACKEND_URL=http://localhost:8000 ./frontend"
                }
            }
        }

        stage('Push Docker Images to Docker Hub') {
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
                echo "Deploying containers to Azure ACI..."
                withCredentials([file(credentialsId: 'azure-auth-json', variable: 'AZURE_AUTH_FILE')]) {
                    powershell """
                        [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
                        Write-Host 'Extracting Azure credentials...'

                        \$filePath = '${env.AZURE_AUTH_FILE}'
                        \$auth = Get-Content \$filePath | ConvertFrom-Json
                        \$clientId = \$auth.clientId
                        \$clientSecret = \$auth.clientSecret
                        \$tenantId = \$auth.tenantId
                        \$subscriptionId = \$auth.subscriptionId

                        Write-Host 'Logging in to Azure...'
                        az login --service-principal --username \$clientId --password \$clientSecret --tenant \$tenantId | Out-Null
                        az account set --subscription \$subscriptionId

                        Write-Host 'Removing old container group if it exists...'
                        az container delete --resource-group ${RESOURCE_GROUP} --name deepfake-app-group --yes

                        Start-Sleep -Seconds 10
                        Write-Host 'Creating new container group from YAML...'
                        az container create --resource-group ${RESOURCE_GROUP} --file ${ACI_YAML}

                        Write-Host 'Deployment completed.'
                    """
                }
            }
        }

        stage('Health Check and Logs') {
            steps {
                echo "Checking Azure container health status..."
                sleep time: 45, unit: 'SECONDS'

                withCredentials([file(credentialsId: 'azure-auth-json', variable: 'AZURE_AUTH_FILE')]) {
                    powershell """
                        [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
                        \$filePath = '${env.AZURE_AUTH_FILE}'
                        \$auth = Get-Content \$filePath | ConvertFrom-Json

                        az login --service-principal --username \$auth.clientId --password \$auth.clientSecret --tenant \$auth.tenantId | Out-Null
                        az account set --subscription \$auth.subscriptionId

                        Write-Host 'Checking container states...'
                        az container show --resource-group ${RESOURCE_GROUP} --name deepfake-app-group --query "properties.containers[].{Name:name,State:properties.instanceView.currentState.state}" -o table

                        Write-Host 'Fetching frontend logs...'
                        az container logs --resource-group ${RESOURCE_GROUP} --name deepfake-app-group --container-name frontend
                    """
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully. Docker images built, pushed, and deployed to Azure ACI."
        }
        failure {
            echo "Pipeline failed. Please check Jenkins logs and Azure deployment output."
        }
        always {
            echo "Cleaning up workspace..."
            cleanWs()
        }
    }
}
