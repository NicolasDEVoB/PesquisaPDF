/**
 * DocIntel - Lógica do Frontend (TypeScript)
 * Código simples e comentado para fácil manutenção.
 */

// Seleção de elementos do DOM com tipos explícitos
const formularioPergunta = document.getElementById('formulario-pergunta') as HTMLFormElement;
const campoPergunta = document.getElementById('campo-pergunta') as HTMLInputElement;
const historicoChat = document.getElementById('historico-chat') as HTMLDivElement;
const seletorArquivo = document.getElementById('arquivo-pdf') as HTMLInputElement;
const statusUpload = document.getElementById('status-upload') as HTMLDivElement;

/**
 * Adiciona uma bolha de mensagem ao chat
 */
function adicionarMensagem(texto: string, remetente: 'user' | 'bot', fontes?: any[]) {
    const divMensagem = document.createElement('div');
    divMensagem.className = `mensagem ${remetente}`;

    const avatar = remetente === 'user' ? '👤' : '🤖';
    
    // Se for o bot, processa o Markdown para HTML
    // Usamos 'any' aqui porque o marked vem via CDN global
    const textoFormatado = remetente === 'bot' 
        ? (window as any).marked.parse(texto) 
        : `<p>${texto}</p>`;

    let conteudoHtml = `<div class="avatar">${avatar}</div>
                        <div class="conteudo">
                            ${textoFormatado}`;
    
    // Se houver fontes (do bot), adiciona na mensagem
    if (fontes && fontes.length > 0) {
        conteudoHtml += `<div class="fontes">
            <strong>Fontes:</strong> ${fontes.map(f => `Pág. ${f.pagina}`).join(', ')}
        </div>`;
    }

    conteudoHtml += `</div>`;
    divMensagem.innerHTML = conteudoHtml;
    
    historicoChat.appendChild(divMensagem);
    
    // Rola para o final do chat
    historicoChat.scrollTop = historicoChat.scrollHeight;
}

/**
 * Função para enviar a pergunta ao backend
 */
async function enviarPergunta(event: Event) {
    event.preventDefault();
    
    const pergunta = campoPergunta.value.trim();
    if (!pergunta) return;

    // Limpa o campo e adiciona a pergunta do usuário na tela
    campoPergunta.value = '';
    adicionarMensagem(pergunta, 'user');

    // Adiciona uma mensagem de "digitando..." temporária
    const idDigitando = 'digitando-' + Date.now();
    const divDigitando = document.createElement('div');
    divDigitando.id = idDigitando;
    divDigitando.className = 'mensagem bot';
    divDigitando.innerHTML = `<div class="avatar">🤖</div><div class="conteudo">Pensando...</div>`;
    historicoChat.appendChild(divDigitando);

    try {
        // Faz a chamada para a API
        const response = await fetch(`/ask?question=${encodeURIComponent(pergunta)}`);
        const dados = await response.json();

        // Remove o "pensando..."
        document.getElementById(idDigitando)?.remove();

        if (dados.answer) {
            adicionarMensagem(dados.answer, 'bot');
        } else if (dados.resposta) {
            adicionarMensagem(dados.resposta, 'bot', dados.fontes);
        } else {
            adicionarMensagem("Desculpe, tive um erro ao processar sua pergunta.", 'bot');
        }
    } catch (erro) {
        console.error("Erro ao perguntar:", erro);
        document.getElementById(idDigitando)?.remove();
        adicionarMensagem("Erro de conexão com o servidor.", 'bot');
    }
}

/**
 * Função para lidar com o upload de arquivos
 */
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
            statusUpload.innerText = "✅ Arquivo enviado! Indexando...";
            adicionarMensagem(`O arquivo **${arquivo.name}** foi enviado com sucesso. Já pode fazer perguntas!`, 'bot');
        } else {
            statusUpload.innerText = `❌ Erro: ${resultado.detail || 'Falha no upload'}`;
        }
    } catch (erro) {
        console.error("Erro no upload:", erro);
        statusUpload.innerText = "❌ Erro de conexão no upload.";
    }
}

const botaoLimpar = document.getElementById('botao-limpar') as HTMLButtonElement;

/**
 * Função para limpar todos os dados do servidor e do chat
 */
async function limparDados() {
    if (!confirm("Tem certeza que deseja apagar todos os documentos e o histórico?")) {
        return;
    }

    try {
        const response = await fetch('/limpar', { method: 'POST' });
        const resultado = await response.json();

        if (response.ok) {
            // Limpa o chat na tela
            historicoChat.innerHTML = '';
            adicionarMensagem("Tudo foi limpo com sucesso! Pode enviar novos arquivos.", 'bot');
            statusUpload.innerText = '';
            alert("Sistema resetado com sucesso.");
        } else {
            alert("Erro ao limpar dados: " + resultado.detail);
        }
    } catch (erro) {
        console.error("Erro ao limpar:", erro);
        alert("Erro de conexão ao tentar limpar.");
    }
}

// Eventos
formularioPergunta.addEventListener('submit', enviarPergunta);
seletorArquivo.addEventListener('change', lidarComUpload);
botaoLimpar.addEventListener('click', limparDados);

// Esta linha abaixo avisa ao TypeScript que este arquivo é um módulo,
// o que resolve o erro de "variáveis duplicadas" caso o arquivo .js esteja na mesma pasta.
export {};
