const formulario = document.getElementById('formulario-pergunta');
const campo = document.getElementById('campo-pergunta');
const botaoEnviar = document.getElementById('botao-enviar');
const historico = document.getElementById('historico-chat');
const seletorArquivo = document.getElementById('arquivo-pdf');
const statusUpload = document.getElementById('status-upload');
const btnMenu = document.getElementById('btnMenu');
const sidebar = document.getElementById('sidebar');
const sidebarOverlay = document.getElementById('sidebarOverlay');
const sidebarClose = document.getElementById('sidebarClose');
const btnNovoChat = document.getElementById('novoChat');

function toggleSidebar(open) {
    sidebar.classList.toggle('open', open);
    sidebarOverlay.classList.toggle('open', open);
}

if (btnMenu) btnMenu.addEventListener('click', () => toggleSidebar(true));
if (sidebarOverlay) sidebarOverlay.addEventListener('click', () => toggleSidebar(false));
if (sidebarClose) sidebarClose.addEventListener('click', () => toggleSidebar(false));

if (btnNovoChat) btnNovoChat.addEventListener('click', () => {
    historico.innerHTML = '';
    historico.appendChild(criarTelaBoasVindas());
    if (window.innerWidth <= 768) toggleSidebar(false);
});

function criarTelaBoasVindas() {
    const div = document.createElement('div');
    div.className = 'chat-welcome';
    div.innerHTML = `
        <div class="welcome-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
        </div>
        <h2>O que você quer saber?</h2>
        <p>Faça upload de um PDF e pergunte qualquer coisa sobre o conteúdo.</p>
        <div class="welcome-dicas">
            <div class="dica" onclick="document.getElementById('campo-pergunta').value = 'Qual é o assunto principal do documento?';">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                Qual é o assunto principal?
            </div>
            <div class="dica" onclick="document.getElementById('campo-pergunta').value = 'Faça um resumo do documento';">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
                Faça um resumo
            </div>
            <div class="dica" onclick="document.getElementById('campo-pergunta').value = 'Quais os principais tópicos abordados?';">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 6h16M4 12h16M4 18h16"/></svg>
                Quais os principais tópicos?
            </div>
        </div>
    `;
    return div;
}

campo.addEventListener('input', () => {
    botaoEnviar.disabled = !campo.value.trim();
});

function adicionarMensagem(texto, remetente, fontes) {
    const div = document.createElement('div');
    div.className = `mensagem ${remetente}`;

    const avatar = remetente === 'user' ? 'U' : 'D';
    const textoFormatado = remetente === 'bot' ? marked.parse(texto) : `<p>${texto.replace(/\n/g, '<br>')}</p>`;

    let html = `<div class="avatar">${avatar}</div><div class="conteudo">${textoFormatado}`;

    if (fontes && fontes.length > 0) {
        html += `<div class="fontes"><strong>Fontes:</strong> ${fontes.map(f => `Pág. ${f.pagina || '?'}`).join(', ')}</div>`;
    }

    html += `</div>`;
    div.innerHTML = html;
    historico.appendChild(div);
    historico.scrollTop = historico.scrollHeight;
}

function mostrarDigitando() {
    const div = document.createElement('div');
    div.id = 'indicador-digitando';
    div.className = 'mensagem bot';
    div.innerHTML = `<div class="avatar">D</div><div class="conteudo"><div class="typing-indicator"><span></span><span></span><span></span></div></div>`;
    historico.appendChild(div);
    historico.scrollTop = historico.scrollHeight;
}

function removerDigitando() {
    const el = document.getElementById('indicador-digitando');
    if (el) el.remove();
}

async function enviarPergunta(event) {
    event.preventDefault();
    const pergunta = campo.value.trim();
    if (!pergunta) return;

    campo.value = '';
    botaoEnviar.disabled = true;

    adicionarMensagem(pergunta, 'user');
    mostrarDigitando();

    try {
        const response = await fetch(`/ask?question=${encodeURIComponent(pergunta)}`);
        const dados = await response.json();
        removerDigitando();

        if (dados.resposta) {
            adicionarMensagem(dados.resposta, 'bot', dados.fontes);
        } else if (dados.answer) {
            adicionarMensagem(dados.answer, 'bot');
        } else {
            adicionarMensagem("Não consegui encontrar uma resposta para isso.", 'bot');
        }
    } catch (erro) {
        console.error("Erro ao perguntar:", erro);
        removerDigitando();
        adicionarMensagem("Erro de conexão com o servidor.", 'bot');
    }
}

async function lidarComUpload() {
    const arquivos = seletorArquivo.files;
    if (!arquivos || arquivos.length === 0) return;

    const arquivo = arquivos[0];
    statusUpload.innerText = `Enviando ${arquivo.name}...`;

    const formData = new FormData();
    formData.append('file', arquivo);

    try {
        const response = await fetch('/upload', { method: 'POST', body: formData });
        const resultado = await response.json();

        if (response.ok) {
            statusUpload.innerText = "PDF enviado! Processando...";
            adicionarMensagem(`**${arquivo.name}** enviado. O sistema está processando o documento agora.`, 'bot');
        } else {
            statusUpload.innerText = `Erro: ${resultado.detail || 'Falha no upload'}`;
        }
    } catch (erro) {
        console.error("Erro no upload:", erro);
        statusUpload.innerText = "Erro de conexão no upload.";
    }
}

async function limparDados() {
    if (!confirm("Tem certeza que deseja apagar todos os documentos e o histórico?")) return;

    try {
        const response = await fetch('/limpar', { method: 'POST' });
        const resultado = await response.json();

        if (response.ok) {
            historico.innerHTML = '';
            historico.appendChild(criarTelaBoasVindas());
            statusUpload.innerText = '';
        } else {
            alert("Erro ao limpar dados: " + resultado.detail);
        }
    } catch (erro) {
        console.error("Erro ao limpar:", erro);
        alert("Erro de conexão ao tentar limpar.");
    }
}

if (formulario) formulario.addEventListener('submit', enviarPergunta);
if (seletorArquivo) seletorArquivo.addEventListener('change', lidarComUpload);
if (document.getElementById('botao-limpar')) {
    document.getElementById('botao-limpar').addEventListener('click', limparDados);
}
