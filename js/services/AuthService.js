export const AuthService = {
    getUsers() {
        const db = JSON.parse(localStorage.getItem('bookboxd_db'));
        return db ? db.users : [];
    },

    getUser(username) {
        return this.getUsers().find(u => u.username.toLowerCase() === username.toLowerCase());
    },

    updateUserPhoto(username, newPhotoUrl) {
        const db = JSON.parse(localStorage.getItem('bookboxd_db'));
        const userIndex = db.users.findIndex(u => u.username === username);
        if (userIndex !== -1) {
            db.users[userIndex].photo = newPhotoUrl;
            localStorage.setItem('bookboxd_db', JSON.stringify(db));
            return true;
        }
        return false;
    }
};