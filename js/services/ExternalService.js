const API_URL = 'http://localhost:8000';

export const ExternalService = {
    async getExternalBooks() {
        const response = await fetch(`${API_URL}/books/external`);
        return await response.json();
    },

    // Comunica com a nova rota de pesquisa do Google Books
    async searchGoogleBooks(query) {
        const response = await fetch(`${API_URL}/books/search?q=${encodeURIComponent(query)}`);
        if (!response.ok) return [];
        return await response.json();
    },

    // Comunica com a nova rota para salvar o livro pessoal
    async addPersonalBook(bookData) {
        await fetch(`${API_URL}/books/external`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(bookData)
        });
    }
};