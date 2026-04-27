import { StorageService } from '../services/StorageService.js';
import { ReadingController } from '../utils/ReadingController.js';
import { Biblioteca } from './Biblioteca.js';
import { Gerenciamento } from './Gerenciamento.js'; // Importação nova

export function Dashboard(user, onLogout) {
    const container = document.createElement('div');
    container.className = 'flex-grow flex flex-col w-full';

    // Para redesenhar a interface se a foto mudar
    const reRender = () => {
        const updatedUser = StorageService.auth.getUser(user.username);
        const parent = container.parentNode;
        if (parent) {
            parent.innerHTML = '';
            parent.appendChild(Dashboard(updatedUser, onLogout));
        }
    };

    container.innerHTML = `
        <header class="bg-letterboxd-panel border-b border-gray-700 p-4 sticky top-0 z-50">
            <div class="max-w-6xl mx-auto flex justify-between items-center">
                <div class="flex items-center gap-8">
                    <h1 class="text-2xl font-bold text-white tracking-tighter">
                        <i class="fas fa-book-open text-letterboxd-green"></i> BookBoxd
                    </h1>
                    <nav class="hidden md:flex gap-6 text-[10px] font-bold uppercase tracking-widest text-gray-400">
                        <button id="nav-home" class="hover:text-white transition">Início</button>
                        <button id="nav-biblioteca" class="hover:text-white transition">Biblioteca Central</button>
                        <button id="nav-gestao" class="hover:text-white transition">Gestão</button>
                    </nav>
                </div>
                <div class="flex items-center space-x-3">
                    <img src="${user.photo}" class="w-8 h-8 rounded-full border border-gray-600 object-cover">
                    <span class="text-white text-xs font-bold hidden sm:inline">${user.username}</span>
                    <button id="logout-btn" class="ml-2 text-gray-500 hover:text-red-400"><i class="fas fa-sign-out-alt"></i></button>
                </div>
            </div>
        </header>
        <main id="main-content" class="max-w-6xl mx-auto w-full p-6 space-y-12">
            </main>
    `;

    const mainContent = container.querySelector('#main-content');
    const navButtons = {
        home: container.querySelector('#nav-home'),
        biblio: container.querySelector('#nav-biblioteca'),
        gestao: container.querySelector('#nav-gestao')
    };

    container.querySelector('#logout-btn').addEventListener('click', onLogout);

    function setActiveNav(activeKey) {
        Object.values(navButtons).forEach(btn => btn.classList.remove('text-white', 'border-b-2', 'border-letterboxd-green', 'pb-1'));
        navButtons[activeKey].classList.add('text-white', 'border-b-2', 'border-letterboxd-green', 'pb-1');
    }

    function showHome() {
        setActiveNav('home');
        
        // AGORA USA O MÓDULO CLUB
        const clubBooks = StorageService.club.getClubBooks();
        const activeBook = clubBooks[0]; // Assume o primeiro do clube

        if (!activeBook) {
            mainContent.innerHTML = `<p class="text-white">Nenhum livro do clube ativo.</p>`;
            return;
        }

        const controlador = new ReadingController(activeBook.totalPages, activeBook.totalChapters, 30);
        controlador.unidadesConcluidas = activeBook.currentProgress;

        mainContent.innerHTML = `
            <section>
                <div class="flex justify-between items-end border-b border-gray-700 pb-2 mb-4">
                    <h2 class="text-xl text-white uppercase tracking-wider font-semibold">Leitura do Mês</h2>
                </div>
                <div class="bg-letterboxd-panel p-6 rounded-lg flex items-center space-x-6">
                    <div class="w-24 h-36 bg-gray-800 rounded book-cover flex-shrink-0 flex items-center justify-center relative overflow-hidden">
                        <img src="${activeBook.cover}" class="absolute inset-0 w-full h-full object-cover">
                    </div>
                    <div class="flex-grow">
                        <h3 class="text-2xl font-bold text-white mb-1">${activeBook.title}</h3>
                        <p class="text-letterboxd-blue text-sm mb-4">${activeBook.author}</p>
                        
                        <div class="flex items-center justify-between mb-2">
                            <span id="texto-meta" class="text-lg font-bold text-letterboxd-green">${controlador.obterTextoMeta()}</span>
                            <span id="texto-progresso" class="text-xs text-gray-400">${Math.round(controlador.calcularProgressoPercentual())}% concluído</span>
                        </div>
                        
                        <div class="w-full bg-gray-700 rounded-full h-2 mb-4">
                            <div id="barra-progresso" class="bg-letterboxd-green h-2 rounded-full transition-all duration-500" style="width: ${controlador.calcularProgressoPercentual()}%"></div>
                        </div>
                        
                        <button id="btn-marcar-leitura" class="bg-gray-700 hover:bg-letterboxd-green hover:text-gray-900 text-white font-bold py-2 px-4 rounded text-sm transition">
                            <i class="fas fa-check mr-2"></i> Marcar meta concluída
                        </button>
                    </div>
                </div>
            </section>
        `;

        const btnMarcar = mainContent.querySelector('#btn-marcar-leitura');
        btnMarcar.addEventListener('click', () => {
            controlador.registrarLeitura();
            // AGORA USA O MÓDULO CLUB
            StorageService.club.updateProgress(activeBook.id, controlador.unidadesConcluidas);
            showHome(); // Atualiza o ecrã para refletir a nova barra de progresso
        });
    }

    function showBiblioteca() {
        setActiveNav('biblio');
        mainContent.innerHTML = '';
        mainContent.appendChild(Biblioteca());
    }

    function showGestao() {
        setActiveNav('gestao');
        mainContent.innerHTML = '';
        mainContent.appendChild(Gerenciamento(user, reRender));
    }

    navButtons.home.addEventListener('click', showHome);
    navButtons.biblio.addEventListener('click', showBiblioteca);
    navButtons.gestao.addEventListener('click', showGestao);

    showHome(); // Inicia na aba Início

    return container;
}