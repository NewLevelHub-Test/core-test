const state = {

    KEYS: {
        USER: 'ro_chess_user',
        ACCESS_TOKEN: 'access_token',
        REFRESH_TOKEN: 'refresh_token'
    },

    setUser(userData) {
        localStorage.setItem(this.KEYS.USER, JSON.stringify(userData));
    },

    getUser() {
        const user = localStorage.getItem(this.KEYS.USER);
        return user ? JSON.parse(user) : null;
    },

    setTokens(access, refresh) {
        if (access) localStorage.setItem(this.KEYS.ACCESS_TOKEN, access);
        if (refresh) localStorage.setItem(this.KEYS.REFRESH_TOKEN, refresh);
    },

    isLoggedIn() {
        return !!localStorage.getItem(this.KEYS.ACCESS_TOKEN);
    },

    logout() {
        localStorage.removeItem(this.KEYS.USER);
        localStorage.removeItem(this.KEYS.ACCESS_TOKEN);
        localStorage.removeItem(this.KEYS.REFRESH_TOKEN);
        window.location.href = 'index.html';
    }
};

window.roChessState = state;