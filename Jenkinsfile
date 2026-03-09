pipeline {

    agent any

    tools {
        maven 'Maven3'
    }

    stages {

        stage('Checkout Dev Code') {
            steps {
                git branch: 'master',
                url: 'https://github.com/vickybond007007/app-dev-repo.git'
            }
        }

        stage('Build Application') {
            steps {
                sh 'mvn clean install'
            }
        }

        stage('Checkout QA Automation Repo') {
            steps {
                dir('qa-tests') {
                    git branch: 'master',
                    url: 'https://github.com/vickybond007007/selenium-ci-cd-demo.git'
                }
            }
        }

        stage('Run Automation Tests') {
            steps {
                dir('qa-tests') {
                    sh 'mvn clean test'
                }
            }
        }

    }
}
