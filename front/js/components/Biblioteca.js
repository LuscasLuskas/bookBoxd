import { ClubService } from '../services/ClubService.js';
import { ExternalService } from '../services/ExternalService.js';

export async function Biblioteca() {
    const container = document.createElement('section');
    container.className = 'space-y-8 animate-fadeIn';
    
    // CHAMADAS ASSÍNCRONAS AO BACKEND (PYTHON)
    const clubBooks = await ClubService.getClubBooks();
    const externalBooks = await ExternalService.getExternalBooks();
    
    // Junta todos os livros num só array para renderizar
    const allBooks = [...clubBooks, ...externalBooks];

    container.innerHTML = `
        <div class="flex justify-between items-center border-b border-gray-700 pb-4">
            <h2 class="text-2xl text-white font-bold tracking-tight">BIBLIOTECA CENTRAL</h2>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-6">
            ${allBooks.map(book => `
                <div class="group cursor-pointer">
                    <div class="relative aspect-[2/3] overflow-hidden rounded border border-gray-700 group-hover:border-letterboxd-green transition">
                        <img 
                            src="${book.cover}" 
                            class="w-full h-full object-cover group-hover:scale-110 transition duration-300" 
                            onerror="this.onerror=null; this.src='https://placehold.co/150x225/2c3440/9ab?text=Sem+Capa'"
                        >
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