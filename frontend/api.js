const API_CONFIG = {
    BASE_URL: 'http://192.168.8.17:5000/api', 
    AUTH_PAGE: 'h1.html'
};

const api = {
    async fetchWithAuth(endpoint, options = {}) {
        const token = localStorage.getItem('access_token');
        const defaultHeaders = {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        };
    
        const baseUrl = API_CONFIG.BASE_URL.replace(/\/+$/, ''); 
        const cleanEndpoint = endpoint.replace(/^\/+/, '');    
        const url = `${baseUrl}/${cleanEndpoint}`;
    
        const config = {
            ...options,
            headers: { ...defaultHeaders, ...options.headers }
        };
    
        try {
            const response = await fetch(url, config);
            if (response.status === 401) { this.logout(); return; }
            const responseData = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(responseData.error || `Ошибка: ${response.status}`);
            return responseData;
        } catch (error) { throw error; }
    },

    async login(credentials) {
        console.log("Отправка данных на вход:", credentials);
        
        const data = await this.fetchWithAuth('/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
        
        console.log("Полный ответ сервера при логине:", data);

        const finalToken = data.access_token || (data.data && data.data.access_token) || data.token;
        const finalUser = data.user || (data.data && data.data.user);

        if (finalToken) {
            console.log("Токен получен! Сохраняю и перехожу на Dashboard...");
            window.roChessState.setTokens(finalToken, data.refresh_token || (data.data && data.data.refresh_token));
            window.roChessState.setUser(finalUser || { name: "Player" });
            
            setTimeout(() => {
                window.location.href = 'Dashboard.html';
            }, 100);
        } else {
            console.error("Сервер ответил успешно, но токена в объекте нет. Проверь консоль выше.");
            throw new Error("Ошибка авторизации: сервер не прислал ключ доступа.");
        }
        return data;
    },

    async register(userData) {
        console.log("Отправка данных на регистрацию:", userData);

        const data = await this.fetchWithAuth('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });

        console.log("Ответ сервера при регистрации:", data);

        const finalToken = data.access_token || (data.data && data.data.access_token) || data.token;
        const finalUser = data.user || (data.data && data.data.user);

        if (finalToken) {
            window.roChessState.setTokens(finalToken, data.refresh_token || (data.data && data.data.refresh_token));
            window.roChessState.setUser(finalUser);
            window.location.href = 'Dashboard.html';
        } else {
            alert("Регистрация успешна! Теперь войдите в свой аккаунт.");
            window.location.reload(); 
        }
        return data;
    },

    async getUserProfile() {
        return await this.fetchWithAuth('/users/profile', {
            method: 'GET'
        });
    },

    async uploadAvatar(file) {
        const formData = new FormData();
        formData.append('avatar', file);
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_CONFIG.BASE_URL}/users/avatar`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (!response.ok) throw new Error("Ошибка загрузки аватара");
        return await response.json();
    },

    async getDashboardData() {
        return await this.fetchWithAuth('/dashboard/', {
            method: 'GET'
        });
    },

    async getRoadmap() {
        return await this.fetchWithAuth('/roadmap/', {
            method: 'GET'
        });
    },

    async generateRoadmap() {
        return await this.fetchWithAuth('/roadmap/generate', {
            method: 'POST'
        });
    },

    async completeRoadmapTask(taskId) {
        return await this.fetchWithAuth(`/roadmap/tasks/${taskId}/complete`, {
            method: 'POST'
        });
    },

    async getTestsList() {
        return await this.fetchWithAuth('/tests/', {
            method: 'GET'
        });
    },

    async startTest(testId) {
        return await this.fetchWithAuth(`/tests/${testId}/start`, {
            method: 'POST'
        });
    },

    async submitTest(testId, answers) {
        return await this.fetchWithAuth(`/tests/${testId}/submit`, {
            method: 'POST',
            body: JSON.stringify({
                answers: answers 
            }) 
        });
    },
    
    
    async getTopics() {
        return await this.fetchWithAuth('/lessons/topics');
    },

    async getLessonsByTopic(topicId) {
        return await this.fetchWithAuth(`/lessons/topics/${topicId}`);
    },

    async getLessonContent(lessonId) {
        return await this.fetchWithAuth(`/lessons/${lessonId}`);
    },

    logout() {
        window.roChessState.logout();
        window.location.href = 'h1.html';
    },

    isAuthenticated() {
        return window.roChessState.isLoggedIn();
    }
};

window.roChessApi = api;