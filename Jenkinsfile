pipeline {
  agent any
  
  environment {
    // Docker Hub credentials (already configured in Jenkins)
    DOCKERHUB_CREDENTIALS = credentials('dockerhub-creds')
    DOCKER_USERNAME = "${DOCKERHUB_CREDENTIALS_USR}"
    DOCKER_PASSWORD = "${DOCKERHUB_CREDENTIALS_PSW}"

    // Docker image names
    BACKEND_IMAGE = "kandhimallayashwanth/farmlink-backend"
    FRONTEND_IMAGE = "kandhimallayashwanth/farmlink-frontend"

    // Tag with Jenkins build number
    DOCKER_TAG = "${env.BUILD_NUMBER}"

    // Optional Render deploy hook (if configured)
    RENDER_DEPLOY_HOOK = credentials('render-deploy-hook')
  }

  options {
    timestamps()
    ansiColor('xterm')
  }

  stages {

    // Step 1: Checkout repo from GitHub
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    // Step 2: Backend setup and tests
    stage('Backend: Set up venv and install deps') {
      steps {
        dir('backend') {
          sh '''
            python3 -m venv venv
            . venv/bin/activate
            pip install --upgrade pip
            pip install -r requirements.txt
            pip install pytest pytest-flask
          '''
        }
      }
    }

    stage('Backend: Tests') {
      steps {
        dir('backend') {
          sh '''
            . venv/bin/activate
            pytest -q || true
          '''
        }
      }
      post {
        always {
          junit allowEmptyResults: true, testResults: 'backend/**/junit*.xml'
        }
      }
    }

    // Step 3: Build Docker image for backend
    stage('Docker: Build Backend') {
      steps {
        dir('backend') {
          script {
            def image = "${BACKEND_IMAGE}:${DOCKER_TAG}"
            sh """
              docker build -t ${image} .
              docker tag ${image} ${BACKEND_IMAGE}:latest
            """
          }
        }
      }
    }

    // Step 4: Build Docker image for frontend (Nginx serving static files)
    stage('Docker: Build Frontend') {
      steps {
        dir('frontend') {
          script {
            def image = "${FRONTEND_IMAGE}:${DOCKER_TAG}"
            sh """
              docker build -t ${image} .
              docker tag ${image} ${FRONTEND_IMAGE}:latest
            """
          }
        }
      }
    }

    // Step 5: Login and push both images to Docker Hub
    stage('Docker: Login & Push') {
      steps {
        script {
          sh """
            echo '${DOCKER_PASSWORD}' | docker login -u '${DOCKER_USERNAME}' --password-stdin
            docker push ${BACKEND_IMAGE}:${DOCKER_TAG}
            docker push ${BACKEND_IMAGE}:latest
            docker push ${FRONTEND_IMAGE}:${DOCKER_TAG}
            docker push ${FRONTEND_IMAGE}:latest
          """
        }
      }
    }

    // Step 6: Optional deploy to Render (via webhook)
    stage('Deploy: Trigger Render (optional)') {
      when {
        expression { return env.RENDER_DEPLOY_HOOK && env.RENDER_DEPLOY_HOOK.trim() }
      }
      steps {
        sh """
          echo "Triggering Render deploy..."
          curl -fsSL -X POST "$RENDER_DEPLOY_HOOK" || true
        """
      }
    }
  }

  post {
    always {
      cleanWs()
    }
  }
}
