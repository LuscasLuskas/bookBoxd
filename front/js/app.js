import { AuthService } from './services/AuthService.js';
import { Login } from './components/Login.js';
import { Dashboard } from './components/Dashboard.js';

const root = document.getElementById('app-root');

function mountLogin() {
    root.innerHTML = '';
    root.appendChild(Login(handleLoginAttempt));
}

// Agora a função é assíncrona
async function handleLoginAttempt(username) {
    const userData = await AuthService.getUser(username);
    
    if (userData) {
        mountDashboard(userData);
    } else {
        alert('Utilizador não encontrado! Tente "outro"');
    }
}

async function mountDashboard(userData) {
    root.innerHTML = '<div class="text-white text-center mt-10">A carregar interface...</div>';
    // O Dashboard agora devolve uma Promise, por isso usamos await
    const dashboardElement = await Dashboard(userData, mountLogin);
    root.innerHTML = '';
    root.appendChild(dashboardElement);
}

mountLogin();