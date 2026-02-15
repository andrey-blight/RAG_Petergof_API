/**
 * Скрипт для тестирования всех API endpoints фронтенда
 * Использует предоставленные учетные данные
 */

const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

const API_URL = 'https://sci-peterhof.teslaistra.ru/api/v1';
const EMAIL = 'danyefimoff@gmail.com';
const PASSWORD = 'pe6-CUe-kEs-Jis';

let accessToken = '';
let refreshToken = '';

// Цвета для консоли
const colors = {
    reset: '\x1b[0m',
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
    console.log(`${colors[color]}${message}${colors.reset}`);
}

function logTest(testName) {
    log(`\n${'='.repeat(60)}`, 'cyan');
    log(`Тест: ${testName}`, 'blue');
    log('='.repeat(60), 'cyan');
}

async function testLogin() {
    logTest('Авторизация (POST /token)');
    try {
        const params = new URLSearchParams();
        params.append('grant_type', 'password');
        params.append('username', EMAIL);
        params.append('password', PASSWORD);

        const response = await axios.post(`${API_URL}/token`, params, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        });

        accessToken = response.data.access_token;
        refreshToken = response.data.refresh_token;
        log('✓ Авторизация успешна', 'green');
        log(`  Access Token: ${accessToken.substring(0, 20)}...`, 'yellow');
        return true;
    } catch (error) {
        log(`✗ Ошибка авторизации: ${error.response?.data?.detail || error.message}`, 'red');
        return false;
    }
}

