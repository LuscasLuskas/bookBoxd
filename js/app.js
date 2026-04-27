import { StorageService } from './services/StorageService.js';
import { Login } from './components/Login.js';
import { Dashboard } from './components/Dashboard.js';

// Inicializa a base de dados
StorageService.init();

const root = document.getElementById('app-root');

function mountLogin() {
    root.innerHTML = '';
    root.appendChild(Login(handleLoginAttempt));
}

function handleLoginAttempt(username) {
    // AGORA USA O MÓDULO AUTH
    const userData = StorageService.auth.getUser(username);
    
    if (userData) {
        mountDashboard(userData);
    } else {
        alert('Utilizador não encontrado! Tente "lucas"');
    }
}

function mountDashboard(userData) {
    root.innerHTML = '';
    root.appendChild(Dashboard(userData, mountLogin));
}

mountLogin();