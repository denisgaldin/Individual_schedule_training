pipeline {
    agent any

    environment {
        BASE_URL = credentials('xfit_base_url')
        CLUB_GUID = credentials('xfit_club_guid')
        HALL_GUID = credentials('xfit_hall_guid')
        SUBSCRIPTION_GUID = credentials('xfit_subscription_guid')
    }

    stages {
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

                    pip install --upgrade pip
                    pip install -r requirements.txt

                    # Записываем все переменные в .env
                    echo "BASE_URL=$BASE_URL" > .env
                    echo "CLUB_GUID=$CLUB_GUID" >> .env
                    echo "HALL_GUID=$HALL_GUID" >> .env
                    echo "SUBSCRIPTION_GUID=$SUBSCRIPTION_GUID" >> .env

                    echo '🧹 Очистка прошлых результатов Allure'
                    rm -rf allure-results

                    echo '🚀 Запуск pytest с выводом и allure'
                    pytest tests/ --alluredir=allure-results --disable-warnings --maxfail=1 -v
                '''
            }
        }

        stage('Allure Report') {
            steps {
                echo '📊 Генерация Allure отчета'
                allure([
                    includeProperties: false,
                    jdk: '',
                    reportBuildPolicy: 'ALWAYS',
                    results: [[path: 'allure-results']]
                ])
            }
        }
    }

    post {
        always {
            echo '🧹 Очистка окружения и .venv'
            sh 'rm -rf .venv'
        }

        failure {
            echo '❌ Сборка упала. Проверь ошибки в логах'
        }
    }
}
