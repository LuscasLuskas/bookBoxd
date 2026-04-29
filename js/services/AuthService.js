const API_URL = 'http://localhost:8000';

export const AuthService = {
    async getUser(username) {
        try {
            const response = await fetch(`${API_URL}/users/${username}`);
            if (!response.ok) return null;
            return await response.json();
        } catch (error) {
            console.error("Erro ao contactar o servidor:", error);
            return null;
        }
    }
};