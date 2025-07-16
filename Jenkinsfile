pipeline {
    agent any

    environment {
        BASE_URL = credentials('xfit_base_url') //
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
                    # Создаем виртуальное окружение
                    python3 -m venv .venv
                    . .venv/bin/activate

                    # Обновляем pip и устанавливаем зависимости
                    pip install --upgrade pip
                    pip install -r requirements.txt

                    # Перезаписываем .env с Jenkins BASE_URL
                    echo "BASE_URL=$BASE_URL" > .env

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
