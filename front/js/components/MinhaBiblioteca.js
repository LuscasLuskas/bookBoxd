import { ExternalService } from '../services/ExternalService.js';

export async function MinhaBiblioteca(user, reRenderDashboard) {
    const container = document.createElement('section');
    container.className = 'space-y-12 animate-fadeIn max-w-6xl mx-auto';

    // Vai buscar apenas os livros externos (pessoais) para mostrar na estante do utilizador
    const allExternalBooks = await ExternalService.getExternalBooks();
    // Filtra para mostrar apenas os livros pertencentes ao utilizador atual
    const myBooks = allExternalBooks.filter(b => b.owner === user.name);

    container.innerHTML = `
        <div class="bg-letterboxd-panel p-6 rounded-lg border border-gray-700 shadow-xl mb-8">
            <h2 class="text-xl text-white font-bold tracking-tight mb-4"><i class="fas fa-search text-letterboxd-green mr-2"></i> Adicionar Livro (Google Books)</h2>
            <div class="flex gap-4 mb-6">
                <input type="text" id="search-input" placeholder="Pesquisar por título, autor ou ISBN..." class="flex-grow bg-gray-800 text-white border border-gray-600 rounded p-3 outline-none focus:border-letterboxd-green transition">
                <button id="search-btn" class="bg-letterboxd-green hover:bg-green-500 text-gray-900 font-bold py-3 px-6 rounded uppercase tracking-widest text-sm transition">
                    Procurar
                </button>
            </div>
            
            <div id="search-results" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-6 hidden">
                </div>
            <div id="search-loader" class="text-center hidden py-8">
                <i class="fas fa-spinner fa-spin text-letterboxd-green text-3xl"></i>
                <p class="text-xs text-gray-400 mt-2 uppercase tracking-widest">A explorar a base de dados...</p>
            </div>
        </div>

        <div class="border-b border-gray-700 pb-4 mb-6 flex justify-between items-end">
            <h2 class="text-2xl text-white font-bold tracking-tight uppercase">Minhas Leituras Pessoais</h2>
            <span class="text-xs text-letterboxd-green font-bold bg-gray-800 px-2 py-1 rounded border border-gray-700">${myBooks.length} Livros</span>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-6">
            ${myBooks.length === 0 ? '<p class="text-gray-500 col-span-full">Ainda não tem livros pessoais. Adicione-os através da pesquisa acima!</p>' : ''}
            ${myBooks.map(book => `
                <div class="group cursor-pointer">
                    <div class="relative aspect-[2/3] overflow-hidden rounded border border-gray-700 group-hover:border-letterboxd-blue transition">
                        <img src="${book.cover}" class="w-full h-full object-cover group-hover:scale-110 transition duration-300" onerror="this.onerror=null; this.src='https://placehold.co/150x225/2c3440/9ab?text=Sem+Capa'">
                        <div class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 flex flex-col justify-end p-3 transition">
                            <p class="text-white text-xs font-bold leading-tight">${book.title}</p>
                            <p class="text-[10px] text-gray-400 mt-1">${book.totalPages} págs</p>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;

    // Lógica do Buscador
    const searchInput = container.querySelector('#search-input');
    const searchBtn = container.querySelector('#search-btn');
    const searchResults = container.querySelector('#search-results');
    const searchLoader = container.querySelector('#search-loader');

    searchBtn.addEventListener('click', async () => {
        const query = searchInput.value.trim();
        if (!query) return;

        // Limpa resultados e mostra o loader
        searchResults.innerHTML = '';
        searchResults.classList.add('hidden');
        searchLoader.classList.remove('hidden');

        // Chama a API do Backend
        const results = await ExternalService.searchGoogleBooks(query);
        
        searchLoader.classList.add('hidden');
        searchResults.classList.remove('hidden');

        if (results.length === 0) {
            searchResults.innerHTML = '<p class="text-gray-400 col-span-full text-center py-4">Nenhum livro encontrado.</p>';
            return;
        }

        // Desenha os resultados
        searchResults.innerHTML = results.map(book => `
            <div class="flex flex-col h-full bg-gray-800 rounded border border-gray-700 overflow-hidden group">
                <div class="relative aspect-[2/3] w-full bg-gray-900 border-b border-gray-700">
                    <img src="${book.cover}" class="absolute inset-0 w-full h-full object-cover">
                </div>
                <div class="p-3 flex flex-col flex-grow justify-between">
                    <div>
                        <h4 class="text-white text-xs font-bold line-clamp-2 leading-tight" title="${book.title}">${book.title}</h4>
                        <p class="text-[10px] text-letterboxd-blue mt-1 truncate" title="${book.author}">${book.author}</p>
                    </div>
                    <button class="add-book-btn mt-3 w-full bg-gray-700 hover:bg-letterboxd-blue hover:text-white text-gray-300 text-[10px] font-bold py-1.5 rounded uppercase tracking-wider transition"
                            data-title="${encodeURIComponent(book.title)}"
                            data-author="${encodeURIComponent(book.author)}"
                            data-cover="${encodeURIComponent(book.cover)}"
                            data-pages="${book.totalPages}">
                        + Adicionar
                    </button>
                </div>
            </div>
        `).join('');

        // Lógica para o botão "+ Adicionar" de cada resultado
        container.querySelectorAll('.add-book-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const bookData = {
                    title: decodeURIComponent(e.target.getAttribute('data-title')),
                    author: decodeURIComponent(e.target.getAttribute('data-author')),
                    cover: decodeURIComponent(e.target.getAttribute('data-cover')),
                    totalPages: parseInt(e.target.getAttribute('data-pages')) || 200,
                    owner: user.name // Associa o livro ao utilizador logado!
                };
                
                // Grava no backend e recarrega o ecrã
                e.target.innerHTML = '<i class="fas fa-check"></i> Adicionado';
                e.target.classList.replace('bg-gray-700', 'bg-letterboxd-green');
                e.target.classList.replace('hover:bg-letterboxd-blue', 'text-gray-900');
                
                await ExternalService.addPersonalBook(bookData);
                setTimeout(() => reRenderDashboard('minhabiblio'), 800); // Dá tempo para ver o check verde
            });
        });
    });

    // Permite pesquisar pressionando "Enter"
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchBtn.click();
    });

    return container;
}