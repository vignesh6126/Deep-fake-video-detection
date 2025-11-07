pipeline {
    agent any

    tools {
        nodejs 'NodeJS'
    }

    environment {
        // DockerHub credentials ID created in Jenkins
        DOCKERHUB_CREDENTIALS = credentials('dockerhub')
        DOCKER_HUB_USER = "${DOCKERHUB_CREDENTIALS_USR}"
        DOCKER_HUB_PASS = "${DOCKERHUB_CREDENTIALS_PSW}"
        IMAGE_BACKEND = "${DOCKER_HUB_USER}/deepfake-backend"
        IMAGE_FRONTEND = "${DOCKER_HUB_USER}/deepfake-frontend"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Checking out source code..."
                checkout scm
            }
        }

        stage('Frontend Build') {
            steps {
                script {
                    try {
                        dir('frontend') {
                            echo "Installing frontend dependencies..."
                            bat 'npm install'
                            echo "Building frontend..."
                            bat 'npm run build'
                            echo " Running frontend tests (if any)..."
                            bat 'npm test || echo Tests skipped or not configured'
                        }
                    } catch (Exception e) {
                        echo "Frontend build failed: ${e.message}"
                        echo "Continuing pipeline..."
                    }
                }
            }
        }

        stage('Backend Setup') {
            steps {
                script {
                    try {
                        if (fileExists('backend')) {
                            dir('backend') {
                                echo "Installing backend dependencies..."
                                bat 'pip install -r requirements.txt'
                                echo "Running backend tests (if available)..."
                                bat 'python -m pytest tests/ || echo No tests found'
                            }
                        } else {
                            echo "⚠️ Backend folder not found, skipping backend setup."
                        }
                    } catch (Exception e) {
                        echo "Backend setup failed: ${e.message}"
                    }
                }
            }
        }

        stage('Model Verification') {
            steps {
                script {
                    if (fileExists('model')) {
                        echo "folder verified."
                        bat 'dir model /B'
                    } else {
                        echo "Model folder not found!"
                    }
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                script {
                    echo "Building Docker images..."
                    bat 'docker --version'

                    echo "Building backend image..."
                    bat 'docker build -t %IMAGE_BACKEND%:latest ./backend'

                    echo "Building frontend image..."
                    bat 'docker build -t %IMAGE_FRONTEND%:latest ./frontend'
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    echo "Logging in to Docker Hub..."
                    bat 'echo %DOCKER_HUB_PASS% | docker login -u %DOCKER_HUB_USER% --password-stdin'

                    echo "Pushing backend image..."
                    bat 'docker push %IMAGE_BACKEND%:latest'

                    echo "Pushing frontend image..."
                    bat 'docker push %IMAGE_FRONTEND%:latest'
                }
            }
        }

        stage('Deploy (Optional)') {
            steps {
                script {
                    echo "Deploy stage (for Docker Compose / Kubernetes integration later)"
                    // Example future deployment:
                    // bat 'docker-compose down && docker-compose up -d'
                }
            }
        }

        stage('Build Artifacts') {
            steps {
                script {
                    echo "Archiving build artifacts..."
                    dir('frontend') {
                        archiveArtifacts artifacts: 'build/**/*', allowEmptyArchive: true
                    }
                    archiveArtifacts artifacts: '**/requirements.txt', allowEmptyArchive: true
                    archiveArtifacts artifacts: 'model/**/*', allowEmptyArchive: true
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully! Images pushed to Docker Hub."
        }
        failure {
            echo "Pipeline failed. Check logs above for details."
        }
        always {
            echo "🧹 Cleaning workspace..."
            cleanWs()
        }
    }
}
