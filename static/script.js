document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const btn = document.querySelector('.btn-login');
    const originalText = btn.textContent;

    btn.textContent = 'Entrando...';
    btn.disabled = true;

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        const result = await response.json();

        if (result.success) {
            // Redirect to dashboard provided by backend
            window.location.href = result.redirect;
        } else {
            alert('Erro no login: ' + (result.error || 'Credenciais inválidas'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao conectar com o servidor.');
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
});

document.getElementById('forgot-password').addEventListener('click', (e) => {
    e.preventDefault();
    alert('Funcionalidade de recuperação de senha em desenvolvimento.');
});
