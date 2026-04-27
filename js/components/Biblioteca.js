import { StorageService } from '../services/StorageService.js';

export function Biblioteca() {
    const container = document.createElement('section');
    container.className = 'space-y-8 animate-fadeIn';
    
    // AGORA JUNTA OS DADOS DOS DOIS MÓDULOS
    const clubBooks = StorageService.club.getClubBooks();
    const externalBooks = StorageService.external.getExternalBooks();
    const allBooks = [...clubBooks, ...externalBooks];

    container.innerHTML = `
        <div class="flex justify-between items-center border-b border-gray-700 pb-4">
            <h2 class="text-2xl text-white font-bold tracking-tight">BIBLIOTECA CENTRAL</h2>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-6">
            ${allBooks.map(book => `
                <div class="group cursor-pointer">
                    <div class="relative aspect-[2/3] overflow-hidden rounded border border-gray-700 group-hover:border-letterboxd-green transition">
                        <img src="${book.cover}" class="w-full h-full object-cover group-hover:scale-110 transition duration-300" onerror="this.src='https://via.placeholder.com/150x225'">
                        <div class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 flex flex-col justify-end p-3 transition">
                            <span class="text-[10px] text-letterboxd-blue font-bold uppercase tracking-widest">${book.owner}</span>
                            <p class="text-white text-xs font-bold leading-tight">${book.title}</p>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;

    return container;
}