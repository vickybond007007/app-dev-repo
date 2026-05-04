pipeline {

    agent any


    environment {
        QA_REPO_URL = 'https://github.com/vickybond007007/selenium-ci-cd-demo.git'
        QA_REPO_BRANCH = 'main'
        QA_REPO_DIR = 'qa-tests'
        QA_IMPACT_JSON = 'qa-impact.json'
        QA_IMPACT_REPORT = 'qa-impact-report.md'
        APP_LOG = 'app-under-test.log'
        APP_PID_FILE = 'app-under-test.pid'
        APP_BASE_URL = 'http://localhost:8080'
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
                dir(env.QA_REPO_DIR) {
                    git branch: env.QA_REPO_BRANCH,
                    url: env.QA_REPO_URL
                }
            }
        }

        stage('Analyze QA Impact') {
            steps {
                sh '''
                    set -eu

                    BASE_COMMIT="${GIT_PREVIOUS_SUCCESSFUL_COMMIT:-}"
                    if [ -z "$BASE_COMMIT" ]; then
                        BASE_COMMIT="${GIT_PREVIOUS_COMMIT:-}"
                    fi
                    if [ -z "$BASE_COMMIT" ] || ! git cat-file -e "$BASE_COMMIT^{commit}" 2>/dev/null; then
                        BASE_COMMIT="HEAD~1"
                    fi

                    git diff --name-status "$BASE_COMMIT" HEAD > dev-changed-files.txt
                    git diff "$BASE_COMMIT" HEAD > dev-changes.patch

                    PYTHON_BIN="$(command -v python3 || command -v python)"

                    "$PYTHON_BIN" tools/qa_impact_agent.py \
                        --changed-files dev-changed-files.txt \
                        --diff dev-changes.patch \
                        --qa-repo "$QA_REPO_DIR" \
                        --rules qa-impact-rules.json \
                        --output-json "$QA_IMPACT_JSON" \
                        --output-report "$QA_IMPACT_REPORT"
                '''
                archiveArtifacts artifacts: 'dev-changed-files.txt,dev-changes.patch,qa-impact.json,qa-impact-report.md', allowEmptyArchive: true
            }
        }

        stage('Start Application Under Test') {
            steps {
                sh '''
                    set -eu

                    APP_JAR="$(ls target/*.jar | head -n 1)"
                    if [ -z "$APP_JAR" ]; then
                        echo "No application jar found under target/"
                        exit 1
                    fi

                    nohup java -jar "$APP_JAR" > "$APP_LOG" 2>&1 &
                    echo "$!" > "$APP_PID_FILE"

                    for i in $(seq 1 30); do
                        if curl -fsS "$APP_BASE_URL/api/calculate/sum?a=1&b=3" >/dev/null; then
                            echo "Application is up on port 8080"
                            exit 0
                        fi
                        sleep 2
                    done

                    echo "Application did not start in time"
                    tail -100 "$APP_LOG" || true
                    exit 1
                '''
            }
        }

        stage('Run Selected QA Tests') {
            steps {
                script {
                    if (fileExists("${env.QA_REPO_DIR}/pom.xml")) {
                        dir(env.QA_REPO_DIR) {
                            sh 'mvn clean test -Dtest=CalculatorApiTest'
                        }
                    } else {
                        echo "QA repo does not contain pom.xml yet. Skipping automation execution and publishing QA impact report only."
                    }
                }
            }
            post {
                always {
                    junit testResults: "${env.QA_REPO_DIR}/target/surefire-reports/*.xml", allowEmptyResults: true
                    archiveArtifacts artifacts: "${env.QA_REPO_DIR}/target/surefire-reports/**", allowEmptyArchive: true
                }
            }
        }

    }

    post {
        always {
            sh '''
                if [ -f "$APP_PID_FILE" ]; then
                    kill "$(cat "$APP_PID_FILE")" 2>/dev/null || true
                fi
            '''
            archiveArtifacts artifacts: 'app-under-test.log', allowEmptyArchive: true
        }
    }
}
