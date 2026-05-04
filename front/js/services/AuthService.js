const API_URL = 'http://localhost:8000';
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'user_data';

export const AuthService = {
    // Get JWT token from localStorage
    getToken() {
        return localStorage.getItem(TOKEN_KEY);
    },

    // Set JWT token in localStorage
    setToken(token) {
        localStorage.setItem(TOKEN_KEY, token);
    },

    // Clear authentication data
    clearAuth() {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
    },

    // Get current user from localStorage
    getCurrentUser() {
        const userJson = localStorage.getItem(USER_KEY);
        return userJson ? JSON.parse(userJson) : null;
    },

    // Set current user in localStorage
    setCurrentUser(user) {
        localStorage.setItem(USER_KEY, JSON.stringify(user));
    },

    // Traditional login with username (kept for backward compatibility)
    async getUser(username) {
        // For demo purposes, return a fake user for "teste"
        if (username === 'teste') {
            return {
                id: 'teste',
                username: 'teste',
                email: 'teste@example.com',
                name: 'Usuário Teste',
                role: 'user',
                photo: 'https://via.placeholder.com/150'
            };
        }
        try {
            const response = await fetch(`${API_URL}/users/${username}`);
            if (!response.ok) return null;
            return await response.json();
        } catch (error) {
            console.error("Erro ao contactar o servidor:", error);
            return null;
        }
    },

    // Google login - exchange Google ID token for JWT
    async loginWithGoogle(googleCredential) {
        try {
            const response = await fetch(`${API_URL}/auth/google`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    id_token: googleCredential.credential
                })
            });

            if (!response.ok) {
                const error = await response.json();
                console.error("Erro na autenticação Google:", error);
                return null;
            }

            const data = await response.json();
            // Store JWT token
            this.setToken(data.access_token);
            
            // Fetch user data using JWT
            const userData = await this.getMe();
            if (userData) {
                this.setCurrentUser(userData);
            }
            return userData;
        } catch (error) {
            console.error("Erro ao fazer login com Google:", error);
            return null;
        }
    },

    // Get authenticated user info using JWT token
    async getMe() {
        try {
            const token = this.getToken();
            if (!token) return null;

            const response = await fetch(`${API_URL}/auth/me`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                if (response.status === 401) {
                    // Token expired or invalid
                    this.clearAuth();
                }
                return null;
            }

            return await response.json();
        } catch (error) {
            console.error("Erro ao obter dados do utilizador:", error);
            return null;
        }
    },

    // Check if user is authenticated
    isAuthenticated() {
        return !!this.getToken();
    }
};