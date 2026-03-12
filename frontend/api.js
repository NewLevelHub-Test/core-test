
const API_CONFIG = {
    // Заменить на URL реального бэкенда в будущем
    BASE_URL: 'http://localhost:3000/api', 
    AUTH_PAGE: 'h1.html'
};

const api = {

    async fetchWithAuth(endpoint, options = {}) {
        const token = localStorage.getItem('jwt_token');
        
        const defaultHeaders = {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        };

        const config = {
            ...options,
            headers: {
                ...defaultHeaders,
                ...options.headers
            }
        };

        try {
            const response = await fetch(`${API_CONFIG.BASE_URL}${endpoint}`, config);

            if (response.status === 401) {
                console.warn('Сессия истекла. Перенаправление на вход...');
                this.logout();
                return;
            }

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `Ошибка API: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error.message);
            throw error;
        }
    },

   
    async login(credentials) {

        const data = await this.fetchWithAuth('/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
        
        if (data.token) {
            localStorage.setItem('jwt_token', data.token);
            window.location.href = 'Dashboard.html';
        }
        return data;
    },

    logout() {
        localStorage.removeItem('jwt_token');
        window.location.href = API_CONFIG.AUTH_PAGE;
    },

    isAuthenticated() {
        return !!localStorage.getItem('jwt_token');
    }
};

window.roChessApi = api;