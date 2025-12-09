# Configuração de E-mail para Produção (VPS)

Atualmente, o sistema está configurado para **auto-confirmar** os e-mails dos usuários no cadastro, facilitando o desenvolvimento em rede local (sem acesso a SMTP externo).

Quando o sistema for migrado para a VPS (Produção), você deve seguir os passos abaixo para reativar a verificação de e-mail, garantindo a segurança e validade dos cadastros.

## 1. Configurar SMTP no Supabase

No painel do seu projeto Supabase:
1.  Acesse **Project Settings** -> **Authentication**.
2.  Em **SMTP Settings**, configure o provedor de e-mail que será usado para enviar os links de confirmação (ex: AWS SES, SendGrid, Resend, ou SMTP próprio).
    *   **Sender Email**: O e-mail que aparecerá como remetente (ex: `nao-responda@bombeiros.sp.gov.br`).
    *   **Sender Name**: Nome do remetente (ex: `Sistema RAIA`).

## 2. Habilitar Confirmação de E-mail

Ainda em **Authentication** -> **Providers** -> **Email**:
1.  Certifique-se de que **Enable Email Confirmations** está **ATIVADO**.
2.  (Opcional) Configure o tempo de validade do token.

## 3. Reverter o Código do Backend (`app.py`)

No arquivo `raia/app.py`, você precisará alterar a função `signup` para parar de usar o cliente Admin (que força a confirmação) e voltar a usar o cliente padrão (que respeita as regras do Supabase).

**Código Atual (Desenvolvimento - Auto Confirm):**
```python
# Usando cliente ADMIN para criar usuário já confirmado
response = supabase_admin.auth.admin.create_user({
    "email": email,
    "password": password,
    "email_confirm": True, # <--- Isso força a confirmação
    "user_metadata": metadata
})
```

**Código para Produção:**
```python
# Usando cliente PADRÃO (envia email de confirmação)
response = supabase.auth.sign_up({
    "email": email,
    "password": password,
    "options": {
        "data": metadata
    }
})
```

## 4. Fluxo de Usuário

Após reverter o código:
1.  O usuário fará o cadastro.
2.  O sistema retornará sucesso, mas avisará: "Verifique seu e-mail para ativar a conta".
3.  O usuário não conseguirá fazer login até clicar no link enviado por e-mail.
