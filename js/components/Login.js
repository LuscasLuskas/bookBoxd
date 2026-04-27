export function Login(onLoginSuccess) {
    const container = document.createElement('div');
    container.className = 'flex-grow flex items-center justify-center';
    
    container.innerHTML = `
        <div class="bg-letterboxd-panel p-8 rounded-lg shadow-2xl w-96 border border-gray-700">
            <div class="text-center mb-8">
                <h1 class="text-3xl font-bold text-white tracking-tighter"><i class="fas fa-book-open text-letterboxd-green"></i> BookBoxd</h1>
                <p class="text-sm mt-2 text-gray-400">Registre suas leituras.</p>
            </div>
            <form id="login-form">
                <div class="mb-4">
                    <label class="block text-xs font-bold mb-2 text-gray-400 uppercase">Usuário</label>
                    <input type="text" id="username" class="w-full p-2 bg-gray-800 text-white rounded border border-gray-600 focus:border-letterboxd-blue focus:outline-none" required>
                </div>
                <div class="mb-6">
                    <label class="block text-xs font-bold mb-2 text-gray-400 uppercase">Senha</label>
                    <input type="password" id="password" class="w-full p-2 bg-gray-800 text-white rounded border border-gray-600 focus:border-letterboxd-blue focus:outline-none" required>
                </div>
                <button type="submit" class="w-full bg-letterboxd-green hover:bg-green-500 text-gray-900 font-bold py-2 px-4 rounded transition uppercase text-sm">
                    Entrar
                </button>
            </form>
        </div>
    `;

    // Interceta o envio do formulário e aciona a função de callback
    container.querySelector('#login-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const usernameValue = container.querySelector('#username').value.toLowerCase();
        onLoginSuccess(usernameValue);
    });

    return container;
}