async function testGetMe() {
    logTest('Получение информации о пользователе (GET /me)');
    try {
        const response = await axios.get(`${API_URL}/me`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        log('✓ Информация о пользователе получена', 'green');
        log(`  Email: ${response.data.email}`, 'yellow');
        log(`  Is Admin: ${response.data.is_admin}`, 'yellow');
        return response.data;
    } catch (error) {
        log(`✗ Ошибка: ${error.response?.data?.detail || error.message}`, 'red');
        return null;
    }
}

async function testGetIndexes() {
    logTest('Получение списка индексов (GET /indexes)');
    try {
        const response = await axios.get(`${API_URL}/indexes`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        log('✓ Список индексов получен', 'green');
        log(`  Количество индексов: ${response.data.indexes?.length || 0}`, 'yellow');
        if (response.data.indexes && response.data.indexes.length > 0) {
            log(`  Индексы: ${response.data.indexes.join(', ')}`, 'yellow');
        }
        return response.data.indexes || [];
    } catch (error) {
        log(`✗ Ошибка: ${error.response?.data?.detail || error.message}`, 'red');
        return [];
    }
}

async function testGetFiles() {
    logTest('Получение списка файлов (GET /files)');
    try {
        const response = await axios.get(`${API_URL}/files`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        log('✓ Список файлов получен', 'green');
        log(`  Количество файлов: ${response.data.files?.length || 0}`, 'yellow');
        if (response.data.files && response.data.files.length > 0) {
            log(`  Файлы: ${response.data.files.slice(0, 5).join(', ')}${response.data.files.length > 5 ? '...' : ''}`, 'yellow');
        }
        return response.data.files || [];
    } catch (error) {
        log(`✗ Ошибка: ${error.response?.status === 403 ? 'Доступ запрещен (не админ)' : error.response?.data?.detail || error.message}`, 'red');
        return [];
    }
}

async function testGetSettings() {
    logTest('Получение настроек (GET /settings)');
    try {
        const response = await axios.get(`${API_URL}/settings`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        log('✓ Настройки получены', 'green');
        log(`  Prompt: ${response.data.prompt?.substring(0, 50)}...`, 'yellow');
        log(`  Temperature: ${response.data.temperature}`, 'yellow');
        log(`  Count Vector: ${response.data.count_vector}`, 'yellow');
        log(`  Count Fulltext: ${response.data.count_fulltext}`, 'yellow');
        return response.data;
    } catch (error) {
        log(`✗ Ошибка: ${error.response?.data?.detail || error.message}`, 'red');
        return null;
    }
}

async function testSendSettings(settings) {
    logTest('Отправка настроек (POST /settings)');
    try {
        const response = await axios.post(`${API_URL}/settings`, settings, {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            }
        });
        log('✓ Настройки сохранены', 'green');
        return true;
    } catch (error) {
        log(`✗ Ошибка: ${error.response?.data?.detail || error.message}`, 'red');
        return false;
    }
}

async function testAskQuestion(indexName) {
    logTest(`Отправка вопроса (POST /answer) - индекс: ${indexName}`);
    try {
        const response = await axios.post(`${API_URL}/answer`, {
            index: indexName,
            question: 'Тестовый вопрос: Что такое Петергоф?'
        }, {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            }
        });

        const taskId = response.data.task_id;
        log(`✓ Задача создана, Task ID: ${taskId}`, 'green');
        log('  Ожидание ответа...', 'yellow');

        // Проверяем статус
        let attempts = 0;
        const maxAttempts = 30;
        while (attempts < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, 1000));
            try {
                const statusResponse = await axios.get(`${API_URL}/answer/status/${taskId}`, {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`
                    }
                });

                if (statusResponse.status === 200) {
                    log('✓ Ответ получен', 'green');
                    log(`  Ответ: ${statusResponse.data.status?.substring(0, 100)}...`, 'yellow');
                    return statusResponse.data.status;
                }
            } catch (statusError) {
                if (statusError.response?.status !== 404) {
                    log(`✗ Ошибка проверки статуса: ${statusError.message}`, 'red');
                    break;
                }
            }
            attempts++;
        }
        log('✗ Превышено время ожидания ответа', 'red');
        return null;
    } catch (error) {
        log(`✗ Ошибка: ${error.response?.data?.detail || error.message}`, 'red');
        return null;
    }
}

async function testSendReview() {
    logTest('Отправка отзыва (POST /review)');
    try {
        const response = await axios.post(`${API_URL}/review`, {
            question: 'Тестовый вопрос',
            model_answer: 'Тестовый ответ',
            is_ok: true,
            correct_answer: null
        }, {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            }
        });
        log('✓ Отзыв отправлен', 'green');
        return true;
    } catch (error) {
        log(`✗ Ошибка: ${error.response?.data?.detail || error.message}`, 'red');
        return false;
    }
}

async function testCheckFileStatus() {
    logTest('Проверка статуса обработки файлов (GET /files/status)');
    try {
        const response = await axios.get(`${API_URL}/files/status`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        log('✓ Статус файлов получен', 'green');
        log(`  Is Running: ${response.data.is_running}`, 'yellow');
        return response.data;
    } catch (error) {
        log(`✗ Ошибка: ${error.response?.status === 403 ? 'Доступ запрещен (не админ)' : error.response?.data?.detail || error.message}`, 'red');
        return null;
    }
}

async function testCheckIndexStatus() {
    logTest('Проверка статуса создания индекса (GET /indexes/status)');
    try {
        const response = await axios.get(`${API_URL}/indexes/status`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        log('✓ Статус индекса получен', 'green');
        log(`  Status: ${response.data.status}`, 'yellow');
        return response.data;
    } catch (error) {
        log(`✗ Ошибка: ${error.response?.status === 403 ? 'Доступ запрещен (не админ)' : error.response?.data?.detail || error.message}`, 'red');
        return null;
    }
}

async function testRefreshToken() {
    logTest('Обновление токена (POST /refresh)');
    try {
        const response = await axios.post(`${API_URL}/refresh`, {}, {
            headers: {
                'refresh-token': refreshToken
            }
        });
        accessToken = response.data.access_token;
        refreshToken = response.data.refresh_token;
        log('✓ Токен обновлен', 'green');
        return true;
    } catch (error) {
        log(`✗ Ошибка: ${error.response?.data?.detail || error.message}`, 'red');
        return false;
    }
}

async function runAllTests() {
    log('\n' + '='.repeat(60), 'cyan');
    log('НАЧАЛО ТЕСТИРОВАНИЯ API', 'cyan');
    log('='.repeat(60) + '\n', 'cyan');

    // 1. Авторизация
    const loginSuccess = await testLogin();
    if (!loginSuccess) {
        log('\n✗ Не удалось авторизоваться. Тестирование остановлено.', 'red');
        return;
    }

    // 2. Получение информации о пользователе
    const userInfo = await testGetMe();
    const isAdmin = userInfo?.is_admin || false;

    // 3. Получение списка индексов
    const indexes = await testGetIndexes();

    // 4. Получение настроек
    const settings = await testGetSettings();

    // 5. Отправка настроек (если получены)
    if (settings) {
        await testSendSettings(settings);
    }

    // 6. Отправка вопроса (если есть индексы)
    if (indexes && indexes.length > 0) {
        await testAskQuestion(indexes[0]);
    } else {
        log('\n⚠ Нет доступных индексов для тестирования вопроса', 'yellow');
    }

    // 7. Отправка отзыва
    await testSendReview();

    // 8. Получение списка файлов (только для админов)
    if (isAdmin) {
        await testGetFiles();
    } else {
        log('\n⚠ Пользователь не является админом, пропуск тестов для админов', 'yellow');
    }

    // 9. Проверка статуса файлов (только для админов)
    if (isAdmin) {
        await testCheckFileStatus();
    }

    // 10. Проверка статуса индекса (только для админов)
    if (isAdmin) {
        await testCheckIndexStatus();
    }

    // 10. Обновление токена
    await testRefreshToken();

    log('\n' + '='.repeat(60), 'cyan');
    log('ТЕСТИРОВАНИЕ ЗАВЕРШЕНО', 'cyan');
    log('='.repeat(60) + '\n', 'cyan');
}

// Запуск тестов
runAllTests().catch(error => {
    log(`\n✗ Критическая ошибка: ${error.message}`, 'red');
    process.exit(1);
});

