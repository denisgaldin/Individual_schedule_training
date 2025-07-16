pipeline {
    agent any

    environment {
        BASE_URL = credentials('xfit_base_url')
        CLUB_GUID = credentials('xfit_club_guid')
        HALL_GUID = credentials('xfit_hall_guid')
        SUBSCRIPTION_GUID = credentials('xfit_subscription_guid')
    }

    stages {

        stage('🚨 ВРЕМЕННО: Вывод переменных для восстановления .env') {
            steps {
                script {
                    // ВНИМАНИЕ! УДАЛИ ЭТО ПОСЛЕ ВОССТАНОВЛЕНИЯ .env
                    echo "BASE_URL=$BASE_URL"
                    echo "CLUB_GUID=$CLUB_GUID"
                    echo "HALL_GUID=$HALL_GUID"
                    echo "SUBSCRIPTION_GUID=$SUBSCRIPTION_GUID"
                    echo "PHONE_NUMBER=$PHONE_NUMBER"
                    echo "SMS_CODE=$SMS_CODE"
                    echo "SMS_TOKEN=$SMS_TOKEN"
                }
            }
        }

        stage('Checkout') {
            steps {
                echo '🔄 Получаем код из репозитория'
                checkout scm
            }
        }

        stage('Install & Run Tests') {
            steps {
                echo '🐍 Установка зависимостей и запуск тестов'
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install -r requirements.txt

                    echo BASE_URL=$BASE_URL > .env
                    echo CLUB_GUID=$CLUB_GUID >> .env
                    echo HALL_GUID=$HALL_GUID >> .env
                    echo SUBSCRIPTION_GUID=$SUBSCRIPTION_GUID >> .env
                    echo PHONE_NUMBER=$PHONE_NUMBER >> .env
                    echo SMS_CODE=$SMS_CODE >> .env
                    echo SMS_TOKEN=$SMS_TOKEN >> .env

                    pytest tests/ --disable-warnings -v
                '''
            }
        }

        stage('Allure Report') {
            steps {
                echo '📊 Генерация Allure отчета'
                allure includeProperties: false, jdk: '', results: [[path: 'allure-results']]
            }
        }
    }

    post {
        always {
            echo '🧹 Очистка окружения'
            sh 'rm -rf .venv'
        }
    }
}
