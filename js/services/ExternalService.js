export const ExternalService = {
    getExternalBooks() {
        const db = JSON.parse(localStorage.getItem('bookboxd_db'));
        return db ? db.books.filter(b => !b.isClubBook) : [];
    },

    addBook(bookData, owner) {
        const db = JSON.parse(localStorage.getItem('bookboxd_db'));
        const newBook = {
            id: Date.now(),
            ...bookData,
            currentProgress: bookData.totalPages, // Assume lido se for manual
            isClubBook: false,
            owner: owner
        };
        db.books.push(newBook);
        localStorage.setItem('bookboxd_db', JSON.stringify(db));
    }
};