/**
 * DocIntel - Lógica do Frontend (JavaScript compilado)
 * Este arquivo é a versão executável do script.ts.
 */

const formularioPergunta = document.getElementById('formulario-pergunta');
const campoPergunta = document.getElementById('campo-pergunta');
const historicoChat = document.getElementById('historico-chat');
const seletorArquivo = document.getElementById('arquivo-pdf');
const statusUpload = document.getElementById('status-upload');

function adicionarMensagem(texto, remetente, fontes) {
    const divMensagem = document.createElement('div');
    divMensagem.className = `mensagem ${remetente}`;

    const avatar = remetente === 'user' ? '👤' : '🤖';
    
    // Processa o Markdown se for o bot
    const textoFormatado = remetente === 'bot' ? marked.parse(texto) : `<p>${texto}</p>`;

    let conteudoHtml = `<div class="avatar">${avatar}</div>
                        <div class="conteudo">
                            ${textoFormatado}`;
    
    if (fontes && fontes.length > 0) {
        conteudoHtml += `<div class="fontes">
            <strong>Fontes:</strong> ${fontes.map(f => `Pág. ${f.pagina || '?'}`).join(', ')}
        </div>`;
    }

    conteudoHtml += `</div>`;
    divMensagem.innerHTML = conteudoHtml;
    
    historicoChat.appendChild(divMensagem);
    historicoChat.scrollTop = historicoChat.scrollHeight;
}

async function enviarPergunta(event) {
    event.preventDefault();
    
    const pergunta = campoPergunta.value.trim();
    if (!pergunta) return;

    campoPergunta.value = '';
    adicionarMensagem(pergunta, 'user');

    const idDigitando = 'digitando-' + Date.now();
    const divDigitando = document.createElement('div');
    divDigitando.id = idDigitando;
    divDigitando.className = 'mensagem bot';
    divDigitando.innerHTML = `<div class="avatar">🤖</div><div class="conteudo">Pensando...</div>`;
    historicoChat.appendChild(divDigitando);

    try {
        const response = await fetch(`/ask?question=${encodeURIComponent(pergunta)}`);
        const dados = await response.json();

        const elemDigitando = document.getElementById(idDigitando);
        if (elemDigitando) elemDigitando.remove();

        if (dados.resposta) {
            adicionarMensagem(dados.resposta, 'bot', dados.fontes);
        } else if (dados.answer) {
            adicionarMensagem(dados.answer, 'bot');
        } else {
            adicionarMensagem("Não consegui encontrar uma resposta para isso.", 'bot');
        }
    } catch (erro) {
        console.error("Erro ao perguntar:", erro);
        const elemDigitando = document.getElementById(idDigitando);
        if (elemDigitando) elemDigitando.remove();
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
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const resultado = await response.json();
        
        if (response.ok) {
            statusUpload.innerText = "✅ Arquivo enviado! Processando...";
            adicionarMensagem(`O arquivo **${arquivo.name}** foi enviado. O sistema está lendo e aprendendo o conteúdo agora!`, 'bot');
        } else {
            statusUpload.innerText = `❌ Erro: ${resultado.detail || 'Falha no upload'}`;
        }
    } catch (erro) {
        console.error("Erro no upload:", erro);
        statusUpload.innerText = "❌ Erro de conexão no upload.";
    }
}

if (formularioPergunta) formularioPergunta.addEventListener('submit', enviarPergunta);
if (seletorArquivo) seletorArquivo.addEventListener('change', lidarComUpload);
