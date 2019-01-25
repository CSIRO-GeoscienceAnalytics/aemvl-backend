pipeline {
    
	environment {
        registry = "https://docker-registry.it.csiro.au"
        imageName = "aemvl/backend"
        registryCredential = "sam-nexus"
        // GIT_REPO = "bitbucket.csiro.au/scm/datmos/data-mosaic-core.git"
    }
	agent none
    options {
        buildDiscarder(logRotator(numToKeepStr: '25', artifactNumToKeepStr: '4'))
        disableConcurrentBuilds()
    }
	
    stages {
        stage('Setup') {
			agent {
				docker {
					image 'continuumio/miniconda3'
					args '-u root:root'
				}
			}
            steps {
                sh 'conda create -n aemvl-backend python=3.6'
                sh 'echo "source activate aemvl-backend" > ~/.bashrc'
				sh 'PATH=/opt/conda/envs/env/bin:$PATH'
				sh 'conda install --file requirements.txt'
				sh 'GDAL_DATA=/opt/miniconda3/envs/aemvl-backend/share/epsg_csv'
				sh 'pip install python-dotenv'
            }
        }
        stage('Test') {
            steps {
                sh 'py.test --verbose --junit-xml test-reports/results.xml'
            }
            post {
                always {
                    junit 'test-reports/results.xml'
					sh 'sh clean.sh'
                }
            }
        }
        stage('Build Image') {
            agent { label 'master' }
            steps {
                script {
                    SECRET = sh (script:"date +%s | sha256sum | base64 | head -c 32 ; echo", returnStdout: true).trim()

                    if( "${env.BRANCH_NAME}" != "master" ) {
                        GIT_TAG = "${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
                    }
                    else {
                        GIT_TAG = "${env.BUILD_NUMBER}"
                    }
                    image = docker.build("${imageName}", " --build-arg version=${GIT_TAG} --build-arg secret=${SECRET} .")
                    println "Newly generated image, " + image.id
                }
            }
        }
		stage('Push Image') {
			agent { label 'master' }
			steps {
				script {
					docker.withRegistry(registry, registryCredential)
					{
						image.push("${env.BRANCH_NAME}")
						if ( "${env.BRANCH_NAME}" == "master" ) {
								image.push("latest")
						}
					}
				}
			}
		}
	}
}