pipeline {
    agent {
        docker {
            image 'python:3.6'
        }
    }
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r requirements.txt'
                //sh 'make develop'
            }
        }
        stage('Test') {
            steps {
                sh 'py.test --verbose --junit-xml test-reports/results.xml'

            }
            post {
                always {
                    junit 'test-reports/results.xml'
                }
            }
        }
        // stage('Docs') {
        //     steps {
        //         sh 'sphinx-build -b html docs build/docs/html'
        //     }
        //     post {
        //         success {
        //             publishHTML (target: [
        //               allowMissing: false,
        //               alwaysLinkToLastBuild: false,
        //               keepAll: true,
        //               reportDir: 'build/docs/html',
        //               reportFiles: 'index.html',
        //               reportName: "Docs"
        //             ])
        //         }
        //     }
        // }
        // stage('Deliver') { 
        //     steps {
        //         sh 'python setup.py bdist_wheel' 
        //     }
        //     post {
        //         success {
        //             archiveArtifacts 'dist/*.whl' 
        //         }
        //     }
        // }
    }
}