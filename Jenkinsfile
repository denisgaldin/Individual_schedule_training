pipeline {
    agent any

    environment {
        BASE_URL = credentials('xfit_base_url')
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
                echo '🐍 Установка зависимостей и запуск всех тестов'
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt

                    echo '🧹 Очистка прошлых результатов Allure'
                    rm -rf allure-results

                    echo '🚀 Запуск всех тестов'
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
            echo '🧹 Очистка окружения'
            sh 'rm -rf .venv'
        }

        failure {
            echo '❌ Ошибка: Проверить тесты и окружение'
        }
    }
}