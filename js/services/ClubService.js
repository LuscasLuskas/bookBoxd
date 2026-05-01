const API_URL = 'http://localhost:8000';

export const ClubService = {
    async getClubBooks() {
        const response = await fetch(`${API_URL}/books/club`);
        return await response.json();
    },

    async updateProgress(bookId, newProgress) {
        await fetch(`${API_URL}/books/${bookId}/progress`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ progress: newProgress })
        });
    },

    async addClubBook(bookData) {
        await fetch(`${API_URL}/books/club`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(bookData)
        });
    }
};