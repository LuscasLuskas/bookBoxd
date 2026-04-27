import { AuthService } from './AuthService.js';
import { ClubService } from './ClubService.js';
import { ExternalService } from './ExternalService.js';

export const StorageService = {
    initialData: {
        users: [
            { id: 1, username: 'lucas', password: '123', photo: 'https://i.pravatar.cc/150?u=lucas', name: 'Dr. Lucas do Ó Soares' },
            { id: 2, username: 'roberto', password: '123', photo: 'https://i.pravatar.cc/150?u=roberto', name: 'Roberto' },
            { id: 3, username: 'daniel', password: '123', photo: 'https://i.pravatar.cc/150?u=daniel', name: 'Daniel' },
            { id: 4, username: 'gabriel', password: '123', photo: 'https://i.pravatar.cc/150?u=gabriel', name: 'Gabriel' },
            { id: 5, username: 'lucas_brenner', password: '123', photo: 'https://i.pravatar.cc/150?u=lucas_brenner', name: 'Lucas Brenner' }
        ],
        books: [
            { 
                id: 1, title: 'Admirável Mundo Novo', author: 'Aldous Huxley', 
                totalPages: 311, totalChapters: 18, currentProgress: 0, 
                cover: 'https://upload.wikimedia.org/wikipedia/en/6/62/BraveNewWorld_FirstEdition.jpg',
                isClubBook: true, owner: 'Clube' 
            },
            { 
                id: 2, title: 'As Nuvens', author: 'Aristófanes', 
                totalPages: 150, totalChapters: 5, currentProgress: 0, 
                cover: 'https://upload.wikimedia.org/wikipedia/commons/a/a5/Aristophanes_Clouds.jpg',
                isClubBook: true, owner: 'Clube' 
            },
            { 
                id: 3, title: '1984', author: 'George Orwell', 
                totalPages: 328, totalChapters: 24, currentProgress: 0, 
                cover: 'https://upload.wikimedia.org/wikipedia/en/c/c3/1984first.jpg',
                isClubBook: true, owner: 'Clube' 
            },
            { 
                id: 4, title: 'O Investidor de Bom Senso', author: 'John C. Bogle', 
                totalPages: 216, totalChapters: 18, currentProgress: 216, 
                cover: 'https://covers.openlibrary.org/b/id/12534505-L.jpg',
                isClubBook: false, owner: 'Dr. Lucas' 
            },
            { 
                id: 5, title: 'Freakonomics', author: 'Steven Levitt & Stephen Dubner', 
                totalPages: 320, totalChapters: 6, currentProgress: 320, 
                cover: 'https://upload.wikimedia.org/wikipedia/en/6/63/Freakonomics.jpg',
                isClubBook: false, owner: 'Dr. Lucas' 
            },
            { 
                id: 6, title: 'A Morte de Ivan Ilitch', author: 'Liev Tolstói', 
                totalPages: 100, totalChapters: 12, currentProgress: 100, 
                cover: 'https://upload.wikimedia.org/wikipedia/commons/e/e7/Tolstoy_-_The_Death_of_Ivan_Ilyich.jpg',
                isClubBook: false, owner: 'Dr. Lucas' 
            }
        ]
    },

    init() {
        const currentDb = JSON.parse(localStorage.getItem('bookboxd_db'));
        
        // Se a base de dados não existir ou se tiver menos de 6 livros, reinicia para incluir os novos
        if (!currentDb || currentDb.books.length < 6) {
            localStorage.setItem('bookboxd_db', JSON.stringify(this.initialData));
            console.log("Base de dados atualizada com os novos livros e utilizadores.");
        }
    },

    auth: AuthService,
    club: ClubService,
    external: ExternalService
};