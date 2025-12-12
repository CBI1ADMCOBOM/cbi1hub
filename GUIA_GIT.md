# Guia Rápido de Comandos Git - CBI-1 Hub

Este documento serve como referência para os principais comandos Git utilizados na manutenção deste projeto.

## 🚀 Fluxo de Trabalho Básico (Dia a Dia)

Sempre que você fizer alterações no código e quiser salvar no GitHub, siga esta sequência:

### 1. Verificar o Status
Veja quais arquivos foram modificados desde o último salvamento.
```bash
git status
```

### 2. Adicionar as Alterações
Prepare os arquivos modificados para serem salvos. O ponto (`.`) adiciona tudo na pasta atual.
```bash
git add .
```

### 3. Criar um Commit (Salvar)
Crie um "pacote" com as suas alterações e dê um nome descritivo.
**Importante:** Use mensagens claras sobre o que foi feito (ex: "Corrigi erro no login", "Adicionei botão de voltar").
```bash
git commit -m "Escreva aqui a descrição da alteração"
```

### 4. Enviar para o GitHub (Push)
Envie o seu commit para o servidor (nuvem).
```bash
git push
```

---

## 🔄 Outros Comandos Úteis

### Baixar Atualizações (Pull)
Se houver alterações no repositório remoto (GitHub) que você não tem no seu computador (por exemplo, editou direto no site ou em outro PC), use este comando para atualizar seu código local.
```bash
git pull
```

### Ver o Histórico
Veja a lista dos últimos commits feitos.
```bash
git log
```
(Pressione `q` para sair da visualização do log)

### Descartar alterações em um arquivo (Antes de commitar)
Se você mexeu em um arquivo e quer voltar para como ele estava no último commit (cancelar edições locais):
```bash
git checkout -- nome_do_arquivo.ext
```
Ou para descartar **todas** as alterações locais atuais (cuidado!):
```bash
git checkout .
```

---
**Dica:** Sempre execute os comandos dentro da pasta do projeto (`cbi1hub`).
