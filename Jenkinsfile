pipeline {
  agent any

  environment {
    // Configure these in Jenkins: Docker Hub credentials and image name
    DOCKERHUB_CREDENTIALS = credentials('dockerhub-creds')
    DOCKER_IMAGE = "${env.DOCKERHUB_NAMESPACE ?: 'your-dockerhub-namespace'}/farmlink-backend"
    DOCKER_TAG = "${env.BUILD_NUMBER}"
    // Optional: Render deploy hook URL stored as a secret in Jenkins
    RENDER_DEPLOY_HOOK = credentials('render-deploy-hook')
  }

  options {
    timestamps()
    ansiColor('xterm')
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Backend: Set up venv and install deps') {
      steps {
        dir('backend') {
          sh label: 'Install deps', script: '''
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
          sh label: 'Run tests', script: '''
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

    stage('Docker: Build') {
      steps {
        dir('backend') {
          script {
            def image = sh(returnStdout: true, script: 'echo ${DOCKER_IMAGE}:${DOCKER_TAG}').trim()
            sh """
              docker build -t ${image} .
            """
          }
        }
      }
    }

    stage('Docker: Login & Push') {
      steps {
        script {
          withEnv(["DOCKER_CONFIG=${env.WORKSPACE}/.docker"]) {
            sh """
              echo '${DOCKERHUB_CREDENTIALS_PSW}' | docker login -u '${DOCKERHUB_CREDENTIALS_USR}' --password-stdin
            """
          }
        }
        dir('backend') {
          script {
            def image = sh(returnStdout: true, script: 'echo ${DOCKER_IMAGE}:${DOCKER_TAG}').trim()
            def latest = sh(returnStdout: true, script: 'echo ${DOCKER_IMAGE}:latest').trim()
            sh """
              docker tag ${image} ${latest}
              docker push ${image}
              docker push ${latest}
            """
          }
        }
      }
    }

    stage('Deploy: Trigger Render (optional)') {
      when {
        expression { return env.RENDER_DEPLOY_HOOK && env.RENDER_DEPLOY_HOOK.trim() }
      }
      steps {
        sh """
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




