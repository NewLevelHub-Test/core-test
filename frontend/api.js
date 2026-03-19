const API_CONFIG = {
    BASE_URL: 'http://192.168.8.53:5000/api', 
    AUTH_PAGE: 'h1.html'
};

const api = {
    async fetchWithAuth(endpoint, options = {}) {
        const token = localStorage.getItem('access_token'); 
        
        const defaultHeaders = {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        };

        const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;

        const config = {
            ...options,
            headers: {
                ...defaultHeaders,
                ...options.headers
            }
        };

        try {
            const response = await fetch(`${API_CONFIG.BASE_URL}${cleanEndpoint}`, config);

            if (response.status === 401) {
                console.warn('Сессия истекла. Перенаправление...');
                this.logout();
                return;
            }

            const responseData = await response.json().catch(() => ({}));

            if (!response.ok) {
                const errorMessage = responseData.error || responseData.message || `Ошибка API: ${response.status}`;
                throw new Error(errorMessage);
            }

            return responseData;
        } catch (error) {
            console.error('API Error:', error.message);
            throw error;
        }
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

    logout() {
        window.roChessState.logout();
        window.location.href = 'h1.html';
    },

    isAuthenticated() {
        return window.roChessState.isLoggedIn();
    }
};

window.roChessApi = api;