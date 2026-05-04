import { AuthService } from './services/AuthService.js';
import { Login } from './components/Login.js';
import { Dashboard } from './components/Dashboard.js';

const root = document.getElementById('app-root');
// ⚠️ CONFIGURAÇÃO GOOGLE OAUTH ⚠️
// Para ativar o login com Google, copie seu Client ID e defina abaixo.
const GOOGLE_CLIENT_ID = 'SUA_GOOGLE_CLIENT_ID_AQUI.apps.googleusercontent.com';

function mountLogin() {
    root.innerHTML = '';
    const loginComponent = Login(handleLoginAttempt, handleGoogleSuccess, GOOGLE_CLIENT_ID);
    root.appendChild(loginComponent);
}

// Traditional login with username
async function handleLoginAttempt(username) {
    const userData = await AuthService.getUser(username);
    
    if (userData) {
        mountDashboard(userData);
    } else {
        alert('Utilizador não encontrado! Tente "outro"');
    }
}

// Google Sign-In callback
async function handleGoogleSuccess(response) {
    const userData = await AuthService.loginWithGoogle(response);
    
    if (userData) {
        mountDashboard(userData);
    } else {
        alert('Erro ao fazer login com Google. Tente novamente.');
    }
}

async function mountDashboard(userData) {
    root.innerHTML = '<div class="text-white text-center mt-10">A carregar interface...</div>';
    // O Dashboard agora devolve uma Promise, por isso usamos await
    const dashboardElement = await Dashboard(userData, handleLogout);
    root.innerHTML = '';
    root.appendChild(dashboardElement);
}

function handleLogout() {
    AuthService.clearAuth();
    mountLogin();
}

// Check if user is already authenticated on page load
async function initializeApp() {
    const isAuthenticated = AuthService.isAuthenticated();
    
    if (isAuthenticated) {
        const userData = await AuthService.getMe();
        if (userData) {
            mountDashboard(userData);
            return;
        } else {
            // Token was invalid, clear auth and show login
            AuthService.clearAuth();
        }
    }
    
    mountLogin();
}

// Initialize the app
initializeApp();