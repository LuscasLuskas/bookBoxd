export const ClubService = {
    getClubBooks() {
        const db = JSON.parse(localStorage.getItem('bookboxd_db'));
        return db ? db.books.filter(b => b.isClubBook) : [];
    },

    updateProgress(bookId, newProgress) {
        const db = JSON.parse(localStorage.getItem('bookboxd_db'));
        const bookIndex = db.books.findIndex(b => b.id === bookId);
        if (bookIndex !== -1) {
            db.books[bookIndex].currentProgress = newProgress;
            localStorage.setItem('bookboxd_db', JSON.stringify(db));
        }
    },

    // NOVA FUNÇÃO: Adiciona um livro oficial do mês
    addClubBook(bookData) {
        const db = JSON.parse(localStorage.getItem('bookboxd_db'));
        const newBook = {
            id: Date.now(),
            ...bookData,
            totalPages: parseInt(bookData.totalPages),
            totalChapters: parseInt(bookData.totalChapters),
            currentProgress: 0,
            isClubBook: true, // Define que é do clube
            owner: 'Clube'
        };
        db.books.push(newBook);
        localStorage.setItem('bookboxd_db', JSON.stringify(db));
    }
};