const DEV_BACKEND_URL = 'http://127.0.0.1:5001';
const DEV_PORTS = ['3000', '5500', '8080'];

function resolveBaseUrl() {
    if (DEV_PORTS.includes(window.location.port)) {
        return `${DEV_BACKEND_URL}/api`;
    }
    return `${window.location.origin}/api`;
}

const API_CONFIG = {
    BASE_URL: resolveBaseUrl(),
    AUTH_PAGE: 'index.html'
};

const api = {
    async refreshAccessToken() {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) return null;

        const response = await fetch(`${API_CONFIG.BASE_URL}/auth/refresh`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${refreshToken}`
            }
        });

        if (!response.ok) return null;
        const data = await response.json().catch(() => ({}));
        if (data.access_token) {
            window.roChessState.setTokens(data.access_token, refreshToken);
            return data.access_token;
        }
        return null;
    },

    async fetchWithAuth(endpoint, options = {}, retryOn401 = true) {
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
            if (response.status === 401 && retryOn401) {
                const newAccessToken = await this.refreshAccessToken();
                if (newAccessToken) {
                    return this.fetchWithAuth(endpoint, options, false);
                }
                this.logout();
                return;
            }
            const responseData = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(responseData.error || responseData.message || `Ошибка: ${response.status}`);
            return responseData;
        } catch (error) { throw error; }
    },

    async login(credentials) {
        const data = await this.fetchWithAuth('/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials)
        }, false);

        const finalToken = data.access_token || (data.data && data.data.access_token) || data.token;
        const finalUser = data.user || (data.data && data.data.user);

        if (finalToken) {
            window.roChessState.setTokens(finalToken, data.refresh_token || (data.data && data.data.refresh_token));
            window.roChessState.setUser(finalUser || { name: "Player" });
            
            setTimeout(() => {
                window.location.href = 'Dashboard.html';
            }, 100);
        } else {
            throw new Error("Ошибка авторизации: сервер не прислал ключ доступа.");
        }
        return data;
    },

    async register(userData) {
        const data = await this.fetchWithAuth('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        }, false);

        const finalToken = data.access_token || (data.data && data.data.access_token) || data.token;
        const finalUser = data.user || (data.data && data.data.user);

        if (finalToken) {
            window.roChessState.setTokens(finalToken, data.refresh_token || (data.data && data.data.refresh_token));
            window.roChessState.setUser(finalUser);
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
        const send = async (token) => fetch(`${API_CONFIG.BASE_URL}/users/avatar`, {
            method: 'POST',
            headers: token ? { 'Authorization': `Bearer ${token}` } : {},
            body: formData
        });

        let token = localStorage.getItem('access_token');
        let response = await send(token);

        if (response.status === 401) {
            const newAccessToken = await this.refreshAccessToken();
            if (newAccessToken) {
                response = await send(newAccessToken);
            }
        }

        const payload = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(payload.error || `Ошибка: ${response.status}`);
        return payload;
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

    async getTaskContent(taskId) {
        return await this.fetchWithAuth(`/roadmap/tasks/${taskId}/content`, {
            method: 'GET'
        });
    },

    async submitTaskQuiz(taskId, answers) {
        return await this.fetchWithAuth(`/roadmap/tasks/${taskId}/quiz`, {
            method: 'POST',
            body: JSON.stringify({ answers })
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

    async getGameAnalysis(gameId) {
        return await this.fetchWithAuth(`/analysis/game/${gameId}`, {
            method: 'GET'
        });
    },

    async getMistakeExercises(mistakeId) {
        return await this.fetchWithAuth(`/analysis/mistakes/${mistakeId}/exercises`, {
            method: 'GET'
        });
    },

    async recognizePhoto(file) {
        const formData = new FormData();
        formData.append('image', file);

        const send = async (token) => fetch(`${API_CONFIG.BASE_URL}/photo/recognize`, {
            method: 'POST',
            headers: token ? { 'Authorization': `Bearer ${token}` } : {},
            body: formData
        });

        let token = localStorage.getItem('access_token');
        let response = await send(token);

        if (response.status === 401) {
            const newAccessToken = await this.refreshAccessToken();
            if (newAccessToken) {
                response = await send(newAccessToken);
            }
        }

        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.error || `Ошибка: ${response.status}`);
        return data;
    },
    
    async correctPhotoPosition(payload) {
        return await this.fetchWithAuth('/photo/correct', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    async analyzePhotoPosition(payload) {
        return await this.fetchWithAuth('/photo/analyze', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    async analyzePgnText(pgn) {
        return await this.fetchWithAuth('/analysis/pgn', {
            method: 'POST',
            body: JSON.stringify({ pgn })
        });
    },

    async analyzePgnPhoto(file) {
        const formData = new FormData();
        formData.append('image', file);

        const send = async (token) => fetch(`${API_CONFIG.BASE_URL}/analysis/pgn-photo`, {
            method: 'POST',
            headers: token ? { 'Authorization': `Bearer ${token}` } : {},
            body: formData
        });

        let token = localStorage.getItem('access_token');
        let response = await send(token);

        if (response.status === 401) {
            const newAccessToken = await this.refreshAccessToken();
            if (newAccessToken) response = await send(newAccessToken);
        }

        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.error || `Ошибка: ${response.status}`);
        return data;
    },

    async getAdminUsers() {
        return await this.fetchWithAuth('/admin/users', {
            method: 'GET'
        });
    },
    
    async getAdminUserDetail(userId) {
        return await this.fetchWithAuth(`/admin/users/${userId}`, {
            method: 'GET'
        });
    },
    
    async deleteAdminUser(userId) {
        return await this.fetchWithAuth(`/admin/users/${userId}`, {
            method: 'DELETE'
        });
    },
    
    async getPlatformStats() {
        return await this.fetchWithAuth('/admin/stats', {
            method: 'GET'
        });
    },
    
    async getLessonsList() {
        return await this.fetchWithAuth('/lessons/', {
            method: 'GET'
        });
    },
    
    async createAdminLesson(payload) {
        return await this.fetchWithAuth('/admin/lessons', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },
    
    async updateAdminLesson(lessonId, payload) {
        return await this.fetchWithAuth(`/admin/lessons/${lessonId}`, {
            method: 'PUT',
            body: JSON.stringify(payload)
        });
    },
    
    async deleteAdminLesson(lessonId) {
        return await this.fetchWithAuth(`/admin/lessons/${lessonId}`, {
            method: 'DELETE'
        });
    },
    
    async getTopicsList() {
        return await this.fetchWithAuth('/lessons/topics', {
            method: 'GET'
        });
    },
    
    async getLessonExercises(lessonId) {
        return await this.fetchWithAuth(`/lessons/${lessonId}/exercises`, {
            method: 'GET'
        });
    },
    
    async createAdminExercise(payload) {
        return await this.fetchWithAuth('/admin/exercises', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },
    
    async updateAdminExercise(exerciseId, payload) {
        return await this.fetchWithAuth(`/admin/exercises/${exerciseId}`, {
            method: 'PUT',
            body: JSON.stringify(payload)
        });
    },
    
    async deleteAdminExercise(exerciseId) {
        return await this.fetchWithAuth(`/admin/exercises/${exerciseId}`, {
            method: 'DELETE'
        });
    },

        // =========================
    // CHAT API
    // =========================

    async getChatSessions() {
        return await this.fetchWithAuth('/chat/sessions', {
            method: 'GET'
        });
    },

    async getChatSession(sessionId) {
        return await this.fetchWithAuth(`/chat/sessions/${sessionId}`, {
            method: 'GET'
        });
    },

    async createChatSession(payload = {}) {
        return await this.fetchWithAuth('/chat/sessions', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    async renameChatSession(sessionId, title) {
        return await this.fetchWithAuth(`/chat/sessions/${sessionId}`, {
            method: 'PATCH',
            body: JSON.stringify({ title })
        });
    },

    async deleteChatSession(sessionId) {
        return await this.fetchWithAuth(`/chat/sessions/${sessionId}`, {
            method: 'DELETE'
        });
    },

    async getChatMessages(sessionId) {
        return await this.fetchWithAuth(`/chat/sessions/${sessionId}/messages`, {
            method: 'GET'
        });
    },

    async sendChatMessage(sessionId, message, context = null) {
        return await this.fetchWithAuth(`/chat/sessions/${sessionId}/messages`, {
            method: 'POST',
            body: JSON.stringify({
                message,
                context
            })
        });
    },

    async createSessionAndSendMessage(message, title = 'Новый разговор', context = null) {
        const sessionData = await this.createChatSession({ title });

        const sessionId =
            sessionData.id ||
            sessionData.session_id ||
            sessionData.chat_id ||
            (sessionData.session && sessionData.session.id);

        if (!sessionId) {
            throw new Error('Не удалось получить id чат-сессии');
        }

        const messageData = await this.sendChatMessage(sessionId, message, context);

        return {
            session: sessionData,
            response: messageData
        };
    },

    async sendSmsCode(phone) {
        return await this.fetchWithAuth('/auth/send-code', {
            method: 'POST',
            body: JSON.stringify({ phone })
        });
    },

    async loginByPhone(phone, code) {
        const data = await this.fetchWithAuth('/auth/login-phone', {
            method: 'POST',
            body: JSON.stringify({ phone, code })
        }, false);

        const finalToken = data.access_token || (data.data && data.data.access_token);
        const finalUser = data.user || (data.data && data.data.user);

        if (finalToken) {
            window.roChessState.setTokens(finalToken, data.refresh_token || (data.data && data.data.refresh_token));
            window.roChessState.setUser(finalUser || { name: "Player" });
            setTimeout(() => { window.location.href = 'Dashboard.html'; }, 100);
        }
        return data;
    },

    async sendRecoveryCode(identifier) {
        const payload = identifier.includes('@') ? { email: identifier } : { phone: identifier };
        return await this.fetchWithAuth('/auth/recover', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    async confirmRecovery(identifier, code, newPassword) {
        const payload = identifier.includes('@')
            ? { email: identifier, code, new_password: newPassword }
            : { phone: identifier, code, new_password: newPassword };
        return await this.fetchWithAuth('/auth/recover/confirm', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    async getUserStats() {
        return await this.fetchWithAuth('/users/stats', { method: 'GET' });
    },

    async getAdminTopics(page = 1) {
        return await this.fetchWithAuth(`/admin/topics?page=${page}`, { method: 'GET' });
    },

    async createAdminTopic(payload) {
        return await this.fetchWithAuth('/admin/topics', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    async updateAdminTopic(topicId, payload) {
        return await this.fetchWithAuth(`/admin/topics/${topicId}`, {
            method: 'PUT',
            body: JSON.stringify(payload)
        });
    },

    async deleteAdminTopic(topicId) {
        return await this.fetchWithAuth(`/admin/topics/${topicId}`, {
            method: 'DELETE'
        });
    },

    async createAdminTest(payload) {
        return await this.fetchWithAuth('/admin/tests', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    async updateAdminTest(testId, payload) {
        return await this.fetchWithAuth(`/admin/tests/${testId}`, {
            method: 'PUT',
            body: JSON.stringify(payload)
        });
    },

    async addAdminQuestion(testId, payload) {
        return await this.fetchWithAuth(`/admin/tests/${testId}/questions`, {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    async updateAdminQuestion(questionId, payload) {
        return await this.fetchWithAuth(`/admin/questions/${questionId}`, {
            method: 'PUT',
            body: JSON.stringify(payload)
        });
    },

    async deleteAdminQuestion(questionId) {
        return await this.fetchWithAuth(`/admin/questions/${questionId}`, {
            method: 'DELETE'
        });
    },

    async getAdminTestDetail(testId) {
        return await this.fetchWithAuth(`/admin/tests/${testId}`, {
            method: 'GET'
        });
    },

    async deleteAdminTest(testId) {
        return await this.fetchWithAuth(`/admin/tests/${testId}`, {
            method: 'DELETE'
        });
    },

    async getPlacementTest() {
        return await this.fetchWithAuth('/onboarding/test', { method: 'GET' });
    },

    async submitPlacementTest(answers) {
        return await this.fetchWithAuth('/onboarding/test/submit', {
            method: 'POST',
            body: JSON.stringify({ answers }),
        });
    },

    async startPlacementGame() {
        return await this.fetchWithAuth('/onboarding/game/start', {
            method: 'POST',
        });
    },

    async completeOnboarding() {
        return await this.fetchWithAuth('/onboarding/complete', {
            method: 'POST',
        });
    },

    async logoutServer() {
        try {
            await this.fetchWithAuth('/auth/logout', { method: 'POST' });
        } catch (e) {}
        window.roChessState.logout();
        window.location.href = 'index.html';
    },

    logout() {
        this.logoutServer();
    },

    isAuthenticated() {
        return window.roChessState.isLoggedIn();
    }
};

function initUnifiedSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (!sidebar) return;

    const nav = sidebar.querySelector('nav');
    if (!nav) return;

    const currentPage = (window.location.pathname.split('/').pop() || '').toLowerCase();
    const user = window.roChessState ? window.roChessState.getUser() : null;
    const isAdmin = user && user.role === 'admin';

    const navItems = [
        { href: 'Dashboard.html', icon: '🏠', label: 'Главная' },
        { href: 'profile.html', icon: '👤', label: 'Профиль' },
        { href: 'study.html', icon: '📚', label: 'Уроки' },
        { href: 'wbots.html', icon: '🤖', label: 'Игра с ботом' },
        { href: 'hist.html', icon: '📜', label: 'История партий' },
        { href: 'analysis.html', icon: '📈', label: 'Анализ' },
        { href: 'position.html', icon: '📸', label: 'Сканер позиции' },
        { href: 'chat.html', icon: '💬', label: 'ИИ-помощник' },
    ];

    if (isAdmin) {
        navItems.push({ href: 'admin.html', icon: '🛠️', label: 'Админ-панель' });
    }

    nav.innerHTML = navItems.map(item => {
        const isActive = currentPage === item.href.toLowerCase();
        const baseClass = 'flex items-center gap-4 p-4 min-h-[52px] rounded-2xl font-black uppercase text-xs tracking-widest transition-all';
        const activeClass = 'bg-indigo-50 text-indigo-600 border-b-4 border-indigo-100';
        const idleClass = 'hover:bg-slate-50 text-slate-400';
        return `
            <a href="${item.href}" class="${baseClass} ${isActive ? activeClass : idleClass}">
                <span class="text-xl">${item.icon}</span>
                <span>${item.label}</span>
            </a>
        `;
    }).join('');
}

document.addEventListener('DOMContentLoaded', initUnifiedSidebar);

window.roChessApi = api;