pipeline {
    agent {
        kubernetes {
            yaml """
apiVersion: v1
kind: Pod
metadata:
  namespace: jenkins
  labels:
    app: jenkins-agent

spec:
  containers:
  - name: docker
    image: docker:dind
    command:
    - cat
    tty: true
    volumeMounts:
    - name: docker-sock
      mountPath: /var/run/docker.sock
  - name: helm
    image: alpine/helm:3.11.1
    command:
    - cat
    tty: true
  volumes:
  - name: docker-sock
    hostPath:
      path: /var/run/docker.sock
"""
        }
    }
    
    environment {
        DOCKER_USERNAME = 'taran20singh' // Replace with your Docker Hub username
        APP_NAME = 'crud-app'
        APP_VERSION = "${BUILD_NUMBER}"
        GIT_REPO_URL = 'https://github.com/TaranpreetSingh/crud-app.git' // Replace with your GitHub repo URL
        GIT_BRANCH = 'main' // Replace with your branch name
    }
    
    stages {
        stage('Checkout from GitHub') {
            steps {
                // Clean workspace before checkout
                cleanWs()
                
                // Checkout from Git
                git branch: "${GIT_BRANCH}", 
                    url: "${GIT_REPO_URL}"
            }
        }
        
        stage('Build Docker Image') {
            steps {
                container('docker') {
                    sh "docker build -t ${DOCKER_USERNAME}/${APP_NAME}:${APP_VERSION} ."
                }
            }
        }
        
        stage('Push Docker Image') {
            steps {
                container('docker') {
                    withCredentials([string(credentialsId: 'docker-hub-password', variable: 'DOCKER_PASSWORD')]) {
                        sh "echo ${DOCKER_PASSWORD} | docker login -u ${DOCKER_USERNAME} --password-stdin"
                        sh "docker push ${DOCKER_USERNAME}/${APP_NAME}:${APP_VERSION}"
                    }
                }
            }
        }
        
        stage('Deploy to Kubernetes with Helm') {
            steps {
                container('helm') {
                    script {
                        // Check if release exists
                        def releaseStatus = sh(script: "helm status ${APP_NAME} -n crud-app 2>&1 || true", returnStdout: true)
                        
                        if (releaseStatus.contains("Error: release: not found")) {
                            // Install new release
                            sh "helm install ${APP_NAME} ./crud-app -n crud-app --set image.repository=${DOCKER_USERNAME}/${APP_NAME} --set image.tag=${APP_VERSION}"
                        } else {
                            // Upgrade existing release
                            sh "helm upgrade ${APP_NAME} ./crud-app -n crud-app --set image.repository=${DOCKER_USERNAME}/${APP_NAME} --set image.tag=${APP_VERSION}"
                        }
                    }
                }
            }
        }
    }
    
    post {
        success {
            echo "Deployment successful!"
            echo "Access the CRUD app at: http://crud-app.example.com"
        }
        failure {
            echo "Deployment failed. Check the Jenkins logs for details."
        }
    }
}