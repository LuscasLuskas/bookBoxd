import { ClubService } from '../services/ClubService.js';

// Estado global deste módulo para lembrar se o admin já fez login nesta sessão
let isAdminLoggedIn = false;

export function Gerenciamento(currentUser, onUpdate) {
    const container = document.createElement('section');
    container.className = 'animate-fadeIn max-w-2xl mx-auto flex flex-col justify-center min-h-[60vh]';

    // Ecrã de Login da Gestão
    const renderLogin = () => {
        container.innerHTML = `
            <div class="bg-letterboxd-panel p-8 rounded-lg shadow-2xl border border-gray-700 w-full max-w-md mx-auto">
                <div class="text-center mb-8">
                    <i class="fas fa-lock text-3xl text-letterboxd-green mb-4"></i>
                    <h2 class="text-2xl font-bold text-white tracking-tight uppercase">Área de Gestão</h2>
                    <p class="text-xs mt-2 text-gray-400">Acesso restrito à administração do clube.</p>
                </div>
                <form id="admin-login-form">
                    <div class="mb-4">
                        <label class="block text-xs font-bold mb-2 text-gray-400 uppercase">Utilizador Gestor</label>
                        <input type="text" id="admin-user" class="w-full p-2 bg-gray-800 text-white rounded border border-gray-600 focus:border-letterboxd-blue outline-none" required>
                    </div>
                    <div class="mb-6">
                        <label class="block text-xs font-bold mb-2 text-gray-400 uppercase">Senha de Acesso</label>
                        <input type="password" id="admin-pass" class="w-full p-2 bg-gray-800 text-white rounded border border-gray-600 focus:border-letterboxd-blue outline-none" required>
                    </div>
                    <button type="submit" class="w-full bg-letterboxd-green hover:bg-green-500 text-gray-900 font-bold py-2 rounded uppercase text-sm transition">
                        Autenticar
                    </button>
                </form>
            </div>
        `;

        container.querySelector('#admin-login-form').addEventListener('submit', (e) => {
            e.preventDefault();
            const user = container.querySelector('#admin-user').value;
            const pass = container.querySelector('#admin-pass').value;

            // Credenciais de segurança da Gestão
            if (user === 'admin' && pass === 'clube2026') {
                isAdminLoggedIn = true;
                renderDashboard(); // Desbloqueia a área
            } else {
                alert('Credenciais incorretas. Acesso negado.');
            }
        });
    };

    // Painel de Gestão (após login correto)
    const renderDashboard = () => {
        container.className = 'space-y-12 animate-fadeIn max-w-2xl mx-auto';
        container.innerHTML = `
            <div class="border-b border-gray-700 pb-4 mb-8 flex justify-between items-end">
                <h2 class="text-2xl text-white font-bold tracking-tight uppercase">Gestão do Clube</h2>
                <span class="text-xs text-letterboxd-green font-bold px-2 py-1 bg-gray-800 rounded border border-letterboxd-green">
                    <i class="fas fa-check-circle mr-1"></i> Admin Autenticado
                </span>
            </div>

            <div class="bg-letterboxd-panel p-6 rounded-lg border border-letterboxd-green shadow-[0_0_15px_rgba(0,224,84,0.1)]">
                <h3 class="text-white font-bold mb-4 flex items-center gap-2">
                    <i class="fas fa-calendar-check text-letterboxd-green"></i> Adicionar Livro Oficial do Mês
                </h3>
                <p class="text-xs text-gray-400 mb-6">Este livro aparecerá no plano de leitura de todos os membros do clube.</p>
                
                <form id="form-livro-clube" class="grid grid-cols-2 gap-4">
                    <div class="col-span-2">
                        <label class="block text-xs font-bold text-gray-400 uppercase mb-1">Título do Livro</label>
                        <input type="text" name="title" required class="w-full bg-gray-800 text-white border border-gray-600 rounded p-2 text-sm outline-none focus:border-letterboxd-green">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-400 uppercase mb-1">Autor</label>
                        <input type="text" name="author" required class="w-full bg-gray-800 text-white border border-gray-600 rounded p-2 text-sm outline-none focus:border-letterboxd-green">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-400 uppercase mb-1">Link da Capa (URL)</label>
                        <input type="text" name="cover" placeholder="https://..." class="w-full bg-gray-800 text-white border border-gray-600 rounded p-2 text-sm outline-none focus:border-letterboxd-green">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-400 uppercase mb-1">Total de Páginas</label>
                        <input type="number" name="totalPages" required class="w-full bg-gray-800 text-white border border-gray-600 rounded p-2 text-sm outline-none focus:border-letterboxd-green">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-400 uppercase mb-1">Total de Capítulos</label>
                        <input type="number" name="totalChapters" required class="w-full bg-gray-800 text-white border border-gray-600 rounded p-2 text-sm outline-none focus:border-letterboxd-green">
                    </div>
                    <div class="col-span-2 mt-4">
                        <button type="submit" class="w-full bg-letterboxd-green hover:bg-green-500 text-gray-900 font-bold py-3 rounded text-xs uppercase transition duration-200 shadow-lg">
                            Definir como Livro do Mês
                        </button>
                    </div>
                </form>
            </div>
            
            <div class="text-center mt-8">
                <button id="btn-sair-admin" class="text-xs text-gray-500 hover:text-white uppercase font-bold tracking-widest transition">
                    <i class="fas fa-lock mr-1"></i> Trancar Gestão
                </button>
            </div>
        `;

        // Lógica assíncrona para adicionar o livro no Python
        container.querySelector('#form-livro-clube').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            // Constrói o objeto de dados a partir do formulário
            const bookData = {
                title: formData.get('title'),
                author: formData.get('author'),
                cover: formData.get('cover'),
                totalPages: parseInt(formData.get('totalPages')),
                totalChapters: parseInt(formData.get('totalChapters'))
            };
            
            // Chama a API do Backend
            await ClubService.addClubBook(bookData);
            
            alert(`"${bookData.title}" foi adicionado com sucesso ao Clube do Livro!`);
            e.target.reset(); // Limpa o formulário
        });

        // Lógica para trancar a sessão de admin
        container.querySelector('#btn-sair-admin').addEventListener('click', () => {
            isAdminLoggedIn = false;
            renderLogin();
        });
    };

    // Decide qual ecrã mostrar ao carregar a página
    if (isAdminLoggedIn) {
        renderDashboard();
    } else {
        renderLogin();
    }

    return container;
}