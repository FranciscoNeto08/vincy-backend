(function(){


/* =====================================================
SESSÃO (via auth.js)
===================================================== */


const session = Auth.requireLogin(); // redireciona pra index.html se não estiver logado




/* =====================================================
USUÁRIO
===================================================== */


const userName = document.getElementById("userName");
const userEmail = document.getElementById("userEmail");


if(userName) userName.textContent = session.name || "Usuário";
if(userEmail) userEmail.textContent = session.email || "";




/* =====================================================
LOGOUT
===================================================== */


const logoutBtn = document.getElementById("logoutBtn");


if(logoutBtn){
    logoutBtn.onclick=function(){
        Auth.logout();
    };
}




/* =====================================================
ESTADO EM MEMÓRIA (preenchido a partir da API)
===================================================== */


let clientes = [];       // lista de clientes (da API)
let comandas = [];       // comandas abertas (da API)
let historico = [];      // comandas finalizadas (da API)
let atividades = [];     // tarefas (da API)
let campanhas = [];      // campanhas de marketing (da API)
let dashboardData = {};  // indicadores (da API)
let colaboradores = [];      // equipe cadastrada (da API)




/* =====================================================
ELEMENTOS
===================================================== */


const faturamentoHTML = document.getElementById("faturamento");
const clientesHTML = document.getElementById("clientesAtendidos");
const comandasHTML = document.getElementById("comandasAbertas");




/* =====================================================
NAVEGAÇÃO
===================================================== */

const ABA_ATIVA_KEY = "vincy_aba_ativa";

const botoes = document.querySelectorAll(
    ".side-btn:not(#logoutBtn)"
);

const paginas = document.querySelectorAll(
    ".page"
);


function abrirPagina(destino){

    if(!destino){
        return;
    }

    const paginaSelecionada =
    document.getElementById(destino);

    if(!paginaSelecionada){
        return;
    }

    botoes.forEach(botao=>{

        botao.classList.toggle(
            "active",
            botao.dataset.page === destino
        );

    });

    paginas.forEach(pagina=>{

        pagina.classList.toggle(
            "active",
            pagina.id === destino
        );

    });

    localStorage.setItem(
        ABA_ATIVA_KEY,
        destino
    );

    // Algumas áreas precisam ser redesenhadas depois de ficarem visíveis.
    if(destino === "financeiro"){
        setTimeout(()=>{
            if(typeof renderizarFinanceiroMensalCompleto === "function"){
                renderizarFinanceiroMensalCompleto();
            }else if(typeof renderizarGraficoFinanceiro === "function"){
                renderizarGraficoFinanceiro();
            }
        }, 0);
    }

    if(destino === "marketing"){
        setTimeout(()=>{
            if(typeof atualizarMarketingCompleto === "function"){
                atualizarMarketingCompleto();
            }
        }, 0);
    }

    // Configurações usa os dados já carregados em memória.
    // Isso evita uma nova requisição a cada clique na aba.
    if(destino === "configuracoes"){
        setTimeout(()=>{
            if(typeof preencherConfiguracoesUsuario === "function"){
                preencherConfiguracoesUsuario();
            }
        }, 0);
    }

}


botoes.forEach(botao=>{

    botao.addEventListener(
        "click",
        ()=>{

            abrirPagina(
                botao.dataset.page
            );

        }
    );

});

/* =====================================================
   SIDEBAR / MENU HAMBÚRGUER
===================================================== */

const sidebar = document.getElementById("appSidebar");
const sidebarToggle = document.getElementById("sidebarToggle");
const sidebarBackdrop = document.getElementById("sidebarBackdrop");


function atualizarAcessibilidadeSidebar(){

    if(!sidebarToggle) return;

    const aberto =
        document.body.classList.contains("sidebar-open");

    sidebarToggle.setAttribute(
        "aria-expanded",
        String(aberto)
    );

    sidebarToggle.setAttribute(
        "aria-label",
        aberto
            ? "Fechar menu"
            : "Abrir menu"
    );
}


function fecharSidebar(){

    document.body.classList.remove("sidebar-open");

    atualizarAcessibilidadeSidebar();
}


function alternarSidebar(){

    document.body.classList.toggle("sidebar-open");

    atualizarAcessibilidadeSidebar();

    setTimeout(()=>{

        if(
            document.getElementById("financeiro")?.classList.contains("active") &&
            typeof renderizarGraficoFinanceiro === "function"
        ){
            renderizarGraficoFinanceiro();
        }

    }, 260);
}


/*
  O menu SEMPRE começa fechado.
  Não usamos mais sidebar-collapsed nem estado salvo.
*/
document.body.classList.remove(
    "sidebar-open",
    "sidebar-collapsed"
);


if(sidebarToggle){

    sidebarToggle.addEventListener(
        "click",
        evento=>{

            evento.preventDefault();
            evento.stopPropagation();

            alternarSidebar();
        }
    );
}


if(sidebarBackdrop){

    sidebarBackdrop.addEventListener(
        "click",
        fecharSidebar
    );
}


/*
  Ao escolher uma página, navega e fecha o drawer.
*/
botoes.forEach(botao=>{

    botao.addEventListener(
        "click",
        ()=>{
            fecharSidebar();
        }
    );
});


document.addEventListener(
    "keydown",
    evento=>{

        if(
            evento.key === "Escape" &&
            document.body.classList.contains("sidebar-open")
        ){
            fecharSidebar();
        }
    }
);


/*
  Não fecha no resize automaticamente.
  O usuário controla abrir/fechar exclusivamente pelo hambúrguer,
  backdrop, item do menu ou ESC.
*/
window.addEventListener(
    "resize",
    atualizarAcessibilidadeSidebar
);


atualizarAcessibilidadeSidebar();


/* =====================================================
NOTIFICAÇÕES BONITAS (substitui os alerts do navegador)
===================================================== */

function garantirEstiloNotificacoes(){

    if(document.getElementById("vincyToastStyles")) return;

    const style = document.createElement("style");
    style.id = "vincyToastStyles";

    style.textContent = `
        #vincyToastContainer{
            position:fixed;
            top:24px;
            right:24px;
            z-index:999999;
            display:flex;
            flex-direction:column;
            gap:12px;
            pointer-events:none;
        }

        .vincy-toast{
            width:min(390px, calc(100vw - 32px));
            display:flex;
            align-items:flex-start;
            gap:12px;
            padding:15px 17px;
            border-radius:14px;
            border:1px solid rgba(139,92,246,.22);
            background:rgba(255,255,255,.97);
            color:#1f1f2b;
            box-shadow:0 18px 50px rgba(31,24,56,.18);
            backdrop-filter:blur(12px);
            opacity:0;
            transform:translateY(-12px) scale(.98);
            transition:opacity .22s ease, transform .22s ease;
            pointer-events:auto;
            overflow:hidden;
            position:relative;
            font-family:Inter, "Segoe UI", Arial, sans-serif;
        }

        [data-theme="escuro"] .vincy-toast{
            background:rgba(30,30,36,.97);
            color:#f7f7fb;
            border-color:rgba(167,139,250,.28);
            box-shadow:0 18px 50px rgba(0,0,0,.38);
        }

        .vincy-toast.show{
            opacity:1;
            transform:translateY(0) scale(1);
        }

        .vincy-toast.hide{
            opacity:0;
            transform:translateY(-8px) scale(.98);
        }

        .vincy-toast-icon{
            width:34px;
            height:34px;
            flex:0 0 34px;
            border-radius:10px;
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:17px;
            font-weight:800;
        }

        .vincy-toast-content{
            flex:1;
            min-width:0;
        }

        .vincy-toast-title{
            margin:0 0 3px;
            font-size:.92rem;
            font-weight:800;
        }

        .vincy-toast-message{
            margin:0;
            font-size:.84rem;
            line-height:1.45;
            color:#696979;
            word-break:break-word;
        }

        [data-theme="escuro"] .vincy-toast-message{
            color:#b9b9c4;
        }

        .vincy-toast-close{
            border:0;
            background:transparent;
            color:inherit;
            opacity:.45;
            cursor:pointer;
            font-size:18px;
            line-height:1;
            padding:2px;
        }

        .vincy-toast-close:hover{
            opacity:.8;
        }

        .vincy-toast.success .vincy-toast-icon{
            color:#18794e;
            background:#e9f8f0;
        }

        .vincy-toast.error .vincy-toast-icon{
            color:#c23636;
            background:#fff0f0;
        }

        .vincy-toast.warning .vincy-toast-icon{
            color:#9a6500;
            background:#fff7df;
        }

        .vincy-toast.info .vincy-toast-icon{
            color:#6d3bd1;
            background:#f1ebff;
        }

        [data-theme="escuro"] .vincy-toast.success .vincy-toast-icon{
            color:#6ee7a8;
            background:rgba(47,143,87,.18);
        }

        [data-theme="escuro"] .vincy-toast.error .vincy-toast-icon{
            color:#ff9292;
            background:rgba(195,75,75,.18);
        }

        [data-theme="escuro"] .vincy-toast.warning .vincy-toast-icon{
            color:#ffd26f;
            background:rgba(176,141,87,.18);
        }

        [data-theme="escuro"] .vincy-toast.info .vincy-toast-icon{
            color:#c4b5fd;
            background:rgba(139,92,246,.18);
        }

        .vincy-toast::after{
            content:"";
            position:absolute;
            left:0;
            bottom:0;
            height:3px;
            width:100%;
            background:#8b5cf6;
            transform-origin:left;
            animation:vincyToastTime 3.8s linear forwards;
        }

        .vincy-toast.success::after{ background:#2f8f57; }
        .vincy-toast.error::after{ background:#c34b4b; }
        .vincy-toast.warning::after{ background:#b08d57; }

        @keyframes vincyToastTime{
            from{ transform:scaleX(1); }
            to{ transform:scaleX(0); }
        }

        @media(max-width:600px){
            #vincyToastContainer{
                top:16px;
                left:16px;
                right:16px;
            }

            .vincy-toast{
                width:100%;
            }
        }
    `;

    document.head.appendChild(style);
}


function mostrarNotificacao(mensagem, tipo="info", titulo=""){

    garantirEstiloNotificacoes();

    let container = document.getElementById("vincyToastContainer");

    if(!container){
        container = document.createElement("div");
        container.id = "vincyToastContainer";
        document.body.appendChild(container);
    }

    const configuracoes = {
        success: { icon:"✓", title:"Tudo certo" },
        error:   { icon:"!", title:"Não foi possível concluir" },
        warning: { icon:"!", title:"Atenção" },
        info:    { icon:"i", title:"Vincy" }
    };

    const config = configuracoes[tipo] || configuracoes.info;

    const toast = document.createElement("div");
    toast.className = `vincy-toast ${tipo}`;

    const icon = document.createElement("div");
    icon.className = "vincy-toast-icon";
    icon.textContent = config.icon;

    const content = document.createElement("div");
    content.className = "vincy-toast-content";

    const titleEl = document.createElement("p");
    titleEl.className = "vincy-toast-title";
    titleEl.textContent = titulo || config.title;

    const messageEl = document.createElement("p");
    messageEl.className = "vincy-toast-message";
    messageEl.textContent = String(mensagem || "");

    const close = document.createElement("button");
    close.type = "button";
    close.className = "vincy-toast-close";
    close.setAttribute("aria-label", "Fechar");
    close.textContent = "×";

    content.appendChild(titleEl);
    content.appendChild(messageEl);

    toast.appendChild(icon);
    toast.appendChild(content);
    toast.appendChild(close);

    container.appendChild(toast);

    requestAnimationFrame(()=>{
        toast.classList.add("show");
    });

    let timer;

    const remover = ()=>{
        clearTimeout(timer);
        toast.classList.remove("show");
        toast.classList.add("hide");

        setTimeout(()=>{
            toast.remove();

            if(container && !container.children.length){
                container.remove();
            }
        }, 230);
    };

    close.onclick = remover;

    timer = setTimeout(remover, 3800);
}


/* Mantém os alert(...) já existentes no sistema,
   mas exibe todos como notificações elegantes. */
window.alert = function(mensagem){

    const texto = String(mensagem || "");
    const minusculo = texto.toLowerCase();

    let tipo = "info";

    if(
        minusculo.includes("sucesso") ||
        minusculo.includes("cadastrado") ||
        minusculo.includes("criado") ||
        minusculo.includes("atualizado") ||
        minusculo.includes("alterada") ||
        minusculo.includes("enviado")
    ){
        tipo = "success";
    }
    else if(
        minusculo.includes("digite") ||
        minusculo.includes("preencha") ||
        minusculo.includes("selecione") ||
        minusculo.includes("informe") ||
        minusculo.includes("adicione") ||
        minusculo.includes("escreva")
    ){
        tipo = "warning";
    }

    mostrarNotificacao(texto, tipo);
};



/* =====================================================
FUNÇÕES AUXILIARES
===================================================== */


function dinheiro(valor){
    return Number(valor||0).toLocaleString("pt-BR",{style:"currency",currency:"BRL"});
}


function formatarData(isoString){
    if(!isoString) return "";
    return new Date(isoString).toLocaleDateString("pt-BR");
}


function formatarHora(isoString){
    if(!isoString) return "";
    return new Date(isoString).toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"});
}


function mostrarErro(err){

    console.error(err);

    mostrarNotificacao(
        err && err.message
            ? err.message
            : "Ocorreu um erro inesperado.",
        "error"
    );
}





/* =====================================================
   PERFORMANCE / PROTEÇÃO CONTRA CLIQUES DUPLOS
===================================================== */

const acoesEmAndamento = new Set();


async function executarComTrava(
    chave,
    botao,
    textoCarregando,
    acao
){

    if(acoesEmAndamento.has(chave)){
        return null;
    }

    acoesEmAndamento.add(chave);

    const textoOriginal =
        botao ? botao.textContent : "";

    if(botao){
        botao.disabled = true;
        botao.classList.add("is-loading");

        if(textoCarregando){
            botao.textContent = textoCarregando;
        }
    }

    try{
        return await acao();
    }finally{

        acoesEmAndamento.delete(chave);

        if(botao){
            botao.disabled = false;
            botao.classList.remove("is-loading");
            botao.textContent = textoOriginal;
        }
    }
}


async function atualizarSomenteComandas(){

    comandas =
        await Api.get(
            "/comandas?status_filter=aberta"
        );

    renderizarComandas();

    if(comandasHTML){
        comandasHTML.textContent = comandas.length;
    }
}


async function atualizarSomenteClientes(){

    clientes = await Api.get("/clients");

    renderizarClientes();
    popularSelectClientes();
    popularSelectClientesAgenda();
}


async function atualizarHistoricoFinanceiro(){

    const resultados =
        await Promise.allSettled([
            Api.get(
                "/comandas?status_filter=finalizada"
            ),
            Api.get("/finance"),
            Api.get("/dashboard")
        ]);

    if(resultados[0].status === "fulfilled"){
        historico = resultados[0].value;
    }

    if(resultados[1].status === "fulfilled"){
        lancamentos = resultados[1].value;
    }

    if(resultados[2].status === "fulfilled"){
        dashboardData = resultados[2].value;
    }

    renderizarHistorico();
    renderizarClientes();
    gerarRelatorios();
    renderizarLancamentos();

    if(typeof renderizarFinanceiroMensalCompleto === "function"){
        renderizarFinanceiroMensalCompleto();
    }else{
        renderizarGraficoFinanceiro();
    }

    const resumo =
        calcularResumoFinanceiro();

    aplicarValorFinanceiro(
        faturamentoHTML,
        resumo.total.liquido
    );

    if(clientesHTML){
        clientesHTML.textContent =
            dashboardData.total_clientes ??
            clientes.length;
    }

    if(comandasHTML){
        comandasHTML.textContent =
            dashboardData.comandas_abertas ??
            comandas.length;
    }
}


/* =====================================================
   SISTEMA DE CLIENTES
===================================================== */


const clienteCadastroNome = document.getElementById("clienteCadastroNome");
const clienteTelefone = document.getElementById("clienteTelefone");
const clienteEmailCadastro = document.getElementById("clienteEmailCadastro");
const clienteObservacao = document.getElementById("clienteObservacao");
const cadastrarClienteBtn = document.getElementById("cadastrarClienteBtn");
const listaClientes = document.getElementById("listaClientes");
const rankingGasto = document.getElementById("rankingGasto");
const rankingFrequencia = document.getElementById("rankingFrequencia");
const rankingColaboradores = document.getElementById("rankingColaboradores");




/* ---------- Cadastrar cliente ---------- */


if(cadastrarClienteBtn){

    cadastrarClienteBtn.onclick=async function(){

        const nome = clienteCadastroNome.value.trim();
        const telefone = clienteTelefone.value.trim();
        const observacao = clienteObservacao.value.trim();

        const email = clienteEmailCadastro ? clienteEmailCadastro.value.trim() : "";

        if(nome===""){
            alert("Digite o nome do cliente");
            return;
        }

        try{

            /* Primeiro salva o cliente.
               Se este POST der certo, o cadastro já foi concluído no backend. */
            await Api.post("/clients",{
                name: nome,
                phone: telefone || null,
                email: email || null,
                note: observacao || null
            });


            /* Limpa os campos */
            clienteCadastroNome.value = "";
            clienteTelefone.value = "";
            clienteObservacao.value = "";

            if(clienteEmailCadastro){
                clienteEmailCadastro.value = "";
            }


            /* Atualiza somente o que depende diretamente de clientes.
               Assim, uma rota de Agenda/Marketing/Financeiro que esteja
               indisponível não faz o cadastro parecer que falhou. */
            try{

                clientes = await Api.get("/clients");

                renderizarClientes();
                popularSelectClientes();
                popularSelectClientesAgenda();

            }catch(atualizacaoErr){

                console.warn(
                    "Cliente foi cadastrado, mas não foi possível atualizar a lista agora:",
                    atualizacaoErr
                );

            }


            /* Atualiza os números do dashboard sem bloquear o cadastro */
            try{

                await atualizarDashboardCards();

            }catch(dashboardErr){

                console.warn(
                    "Cliente foi cadastrado, mas o dashboard não pôde ser atualizado agora:",
                    dashboardErr
                );

            }


            mostrarNotificacao(
                "Cliente cadastrado e pronto para ser usado nas comandas.",
                "success",
                "Cliente cadastrado"
            );


        }catch(err){

            mostrarErro(err);

        }
    };

}




/* ---------- Render clientes ---------- */


function calcularEstatisticasCliente(clientId){
    let totalGasto = 0;
    let quantidadeCompras = 0;

    historico.forEach(comanda=>{
        if(comanda.client_id === clientId){
            totalGasto += comanda.total;
            quantidadeCompras += 1;
        }
    });

    return { totalGasto, quantidadeCompras };
}


function renderizarClientes(){

    if(!listaClientes) return;
    const total=document.getElementById("clientesResumoTotal"); if(total) total.textContent=clientes.length;
    const andamento=document.getElementById("clientesResumoAndamento"); if(andamento) andamento.textContent=comandas.length;
    const finalizados=document.getElementById("clientesResumoFinalizados"); if(finalizados) finalizados.textContent=historico.length;

    listaClientes.innerHTML="";

    const termoBusca = (document.getElementById("buscaClientes")?.value || "").trim().toLowerCase();

    const clientesFiltrados = termoBusca
        ? clientes.filter(c=>
            (c.name || "").toLowerCase().includes(termoBusca) ||
            (c.phone || "").toLowerCase().includes(termoBusca) ||
            (c.email || "").toLowerCase().includes(termoBusca)
          )
        : clientes;

    if(clientesFiltrados.length===0){
        listaClientes.innerHTML = termoBusca
            ? `<p class="muted">Nenhum cliente encontrado para "${termoBusca}".</p>`
            : `<p class="muted">Nenhum cliente cadastrado.</p>`;
        gerarRankingClientes();
        return;
    }

    clientesFiltrados.forEach(cliente=>{

        const stats = calcularEstatisticasCliente(cliente.id);

        const div = document.createElement("div");
        div.className = "cliente-card";

        div.innerHTML=`
            <h3>${cliente.name}</h3>
            <p> ${cliente.phone || "Sem telefone"}</p>
            <p> ${cliente.email || "Sem e-mail"}</p>
            <p> ${cliente.note || "Sem observação"}</p>
            <p> Total gasto: ${dinheiro(stats.totalGasto)}</p>
            <p> Compras: ${stats.quantidadeCompras}</p>
            <div class="cliente-card-actions">
                <button type="button" class="btn-editar-cliente">Editar</button>
                <button type="button" class="btn-remover-cliente">Remover</button>
            </div>
        `;

        div.querySelector(".btn-editar-cliente").onclick=function(){
            abrirModalEdicaoCliente(cliente);
        };

        div.querySelector(".btn-remover-cliente").onclick=function(){
            confirmarRemocaoCliente(cliente);
        };

        listaClientes.appendChild(div);
    });

    gerarRankingClientes();
}





/* =====================================================
   REMOVER CLIENTE
===================================================== */

function garantirModalConfirmacaoCliente(){

    let overlay = document.getElementById("confirmarRemocaoClienteModal");

    if(overlay) return overlay;

    overlay = document.createElement("div");
    overlay.id = "confirmarRemocaoClienteModal";
    overlay.className = "confirm-delete-overlay";

    overlay.innerHTML = `
        <div class="confirm-delete-box" role="dialog" aria-modal="true" aria-labelledby="confirmDeleteTitle">
            <div class="confirm-delete-mark">!</div>

            <h3 id="confirmDeleteTitle">Remover cliente</h3>

            <p id="confirmDeleteText">
                Tem certeza que deseja remover este cliente?
            </p>

            <p class="confirm-delete-note">
                Essa ação pode não ser desfeita.
            </p>

            <div class="confirm-delete-actions">
                <button type="button" class="btn-confirm-cancel">Cancelar</button>
                <button type="button" class="btn-confirm-delete">Remover cliente</button>
            </div>
        </div>
    `;

    document.body.appendChild(overlay);

    overlay.addEventListener("click", function(event){
        if(event.target === overlay){
            overlay.classList.remove("active");
        }
    });

    return overlay;
}


function confirmarRemocaoCliente(cliente){

    const overlay = garantirModalConfirmacaoCliente();

    const texto = overlay.querySelector("#confirmDeleteText");
    const cancelar = overlay.querySelector(".btn-confirm-cancel");
    const remover = overlay.querySelector(".btn-confirm-delete");

    texto.textContent = `Tem certeza que deseja remover ${cliente.name}?`;

    overlay.classList.add("active");

    cancelar.onclick = function(){
        overlay.classList.remove("active");
    };

    remover.onclick = async function(){

        remover.disabled = true;
        remover.textContent = "Removendo...";

        try{

            await Api.del(`/clients/${cliente.id}`);

            overlay.classList.remove("active");

            clientes = await Api.get("/clients");

            renderizarClientes();
            popularSelectClientes();
            popularSelectClientesAgenda();

            try{
                await atualizarDashboardCards();
            }catch(err){
                console.warn("Dashboard não pôde ser atualizado após remover cliente:", err);
            }

            mostrarNotificacao(
                "O cliente foi removido da sua base.",
                "success",
                "Cliente removido"
            );

        }catch(err){

            mostrarErro(err);

        }finally{

            remover.disabled = false;
            remover.textContent = "Remover cliente";

        }
    };
}


/* =====================================================
   EDITAR CLIENTE (modal com aba de e-mail)
===================================================== */


const editarClienteModal = document.getElementById("editarClienteModal");
const fecharModalCliente = document.getElementById("fecharModalCliente");
const editClienteNome = document.getElementById("editClienteNome");
const editClienteTelefone = document.getElementById("editClienteTelefone");
const editClienteObservacao = document.getElementById("editClienteObservacao");
const editClienteEmail = document.getElementById("editClienteEmail");
const salvarEdicaoClienteBtn = document.getElementById("salvarEdicaoClienteBtn");

let clienteEmEdicaoId = null;


function abrirModalEdicaoCliente(cliente){
    if(!editarClienteModal) return;

    clienteEmEdicaoId = cliente.id;

    editClienteNome.value = cliente.name || "";
    editClienteTelefone.value = cliente.phone || "";
    editClienteObservacao.value = cliente.note || "";
    editClienteEmail.value = cliente.email || "";

    editarClienteModal.classList.add("active");
}


function fecharModalDeEdicao(){
    if(editarClienteModal) editarClienteModal.classList.remove("active");
    clienteEmEdicaoId = null;
}


if(fecharModalCliente){
    fecharModalCliente.onclick = fecharModalDeEdicao;
}

if(editarClienteModal){
    editarClienteModal.addEventListener("click", function(e){
        if(e.target === editarClienteModal) fecharModalDeEdicao();
    });
}

if(salvarEdicaoClienteBtn){

    salvarEdicaoClienteBtn.onclick = async function(){

        if(!clienteEmEdicaoId) return;

        const nome = editClienteNome.value.trim();

        if(nome===""){
            alert("Digite o nome do cliente");
            return;
        }

        try{
            await Api.put(`/clients/${clienteEmEdicaoId}`, {
                name: nome,
                phone: editClienteTelefone.value.trim() || null,
                email: editClienteEmail.value.trim() || null,
                note: editClienteObservacao.value.trim() || null
            });

            fecharModalDeEdicao();

            await atualizarSomenteClientes();

            mostrarNotificacao(
                "Os dados do cliente foram atualizados.",
                "success",
                "Cliente atualizado"
            );
        }catch(err){
            mostrarErro(err);
        }
    };

}




/* ---------- Ranking clientes ---------- */


function gerarRankingClientes(){

    if(!rankingGasto || !rankingFrequencia) return;

    const comEstatisticas = clientes.map(cliente=>{
        const stats = calcularEstatisticasCliente(cliente.id);
        return { nome: cliente.name, ...stats };
    });

    // Sempre limita os rankings de cliente aos 5 primeiros.
    const maiorGasto = [...comEstatisticas]
        .filter(item=>item.totalGasto > 0)
        .sort((a,b)=> b.totalGasto - a.totalGasto)
        .slice(0,5);

    const maisFrequentes = [...comEstatisticas]
        .filter(item=>item.quantidadeCompras > 0)
        .sort((a,b)=> b.quantidadeCompras - a.quantidadeCompras)
        .slice(0,5);

    rankingGasto.innerHTML="";

    if(maiorGasto.length===0){
        rankingGasto.innerHTML=`<p class="muted">Sem dados ainda.</p>`;
    }else{
        maiorGasto.forEach((cliente,index)=>{
            rankingGasto.innerHTML+=`
                <div class="ranking-item">
                    <strong>${index+1}º ${cliente.nome}</strong>
                    <br>
                    ${dinheiro(cliente.totalGasto)}
                </div>
            `;
        });
    }

    rankingFrequencia.innerHTML="";

    if(maisFrequentes.length===0){
        rankingFrequencia.innerHTML=`<p class="muted">Sem dados ainda.</p>`;
    }else{
        maisFrequentes.forEach((cliente,index)=>{
            rankingFrequencia.innerHTML+=`
                <div class="ranking-item">
                    <strong>${index+1}º ${cliente.nome}</strong>
                    <br>
                    ${cliente.quantidadeCompras} visitas
                </div>
            `;
        });
    }

    gerarRankingColaboradores();
}


function gerarRankingColaboradores(){

    if(!rankingColaboradores) return;

    const mapa = new Map();

    colaboradores.forEach(colaborador=>{
        mapa.set(String(colaborador.id), {
            id: colaborador.id,
            nome: colaborador.name,
            atendimentos: 0,
            faturamento: 0
        });
    });

    historico.forEach(comanda=>{

        const id =
            comanda.employee_id ??
            comanda.colaborador_id ??
            (comanda.employee && comanda.employee.id);

        if(id === null || id === undefined) return;

        const chave = String(id);
        const atual = mapa.get(chave) || {
            id,
            nome:
                comanda.employee_name ||
                comanda.colaborador_name ||
                "Colaborador",
            atendimentos: 0,
            faturamento: 0
        };

        atual.atendimentos += 1;
        atual.faturamento += Number(comanda.total || 0);

        mapa.set(chave, atual);
    });

    const ranking = [...mapa.values()]
        .filter(item=>item.atendimentos > 0)
        .sort((a,b)=>
            b.atendimentos - a.atendimentos ||
            b.faturamento - a.faturamento
        )
        .slice(0,5);

    rankingColaboradores.innerHTML = "";

    if(ranking.length===0){
        rankingColaboradores.innerHTML =
            `<p class="muted">Sem atendimentos vinculados à equipe.</p>`;
        return;
    }

    ranking.forEach((item,index)=>{
        rankingColaboradores.innerHTML += `
            <div class="ranking-item">
                <strong>${index+1}º ${item.nome}</strong>
                <br>
                ${item.atendimentos} atendimento${item.atendimentos === 1 ? "" : "s"}
                · ${dinheiro(item.faturamento)}
            </div>
        `;
    });
}



/* =====================================================
   ELEMENTOS COMANDA
===================================================== */


const clienteSelecionado = document.getElementById("clienteSelecionado");
const colaboradorSelecionado = document.getElementById("colaboradorSelecionado");
const abrirComandaBtn = document.getElementById("abrirComandaBtn");
const listaComandas = document.getElementById("listaComandas");


/* ---------- Popular o <select> de clientes ---------- */


function popularSelectClientes(){

    if(!clienteSelecionado) return;

    const valorAtual = clienteSelecionado.value;

    clienteSelecionado.innerHTML = `<option value="">Selecione um cliente</option>`;

    clientes.forEach(cliente=>{
        const option = document.createElement("option");
        option.value = cliente.id;
        option.textContent = cliente.name;
        clienteSelecionado.appendChild(option);
    });

    if(valorAtual) clienteSelecionado.value = valorAtual;
}






function popularSelectColaboradores(){

    if(!colaboradorSelecionado) return;

    const valorAtual = colaboradorSelecionado.value;

    colaboradorSelecionado.innerHTML =
        `<option value="">Selecione um colaborador</option>`;

    colaboradores
        .filter(item=>item.active !== false)
        .forEach(colaborador=>{
            const option = document.createElement("option");
            option.value = colaborador.id;
            option.textContent = colaborador.name;
            colaboradorSelecionado.appendChild(option);
        });

    if(valorAtual){
        colaboradorSelecionado.value = valorAtual;
    }
}


/* ---------- Abrir comanda ---------- */


if(abrirComandaBtn){

    abrirComandaBtn.onclick = async function(){

        const clientId =
            Number(clienteSelecionado.value);

        const employeeId =
            colaboradorSelecionado
                ? Number(colaboradorSelecionado.value)
                : 0;

        if(!clientId){
            alert("Selecione um cliente");
            return;
        }

        if(!employeeId){
            alert(
                "Selecione o colaborador que realizou o atendimento"
            );
            return;
        }

        try{

            await executarComTrava(
                "abrir-comanda",
                abrirComandaBtn,
                "Abrindo...",
                async ()=>{

                    const novaComanda =
                        await Api.post(
                            "/comandas",
                            {
                                client_id: clientId,
                                employee_id: employeeId
                            }
                        );

                    /*
                      O backend já devolveu a comanda criada.
                      Não precisamos recarregar o sistema inteiro.
                    */
                    if(novaComanda){

                        comandas = [
                            novaComanda,
                            ...comandas.filter(
                                item=>
                                    String(item.id) !==
                                    String(novaComanda.id)
                            )
                        ];

                        renderizarComandas();

                        if(comandasHTML){
                            comandasHTML.textContent =
                                comandas.length;
                        }

                    }else{

                        await atualizarSomenteComandas();
                    }

                    clienteSelecionado.value = "";
                    colaboradorSelecionado.value = "";

                    mostrarNotificacao(
                        "Comanda aberta e pronta para receber serviços.",
                        "success",
                        "Comanda aberta"
                    );

                    /*
                      Atualiza apenas os cards em segundo plano.
                      O usuário não precisa esperar isso para continuar.
                    */
                    atualizarDashboardCards()
                        .catch(err=>
                            console.warn(
                                "Dashboard não atualizado:",
                                err
                            )
                        );
                }
            );

        }catch(err){
            mostrarErro(err);
        }
    };
}



/* ---------- Renderizar comandas abertas ---------- */


function renderizarComandas(){

    if(!listaComandas) return;

    listaComandas.innerHTML="";

    const termoBusca = (document.getElementById("buscaComandas")?.value || "").trim().toLowerCase();

    const comandasFiltradas = termoBusca
        ? comandas.filter(c=> (c.client_name || "").toLowerCase().includes(termoBusca))
        : comandas;

    if(comandasFiltradas.length===0){
        listaComandas.innerHTML = termoBusca
            ? `<p class="muted">Nenhuma comanda encontrada para "${termoBusca}".</p>`
            : `<p class="muted">Nenhuma comanda aberta.</p>`;
        return;
    }

    comandasFiltradas.forEach(comanda=>{

        const div = document.createElement("div");
        div.className = "comanda";

        div.innerHTML=`
            <div class="comanda-header">
                <div>
                    <h3>${comanda.client_name || "Cliente"}</h3>
                    <p class="comanda-colaborador">
                        Colaborador: ${comanda.employee_name || comanda.colaborador_name || "Não informado"}
                    </p>
                </div>
                <span class="status">Aberta</span>
            </div>

            <select class="servicoCatalogo">
                <option value="">Escolher do catálogo (opcional)</option>
                ${servicos.filter(s=>s.active).map(s=>`<option value="${s.id}" data-preco="${s.price}">${s.name} — ${dinheiro(s.price)}</option>`).join("")}
            </select>

            <input class="nomeServico" placeholder="Nome do serviço">
            <input class="valorServico" type="number" placeholder="Valor">

            <button type="button" class="btn-primary adicionarServico">Adicionar Serviço</button>

            <div class="lista-servicos">
                ${comanda.items.map(item=>`
                    <div class="servico-item">
                        <span>${item.name}${item.quantity>1 ? " x"+item.quantity : ""}</span>
                        <span>${dinheiro(item.price*item.quantity)}</span>
                    </div>
                `).join("")}
            </div>

            <div class="total-comanda">
                <strong>Total</strong>
                <strong>${dinheiro(comanda.total)}</strong>
            </div>

            <div class="comanda-actions">
                <button type="button" class="btn-cancelar-comanda">Cancelar comanda</button>
                <button type="button" class="btn-fechar">Finalizar atendimento</button>
            </div>
        `;

        const catalogoSelect = div.querySelector(".servicoCatalogo");

        if(catalogoSelect){
            catalogoSelect.onchange = function(){
                const opcao = catalogoSelect.selectedOptions[0];
                if(!opcao || !opcao.value) return;

                div.querySelector(".nomeServico").value = opcao.textContent.split(" — ")[0];
                div.querySelector(".valorServico").value = opcao.dataset.preco;
            };
        }

        const adicionar = div.querySelector(".adicionarServico");

        adicionar.onclick = async function(){

            const nomeServico =
                div.querySelector(
                    ".nomeServico"
                ).value.trim();

            const valorServico =
                Number(
                    div.querySelector(
                        ".valorServico"
                    ).value
                );

            if(
                nomeServico === "" ||
                valorServico <= 0
            ){
                alert("Informe serviço e valor");
                return;
            }

            try{

                await executarComTrava(
                    `adicionar-servico-${comanda.id}`,
                    adicionar,
                    "Adicionando...",
                    async ()=>{

                        const atualizada =
                            await Api.post(
                                `/comandas/${comanda.id}/items`,
                                {
                                    name: nomeServico,
                                    price: valorServico,
                                    quantity: 1
                                }
                            );

                        if(atualizada){

                            comandas =
                                comandas.map(item=>
                                    String(item.id) ===
                                    String(atualizada.id)
                                        ? atualizada
                                        : item
                                );

                            renderizarComandas();

                        }else{

                            await atualizarSomenteComandas();
                        }
                    }
                );

            }catch(err){
                mostrarErro(err);
            }
        };

        const cancelar = div.querySelector(".btn-cancelar-comanda");

        cancelar.onclick = async function(){

            const confirmou = confirm(
                `Cancelar a comanda de ${comanda.client_name || "Cliente"}?`
            );

            if(!confirmou) return;

            cancelar.disabled = true;
            cancelar.textContent = "Cancelando...";

            try{
                // O backend já possui POST /comandas/{id}/cancelar.
                await Api.post(`/comandas/${comanda.id}/cancelar`);

                mostrarNotificacao(
                    "A comanda foi cancelada e removida das comandas abertas.",
                    "success",
                    "Comanda cancelada"
                );

                // Remove instantaneamente da tela.
                comandas = comandas.filter(item =>
                    String(item.id) !== String(comanda.id)
                );

                renderizarComandas();

                if(comandasHTML){
                    comandasHTML.textContent = comandas.length;
                }

                // Sincroniza só os indicadores necessários em paralelo.
                Promise.allSettled([
                    atualizarDashboardCards(),
                    carregarFinanceiro()
                ]).then(()=>{
                    gerarRelatorios();
                    renderizarGraficoFinanceiro();
                });

            }catch(err){

                mostrarErro(err);

            }finally{

                cancelar.disabled = false;
                cancelar.textContent = "Cancelar comanda";

            }
        };

        const fechar = div.querySelector(".btn-fechar");

        fechar.onclick = async function(){

            if(comanda.total <= 0){
                alert(
                    "Adicione serviços antes de finalizar. Se abriu por engano, use Cancelar comanda."
                );
                return;
            }

            try{

                await executarComTrava(
                    `finalizar-comanda-${comanda.id}`,
                    fechar,
                    "Finalizando...",
                    async ()=>{

                        const finalizada =
                            await Api.post(
                                `/comandas/${comanda.id}/finalizar`
                            );

                        /*
                          Remove imediatamente das comandas abertas.
                        */
                        comandas =
                            comandas.filter(item=>
                                String(item.id) !==
                                String(comanda.id)
                            );

                        if(finalizada){

                            historico = [
                                finalizada,
                                ...historico.filter(item=>
                                    String(item.id) !==
                                    String(finalizada.id)
                                )
                            ];
                        }

                        renderizarComandas();
                        renderizarHistorico();
                        renderizarClientes();

                        if(comandasHTML){
                            comandasHTML.textContent =
                                comandas.length;
                        }

                        gerarRelatorios();
                        renderizarGraficoFinanceiro();

                        if(finalizada && finalizada.feedback_url){
                            try{ await navigator.clipboard.writeText(finalizada.feedback_url); }catch(_){ }
                            mostrarNotificacao("Atendimento finalizado. O link de avaliação foi copiado para você enviar ao cliente.","success","Comanda finalizada");
                        }else{
                            mostrarNotificacao("Atendimento finalizado com sucesso.","success","Comanda finalizada");
                        }

                        /*
                          Sincronização fina em segundo plano.
                          A interface já respondeu ao clique.
                        */
                        atualizarHistoricoFinanceiro()
                            .catch(err=>
                                console.warn(
                                    "Sincronização pós-finalização falhou:",
                                    err
                                )
                            );
                    }
                );

            }catch(err){
                mostrarErro(err);
            }
        };

        listaComandas.appendChild(div);
    });
}


/* =====================================================
   HISTÓRICO
===================================================== */


const listaHistoricoHTML = document.getElementById("listaHistorico");
const buscarClienteHistorico = document.getElementById("buscarClienteHistorico");
const limparBuscaHistorico = document.getElementById("limparBuscaHistorico");
const historicoBuscaResumo = document.getElementById("historicoBuscaResumo");


function normalizarBuscaHistorico(valor){

    return String(valor || "")
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .trim();
}


function historicoFiltrado(){

    const termo = normalizarBuscaHistorico(
        buscarClienteHistorico
            ? buscarClienteHistorico.value
            : ""
    );

    if(!termo){
        return [...historico];
    }

    return historico.filter(item=>{

        const nomeCliente = normalizarBuscaHistorico(
            item.client_name || "Cliente"
        );

        return nomeCliente.includes(termo);
    });
}


function atualizarResumoBuscaHistorico(totalMostrado){

    if(!historicoBuscaResumo) return;

    const termo = buscarClienteHistorico
        ? buscarClienteHistorico.value.trim()
        : "";

    if(!termo){

        historicoBuscaResumo.textContent =
            historico.length === 1
                ? "1 atendimento no histórico."
                : `${historico.length} atendimentos no histórico.`;

        return;
    }

    historicoBuscaResumo.textContent =
        totalMostrado === 1
            ? `1 atendimento encontrado para "${termo}".`
            : `${totalMostrado} atendimentos encontrados para "${termo}".`;
}


function renderizarHistorico(){

    if(!listaHistoricoHTML) return;

    listaHistoricoHTML.innerHTML="";

    if(historico.length===0){

        listaHistoricoHTML.innerHTML=`
            <div class="historico-vazio">
                <p class="muted">Nenhuma venda realizada.</p>
            </div>
        `;

        atualizarResumoBuscaHistorico(0);
        return;
    }

    const itens = historicoFiltrado();

    atualizarResumoBuscaHistorico(itens.length);

    if(itens.length===0){

        listaHistoricoHTML.innerHTML=`
            <div class="historico-vazio historico-sem-resultado">
                <strong>Nenhum atendimento encontrado</strong>
                <p class="muted">
                    Tente pesquisar outro nome de cliente.
                </p>
            </div>
        `;

        return;
    }

    itens.forEach(item=>{

        const div = document.createElement("div");
        div.className = "historico-item";

        div.innerHTML=`
            <div class="historico-item-topo">
                <div>
                    <span class="historico-item-label">Cliente</span>
                    <strong class="historico-cliente-nome">
                        ${item.client_name || "Cliente"}
                    </strong>
                </div>

                <strong class="historico-item-total">
                    ${dinheiro(item.total)}
                </strong>
            </div>

            <div class="historico-item-detalhes">
                <p>
                    <strong>Colaborador:</strong>
                    ${item.employee_name || item.colaborador_name || "Não informado"}
                </p>

                <p>
                    <strong>Data:</strong>
                    ${formatarData(item.data_fechamento || item.data_abertura)}
                    às
                    ${formatarHora(item.data_fechamento || item.data_abertura)}
                </p>
            </div>

            <div class="historico-servicos">
                <span class="historico-item-label">Serviços</span>

                ${item.items.map(servico=>`
                    <div class="historico-servico-linha">
                        <span>
                            ${servico.name}
                            ${servico.quantity>1 ? " x"+servico.quantity : ""}
                        </span>

                        <strong>
                            ${dinheiro(servico.price*servico.quantity)}
                        </strong>
                    </div>
                `).join("")}
            </div>
        `;

        listaHistoricoHTML.appendChild(div);
    });
}


if(buscarClienteHistorico){

    buscarClienteHistorico.addEventListener("input", ()=>{
        renderizarHistorico();
    });

    buscarClienteHistorico.addEventListener("search", ()=>{
        renderizarHistorico();
    });
}


if(limparBuscaHistorico){

    limparBuscaHistorico.addEventListener("click", ()=>{

        if(buscarClienteHistorico){
            buscarClienteHistorico.value = "";
            buscarClienteHistorico.focus();
        }

        renderizarHistorico();
    });
}



/* =====================================================
   LIMPAR HISTÓRICO
===================================================== */


const limparHistoricoBtn = document.getElementById("limparHistoricoBtn");


if(limparHistoricoBtn){

    limparHistoricoBtn.onclick = async function(){

        if(!confirm("Deseja apagar todo histórico?")){
            return;
        }

        try{

            await executarComTrava(
                "limpar-historico",
                limparHistoricoBtn,
                "Limpando...",
                async ()=>{

                    await Api.del("/comandas/historico");

                    historico = [];

                    renderizarHistorico();
                    renderizarClientes();
                    gerarRelatorios();
                    renderizarGraficoFinanceiro();

                    await atualizarDashboardCards();

                    mostrarNotificacao(
                        "O histórico foi limpo.",
                        "success",
                        "Histórico limpo"
                    );
                }
            );

        }catch(err){
            mostrarErro(err);
        }
    };

}




/* =====================================================
   FINANCEIRO
===================================================== */


const faturamentoSemanaHTML = document.getElementById("faturamentoSemana");
const faturamentoMesHTML = document.getElementById("faturamentoMes");



function dataFinanceiraDaComanda(comanda){

    return new Date(
        comanda.data_fechamento ||
        comanda.updated_at ||
        comanda.data_abertura ||
        comanda.created_at
    );
}


function despesasRegistradas(){

    return lancamentos.filter(item=>item.type === "saida");
}


function calcularFinanceiroEntre(inicio = null, fim = null){

    const dentroDoPeriodo = (data)=>{
        if(Number.isNaN(data.getTime())) return false;
        if(inicio && data < inicio) return false;
        if(fim && data > fim) return false;
        return true;
    };

    const vendas = historico.reduce((total, comanda)=>{

        const data = dataFinanceiraDaComanda(comanda);

        if(!dentroDoPeriodo(data)){
            return total;
        }

        return total + Number(comanda.total || 0);

    }, 0);

    const despesas = despesasRegistradas().reduce((total, lancamento)=>{

        const data = new Date(lancamento.created_at);

        if(!dentroDoPeriodo(data)){
            return total;
        }

        return total + Number(lancamento.amount || 0);

    }, 0);

    return {
        vendas,
        despesas,
        liquido: vendas - despesas
    };
}


function calcularResumoFinanceiro(){

    const agora = new Date();

    const inicioSemana =
        new Date(
            agora.getFullYear(),
            agora.getMonth(),
            agora.getDate() - 6,
            0,0,0,0
        );

    const inicioMes =
        new Date(
            agora.getFullYear(),
            agora.getMonth(),
            1,
            0,0,0,0
        );

    const fimAmanha =
        new Date(
            agora.getFullYear(),
            agora.getMonth(),
            agora.getDate() + 1,
            0,0,0,0
        );

    const semana =
        resumoMovimentosNoPeriodo(
            inicioSemana,
            fimAmanha
        );

    /*
      Para o total do dashboard usamos o mês corrente,
      que é a mesma lógica da competência financeira atual.
    */
    const mes =
        resumoMovimentosNoPeriodo(
            inicioMes,
            fimAmanha
        );

    return {
        semana:{
            receita:semana.entradas,
            despesa:semana.saidas,
            liquido:semana.saldo
        },

        mes:{
            receita:mes.entradas,
            despesa:mes.saidas,
            liquido:mes.saldo
        },

        total:{
            receita:mes.entradas,
            despesa:mes.saidas,
            liquido:mes.saldo
        }
    };
}


function aplicarValorFinanceiro(elemento, valor){
    if(!elemento) return;

    const numero = Number(valor || 0);

    elemento.textContent = dinheiro(numero);

    elemento.classList.toggle("valor-negativo", numero < 0);
    elemento.classList.toggle("valor-positivo", numero > 0);
    elemento.classList.toggle("valor-zero", numero === 0);
}


function gerarRelatorios(){

    if(!faturamentoSemanaHTML || !faturamentoMesHTML) return;

    const resumo = calcularResumoFinanceiro();

    faturamentoSemanaHTML.innerHTML=`
        <div class="finance-card finance-resumo">
            <div class="finance-resumo-linha">
                <span>Vendas</span>
                <strong>${dinheiro(resumo.semana.vendas)}</strong>
            </div>

            <div class="finance-resumo-linha despesa">
                <span>Despesas</span>
                <strong>- ${dinheiro(resumo.semana.despesas)}</strong>
            </div>

            <div class="finance-resumo-total ${resumo.semana.liquido < 0 ? "negativo" : ""}">
                <span>Resultado</span>
                <strong>${dinheiro(resumo.semana.liquido)}</strong>
            </div>
        </div>
    `;

    faturamentoMesHTML.innerHTML=`
        <div class="finance-card finance-resumo">
            <div class="finance-resumo-linha">
                <span>Vendas</span>
                <strong>${dinheiro(resumo.mes.vendas)}</strong>
            </div>

            <div class="finance-resumo-linha despesa">
                <span>Despesas</span>
                <strong>- ${dinheiro(resumo.mes.despesas)}</strong>
            </div>

            <div class="finance-resumo-total ${resumo.mes.liquido < 0 ? "negativo" : ""}">
                <span>Resultado</span>
                <strong>${dinheiro(resumo.mes.liquido)}</strong>
            </div>
        </div>
    `;
}



/* =====================================================
   ATIVIDADES
===================================================== */


const novaAtividadeBtn = document.getElementById("novaAtividadeBtn");
const atividadeForm = document.getElementById("atividadeForm");
const salvarAtividadeBtn = document.getElementById("salvarAtividadeBtn");
const atividadeTitulo = document.getElementById("atividadeTitulo");
const atividadePrioridade = document.getElementById("atividadePrioridade");
const listaAtividades = document.getElementById("listaAtividades");


if(novaAtividadeBtn){
    novaAtividadeBtn.onclick=function(){
        atividadeForm.classList.toggle("active");
    };
}


if(salvarAtividadeBtn){

    salvarAtividadeBtn.onclick=async function(){

        const titulo = atividadeTitulo.value.trim();

        if(titulo===""){
            alert("Digite a atividade");
            return;
        }

        try{
            await Api.post("/activities", { title: titulo, priority: atividadePrioridade.value });

            atividadeTitulo.value="";
            atividadeForm.classList.remove("active");

            await carregarAtividades();
            renderizarAtividades();
        }catch(err){
            mostrarErro(err);
        }
    };

}


function renderizarAtividades(){

    if(!listaAtividades) return;

    listaAtividades.innerHTML="";

    if(atividades.length===0){
        listaAtividades.innerHTML=`
            <div class="empty-state">
                
                <p>Nenhuma atividade cadastrada.</p>
            </div>
        `;
        return;
    }

    atividades.forEach(item=>{

        const div = document.createElement("div");
        div.className = "atividade-card";

        div.innerHTML=`
            <h3>${item.title}</h3>
            <p>Prioridade: ${item.priority}</p>
            <p>Criada: ${formatarData(item.created_at)}</p>

            <button type="button" class="btn-check">${item.completed ? "Concluída ✓" : "Finalizar"}</button>
            <button type="button" class="btn-delete">Excluir</button>
        `;

        div.querySelector(".btn-check").onclick=async function(){
            try{
                await Api.patch(`/activities/${item.id}/toggle`);
                await carregarAtividades();
                renderizarAtividades();
            }catch(err){
                mostrarErro(err);
            }
        };

        div.querySelector(".btn-delete").onclick=async function(){
            try{
                await Api.del(`/activities/${item.id}`);
                await carregarAtividades();
                renderizarAtividades();
            }catch(err){
                mostrarErro(err);
            }
        };

        listaAtividades.appendChild(div);
    });
}




/* =====================================================
   ABAS GENÉRICAS (usadas no Marketing e no modal de Cliente)
===================================================== */


function configurarAbas(){

    document.querySelectorAll(".tabs").forEach(tabsContainer=>{

        const botoesAba = tabsContainer.querySelectorAll(".tab-btn");
        const container = tabsContainer.parentElement;

        botoesAba.forEach(botao=>{

            botao.onclick = function(){

                botoesAba.forEach(b=> b.classList.remove("active"));
                botao.classList.add("active");

                container.querySelectorAll(":scope > .tab-content").forEach(painel=>{
                    painel.classList.toggle(
                        "active",
                        painel.dataset.tabPanel === botao.dataset.tab
                    );
                });
            };
        });
    });
}


configurarAbas();




/* =====================================================
   FILTROS DE BUSCA (Clientes, Serviços, Equipe, Comandas, Agenda)
===================================================== */


function configurarFiltrosDeBusca(){

    const mapaFiltros = [
        ["buscaClientes", renderizarClientes],
        ["buscaServicos", renderizarServicos],
        ["buscaColaboradores", renderizarColaboradores],
        ["buscaComandas", renderizarComandas],
        ["buscaAgenda", renderizarAgenda],
    ];

    mapaFiltros.forEach(([inputId, renderizarFn])=>{

        const input = document.getElementById(inputId);
        if(!input) return;

        let debounceTimer = null;

        input.addEventListener("input", function(){
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(()=> renderizarFn(), 200);
        });
    });
}


configurarFiltrosDeBusca();




/* =====================================================
   SERVIÇOS (catálogo)
===================================================== */


let servicos = [];

const servicoNome = document.getElementById("servicoNome");
const servicoPreco = document.getElementById("servicoPreco");
const servicoDuracao = document.getElementById("servicoDuracao");
const servicoDescricao = document.getElementById("servicoDescricao");
const cadastrarServicoBtn = document.getElementById("cadastrarServicoBtn");
const listaServicos = document.getElementById("listaServicos");


if(cadastrarServicoBtn){

    cadastrarServicoBtn.onclick = async function(){

        const nome = servicoNome.value.trim();
        const preco = Number(servicoPreco.value);

        if(nome===""){
            alert("Digite o nome do serviço");
            return;
        }

        try{
            await Api.post("/services", {
                name: nome,
                price: preco || 0,
                duration: servicoDuracao.value ? Number(servicoDuracao.value) : null,
                description: servicoDescricao.value.trim() || null
            });

            servicoNome.value = "";
            servicoPreco.value = "";
            servicoDuracao.value = "";
            servicoDescricao.value = "";

            await carregarServicos();
            renderizarServicos();
            popularSelectServicos();
        }catch(err){
            mostrarErro(err);
        }
    };
}


function renderizarServicos(){

    if(!listaServicos) return;

    listaServicos.innerHTML = "";

    const termoBusca = (document.getElementById("buscaServicos")?.value || "").trim().toLowerCase();

    const servicosFiltrados = termoBusca
        ? servicos.filter(s=> (s.name || "").toLowerCase().includes(termoBusca))
        : servicos;

    if(servicosFiltrados.length===0){
        listaServicos.innerHTML = termoBusca
            ? `<p class="muted">Nenhum serviço encontrado para "${termoBusca}".</p>`
            : `<p class="muted">Nenhum serviço cadastrado.</p>`;
        return;
    }

    servicosFiltrados.forEach(servico=>{

        const div = document.createElement("div");
        div.className = "item-card";

        div.innerHTML = `
            <div class="item-info">
                <h4>${servico.name} <span class="badge-status ${servico.active ? "" : "inativo"}">${servico.active ? "Ativo" : "Inativo"}</span></h4>
                <p> ${dinheiro(servico.price)}${servico.duration ? " •  " + servico.duration + " min" : ""}</p>
                <p>${servico.description || ""}</p>
            </div>
            <div class="item-actions">
                <button type="button" class="btn-toggle-servico">${servico.active ? "Desativar" : "Ativar"}</button>
                <button type="button" class="btn-item-delete">Excluir</button>
            </div>
        `;

        div.querySelector(".btn-toggle-servico").onclick = async function(){
            try{
                await Api.put(`/services/${servico.id}`, { active: !servico.active });
                await carregarServicos();
                renderizarServicos();
                popularSelectServicos();
            }catch(err){
                mostrarErro(err);
            }
        };

        div.querySelector(".btn-item-delete").onclick = async function(){
            if(!confirm("Excluir este serviço?")) return;
            try{
                await Api.del(`/services/${servico.id}`);
                await carregarServicos();
                renderizarServicos();
                popularSelectServicos();
            }catch(err){
                mostrarErro(err);
            }
        };

        listaServicos.appendChild(div);
    });
}


/* Preenche os <select> de serviço usados na Agenda */

function popularSelectServicos(){

    const agendaServico = document.getElementById("agendaServico");
    if(!agendaServico) return;

    const valorAtual = agendaServico.value;

    agendaServico.innerHTML = `<option value="">Nenhum</option>`;

    servicos.filter(s=>s.active).forEach(servico=>{
        const option = document.createElement("option");
        option.value = servico.id;
        option.textContent = `${servico.name} — ${dinheiro(servico.price)}`;
        agendaServico.appendChild(option);
    });

    if(valorAtual) agendaServico.value = valorAtual;
}





/* =====================================================
   EQUIPE / COLABORADORES
===================================================== */

const servicosTabs = document.querySelectorAll("[data-servicos-tab]");
const servicosTabContents = document.querySelectorAll(".servicos-tab-content");

servicosTabs.forEach(botao=>{
    botao.addEventListener("click", ()=>{

        const destino = botao.dataset.servicosTab;

        servicosTabs.forEach(item=>
            item.classList.toggle("active", item === botao)
        );

        servicosTabContents.forEach(painel=>
            painel.classList.toggle(
                "active",
                painel.id === `tab-${destino}`
            )
        );
    });
});


const colaboradorNome = document.getElementById("colaboradorNome");
const colaboradorTelefone = document.getElementById("colaboradorTelefone");
const colaboradorEmail = document.getElementById("colaboradorEmail");
const cadastrarColaboradorBtn = document.getElementById("cadastrarColaboradorBtn");
const listaColaboradores = document.getElementById("listaColaboradores");


if(cadastrarColaboradorBtn){

    cadastrarColaboradorBtn.onclick = async function(){

        const name = colaboradorNome.value.trim();
        const phone = colaboradorTelefone.value.trim();
        const email = colaboradorEmail.value.trim();

        if(!name){
            alert("Informe o nome do colaborador");
            return;
        }

        try{

            await Api.post("/employees", {
                name,
                phone: phone || null,
                email: email || null
            });

            colaboradorNome.value = "";
            colaboradorTelefone.value = "";
            colaboradorEmail.value = "";

            colaboradores = await Api.get("/employees");

            renderizarColaboradores();
            popularSelectColaboradores();
            gerarRankingColaboradores();

            mostrarNotificacao(
                "Colaborador cadastrado e disponível nas comandas.",
                "success",
                "Equipe atualizada"
            );

        }catch(err){
            mostrarErro(err);
        }
    };
}


function renderizarColaboradores(){

    if(!listaColaboradores) return;

    listaColaboradores.innerHTML = "";

    const termoBusca = (document.getElementById("buscaColaboradores")?.value || "").trim().toLowerCase();

    const colaboradoresFiltrados = termoBusca
        ? colaboradores.filter(c=> (c.name || "").toLowerCase().includes(termoBusca))
        : colaboradores;

    if(colaboradoresFiltrados.length === 0){
        listaColaboradores.innerHTML = termoBusca
            ? `<p class="muted">Nenhum colaborador encontrado para "${termoBusca}".</p>`
            : `<p class="muted">Nenhum colaborador cadastrado.</p>`;
        return;
    }

    colaboradoresFiltrados.forEach(colaborador=>{

        const div = document.createElement("div");
        div.className = "item-card colaborador-card";

        div.innerHTML = `
            <div class="item-info">
                <h4>${colaborador.name}</h4>
                <p>${colaborador.phone || "Sem celular"}</p>
                <p>${colaborador.email || "Sem e-mail"}</p>
            </div>
            <div class="item-actions">
                <button type="button" class="btn-item-delete">
                    Remover
                </button>
            </div>
        `;

        div.querySelector(".btn-item-delete").onclick = async function(){

            if(!confirm(`Remover ${colaborador.name} da equipe?`)){
                return;
            }

            try{

                await Api.del(`/employees/${colaborador.id}`);

                colaboradores = await Api.get("/employees");

                renderizarColaboradores();
                popularSelectColaboradores();
                gerarRankingColaboradores();

            }catch(err){
                mostrarErro(err);
            }
        };

        listaColaboradores.appendChild(div);
    });
}


/* =====================================================
   AGENDA (com lembrete via notificação do navegador)
===================================================== */


let agendamentos = [];
const agendamentosNotificadosLocalmente = new Set();

const agendaCliente = document.getElementById("agendaCliente");
const agendaServicoSelect = document.getElementById("agendaServico");
const agendaData = document.getElementById("agendaData");
const agendaHora = document.getElementById("agendaHora");
const agendaLembrete = document.getElementById("agendaLembrete");
const agendaNotas = document.getElementById("agendaNotas");
const agendarBtn = document.getElementById("agendarBtn");
const listaAgenda = document.getElementById("listaAgenda");
const notificacaoStatus = document.getElementById("notificacaoStatus");


function popularSelectClientesAgenda(){

    if(!agendaCliente) return;

    const valorAtual = agendaCliente.value;

    agendaCliente.innerHTML = `<option value="">Selecione um cliente</option>`;

    clientes.forEach(cliente=>{
        const option = document.createElement("option");
        option.value = cliente.id;
        option.textContent = cliente.name;
        agendaCliente.appendChild(option);
    });

    if(valorAtual) agendaCliente.value = valorAtual;
}


if(agendarBtn){

    agendarBtn.onclick = async function(){

        const clientId = Number(agendaCliente.value);

        if(!clientId){
            alert("Selecione um cliente");
            return;
        }

        if(!agendaData.value || !agendaHora.value){
            alert("Selecione a data e o horário");
            return;
        }

        const scheduledAt = new Date(`${agendaData.value}T${agendaHora.value}:00`);

        try{
            await Api.post("/appointments", {
                client_id: clientId,
                service_id: agendaServicoSelect.value ? Number(agendaServicoSelect.value) : null,
                scheduled_at: scheduledAt.toISOString(),
                reminder_minutes_before: Number(agendaLembrete.value),
                notes: agendaNotas.value.trim() || null
            });

            agendaData.value = "";
            agendaHora.value = "";
            agendaNotas.value = "";

            await carregarAgenda();
            renderizarAgenda();

            alert("Agendamento criado!");
        }catch(err){
            mostrarErro(err);
        }
    };
}


function renderizarAgenda(){

    if(!listaAgenda) return;

    listaAgenda.innerHTML = "";

    const termoBusca = (document.getElementById("buscaAgenda")?.value || "").trim().toLowerCase();

    const futuros = agendamentos
        .filter(a=> a.status === "agendado")
        .filter(a=> !termoBusca || (a.client_name || "").toLowerCase().includes(termoBusca))
        .sort((a,b)=> new Date(a.scheduled_at) - new Date(b.scheduled_at));

    if(futuros.length===0){
        listaAgenda.innerHTML = termoBusca
            ? `<p class="muted">Nenhum agendamento encontrado para "${termoBusca}".</p>`
            : `<p class="muted">Nenhum agendamento.</p>`;
        return;
    }

    futuros.forEach(agendamento=>{

        const data = new Date(agendamento.scheduled_at);

        const div = document.createElement("div");
        div.className = "item-card";

        div.innerHTML = `
            <div class="item-info">
                <h4>${agendamento.client_name || "Cliente"}</h4>
                <p> ${formatarData(agendamento.scheduled_at)} às ${formatarHora(agendamento.scheduled_at)}</p>
                <p>${agendamento.service_name ? " " + agendamento.service_name : ""}</p>
                <p>${agendamento.notes || ""}</p>
            </div>
            <div class="item-actions">
                <button type="button" class="btn-concluir-agenda">Concluir</button>
                <button type="button" class="btn-item-delete">Excluir</button>
            </div>
        `;

        div.querySelector(".btn-concluir-agenda").onclick = async function(){
            try{
                await Api.put(`/appointments/${agendamento.id}`, { status: "concluido" });
                await carregarAgenda();
                renderizarAgenda();
            }catch(err){
                mostrarErro(err);
            }
        };

        div.querySelector(".btn-item-delete").onclick = async function(){
            if(!confirm("Excluir este agendamento?")) return;
            try{
                await Api.del(`/appointments/${agendamento.id}`);
                await carregarAgenda();
                renderizarAgenda();
            }catch(err){
                mostrarErro(err);
            }
        };

        listaAgenda.appendChild(div);
    });
}


/* ---------- Lembretes via notificação do navegador ---------- */


function pedirPermissaoNotificacao(){

    if(!notificacaoStatus) return;

    if(!("Notification" in window)){
        notificacaoStatus.textContent = "Seu navegador não suporta notificações.";
        return;
    }

    if(Notification.permission === "granted"){
        notificacaoStatus.textContent = " Lembretes ativados";
    }else if(Notification.permission !== "denied"){
        Notification.requestPermission().then(permissao=>{
            notificacaoStatus.textContent = permissao === "granted"
                ? " Lembretes ativados"
                : " Lembretes desativados (permita notificações no navegador)";
        });
    }else{
        notificacaoStatus.textContent = " Notificações bloqueadas no navegador";
    }
}


async function verificarLembretes(){

    const agora = Date.now();

    for(const agendamento of agendamentos){

        if(agendamento.status !== "agendado") continue;
        if(agendamento.notified) continue;
        if(agendamentosNotificadosLocalmente.has(agendamento.id)) continue;

        const horario = new Date(agendamento.scheduled_at).getTime();
        const disparaEm = horario - (agendamento.reminder_minutes_before * 60000);

        if(agora >= disparaEm && agora < horario){

            agendamentosNotificadosLocalmente.add(agendamento.id);

            const titulo = "Lembrete de agendamento";
            const corpo = `${agendamento.client_name || "Cliente"} às ${formatarHora(agendamento.scheduled_at)}${agendamento.service_name ? " — " + agendamento.service_name : ""}`;

            if("Notification" in window && Notification.permission === "granted"){
                new Notification(titulo, { body: corpo });
            }else{
                console.log(`${titulo}: ${corpo}`);
            }

            try{
                await Api.put(`/appointments/${agendamento.id}`, { notified: true });
            }catch(err){
                // silencioso: só marca localmente se a API falhar
            }
        }
    }
}


// Verifica lembretes a cada 30 segundos enquanto a aba estiver aberta.
setInterval(verificarLembretes, 30000);




/* =====================================================
   MARKETING PROFISSIONAL — E-MAIL + WHATSAPP
===================================================== */
const emailAssunto=document.getElementById("emailAssunto");
const emailMensagem=document.getElementById("emailMensagem");
const enviarEmailBtn=document.getElementById("enviarEmailBtn");
const whatsappMensagem=document.getElementById("whatsappMensagem");
const gerarWhatsappBtn=document.getElementById("gerarWhatsappBtn");
const listaWhatsappLinks=document.getElementById("listaWhatsappLinks");
const listaCampanhas=document.getElementById("listaCampanhas");
const emailPublico=document.getElementById("emailPublico");
const whatsappPublico=document.getElementById("whatsappPublico");
const emailPublicoResumo=document.getElementById("emailPublicoResumo");
const whatsappPublicoResumo=document.getElementById("whatsappPublicoResumo");
const emailClientesEspecificos=document.getElementById("emailClientesEspecificos");
const whatsappClientesEspecificos=document.getElementById("whatsappClientesEspecificos");

function marketingEscape(valor){return String(valor??"").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;");}
function estatisticasMarketingCliente(cliente){const compras=historico.filter(item=>String(item.client_id)===String(cliente.id));const totalGasto=compras.reduce((soma,item)=>soma+Number(item.total||0),0);const datas=compras.map(item=>new Date(item.data_fechamento||item.data_abertura)).filter(data=>!Number.isNaN(data.getTime())).sort((a,b)=>b-a);return{totalGasto,quantidadeCompras:compras.length,ultimaCompra:datas[0]||null};}
function clientesDoPublico(tipo){if(tipo==="todos")return[...clientes];if(tipo==="top3")return[...clientes].map(cliente=>({cliente,stats:estatisticasMarketingCliente(cliente)})).filter(item=>item.stats.quantidadeCompras>0).sort((a,b)=>b.stats.totalGasto-a.stats.totalGasto).slice(0,3).map(item=>item.cliente);if(tipo==="frequentes")return[...clientes].map(cliente=>({cliente,stats:estatisticasMarketingCliente(cliente)})).filter(item=>item.stats.quantidadeCompras>0).sort((a,b)=>b.stats.quantidadeCompras-a.stats.quantidadeCompras).slice(0,3).map(item=>item.cliente);if(tipo==="inativos30"){const limite=new Date();limite.setDate(limite.getDate()-30);return clientes.filter(cliente=>{const stats=estatisticasMarketingCliente(cliente);return !stats.ultimaCompra||stats.ultimaCompra<limite;});}return[];}
function clienteElegivelCanal(cliente,canal){return canal==="email"?Boolean(String(cliente.email||"").trim()):Boolean(String(cliente.phone||"").trim());}
function renderizarClientesEspecificos(container,canal){if(!container)return;container.innerHTML="";if(clientes.length===0){container.innerHTML='<p class="muted">Nenhum cliente cadastrado.</p>';return;}const grid=document.createElement("div");grid.className="marketing-check-grid";clientes.forEach(cliente=>{const elegivel=clienteElegivelCanal(cliente,canal);const label=document.createElement("label");label.className=`marketing-check-item ${elegivel?"":"disabled"}`;const checkbox=document.createElement("input");checkbox.type="checkbox";checkbox.value=cliente.id;checkbox.dataset.marketingClient="true";checkbox.disabled=!elegivel;const texto=document.createElement("span");const contato=canal==="email"?cliente.email:cliente.phone;texto.textContent=`${cliente.name}${contato?" — "+contato:" — sem "+(canal==="email"?"e-mail":"telefone")}`;label.append(checkbox,texto);grid.appendChild(label);});container.appendChild(grid);container.querySelectorAll('input[data-marketing-client="true"]').forEach(input=>input.addEventListener("change",atualizarMarketingCompleto));}
function listaSelecionadaMarketing(select,container,canal){if(!select)return[];let base;if(select.value==="especificos"){const ids=[...container.querySelectorAll('input[data-marketing-client="true"]:checked')].map(i=>String(i.value));base=clientes.filter(c=>ids.includes(String(c.id)));}else{base=clientesDoPublico(select.value);}return base.filter(cliente=>clienteElegivelCanal(cliente,canal));}
function idsPublicoMarketing(select,container){if(!select)return null;if(select.value==="todos")return null;if(select.value==="especificos")return[...container.querySelectorAll('input[data-marketing-client="true"]:checked')].map(input=>Number(input.value));return clientesDoPublico(select.value).map(cliente=>cliente.id);}
function atualizarPublicoMarketing(select,resumo,container,canal){if(!select)return;const tipo=select.value;if(container)container.classList.toggle("active",tipo==="especificos");if(tipo==="especificos")renderizarClientesEspecificos(container,canal);const elegiveis=listaSelecionadaMarketing(select,container,canal);const totalBase=tipo==="especificos"?elegiveis.length:clientesDoPublico(tipo).length;if(resumo)resumo.textContent=`${elegiveis.length} destinatário(s) elegível(is)${totalBase>elegiveis.length?` · ${totalBase-elegiveis.length} sem ${canal==="email"?"e-mail":"telefone"}`:""}.`;}
function substituirNomeMarketing(texto,nome){return String(texto||"").replaceAll("{nome}",nome||"Cliente");}
function primeiroClientePreview(){const lista=listaSelecionadaMarketing(emailPublico,emailClientesEspecificos,"email");return lista[0]||clientes.find(c=>c.email)||{name:"Cliente"};}
function atualizarPreviewMarketing(){const cliente=primeiroClientePreview();const nomeConta=(usuarioAtual?.name||session?.name||"Seu negócio").trim();const emailConta=(usuarioAtual?.email||session?.email||"seu@email.com").trim();const assunto=(emailAssunto?.value||"").trim()||"Sua campanha";const mensagem=(emailMensagem?.value||"").trim()||"Escreva uma mensagem para visualizar o e-mail.";const setText=(id,valor)=>{const el=document.getElementById(id);if(el)el.textContent=valor;};setText("marketingPreviewFrom",`${nomeConta} via Vynce <no-reply@vynce.tech>`);setText("marketingPreviewReply",emailConta);setText("marketingPreviewSubject",substituirNomeMarketing(assunto,cliente.name));setText("marketingPreviewBrand",nomeConta);setText("marketingPreviewTitle",substituirNomeMarketing(assunto,cliente.name));setText("marketingPreviewMessage",substituirNomeMarketing(mensagem,cliente.name));const ac=document.getElementById("emailAssuntoCount");if(ac)ac.textContent=`${emailAssunto?.value.length||0}/200`;const mc=document.getElementById("emailMensagemCount");if(mc)mc.textContent=`${emailMensagem?.value.length||0}/5000`;}
function atualizarMarketingCompleto(){const total=clientes.length;const comEmail=clientes.filter(c=>c.email).length;const set=(id,v)=>{const el=document.getElementById(id);if(el)el.textContent=v;};set("marketingTotalClientes",total);set("marketingClientesEmail",comEmail);set("marketingClientesSemEmail",total-comEmail);set("marketingTotalCampanhas",campanhas.length);if(emailPublico){const list=listaSelecionadaMarketing(emailPublico,emailClientesEspecificos,"email");set("emailDestinatariosCount",`${list.length} destinatário${list.length===1?"":"s"}`);if(emailPublico.value!=="especificos")atualizarPublicoMarketing(emailPublico,emailPublicoResumo,emailClientesEspecificos,"email");}if(whatsappPublico&&whatsappPublico.value!=="especificos")atualizarPublicoMarketing(whatsappPublico,whatsappPublicoResumo,whatsappClientesEspecificos,"whatsapp");atualizarPreviewMarketing();}
function validarPublicoMarketing(ids){if(Array.isArray(ids)&&ids.length===0){mostrarNotificacao("Esse público não possui destinatários elegíveis.","warning","Nenhum destinatário");return false;}return true;}
emailPublico?.addEventListener("change",()=>{atualizarPublicoMarketing(emailPublico,emailPublicoResumo,emailClientesEspecificos,"email");atualizarMarketingCompleto();});
whatsappPublico?.addEventListener("change",()=>atualizarPublicoMarketing(whatsappPublico,whatsappPublicoResumo,whatsappClientesEspecificos,"whatsapp"));
emailAssunto?.addEventListener("input",atualizarPreviewMarketing);emailMensagem?.addEventListener("input",atualizarPreviewMarketing);
document.querySelectorAll(".marketing-variable-chip").forEach(btn=>btn.addEventListener("click",()=>{if(!emailMensagem)return;const valor=btn.dataset.variable||"{nome}";const inicio=emailMensagem.selectionStart??emailMensagem.value.length;const fim=emailMensagem.selectionEnd??inicio;emailMensagem.value=emailMensagem.value.slice(0,inicio)+valor+emailMensagem.value.slice(fim);emailMensagem.focus();emailMensagem.selectionStart=emailMensagem.selectionEnd=inicio+valor.length;atualizarPreviewMarketing();}));
const MARKETING_TEMPLATES={promocao:{subject:"Uma condição especial para você, {nome}",message:"Olá, {nome}!\n\nPreparamos uma condição especial para você. Entre em contato com a gente para saber mais.\n\nEsperamos você!"},reativacao:{subject:"Sentimos sua falta, {nome}",message:"Olá, {nome}!\n\nFaz um tempinho que não vemos você por aqui. Será um prazer receber você novamente.\n\nQuando quiser, fale com a gente e agende seu próximo atendimento."},agradecimento:{subject:"Obrigado pela confiança, {nome}",message:"Olá, {nome}!\n\nObrigado por escolher nosso trabalho. Sua confiança é muito importante para nós.\n\nEsperamos ver você novamente em breve!"}};
document.querySelectorAll(".marketing-template-btn").forEach(btn=>btn.addEventListener("click",()=>{const modelo=MARKETING_TEMPLATES[btn.dataset.template];if(!modelo)return;emailAssunto.value=modelo.subject;emailMensagem.value=modelo.message;atualizarPreviewMarketing();}));
if(enviarEmailBtn){enviarEmailBtn.onclick=async function(){const assunto=emailAssunto.value.trim();const mensagem=emailMensagem.value.trim();if(!assunto){mostrarNotificacao("Informe um assunto para a campanha.","warning","Assunto obrigatório");emailAssunto.focus();return;}if(!mensagem){mostrarNotificacao("Escreva a mensagem do e-mail.","warning","Mensagem obrigatória");emailMensagem.focus();return;}const clientIds=idsPublicoMarketing(emailPublico,emailClientesEspecificos);if(!validarPublicoMarketing(clientIds))return;const elegiveis=listaSelecionadaMarketing(emailPublico,emailClientesEspecificos,"email");if(elegiveis.length===0){mostrarNotificacao("Nenhum cliente selecionado possui e-mail cadastrado.","warning","Sem destinatários");return;}const confirmou=confirm(`Enviar esta campanha para ${elegiveis.length} destinatário(s)?\n\nAssunto: ${assunto}\n\nO envio não poderá ser desfeito.`);if(!confirmou)return;const textoOriginal=enviarEmailBtn.textContent;enviarEmailBtn.disabled=true;enviarEmailBtn.textContent=`Enviando para ${elegiveis.length} cliente(s)...`;try{const resultado=await Api.post("/campaigns",{channel:"email",subject:assunto,message:mensagem,client_ids:clientIds},{timeout:65000});const c=resultado.campaign;mostrarNotificacao(`${c.total_enviados} de ${c.total_destinatarios} e-mail(s) colocados para envio${c.total_falhas?` · ${c.total_falhas} falha(s)`:""}.`,c.total_falhas?"warning":"success",c.total_falhas?"Campanha concluída com alertas":"Campanha enviada");emailAssunto.value="";emailMensagem.value="";await carregarCampanhas();renderizarCampanhas();atualizarMarketingCompleto();}catch(err){mostrarErro(err);}finally{enviarEmailBtn.disabled=false;enviarEmailBtn.textContent=textoOriginal;atualizarPreviewMarketing();}};}
if(gerarWhatsappBtn){gerarWhatsappBtn.onclick=async function(){const mensagem=whatsappMensagem.value.trim();if(!mensagem){mostrarNotificacao("Escreva a mensagem.","warning","Mensagem obrigatória");return;}const clientIds=idsPublicoMarketing(whatsappPublico,whatsappClientesEspecificos);if(!validarPublicoMarketing(clientIds))return;try{gerarWhatsappBtn.disabled=true;gerarWhatsappBtn.textContent="Preparando...";const resultado=await Api.post("/campaigns",{channel:"whatsapp",message:mensagem,client_ids:clientIds});renderizarLinksWhatsapp(resultado.whatsapp_links||[]);mostrarNotificacao("Os contatos foram preparados. Clique em Enviar para abrir a conversa no WhatsApp.","success","Mensagens preparadas");await carregarCampanhas();renderizarCampanhas();atualizarMarketingCompleto();}catch(err){mostrarErro(err);}finally{gerarWhatsappBtn.disabled=false;gerarWhatsappBtn.textContent="Gerar links do WhatsApp";}};}
function renderizarLinksWhatsapp(links){if(!listaWhatsappLinks)return;listaWhatsappLinks.innerHTML="";if(links.length===0){listaWhatsappLinks.innerHTML='<p class="muted">Nenhum cliente com telefone cadastrado.</p>';return;}links.forEach(item=>{const div=document.createElement("div");div.className="whatsapp-link-item";const span=document.createElement("span");span.textContent=`${item.client_name} — ${item.phone}`;const a=document.createElement("a");a.href=item.link;a.target="_blank";a.rel="noopener";a.textContent="Enviar";div.append(span,a);listaWhatsappLinks.appendChild(div);});}
function renderizarCampanhas(){if(!listaCampanhas)return;listaCampanhas.innerHTML="";if(campanhas.length===0){listaCampanhas.innerHTML='<p class="muted">Nenhuma campanha enviada ainda.</p>';atualizarMarketingCompleto();return;}campanhas.forEach(campanha=>{const div=document.createElement("article");div.className="marketing-history-item";const canal=campanha.channel==="email"?"E-mail":"WhatsApp";const sucesso=Number(campanha.total_falhas||0)===0;div.innerHTML=`<div class="marketing-history-icon">${campanha.channel==="email"?"✉":"↗"}</div><div class="marketing-history-content"><div class="marketing-history-title-row"><h4>${marketingEscape(canal)}${campanha.subject?" — "+marketingEscape(campanha.subject):""}</h4><span class="marketing-history-status ${sucesso?"success":"warning"}">${sucesso?"Concluída":"Com falhas"}</span></div><p class="marketing-history-message">${marketingEscape(campanha.message)}</p><div class="marketing-history-meta"><span>${campanha.total_destinatarios} destinatário(s)</span><span class="success">${campanha.total_enviados} enviados</span><span class="${campanha.total_falhas?"danger":""}">${campanha.total_falhas} falha(s)</span><span>${formatarData(campanha.created_at)} às ${formatarHora(campanha.created_at)}</span></div></div>`;listaCampanhas.appendChild(div);});atualizarMarketingCompleto();}

/* =====================================================
   CONFIGURAÇÕES (perfil, senha, tema)
===================================================== */


let usuarioAtual = null;

const configNome = document.getElementById("configNome");
const configEmail = document.getElementById("configEmail");
const configTelefone = document.getElementById("configTelefone");
const salvarPerfilBtn = document.getElementById("salvarPerfilBtn");

const configSenhaAtual = document.getElementById("configSenhaAtual");
const configSenhaNova = document.getElementById("configSenhaNova");
const trocarSenhaBtn = document.getElementById("trocarSenhaBtn");

const temaToggle = document.getElementById("temaToggle");

const TEMA_KEY = "vincy_tema";


function aplicarTema(tema, salvarLocal = true){

    const temaSeguro = tema === "claro" ? "claro" : "escuro";

    // Troca visual instantânea, sem esperar o backend.
    document.documentElement.setAttribute("data-theme", temaSeguro);

    if(salvarLocal){
        localStorage.setItem(TEMA_KEY, temaSeguro);
    }

    if(temaToggle){
        temaToggle.checked = (temaSeguro === "claro");
    }

    // Atualiza somente a aparência do gráfico.
    requestAnimationFrame(()=>{
        if(typeof renderizarGraficoFinanceiro === "function"){
            renderizarGraficoFinanceiro();
        }
    });
}


function preencherConfiguracoesUsuario(){

    const sessao = Auth.getSession();

    const nome =
        (usuarioAtual && usuarioAtual.name) ||
        (sessao && sessao.name) ||
        "";

    const email =
        (usuarioAtual && usuarioAtual.email) ||
        (sessao && sessao.email) ||
        "";

    const telefone =
        (usuarioAtual && usuarioAtual.phone) ||
        "";

    if(configNome) configNome.value = nome;
    if(configEmail) configEmail.value = email;
    if(configTelefone) configTelefone.value = telefone;

    const configDadosStatus = document.getElementById("configDadosStatus");

    if(configDadosStatus){
        configDadosStatus.textContent = usuarioAtual
            ? "Dados atuais carregados."
            : "Exibindo os dados salvos da sessão.";
    }
}


// Aplica imediatamente o último tema escolhido pelo usuário.
// Isso impede "piscar" ou voltar de tema quando uma resposta da API chega.
const temaInicialLocal = localStorage.getItem(TEMA_KEY) || "claro";

if(!localStorage.getItem(TEMA_KEY)){
    localStorage.setItem(TEMA_KEY, temaInicialLocal);
}

aplicarTema(temaInicialLocal, false);


if(temaToggle){

    temaToggle.onchange = async function(){

        const novoTema = temaToggle.checked ? "claro" : "escuro";

        // Primeiro muda na tela e salva localmente.
        aplicarTema(novoTema, true);

        // Depois sincroniza com o backend sem bloquear a interface.
        if(usuarioAtual){

            const userId = usuarioAtual.id;

            try{
                const atualizado = await Api.put(`/users/${userId}`, {
                    theme: novoTema
                });

                // Atualiza apenas os dados recebidos.
                // NÃO reaplica o tema vindo da resposta para evitar corrida.
                usuarioAtual = {
                    ...usuarioAtual,
                    ...atualizado,
                    theme: novoTema
                };

            }catch(err){

                console.warn(
                    "Tema alterado localmente, mas não foi possível sincronizar com o servidor:",
                    err
                );
            }
        }
    };
}


async function carregarUsuarioAtual(){

    const configDadosStatus = document.getElementById("configDadosStatus");

    preencherConfiguracoesUsuario();

    if(configDadosStatus){
        configDadosStatus.textContent = "Atualizando seus dados...";
    }

    try{

        const atualizado = await Api.get("/users/me");

        usuarioAtual = atualizado;

        preencherConfiguracoesUsuario();

        // O tema local tem prioridade visual para evitar que uma resposta
        // atrasada da API troque o tema enquanto o usuário usa o sistema.
        const temaLocal = localStorage.getItem(TEMA_KEY);

        if(!temaLocal && atualizado.theme){
            aplicarTema(atualizado.theme, true);
        }else if(temaLocal){
            aplicarTema(temaLocal, false);
        }

        return usuarioAtual;

    }catch(err){

        if(configDadosStatus){
            configDadosStatus.textContent =
                "Não foi possível atualizar os dados agora. Os dados salvos continuam visíveis.";
        }

        throw err;
    }
}


if(salvarPerfilBtn){

    salvarPerfilBtn.onclick = async function(){

        if(!usuarioAtual) return;

        try{
            const atualizado = await Api.put(`/users/${usuarioAtual.id}`, {
                name: configNome.value.trim(),
                email: configEmail.value.trim(),
                phone: configTelefone.value.trim() || null
            });

            usuarioAtual = atualizado;

            const sessao = Auth.getSession();
            if(sessao){
                Auth.saveSession({ ...sessao, name: atualizado.name, email: atualizado.email });
            }
            if(userName) userName.textContent = atualizado.name;
            if(userEmail) userEmail.textContent = atualizado.email;

            alert("Dados atualizados!");
        }catch(err){
            mostrarErro(err);
        }
    };
}


if(trocarSenhaBtn){

    trocarSenhaBtn.onclick = async function(){

        if(!usuarioAtual) return;

        const senhaAtual = configSenhaAtual.value;
        const senhaNova = configSenhaNova.value;

        if(!senhaAtual || !senhaNova){
            alert("Preencha a senha atual e a nova senha");
            return;
        }

        if(senhaNova.length < 6){
            alert("A nova senha precisa ter pelo menos 6 caracteres");
            return;
        }

        try{
            await Api.put(`/users/${usuarioAtual.id}`, {
                current_password: senhaAtual,
                password: senhaNova
            });

            configSenhaAtual.value = "";
            configSenhaNova.value = "";

            alert("Senha alterada com sucesso!");
        }catch(err){
            mostrarErro(err);
        }
    };
}




/* =====================================================
   GRÁFICO FINANCEIRO
===================================================== */


let graficoFinanceiroInstance = null;
let periodoGraficoAtual = "1m";

const lancamentoDescricao = document.getElementById("lancamentoDescricao");
const lancamentoValor = document.getElementById("lancamentoValor");
const salvarLancamentoBtn = document.getElementById("salvarLancamentoBtn");
const listaLancamentos = document.getElementById("listaLancamentos");
const novoLancamentoBtn = document.getElementById("novoLancamentoBtn");
const lancamentoForm = document.getElementById("lancamentoForm");
const botoesPeriodoGrafico = document.querySelectorAll(".chart-period-btn");

let lancamentos = [];


botoesPeriodoGrafico.forEach(botao=>{

    botao.addEventListener("click", ()=>{

        periodoGraficoAtual = botao.dataset.periodo || "6m";

        botoesPeriodoGrafico.forEach(item=>
            item.classList.toggle("active", item === botao)
        );

        renderizarGraficoFinanceiro();
    });
});


if(novoLancamentoBtn){
    novoLancamentoBtn.onclick = function(){
        lancamentoForm.classList.toggle("active");
    };
}


if(salvarLancamentoBtn){

    salvarLancamentoBtn.onclick = async function(){

        const descricao = lancamentoDescricao.value.trim();
        const valor = Number(lancamentoValor.value);

        if(descricao==="" || !valor || valor<=0){
            alert("Informe a descrição e o valor da despesa");
            return;
        }

        try{
            await Api.post("/finance", {
                type: "saida",
                description: descricao,
                amount: valor
            });

            lancamentoDescricao.value = "";
            lancamentoValor.value = "";
            lancamentoForm.classList.remove("active");

            await carregarFinanceiro();
            renderizarLancamentos();
            gerarRelatorios();
            renderizarGraficoFinanceiro();
            await atualizarDashboardCards();

        }catch(err){
            mostrarErro(err);
        }
    };
}


function renderizarLancamentos(){

    if(!listaLancamentos) return;

    listaLancamentos.innerHTML = "";

    if(lancamentos.length===0){
        listaLancamentos.innerHTML = `<p class="muted">Nenhum lançamento ainda.</p>`;
        return;
    }

    const despesas = lancamentos
        .filter(item=>item.type === "saida")
        .slice(0,20);

    if(despesas.length===0){
        listaLancamentos.innerHTML =
            `<p class="muted">Nenhuma despesa cadastrada.</p>`;
        return;
    }

    despesas.forEach(lancamento=>{
        const div = document.createElement("div");
        div.className = "item-card";
        div.innerHTML = `
            <div class="item-info">
                <h4>${lancamento.description}</h4>
                <p>Despesa · ${dinheiro(lancamento.amount)} · ${formatarData(lancamento.created_at)}</p>
            </div>
        `;
        listaLancamentos.appendChild(div);
    });
}


function inicioPeriodoGrafico(periodo){

    const agora = new Date();
    const inicio = new Date(agora);

    switch(periodo){

        case "1d":
            inicio.setHours(0,0,0,0);
            return inicio;

        case "1w":
            inicio.setDate(inicio.getDate() - 6);
            inicio.setHours(0,0,0,0);
            return inicio;

        /*
          "1 mês" agora significa a competência atual:
          SEMPRE começa no dia 01, em vez de usar os últimos 30 dias.
        */
        case "1m":
            return new Date(
                agora.getFullYear(),
                agora.getMonth(),
                1,
                0,0,0,0
            );

        case "3m":
            inicio.setMonth(inicio.getMonth() - 2, 1);
            inicio.setHours(0,0,0,0);
            return inicio;

        case "6m":
            inicio.setMonth(inicio.getMonth() - 5, 1);
            inicio.setHours(0,0,0,0);
            return inicio;

        case "ytd":
            return new Date(agora.getFullYear(), 0, 1);

        case "1y":
            inicio.setMonth(inicio.getMonth() - 11, 1);
            inicio.setHours(0,0,0,0);
            return inicio;

        case "5y":
            return new Date(agora.getFullYear() - 4, 0, 1);

        case "all":{
            const datas = [
                ...lancamentos.map(item=>new Date(item.created_at)),
                ...historico.map(item=>new Date(
                    item.data_fechamento ||
                    item.updated_at ||
                    item.data_abertura ||
                    item.created_at
                )),
                ...(typeof movimentosFinanceirosV2ParaGrafico === "function"
                    ? movimentosFinanceirosV2ParaGrafico().map(item=>new Date(item.date))
                    : [])
            ].filter(data=>!Number.isNaN(data.getTime()));

            if(datas.length===0){
                return new Date(agora.getFullYear(), 0, 1);
            }

            const primeira = new Date(
                Math.min(...datas.map(data=>data.getTime()))
            );

            return new Date(
                primeira.getFullYear(),
                primeira.getMonth(),
                1
            );
        }

        default:
            inicio.setMonth(inicio.getMonth() - 5, 1);
            return inicio;
    }
}


function chaveBucket(data, modo){

    if(modo === "hora"){
        return `${data.getFullYear()}-${String(data.getMonth()+1).padStart(2,"0")}-${String(data.getDate()).padStart(2,"0")} ${String(data.getHours()).padStart(2,"0")}`;
    }

    if(modo === "dia"){
        return `${data.getFullYear()}-${String(data.getMonth()+1).padStart(2,"0")}-${String(data.getDate()).padStart(2,"0")}`;
    }

    if(modo === "mes"){
        return `${data.getFullYear()}-${String(data.getMonth()+1).padStart(2,"0")}`;
    }

    return String(data.getFullYear());
}


function labelBucket(data, modo){

    if(modo === "hora"){
        return `${String(data.getHours()).padStart(2,"0")}h`;
    }

    if(modo === "dia"){
        return data.toLocaleDateString("pt-BR", {
            day:"2-digit",
            month:"2-digit"
        });
    }

    if(modo === "mes"){
        return data.toLocaleDateString("pt-BR", {
            month:"short",
            year:"2-digit"
        }).replace(".", "");
    }

    return String(data.getFullYear());
}


function bucketsPeriodo(periodo){

    const agora = new Date();
    const inicio = inicioPeriodoGrafico(periodo);
    let modo;

    if(periodo === "1d") modo = "hora";
    else if(periodo === "1w" || periodo === "1m") modo = "dia";
    else if(periodo === "5y") modo = "ano";
    else if(periodo === "all"){
        const meses = (agora.getFullYear() - inicio.getFullYear()) * 12 +
            (agora.getMonth() - inicio.getMonth());
        modo = meses > 24 ? "ano" : "mes";
    }else modo = "mes";

    const buckets = [];

    if(modo === "hora"){

        for(let hora=0; hora<24; hora+=3){
            const data = new Date(agora);
            data.setHours(hora,0,0,0);

            buckets.push({
                key:`${data.getFullYear()}-${String(data.getMonth()+1).padStart(2,"0")}-${String(data.getDate()).padStart(2,"0")} ${String(hora).padStart(2,"0")}`,
                label:`${String(hora).padStart(2,"0")}h`,
                inicio:data,
                fim:new Date(data.getFullYear(), data.getMonth(), data.getDate(), hora+3, 0, 0, 0)
            });
        }

        return { modo, buckets, inicio };
    }

    let cursor = new Date(inicio);

    if(modo === "dia"){
        cursor.setHours(0,0,0,0);

        while(cursor <= agora){
            const data = new Date(cursor);
            buckets.push({
                key:chaveBucket(data, "dia"),
                label:labelBucket(data, "dia"),
                inicio:data,
                fim:new Date(data.getFullYear(), data.getMonth(), data.getDate()+1)
            });
            cursor.setDate(cursor.getDate()+1);
        }
    }

    if(modo === "mes"){
        cursor = new Date(inicio.getFullYear(), inicio.getMonth(), 1);

        while(cursor <= agora){
            const data = new Date(cursor);
            buckets.push({
                key:chaveBucket(data, "mes"),
                label:labelBucket(data, "mes"),
                inicio:data,
                fim:new Date(data.getFullYear(), data.getMonth()+1, 1)
            });
            cursor.setMonth(cursor.getMonth()+1);
        }
    }

    if(modo === "ano"){
        cursor = new Date(inicio.getFullYear(), 0, 1);

        while(cursor <= agora){
            const data = new Date(cursor);
            buckets.push({
                key:chaveBucket(data, "ano"),
                label:labelBucket(data, "ano"),
                inicio:data,
                fim:new Date(data.getFullYear()+1, 0, 1)
            });
            cursor.setFullYear(cursor.getFullYear()+1);
        }
    }

    return { modo, buckets, inicio };
}



function dataValidaFinanceira(valor){
    const d = new Date(valor);
    return Number.isNaN(d.getTime()) ? null : d;
}


function movimentosFinanceirosConsolidados(){
    const movimentos = [];

    /*
      ENTRADAS:
      toda comanda finalizada é uma entrada realizada.
    */
    historico.forEach(comanda=>{
        const data = dataValidaFinanceira(
            comanda.data_fechamento ||
            comanda.updated_at ||
            comanda.data_abertura ||
            comanda.created_at
        );

        if(!data) return;

        const valor = Number(comanda.total || 0);
        if(!(valor > 0)) return;

        movimentos.push({
            id:`entrada-${comanda.id ?? Math.random()}`,
            type:"entrada",
            amount:valor,
            date:data,
            description:
                comanda.cliente_nome ||
                comanda.client_name ||
                "Atendimento",
            source:"comanda"
        });
    });

    /*
      SAÍDAS LEGADAS:
      lançamentos antigos da API continuam válidos.
      Eles entram UMA vez aqui.
    */
    lancamentos
        .filter(item=>item.type === "saida")
        .forEach(item=>{
            const data = dataValidaFinanceira(item.created_at);
            const valor = Number(item.amount || 0);

            if(!data || !(valor > 0)) return;

            movimentos.push({
                id:`legacy-${item.id}`,
                type:"saida",
                amount:valor,
                date:data,
                description:item.description || "Despesa",
                source:"legacy"
            });
        });

    /*
      SAÍDAS DO FINANCEIRO 3.x:
      só o que efetivamente está PAGO vira saída realizada.
      Importante: esta função NÃO inclui despesas legadas,
      porque elas já entraram acima via /finance.
    */

    Object.entries(financeiroV2State.closings || {})
        .forEach(([competencia, fechamento])=>{

            (fechamento.fixedItems || [])
                .filter(item=>Boolean(item.paid))
                .forEach(item=>{
                    const data =
                        dataValidaFinanceira(item.paidAt) ||
                        competenciaParaData(
                            competencia,
                            item.dueDay || 1
                        );

                    movimentos.push({
                        id:`closed-fixed-${competencia}-${item.id}`,
                        type:"saida",
                        amount:Number(item.amount || 0),
                        date:data,
                        description:item.description || "Despesa fixa",
                        source:"fixed"
                    });
                });

            (fechamento.additionalItems || [])
                .filter(item=>
                    item.paid === undefined
                        ? true
                        : Boolean(item.paid)
                )
                .forEach(item=>{
                    const data =
                        dataValidaFinanceira(item.paidAt) ||
                        dataValidaFinanceira(item.createdAt) ||
                        competenciaParaData(competencia, 15);

                    movimentos.push({
                        id:`closed-additional-${competencia}-${item.id}`,
                        type:"saida",
                        amount:Number(item.amount || 0),
                        date:data,
                        description:item.description || "Despesa adicional",
                        source:"additional"
                    });
                });
        });

    /*
      Competências ainda abertas.
    */
    Object.entries(financeiroV2State.additional || {})
        .forEach(([competencia, itens])=>{

            if(financeiroV2State.closings?.[competencia]){
                return;
            }

            (itens || [])
                .filter(item=>Boolean(item.paid))
                .forEach(item=>{
                    const data =
                        dataValidaFinanceira(item.paidAt) ||
                        dataValidaFinanceira(item.createdAt) ||
                        competenciaParaData(competencia, 15);

                    movimentos.push({
                        id:`open-additional-${competencia}-${item.id}`,
                        type:"saida",
                        amount:Number(item.amount || 0),
                        date:data,
                        description:item.description || "Despesa adicional",
                        source:"additional"
                    });
                });
        });

    /*
      Fixas pagas em competências abertas.
    */
    (financeiroV2State.fixedRules || [])
        .forEach(regra=>{

            Object.entries(financeiroV2State.fixedStatus || {})
                .forEach(([competencia, statusMes])=>{

                    if(financeiroV2State.closings?.[competencia]){
                        return;
                    }

                    if(!regraFixaValeNaCompetencia(regra, competencia)){
                        return;
                    }

                    const status = statusMes?.[regra.id];

                    if(!status?.paid){
                        return;
                    }

                    const data =
                        dataValidaFinanceira(status.paidAt) ||
                        competenciaParaData(
                            competencia,
                            regra.dueDay || 1
                        );

                    movimentos.push({
                        id:`open-fixed-${competencia}-${regra.id}`,
                        type:"saida",
                        amount:Number(regra.amount || 0),
                        date:data,
                        description:regra.description || "Despesa fixa",
                        source:"fixed"
                    });
                });
        });

    return movimentos
        .filter(item=>
            item.date instanceof Date &&
            !Number.isNaN(item.date.getTime()) &&
            Number(item.amount) > 0
        )
        .sort((a,b)=>a.date-b.date);
}


function resumoMovimentosNoPeriodo(inicio, fim){
    const movimentos = movimentosFinanceirosConsolidados()
        .filter(item=>
            item.date >= inicio &&
            item.date < fim
        );

    const entradas = movimentos
        .filter(item=>item.type === "entrada")
        .reduce((soma,item)=>soma+Number(item.amount||0),0);

    const saidas = movimentos
        .filter(item=>item.type === "saida")
        .reduce((soma,item)=>soma+Number(item.amount||0),0);

    return {
        entradas,
        saidas,
        saldo:entradas-saidas,
        movimentos
    };
}


function corComAlpha(cor, alpha){

    const hex = String(cor || "").trim();

    if(/^#[0-9a-f]{6}$/i.test(hex)){
        const r = parseInt(hex.slice(1,3),16);
        const g = parseInt(hex.slice(3,5),16);
        const b = parseInt(hex.slice(5,7),16);
        return `rgba(${r},${g},${b},${alpha})`;
    }

    return hex;
}


function escaparSvg(valor){
    return String(valor ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
}


function caminhoLinha(valores, largura, altura, margem, maximo){

    if(!valores.length) return "";

    const larguraUtil = largura - margem.esq - margem.dir;
    const alturaUtil = altura - margem.top - margem.bottom;

    return valores.map((valor, indice)=>{

        const x = valores.length === 1
            ? margem.esq + larguraUtil / 2
            : margem.esq + (indice / (valores.length - 1)) * larguraUtil;

        const y = margem.top + alturaUtil -
            (Number(valor || 0) / maximo) * alturaUtil;

        return `${indice === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;

    }).join(" ");
}


function pontosLinha(valores, largura, altura, margem, maximo){

    const larguraUtil = largura - margem.esq - margem.dir;
    const alturaUtil = altura - margem.top - margem.bottom;

    return valores.map((valor, indice)=>{

        const x = valores.length === 1
            ? margem.esq + larguraUtil / 2
            : margem.esq + (indice / (valores.length - 1)) * larguraUtil;

        const y = margem.top + alturaUtil -
            (Number(valor || 0) / maximo) * alturaUtil;

        return { x, y, valor:Number(valor || 0) };
    });
}



function caminhoArea(valores, largura, altura, margem, maximo){

    if(!valores.length) return "";

    const pontos = pontosLinha(
        valores,
        largura,
        altura,
        margem,
        maximo
    );

    if(!pontos.length) return "";

    const baseY = altura - margem.bottom;

    const linha = pontos
        .map((ponto, indice)=>
            `${indice === 0 ? "M" : "L"} ${ponto.x.toFixed(2)} ${ponto.y.toFixed(2)}`
        )
        .join(" ");

    const ultimo = pontos[pontos.length - 1];
    const primeiro = pontos[0];

    return `
        ${linha}
        L ${ultimo.x.toFixed(2)} ${baseY}
        L ${primeiro.x.toFixed(2)} ${baseY}
        Z
    `;
}


function animarLinhaGrafico(path, atraso = 0){

    if(!path) return;

    const comprimento = path.getTotalLength();

    path.style.strokeDasharray = `${comprimento}`;
    path.style.strokeDashoffset = `${comprimento}`;

    requestAnimationFrame(()=>{

        path.style.transition =
            `stroke-dashoffset .95s cubic-bezier(.22,.8,.25,1) ${atraso}ms`;

        path.style.strokeDashoffset = "0";
    });
}


function animarPontosGrafico(container){

    if(!container) return;

    const pontos = [
        ...container.querySelectorAll(".grafico-ponto")
    ];

    pontos.forEach((ponto, indice)=>{

        ponto.style.opacity = "0";
        ponto.style.transformBox = "fill-box";
        ponto.style.transformOrigin = "center";
        ponto.style.transform = "scale(.55)";

        setTimeout(()=>{

            ponto.style.transition =
                "opacity .28s ease, transform .38s cubic-bezier(.2,.9,.3,1.15)";

            ponto.style.opacity = "1";
            ponto.style.transform = "scale(1)";

        }, 280 + Math.min(indice * 22, 420));
    });
}


function renderizarGraficoFinanceiro(){

    const container =
        document.getElementById("graficoFinanceiro");

    if(!container) return;


    const {
        buckets,
        inicio
    } =
        bucketsPeriodo(periodoGraficoAtual);


    const agora = new Date();

    const fimPeriodo =
        periodoGraficoAtual === "1d"
            ? new Date(
                agora.getFullYear(),
                agora.getMonth(),
                agora.getDate()+1
              )
            : new Date(
                agora.getFullYear(),
                agora.getMonth(),
                agora.getDate()+1
              );


    const movimentos =
        movimentosFinanceirosConsolidados();


    const entradas =
        buckets.map(()=>0);

    const saidas =
        buckets.map(()=>0);


    movimentos.forEach(movimento=>{

        const indice =
            buckets.findIndex(bucket=>
                movimento.date >= bucket.inicio &&
                movimento.date < bucket.fim
            );

        if(indice < 0) return;

        if(movimento.type === "entrada"){
            entradas[indice] +=
                Number(movimento.amount || 0);
        }else{
            saidas[indice] +=
                Number(movimento.amount || 0);
        }
    });


    const totalEntradas =
        entradas.reduce(
            (soma,valor)=>soma+valor,
            0
        );

    const totalSaidas =
        saidas.reduce(
            (soma,valor)=>soma+valor,
            0
        );

    const saldoPeriodo =
        totalEntradas -
        totalSaidas;


    const kpiEntradas =
        document.getElementById(
            "graficoKpiEntradas"
        );

    const kpiSaidas =
        document.getElementById(
            "graficoKpiSaidas"
        );

    const kpiSaldo =
        document.getElementById(
            "graficoKpiSaldo"
        );


    if(kpiEntradas){
        kpiEntradas.textContent =
            dinheiro(totalEntradas);
    }


    if(kpiSaidas){
        kpiSaidas.textContent =
            totalSaidas > 0
                ? `- ${dinheiro(totalSaidas)}`
                : dinheiro(0);
    }


    if(kpiSaldo){
        aplicarValorFinanceiro(
            kpiSaldo,
            saldoPeriodo
        );
    }


    const entradasAssinadas =
        entradas.map(
            valor=>
                Math.abs(
                    Number(valor || 0)
                )
        );


    const saidasAssinadas =
        saidas.map(
            valor=>
                -Math.abs(
                    Number(valor || 0)
                )
        );


    const estilo =
        getComputedStyle(
            document.documentElement
        );


    const verde =
        estilo
            .getPropertyValue("--green")
            .trim() ||
        "#319b67";


    const vermelho =
        estilo
            .getPropertyValue("--red")
            .trim() ||
        "#d15362";


    const texto =
        estilo
            .getPropertyValue("--text")
            .trim() ||
        "#ffffff";


    const muted =
        estilo
            .getPropertyValue("--muted")
            .trim() ||
        "#90909a";


    const border =
        estilo
            .getPropertyValue("--border")
            .trim() ||
        "rgba(255,255,255,.10)";


    const largura = 1000;
    const altura = 420;


    const margem = {
        esq:88,
        dir:28,
        top:34,
        bottom:64
    };


    const larguraUtil =
        largura -
        margem.esq -
        margem.dir;


    const alturaUtil =
        altura -
        margem.top -
        margem.bottom;


    const maiorEntrada =
        Math.max(
            0,
            ...entradasAssinadas
        );


    const maiorSaida =
        Math.max(
            0,
            ...saidas
        );


    const maiorAbsoluto =
        Math.max(
            maiorEntrada,
            maiorSaida
        );


    /*
      Escala arredondada para números mais limpos no eixo.
    */
    function escalaBonita(valor){

        if(!(valor > 0)){
            return 100;
        }

        const bruto =
            valor * 1.18;

        const expoente =
            Math.pow(
                10,
                Math.floor(
                    Math.log10(bruto)
                )
            );

        const normal =
            bruto / expoente;

        let arredondado;

        if(normal <= 1){
            arredondado = 1;
        }else if(normal <= 2){
            arredondado = 2;
        }else if(normal <= 5){
            arredondado = 5;
        }else{
            arredondado = 10;
        }

        return arredondado * expoente;
    }


    const escalaMax =
        escalaBonita(
            maiorAbsoluto
        );


    const zeroY =
        margem.top +
        alturaUtil / 2;


    function yPorValor(valor){

        const normalizado =
            Math.max(
                -escalaMax,
                Math.min(
                    escalaMax,
                    Number(valor || 0)
                )
            )
            /
            escalaMax;

        return (
            zeroY -
            normalizado *
            (alturaUtil / 2)
        );
    }


    function pontosAssinados(valores){

        return valores.map(
            (valor,indice)=>{

                const x =
                    valores.length === 1
                        ? margem.esq +
                          larguraUtil / 2
                        : margem.esq +
                          (
                            indice /
                            (
                                valores.length -
                                1
                            )
                          ) *
                          larguraUtil;

                return {
                    x,
                    y:yPorValor(valor),
                    valor:Number(valor || 0)
                };
            }
        );
    }


    function caminhoDosPontos(pontos){

        if(!pontos.length){
            return "";
        }

        return pontos
            .map(
                (ponto,indice)=>
                    `${
                        indice === 0
                            ? "M"
                            : "L"
                    } ` +
                    `${ponto.x.toFixed(2)} ` +
                    `${ponto.y.toFixed(2)}`
            )
            .join(" ");
    }


    function areaAteZero(pontos){

        if(!pontos.length){
            return "";
        }

        const linha =
            caminhoDosPontos(pontos);

        const primeiro =
            pontos[0];

        const ultimo =
            pontos[
                pontos.length - 1
            ];

        return `
            ${linha}
            L ${ultimo.x.toFixed(2)} ${zeroY.toFixed(2)}
            L ${primeiro.x.toFixed(2)} ${zeroY.toFixed(2)}
            Z
        `;
    }


    const pontosEntradas =
        pontosAssinados(
            entradasAssinadas
        );


    const pontosSaidas =
        pontosAssinados(
            saidasAssinadas
        );


    const caminhoEntradas =
        caminhoDosPontos(
            pontosEntradas
        );


    const caminhoSaidas =
        caminhoDosPontos(
            pontosSaidas
        );


    const areaEntradas =
        areaAteZero(
            pontosEntradas
        );


    const areaSaidas =
        areaAteZero(
            pontosSaidas
        );


    let gridSvg = "";
    let labelsYSvg = "";


    const niveis =
        [1,.5,0,-.5,-1];


    niveis.forEach(
        nivel=>{

            const valor =
                escalaMax *
                nivel;

            const y =
                yPorValor(
                    valor
                );

            gridSvg += `
                <line
                    x1="${margem.esq}"
                    y1="${y}"
                    x2="${largura - margem.dir}"
                    y2="${y}"
                    stroke="${
                        nivel === 0
                            ? texto
                            : border
                    }"
                    stroke-opacity="${
                        nivel === 0
                            ? ".30"
                            : "1"
                    }"
                    stroke-width="${
                        nivel === 0
                            ? "1.5"
                            : "1"
                    }"
                    ${
                        nivel === 0
                            ? 'stroke-dasharray="5 6"'
                            : ""
                    }
                />
            `;

            labelsYSvg += `
                <text
                    x="${margem.esq - 14}"
                    y="${y + 4}"
                    text-anchor="end"
                    font-size="12"
                    font-weight="${
                        nivel === 0
                            ? "700"
                            : "600"
                    }"
                    fill="${
                        valor > 0
                            ? verde
                            : valor < 0
                                ? vermelho
                                : muted
                    }">
                    ${escaparSvg(
                        Number(valor)
                            .toLocaleString(
                                "pt-BR",
                                {
                                    style:"currency",
                                    currency:"BRL",
                                    maximumFractionDigits:0
                                }
                            )
                    )}
                </text>
            `;
        }
    );


    const maxRotulos = 10;


    const passoRotulo =
        Math.max(
            1,
            Math.ceil(
                buckets.length /
                maxRotulos
            )
        );


    let labelsXSvg = "";


    buckets.forEach(
        (bucket,indice)=>{

            if(
                indice %
                passoRotulo !== 0
                &&
                indice !==
                buckets.length - 1
            ){
                return;
            }

            const x =
                buckets.length === 1
                    ? margem.esq +
                      larguraUtil / 2
                    : margem.esq +
                      (
                        indice /
                        (
                            buckets.length -
                            1
                        )
                      ) *
                      larguraUtil;

            labelsXSvg += `
                <text
                    x="${x}"
                    y="${altura - 25}"
                    text-anchor="middle"
                    font-size="12"
                    fill="${muted}">
                    ${escaparSvg(
                        bucket.label
                    )}
                </text>
            `;
        }
    );


    const pontosEntradaSvg =
        pontosEntradas
            .map(
                (p,indice)=>`
                    <g
                        class="grafico-ponto grafico-ponto-entrada"
                        data-index="${indice}"
                        data-tipo="entrada"
                        data-periodo="${
                            escaparSvg(
                                buckets[indice]?.label ||
                                ""
                            )
                        }">

                        <circle
                            class="grafico-ponto-visivel"
                            cx="${p.x}"
                            cy="${p.y}"
                            r="4"
                            fill="${verde}">
                        </circle>

                        <circle
                            class="grafico-ponto-hit"
                            cx="${p.x}"
                            cy="${p.y}"
                            r="16"
                            fill="transparent">
                        </circle>
                    </g>
                `
            )
            .join("");


    const pontosSaidaSvg =
        pontosSaidas
            .map(
                (p,indice)=>`
                    <g
                        class="grafico-ponto grafico-ponto-saida"
                        data-index="${indice}"
                        data-tipo="saida"
                        data-periodo="${
                            escaparSvg(
                                buckets[indice]?.label ||
                                ""
                            )
                        }">

                        <circle
                            class="grafico-ponto-visivel"
                            cx="${p.x}"
                            cy="${p.y}"
                            r="4"
                            fill="${vermelho}">
                        </circle>

                        <circle
                            class="grafico-ponto-hit"
                            cx="${p.x}"
                            cy="${p.y}"
                            r="16"
                            fill="transparent">
                        </circle>
                    </g>
                `
            )
            .join("");


    const semDados =
        maiorAbsoluto === 0
            ? `
                <text
                    x="${largura / 2}"
                    y="${zeroY - 12}"
                    text-anchor="middle"
                    font-size="15"
                    font-weight="600"
                    fill="${texto}"
                    opacity=".72">
                    Nenhuma movimentação neste período
                </text>

                <text
                    x="${largura / 2}"
                    y="${zeroY + 16}"
                    text-anchor="middle"
                    font-size="12"
                    fill="${muted}">
                    Entradas aparecem acima e despesas pagas abaixo da linha zero.
                </text>
            `
            : "";


    container.innerHTML = `
        <div class="grafico-legenda">
            <span>
                <i class="grafico-legenda-cor entrada"></i>
                Entradas realizadas
            </span>

            <span>
                <i class="grafico-legenda-cor saida"></i>
                Saídas pagas
            </span>
        </div>

        <svg
            class="grafico-svg"
            viewBox="0 0 ${largura} ${altura}"
            preserveAspectRatio="none"
            aria-hidden="true">

            <defs>
                <linearGradient
                    id="graficoAreaEntrada"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1">

                    <stop
                        offset="0%"
                        stop-color="${verde}"
                        stop-opacity=".24">
                    </stop>

                    <stop
                        offset="100%"
                        stop-color="${verde}"
                        stop-opacity=".02">
                    </stop>
                </linearGradient>

                <linearGradient
                    id="graficoAreaSaida"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1">

                    <stop
                        offset="0%"
                        stop-color="${vermelho}"
                        stop-opacity=".02">
                    </stop>

                    <stop
                        offset="100%"
                        stop-color="${vermelho}"
                        stop-opacity=".22">
                    </stop>
                </linearGradient>
            </defs>

            ${gridSvg}
            ${labelsYSvg}
            ${labelsXSvg}

            <path
                class="grafico-area grafico-area-entrada"
                d="${areaEntradas}"
                fill="url(#graficoAreaEntrada)">
            </path>

            <path
                class="grafico-area grafico-area-saida"
                d="${areaSaidas}"
                fill="url(#graficoAreaSaida)">
            </path>

            <line
                class="grafico-guide"
                id="graficoGuide"
                x1="0"
                y1="${margem.top}"
                x2="0"
                y2="${altura - margem.bottom}"
                stroke="${muted}"
                stroke-opacity=".28"
                stroke-width="1.2"
                stroke-dasharray="4 6"
                visibility="hidden">
            </line>

            <path
                class="grafico-linha grafico-linha-entrada"
                d="${caminhoEntradas}"
                fill="none"
                stroke="${verde}"
                stroke-width="3.5"
                stroke-linecap="round"
                stroke-linejoin="round">
            </path>

            <path
                class="grafico-linha grafico-linha-saida"
                d="${caminhoSaidas}"
                fill="none"
                stroke="${vermelho}"
                stroke-width="3.5"
                stroke-linecap="round"
                stroke-linejoin="round">
            </path>

            ${pontosEntradaSvg}
            ${pontosSaidaSvg}
            ${semDados}
        </svg>

        <div
            class="grafico-tooltip"
            id="graficoTooltip"
            aria-hidden="true">
        </div>
    `;


    const tooltip =
        container.querySelector(
            "#graficoTooltip"
        );


    const guide =
        container.querySelector(
            "#graficoGuide"
        );


    const linhaEntrada =
        container.querySelector(
            ".grafico-linha-entrada"
        );


    const linhaSaida =
        container.querySelector(
            ".grafico-linha-saida"
        );


    animarLinhaGrafico(
        linhaEntrada,
        20
    );


    animarLinhaGrafico(
        linhaSaida,
        100
    );


    animarPontosGrafico(
        container
    );


    container
        .querySelectorAll(
            ".grafico-ponto"
        )
        .forEach(
            ponto=>{

                const indice =
                    Number(
                        ponto.dataset.index
                    );

                const mostrarTooltip =
                    event=>{

                        const periodo =
                            ponto.dataset.periodo ||
                            "";

                        const entrada =
                            Number(
                                entradas[
                                    indice
                                ] || 0
                            );

                        const saida =
                            Number(
                                saidas[
                                    indice
                                ] || 0
                            );

                        const saldo =
                            entrada -
                            saida;

                        tooltip.innerHTML = `
                            <span class="grafico-tooltip-periodo">
                                ${periodo}
                            </span>

                            <div class="grafico-tooltip-row">
                                <span class="grafico-tooltip-dot positivo"></span>
                                <strong>Entradas</strong>
                                <b class="valor-positivo">
                                    ${dinheiro(entrada)}
                                </b>
                            </div>

                            <div class="grafico-tooltip-row">
                                <span class="grafico-tooltip-dot negativo"></span>
                                <strong>Saídas</strong>
                                <b class="valor-negativo">
                                    ${saida > 0 ? "- " : ""}
                                    ${dinheiro(saida)}
                                </b>
                            </div>

                            <div class="grafico-tooltip-row grafico-tooltip-saldo">
                                <span></span>
                                <strong>Saldo</strong>
                                <b class="${
                                    saldo > 0
                                        ? "valor-positivo"
                                        : saldo < 0
                                            ? "valor-negativo"
                                            : "valor-zero"
                                }">
                                    ${dinheiro(saldo)}
                                </b>
                            </div>
                        `;

                        tooltip.classList.add(
                            "show"
                        );

                        tooltip.setAttribute(
                            "aria-hidden",
                            "false"
                        );

                        const pontoVisivel =
                            ponto.querySelector(
                                ".grafico-ponto-visivel"
                            );

                        if(
                            pontoVisivel &&
                            guide
                        ){

                            const cx =
                                Number(
                                    pontoVisivel
                                        .getAttribute(
                                            "cx"
                                        ) ||
                                    0
                                );

                            guide.setAttribute(
                                "x1",
                                cx
                            );

                            guide.setAttribute(
                                "x2",
                                cx
                            );

                            guide.setAttribute(
                                "visibility",
                                "visible"
                            );
                        }

                        moverTooltip(
                            event
                        );
                    };


                const moverTooltip =
                    event=>{

                        const rect =
                            container
                                .getBoundingClientRect();

                        let x =
                            event.clientX -
                            rect.left +
                            16;

                        let y =
                            event.clientY -
                            rect.top -
                            36;

                        const larguraTooltip =
                            tooltip.offsetWidth ||
                            220;

                        const alturaTooltip =
                            tooltip.offsetHeight ||
                            120;

                        if(
                            x +
                            larguraTooltip >
                            rect.width -
                            8
                        ){
                            x =
                                event.clientX -
                                rect.left -
                                larguraTooltip -
                                16;
                        }

                        if(y < 8){
                            y =
                                event.clientY -
                                rect.top +
                                18;
                        }

                        if(
                            y +
                            alturaTooltip >
                            rect.height -
                            8
                        ){
                            y =
                                rect.height -
                                alturaTooltip -
                                8;
                        }

                        tooltip.style.left =
                            `${Math.max(8,x)}px`;

                        tooltip.style.top =
                            `${Math.max(8,y)}px`;
                    };


                ponto.addEventListener(
                    "mouseenter",
                    mostrarTooltip
                );

                ponto.addEventListener(
                    "mousemove",
                    moverTooltip
                );

                ponto.addEventListener(
                    "mouseleave",
                    ()=>{

                        tooltip
                            .classList
                            .remove(
                                "show"
                            );

                        tooltip
                            .setAttribute(
                                "aria-hidden",
                                "true"
                            );

                        if(guide){
                            guide.setAttribute(
                                "visibility",
                                "hidden"
                            );
                        }
                    }
                );
            }
        );
}

/* =====================================================
   CARREGAMENTO DE DADOS (API)
===================================================== */


async function carregarAtividades(){
    atividades = await Api.get("/activities");
}


async function carregarServicos(){
    servicos = await Api.get("/services");
}


async function carregarAgenda(){
    agendamentos = await Api.get("/appointments");
}


async function carregarCampanhas(){
    campanhas = await Api.get("/campaigns");
}


async function carregarFinanceiro(){
    lancamentos = await Api.get("/finance");
}


async function atualizarDashboardCards(){

    dashboardData = await Api.get("/dashboard");

    const resumo = calcularResumoFinanceiro();

    aplicarValorFinanceiro(
        faturamentoHTML,
        resumo.total.liquido
    );

    if(clientesHTML){
        clientesHTML.textContent = dashboardData.total_clientes;
    }

    if(comandasHTML){
        comandasHTML.textContent = dashboardData.comandas_abertas;
    }
}


async function carregarTudo(){

    /*
      FASE 1 — dados necessários para começar a usar o sistema.
      Evita esperar Agenda/Marketing/Atividades antes de liberar a interface.
    */
    const principais =
        await Promise.allSettled([
            Api.get("/clients"),
            Api.get(
                "/comandas?status_filter=aberta"
            ),
            Api.get(
                "/comandas?status_filter=finalizada"
            ),
            Api.get("/services"),
            Api.get("/finance"),
            Api.get("/dashboard"),
            Api.get("/users/me"),
            Api.get("/employees")
        ]);


    const valorPrincipal =
        (indice, fallback)=>{

            const resultado =
                principais[indice];

            if(
                resultado &&
                resultado.status === "fulfilled"
            ){
                return resultado.value;
            }

            if(
                resultado &&
                resultado.status === "rejected"
            ){
                console.warn(
                    "Falha parcial no carregamento principal:",
                    resultado.reason
                );
            }

            return fallback;
        };


    clientes =
        valorPrincipal(0, clientes);

    comandas =
        valorPrincipal(1, comandas);

    historico =
        valorPrincipal(2, historico);

    servicos =
        valorPrincipal(3, servicos);

    lancamentos =
        valorPrincipal(4, lancamentos);

    dashboardData =
        valorPrincipal(5, dashboardData);

    const usuarioRecebido =
        valorPrincipal(6, null);

    colaboradores =
        valorPrincipal(7, colaboradores);


    if(usuarioRecebido){

        usuarioAtual =
            usuarioRecebido;

        preencherConfiguracoesUsuario();

        const temaLocal =
            localStorage.getItem(TEMA_KEY);

        if(
            !temaLocal &&
            usuarioRecebido.theme
        ){
            aplicarTema(
                usuarioRecebido.theme,
                true
            );
        }else{
            aplicarTema(
                temaLocal || "escuro",
                false
            );
        }
    }


    if(faturamentoHTML){

        const resumoFinanceiro =
            calcularResumoFinanceiro();

        aplicarValorFinanceiro(
            faturamentoHTML,
            resumoFinanceiro.total.liquido
        );
    }


    if(clientesHTML){

        clientesHTML.textContent =
            dashboardData.total_clientes ??
            clientes.length;
    }


    if(comandasHTML){

        comandasHTML.textContent =
            dashboardData.comandas_abertas ??
            comandas.length;
    }


    popularSelectClientes();
    popularSelectClientesAgenda();
    popularSelectServicos();
    popularSelectColaboradores();

    renderizarComandas();
    renderizarHistorico();
    renderizarClientes();
    gerarRelatorios();
    renderizarServicos();
    renderizarColaboradores();
    renderizarLancamentos();
    renderizarGraficoFinanceiro();


    /*
      FASE 2 — módulos secundários.
      Carregam sem travar a utilização de comandas/clientes/financeiro.
    */
    Promise.allSettled([
        Api.get("/activities"),
        Api.get("/appointments"),
        Api.get("/campaigns")
    ])
    .then(resultados=>{

        if(
            resultados[0].status ===
            "fulfilled"
        ){
            atividades =
                resultados[0].value;
        }

        if(
            resultados[1].status ===
            "fulfilled"
        ){
            agendamentos =
                resultados[1].value;
        }

        if(
            resultados[2].status ===
            "fulfilled"
        ){
            campanhas =
                resultados[2].value;
        }

        renderizarAtividades();
        renderizarAgenda();
        renderizarCampanhas();

        atualizarPublicoMarketing(
            emailPublico,
            emailPublicoResumo,
            emailClientesEspecificos
        );

        atualizarPublicoMarketing(
            whatsappPublico,
            whatsappPublicoResumo,
            whatsappClientesEspecificos
        );

    })
    .catch(err=>
        console.warn(
            "Falha no carregamento secundário:",
            err
        )
    );
}





/* =====================================================
   VYNCE — FINANCEIRO MENSAL 3.0
   Frontend: despesas fixas, adicionais, competência e fechamento.
   Observação: até o backend financeiro receber os novos campos/tabelas,
   este módulo persiste o estado específico no localStorage por conta.
===================================================== */

const FINANCEIRO_V2_KEY =
    `vynce_financeiro_v2:${String(session.email || "usuario").toLowerCase()}`;

let competenciaFinanceiraAtual = (() => {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}`;
})();

let financeiroV2State = carregarFinanceiroV2State();


function financeiroV2EstadoInicial(){
    return {
        version: 2,
        fixedRules: [],
        fixedStatus: {},
        additional: {},
        closings: {}
    };
}


function carregarFinanceiroV2State(){
    try{
        const raw = localStorage.getItem(FINANCEIRO_V2_KEY);
        if(!raw) return financeiroV2EstadoInicial();

        const parsed = JSON.parse(raw);

        return {
            ...financeiroV2EstadoInicial(),
            ...parsed,
            fixedRules: Array.isArray(parsed.fixedRules) ? parsed.fixedRules : [],
            fixedStatus: parsed.fixedStatus || {},
            additional: parsed.additional || {},
            closings: parsed.closings || {}
        };
    }catch(err){
        console.warn("Não foi possível carregar o financeiro mensal:", err);
        return financeiroV2EstadoInicial();
    }
}


function salvarFinanceiroV2State(){
    localStorage.setItem(
        FINANCEIRO_V2_KEY,
        JSON.stringify(financeiroV2State)
    );
}


function escaparHtmlFinanceiro(valor){
    return String(valor ?? "")
        .replaceAll("&","&amp;")
        .replaceAll("<","&lt;")
        .replaceAll(">","&gt;")
        .replaceAll('"',"&quot;")
        .replaceAll("'","&#039;");
}


function competenciaHoje(){
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}`;
}


function competenciaParaData(competencia, dia=1){
    const [ano, mes] = String(competencia).split("-").map(Number);
    const ultimoDia = new Date(ano, mes, 0).getDate();

    return new Date(
        ano,
        mes - 1,
        Math.min(Math.max(Number(dia)||1,1),ultimoDia),
        12,0,0,0
    );
}


function deslocarCompetencia(competencia, meses){
    const [ano, mes] = String(competencia).split("-").map(Number);
    const d = new Date(ano, mes - 1 + meses, 1);

    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}`;
}


function nomeCompetencia(competencia){
    const d = competenciaParaData(competencia);

    return d.toLocaleDateString(
        "pt-BR",
        { month:"long", year:"numeric" }
    );
}


function intervaloCompetencia(competencia){
    const [ano, mes] = String(competencia).split("-").map(Number);

    return {
        inicio: new Date(ano, mes - 1, 1, 0,0,0,0),
        fim: new Date(ano, mes, 1, 0,0,0,0)
    };
}


function competenciaDaData(data){
    const d = new Date(data);
    if(Number.isNaN(d.getTime())) return "";

    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}`;
}


function mesEstaFechado(competencia){
    return Boolean(financeiroV2State.closings[competencia]);
}


function receitaBrutaDaCompetencia(competencia){
    const fechamento = financeiroV2State.closings[competencia];

    if(fechamento){
        return Number(fechamento.grossRevenue || 0);
    }

    return historico.reduce((total, comanda)=>{
        const data = dataFinanceiraDaComanda(comanda);

        if(
            !data ||
            Number.isNaN(data.getTime()) ||
            competenciaDaData(data) !== competencia
        ){
            return total;
        }

        return total + Number(comanda.total || 0);
    },0);
}


function despesasLegadasDaCompetencia(competencia){
    return lancamentos
        .filter(item=>
            item.type === "saida" &&
            competenciaDaData(item.created_at) === competencia
        )
        .map(item=>({
            id:`legacy-${item.id}`,
            description:item.description || "Despesa",
            amount:Number(item.amount || 0),
            category:"Lançamento anterior",
            createdAt:item.created_at,
            legacy:true
        }));
}


function regraFixaValeNaCompetencia(regra, competencia){
    if(regra.startMonth && competencia < regra.startMonth){
        return false;
    }

    if(regra.endMonth && competencia > regra.endMonth){
        return false;
    }

    return true;
}


function regrasFixasDaCompetencia(competencia){
    const fechamento = financeiroV2State.closings[competencia];

    if(fechamento && Array.isArray(fechamento.fixedItems)){
        return fechamento.fixedItems.map(item=>({
            ...item,
            closedSnapshot:true
        }));
    }

    return financeiroV2State.fixedRules
        .filter(regra=>regraFixaValeNaCompetencia(regra, competencia))
        .map(regra=>({
            ...regra,
            paid:Boolean(
                financeiroV2State.fixedStatus?.[competencia]?.[regra.id]?.paid
            )
        }));
}


function adicionaisDaCompetencia(competencia){
    const fechamento = financeiroV2State.closings[competencia];

    if(fechamento){
        const snapshots =
            Array.isArray(fechamento.additionalItems)
                ? fechamento.additionalItems
                : [];

        return snapshots.map(item=>({
            ...item,
            /*
              Fechamentos antigos não tinham status explícito.
              Mantemos como pago para preservar o valor histórico
              que já havia sido descontado antes desta versão.
            */
            paid:item.paid === undefined ? true : Boolean(item.paid)
        }));
    }

    return (financeiroV2State.additional[competencia] || [])
        .map(item=>({
            ...item,
            paid:Boolean(item.paid)
        }));
}


function resumoFinanceiroV2(competencia){
    const fechamento = financeiroV2State.closings[competencia];

    if(fechamento){
        const additionalPaid = Number(
            fechamento.additionalPaid ??
            fechamento.additional ??
            0
        );

        const additionalPending = Number(
            fechamento.additionalPending ?? 0
        );

        const fixedPaid = Number(fechamento.fixedPaid || 0);
        const fixedPending = Number(fechamento.fixedPending || 0);
        const legacy = Number(fechamento.legacy || 0);
        const gross = Number(fechamento.grossRevenue || 0);

        const totalPaid =
            Number(
                fechamento.totalPaidExpenses ??
                (fixedPaid + additionalPaid + legacy)
            );

        return {
            gross,
            fixedPaid,
            fixedPending,
            additionalPaid,
            additionalPending,
            legacy,
            totalPaid,
            totalPending:fixedPending + additionalPending,
            net:Number(
                fechamento.net ??
                (gross - totalPaid)
            ),
            projected:Number(
                fechamento.projected ??
                (
                    gross -
                    totalPaid -
                    fixedPending -
                    additionalPending
                )
            ),
            closed:true
        };
    }

    const fixas = regrasFixasDaCompetencia(competencia);
    const adicionais = adicionaisDaCompetencia(competencia);

    const fixedPaid = fixas
        .filter(item=>item.paid)
        .reduce((total,item)=>total+Number(item.amount||0),0);

    const fixedPending = fixas
        .filter(item=>!item.paid)
        .reduce((total,item)=>total+Number(item.amount||0),0);

    const additionalPaid = adicionais
        .filter(item=>item.paid)
        .reduce((total,item)=>total+Number(item.amount||0),0);

    const additionalPending = adicionais
        .filter(item=>!item.paid)
        .reduce((total,item)=>total+Number(item.amount||0),0);

    /*
      Lançamentos antigos da rota /finance já eram tratados como
      despesas realizadas, por isso continuam como pagos.
    */
    const legacy = despesasLegadasDaCompetencia(competencia)
        .reduce((total,item)=>total+Number(item.amount||0),0);

    const gross = receitaBrutaDaCompetencia(competencia);

    const totalPaid =
        fixedPaid +
        additionalPaid +
        legacy;

    const totalPending =
        fixedPending +
        additionalPending;

    return {
        gross,
        fixedPaid,
        fixedPending,
        additionalPaid,
        additionalPending,
        legacy,
        totalPaid,
        totalPending,
        net:gross-totalPaid,
        projected:gross-totalPaid-totalPending,
        closed:false
    };
}


function atualizarResumoFinanceiroV2(){
    const resumo = resumoFinanceiroV2(competenciaFinanceiraAtual);

    const setValor = (id, valor, tipo="saldo")=>{
        const el = document.getElementById(id);
        if(!el) return;

        const numero = Number(valor || 0);

        el.classList.remove(
            "valor-positivo",
            "valor-negativo",
            "valor-zero"
        );

        if(tipo === "saida"){
            el.textContent =
                numero > 0
                    ? `- ${dinheiro(numero)}`
                    : dinheiro(0);

            el.classList.add(
                numero > 0
                    ? "valor-negativo"
                    : "valor-zero"
            );

            return;
        }

        el.textContent = dinheiro(numero);

        el.classList.add(
            numero > 0
                ? "valor-positivo"
                : numero < 0
                    ? "valor-negativo"
                    : "valor-zero"
        );
    };

    setValor(
        "financeReceitaBruta",
        resumo.gross,
        "entrada"
    );

    setValor(
        "financeDespesasTotais",
        resumo.totalPaid,
        "saida"
    );

    setValor(
        "financeFixasPagas",
        resumo.fixedPaid,
        "saida"
    );

    setValor(
        "financeAdicionais",
        resumo.additionalPaid + resumo.legacy,
        "saida"
    );

    setValor(
        "financeLiquidoMes",
        resumo.net,
        "saldo"
    );

    setValor(
        "financeFixasPendentes",
        resumo.totalPending,
        "saida"
    );

    const previsto =
        document.getElementById(
            "financeResultadoPrevisto"
        );

    if(previsto){
        const classe =
            resumo.projected > 0
                ? "valor-positivo"
                : resumo.projected < 0
                    ? "valor-negativo"
                    : "valor-zero";

        previsto.innerHTML =
            `Resultado previsto se pagar tudo: ` +
            `<strong class="${classe}">` +
            `${dinheiro(resumo.projected)}` +
            `</strong>`;
    }

    const resumoMes =
        document.getElementById(
            "faturamentoMes"
        );

    if(resumoMes){
        const classeLiquido =
            resumo.net > 0
                ? "valor-positivo"
                : resumo.net < 0
                    ? "valor-negativo"
                    : "valor-zero";

        resumoMes.innerHTML = `
            <div class="finance-resumo">

                <div class="finance-resumo-linha">
                    <span>Receita bruta</span>

                    <strong class="${resumo.gross > 0 ? "valor-positivo" : "valor-zero"}">
                        ${dinheiro(resumo.gross)}
                    </strong>
                </div>

                <div class="finance-resumo-linha despesa">
                    <span>Despesas pagas</span>

                    <strong class="${resumo.totalPaid > 0 ? "valor-negativo" : "valor-zero"}">
                        ${resumo.totalPaid > 0 ? "- " : ""}
                        ${dinheiro(resumo.totalPaid)}
                    </strong>
                </div>

                <div class="finance-resumo-linha despesa">
                    <span>Despesas pendentes</span>

                    <strong class="${resumo.totalPending > 0 ? "valor-negativo" : "valor-zero"}">
                        ${resumo.totalPending > 0 ? "- " : ""}
                        ${dinheiro(resumo.totalPending)}
                    </strong>
                </div>

                <div class="finance-resumo-total ${resumo.net < 0 ? "negativo" : ""}">
                    <span>Líquido realizado</span>

                    <strong class="${classeLiquido}">
                        ${dinheiro(resumo.net)}
                    </strong>
                </div>

            </div>
        `;
    }

    const resumoAtual =
        resumoFinanceiroV2(
            competenciaHoje()
        );

    aplicarValorFinanceiro(
        faturamentoHTML,
        resumoAtual.net
    );
}


function atualizarCabecalhoCompetencia(){
    const label = document.getElementById("financeiroMesAtualLabel");
    const status = document.getElementById("financeiroStatusMes");
    const fecharBtn = document.getElementById("fecharMesBtn");
    const proximoBtn = document.getElementById("financeiroMesProximo");

    if(label){
        label.textContent = nomeCompetencia(competenciaFinanceiraAtual);
    }

    const fechado = mesEstaFechado(competenciaFinanceiraAtual);

    if(status){
        status.textContent = fechado ? "Fechado" : "Em aberto";
        status.classList.toggle("fechado", fechado);
        status.classList.toggle("aberto", !fechado);
    }

    if(fecharBtn){
        fecharBtn.disabled = fechado;
        fecharBtn.textContent =
            fechado
                ? "Faturamento fechado"
                : "Fechar faturamento do mês";
    }

    if(proximoBtn){
        proximoBtn.disabled =
            competenciaFinanceiraAtual >= competenciaHoje();
    }
}


function renderizarDespesasFixasV2(){
    const lista = document.getElementById("listaDespesasFixas");
    if(!lista) return;

    const fechado = mesEstaFechado(competenciaFinanceiraAtual);
    const regras = regrasFixasDaCompetencia(competenciaFinanceiraAtual);

    lista.innerHTML = "";

    if(!regras.length){
        lista.innerHTML =
            `<p class="muted">Nenhuma despesa fixa nesta competência.</p>`;
        return;
    }

    regras.forEach(regra=>{
        const item = document.createElement("div");
        item.className = "finance-expense-item";

        const pago = Boolean(regra.paid);

        item.innerHTML = `
            <div class="finance-expense-main">
                <strong>${escaparHtmlFinanceiro(regra.description)}</strong>
                <span class="finance-expense-meta">
                    ${escaparHtmlFinanceiro(regra.category || "Sem categoria")}
                    · vence dia ${String(regra.dueDay || 1).padStart(2,"0")}
                </span>
            </div>

            <strong class="finance-expense-value valor-negativo">
                - ${dinheiro(regra.amount)}
            </strong>

            <div class="finance-expense-actions">
                <span class="${pago ? "finance-paid-badge" : "finance-pending-badge"}">
                    ${pago ? "Pago" : "Pendente"}
                </span>

                ${
                    !fechado
                        ? `
                            <button
                                type="button"
                                class="finance-action-btn ${pago ? "" : "pay"}"
                                data-fixa-pagamento="${escaparHtmlFinanceiro(regra.id)}">
                                ${pago ? "Marcar pendente" : "Marcar pago"}
                            </button>

                            <button
                                type="button"
                                class="finance-action-btn"
                                data-fixa-editar="${escaparHtmlFinanceiro(regra.id)}">
                                Editar
                            </button>

                            <button
                                type="button"
                                class="finance-action-btn danger"
                                data-fixa-desativar="${escaparHtmlFinanceiro(regra.id)}">
                                Desativar
                            </button>
                        `
                        : ""
                }
            </div>
        `;

        lista.appendChild(item);
    });

    if(fechado){
        const nota = document.createElement("div");
        nota.className = "finance-closed-note";
        nota.textContent =
            "Este mês está fechado. Os valores exibidos são a fotografia registrada no fechamento.";
        lista.appendChild(nota);
    }
}


function renderizarDespesasAdicionaisV2(){
    const lista = document.getElementById("listaDespesasAdicionais");
    if(!lista) return;

    const fechado = mesEstaFechado(competenciaFinanceiraAtual);

    const adicionais =
        adicionaisDaCompetencia(competenciaFinanceiraAtual);

    const legadas = fechado
        ? (
            financeiroV2State.closings[competenciaFinanceiraAtual]?.legacyItems || []
          )
        : despesasLegadasDaCompetencia(competenciaFinanceiraAtual);

    lista.innerHTML = "";

    const todos = [
        ...adicionais.map(item=>({...item,legacy:false})),
        ...legadas.map(item=>({...item,legacy:true,paid:true}))
    ];

    if(!todos.length){
        lista.innerHTML =
            `<p class="muted">Nenhuma despesa adicional nesta competência.</p>`;
        return;
    }

    todos.forEach(despesa=>{
        const item = document.createElement("div");
        item.className = "finance-expense-item";

        const pago = Boolean(despesa.paid);

        item.innerHTML = `
            <div class="finance-expense-main">
                <strong>${escaparHtmlFinanceiro(despesa.description)}</strong>

                <span class="finance-expense-meta">
                    ${escaparHtmlFinanceiro(despesa.category || "Adicional")}
                    ${
                        despesa.createdAt || despesa.created_at
                            ? " · " + formatarData(despesa.createdAt || despesa.created_at)
                            : ""
                    }
                </span>
            </div>

            <strong class="finance-expense-value valor-negativo">
                - ${dinheiro(despesa.amount)}
            </strong>

            <div class="finance-expense-actions">
                ${
                    despesa.legacy
                        ? `
                            <span class="finance-paid-badge">Pago</span>
                            <span class="finance-legacy-badge">Anterior</span>
                          `
                        : (
                            fechado
                                ? `
                                    <span class="${pago ? "finance-paid-badge" : "finance-pending-badge"}">
                                        ${pago ? "Pago" : "Pendente"}
                                    </span>
                                    <span class="finance-legacy-badge">Arquivada</span>
                                  `
                                : `
                                    <span class="${pago ? "finance-paid-badge" : "finance-pending-badge"}">
                                        ${pago ? "Pago" : "Pendente"}
                                    </span>

                                    <button
                                        type="button"
                                        class="finance-action-btn ${pago ? "" : "pay"}"
                                        data-adicional-pagamento="${escaparHtmlFinanceiro(despesa.id)}">
                                        ${pago ? "Marcar pendente" : "Marcar pago"}
                                    </button>

                                    <button
                                        type="button"
                                        class="finance-action-btn"
                                        data-adicional-editar="${escaparHtmlFinanceiro(despesa.id)}">
                                        Editar
                                    </button>

                                    <button
                                        type="button"
                                        class="finance-action-btn danger"
                                        data-adicional-remover="${escaparHtmlFinanceiro(despesa.id)}">
                                        Remover
                                    </button>
                                  `
                          )
                }
            </div>
        `;

        lista.appendChild(item);
    });

    if(fechado){
        const nota = document.createElement("div");
        nota.className = "finance-closed-note";
        nota.textContent =
            "As despesas adicionais deste mês estão preservadas dentro do fechamento e não se repetem no mês seguinte.";
        lista.appendChild(nota);
    }
}



function despesasPagasParaRanking(competencia){
    const fechado = financeiroV2State.closings[competencia];

    if(fechado){
        const fixas = (fechamentoArray(fechado.fixedItems))
            .filter(item=>item.paid)
            .map(item=>({
                description:item.description,
                category:item.category || "Fixa",
                amount:Number(item.amount||0),
                type:"Fixa"
            }));

        const adicionais = (fechamentoArray(fechado.additionalItems))
            .filter(item=>item.paid === undefined ? true : item.paid)
            .map(item=>({
                description:item.description,
                category:item.category || "Adicional",
                amount:Number(item.amount||0),
                type:"Adicional"
            }));

        const legadas = (fechamentoArray(fechado.legacyItems))
            .map(item=>({
                description:item.description,
                category:item.category || "Lançamento anterior",
                amount:Number(item.amount||0),
                type:"Adicional"
            }));

        return [...fixas,...adicionais,...legadas]
            .filter(item=>item.amount>0)
            .sort((a,b)=>b.amount-a.amount);
    }

    const fixas = regrasFixasDaCompetencia(competencia)
        .filter(item=>item.paid)
        .map(item=>({
            description:item.description,
            category:item.category || "Fixa",
            amount:Number(item.amount||0),
            type:"Fixa"
        }));

    const adicionais = adicionaisDaCompetencia(competencia)
        .filter(item=>item.paid)
        .map(item=>({
            description:item.description,
            category:item.category || "Adicional",
            amount:Number(item.amount||0),
            type:"Adicional"
        }));

    const legadas = despesasLegadasDaCompetencia(competencia)
        .map(item=>({
            description:item.description,
            category:item.category || "Lançamento anterior",
            amount:Number(item.amount||0),
            type:"Adicional"
        }));

    return [...fixas,...adicionais,...legadas]
        .filter(item=>item.amount>0)
        .sort((a,b)=>b.amount-a.amount);
}


function fechamentoArray(valor){
    return Array.isArray(valor) ? valor : [];
}


function renderizarRankingDespesasV2(){
    const lista = document.getElementById("rankingDespesas");
    const totalEl = document.getElementById("rankingDespesasTotal");

    if(!lista) return;

    const itens = despesasPagasParaRanking(
        competenciaFinanceiraAtual
    );

    const total = itens.reduce(
        (soma,item)=>soma+Number(item.amount||0),
        0
    );

    if(totalEl){
        totalEl.textContent = dinheiro(total);
    }

    lista.innerHTML = "";

    if(!itens.length){
        lista.innerHTML =
            `<p class="muted">Nenhuma despesa paga nesta competência.</p>`;
        return;
    }

    itens.forEach((despesa,indice)=>{
        const percentual =
            total > 0
                ? (Number(despesa.amount||0) / total) * 100
                : 0;

        const item = document.createElement("div");
        item.className = "finance-ranking-item";

        item.innerHTML = `
            <div class="finance-ranking-position">
                ${indice+1}
            </div>

            <div class="finance-ranking-content">
                <div class="finance-ranking-line">
                    <div>
                        <strong>${escaparHtmlFinanceiro(despesa.description)}</strong>
                        <span>
                            ${escaparHtmlFinanceiro(despesa.type)}
                            · ${escaparHtmlFinanceiro(despesa.category)}
                        </span>
                    </div>

                    <div class="finance-ranking-value">
                        <strong class="valor-negativo">- ${dinheiro(despesa.amount)}</strong>
                        <span>${percentual.toFixed(1).replace(".",",")}%</span>
                    </div>
                </div>

                <div class="finance-ranking-bar">
                    <span style="width:${Math.max(2, Math.min(100, percentual)).toFixed(2)}%"></span>
                </div>
            </div>
        `;

        lista.appendChild(item);
    });
}


function renderizarFechamentosV2(){
    const lista =
        document.getElementById(
            "listaFechamentosMensais"
        );

    if(!lista) return;

    const fechamentos =
        Object.entries(
            financeiroV2State.closings
        )
        .sort(
            ([a],[b])=>
                b.localeCompare(a)
        );

    lista.innerHTML = "";

    if(!fechamentos.length){
        lista.innerHTML =
            `<p class="muted">Nenhum faturamento fechado ainda.</p>`;

        return;
    }

    fechamentos.forEach(
        ([competencia,fechamento])=>{

            const item =
                document.createElement("div");

            item.className =
                "finance-closing-item";

            const bruto =
                Number(
                    fechamento.grossRevenue || 0
                );

            const fixas =
                Number(
                    fechamento.fixedPaid || 0
                );

            const adicionais =
                Number(
                    fechamento.additionalPaid ??
                    fechamento.additional ??
                    0
                ) +
                Number(
                    fechamento.legacy || 0
                );

            const liquido =
                Number(
                    fechamento.net || 0
                );

            item.innerHTML = `
                <div class="finance-closing-month">

                    <strong>
                        ${escaparHtmlFinanceiro(
                            nomeCompetencia(
                                competencia
                            )
                        )}
                    </strong>

                    <span class="finance-expense-meta">
                        Fechado em
                        ${formatarData(
                            fechamento.closedAt
                        )}
                    </span>

                </div>


                <div class="finance-closing-metric">

                    <span>Bruto</span>

                    <strong class="${bruto > 0 ? "valor-positivo" : "valor-zero"}">
                        ${dinheiro(bruto)}
                    </strong>

                </div>


                <div class="finance-closing-metric">

                    <span>Fixas pagas</span>

                    <strong class="${fixas > 0 ? "valor-negativo" : "valor-zero"}">
                        ${fixas > 0 ? "- " : ""}
                        ${dinheiro(fixas)}
                    </strong>

                </div>


                <div class="finance-closing-metric">

                    <span>Adicionais</span>

                    <strong class="${adicionais > 0 ? "valor-negativo" : "valor-zero"}">
                        ${adicionais > 0 ? "- " : ""}
                        ${dinheiro(adicionais)}
                    </strong>

                </div>


                <div class="finance-closing-metric net">

                    <span>Líquido</span>

                    <strong class="${
                        liquido > 0
                            ? "valor-positivo"
                            : liquido < 0
                                ? "valor-negativo"
                                : "valor-zero"
                    }">
                        ${dinheiro(liquido)}
                    </strong>

                </div>
            `;

            item.addEventListener(
                "click",
                ()=>{
                    competenciaFinanceiraAtual =
                        competencia;

                    renderizarFinanceiroMensalCompleto();
                }
            );

            lista.appendChild(item);
        }
    );
}


function renderizarFinanceiroMensalCompleto(){
    atualizarCabecalhoCompetencia();
    atualizarResumoFinanceiroV2();
    renderizarDespesasFixasV2();
    renderizarDespesasAdicionaisV2();
    renderizarRankingDespesasV2();
    renderizarFechamentosV2();

    const fechado = mesEstaFechado(competenciaFinanceiraAtual);

    [
        "novaDespesaFixaBtn",
        "novaDespesaAdicionalBtn"
    ].forEach(id=>{
        const el = document.getElementById(id);
        if(el) el.disabled = fechado;
    });

    if(typeof renderizarGraficoFinanceiro === "function"){
        renderizarGraficoFinanceiro();
    }
}


function novaIdFinanceiro(prefix){
    if(globalThis.crypto?.randomUUID){
        return `${prefix}-${crypto.randomUUID()}`;
    }

    return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}


function configurarFinanceiroMensalV2(){
    const mesAnterior = document.getElementById("financeiroMesAnterior");
    const mesProximo = document.getElementById("financeiroMesProximo");

    const novaFixaBtn = document.getElementById("novaDespesaFixaBtn");
    const fixaForm = document.getElementById("despesaFixaForm");
    const salvarFixaBtn = document.getElementById("salvarDespesaFixaBtn");
    const cancelarFixaBtn = document.getElementById("cancelarDespesaFixaBtn");

    const novaAdicionalBtn = document.getElementById("novaDespesaAdicionalBtn");
    const adicionalForm = document.getElementById("despesaAdicionalForm");
    const salvarAdicionalBtn = document.getElementById("salvarDespesaAdicionalBtn");
    const cancelarAdicionalBtn = document.getElementById("cancelarDespesaAdicionalBtn");

    const fecharMesBtn = document.getElementById("fecharMesBtn");
    const listaFixas = document.getElementById("listaDespesasFixas");
    const listaAdicionais = document.getElementById("listaDespesasAdicionais");

    let fixaEditandoId = null;
    let adicionalEditandoId = null;

    function limparFormFixa(){
        ["fixaDescricao","fixaValor","fixaDia","fixaCategoria"]
            .forEach(id=>{
                const el = document.getElementById(id);
                if(el) el.value="";
            });

        fixaEditandoId = null;

        if(salvarFixaBtn){
            salvarFixaBtn.textContent = "Salvar despesa fixa";
        }

        fixaForm?.classList.remove("active");
    }

    function limparFormAdicional(){
        ["adicionalDescricao","adicionalValor","adicionalCategoria"]
            .forEach(id=>{
                const el = document.getElementById(id);
                if(el) el.value="";
            });

        adicionalEditandoId = null;

        if(salvarAdicionalBtn){
            salvarAdicionalBtn.textContent = "Adicionar despesa";
        }

        adicionalForm?.classList.remove("active");
    }

    mesAnterior?.addEventListener("click", ()=>{
        limparFormFixa();
        limparFormAdicional();

        competenciaFinanceiraAtual =
            deslocarCompetencia(competenciaFinanceiraAtual,-1);

        renderizarFinanceiroMensalCompleto();
    });

    mesProximo?.addEventListener("click", ()=>{
        if(competenciaFinanceiraAtual >= competenciaHoje()) return;

        limparFormFixa();
        limparFormAdicional();

        competenciaFinanceiraAtual =
            deslocarCompetencia(competenciaFinanceiraAtual,1);

        renderizarFinanceiroMensalCompleto();
    });

    novaFixaBtn?.addEventListener("click", ()=>{
        if(mesEstaFechado(competenciaFinanceiraAtual)) return;

        fixaEditandoId = null;

        if(salvarFixaBtn){
            salvarFixaBtn.textContent = "Salvar despesa fixa";
        }

        fixaForm?.classList.toggle("active");
    });

    cancelarFixaBtn?.addEventListener("click", limparFormFixa);

    salvarFixaBtn?.addEventListener("click", ()=>{
        if(mesEstaFechado(competenciaFinanceiraAtual)) return;

        const descricao =
            document.getElementById("fixaDescricao")?.value.trim() || "";

        const valor =
            Number(document.getElementById("fixaValor")?.value || 0);

        const dia =
            Number(document.getElementById("fixaDia")?.value || 0);

        const categoria =
            document.getElementById("fixaCategoria")?.value.trim() || "";

        if(!descricao || !valor || valor<=0 || !dia || dia<1 || dia>31){
            mostrarNotificacao(
                "Informe descrição, valor e um dia de vencimento entre 1 e 31.",
                "warning",
                "Revise a despesa fixa"
            );
            return;
        }

        if(fixaEditandoId){
            const regra =
                financeiroV2State.fixedRules.find(
                    item=>item.id===fixaEditandoId
                );

            if(regra){
                regra.description = descricao;
                regra.amount = valor;
                regra.dueDay = dia;
                regra.category = categoria || "Fixa";
                regra.updatedAt = new Date().toISOString();
            }

            mostrarNotificacao(
                "A despesa fixa foi atualizada.",
                "success",
                "Despesa editada"
            );
        }else{
            financeiroV2State.fixedRules.push({
                id:novaIdFinanceiro("fixa"),
                description:descricao,
                amount:valor,
                dueDay:dia,
                category:categoria || "Fixa",
                startMonth:competenciaFinanceiraAtual,
                endMonth:null,
                createdAt:new Date().toISOString()
            });

            mostrarNotificacao(
                "A despesa fixa foi cadastrada como pendente.",
                "success",
                "Despesa fixa criada"
            );
        }

        salvarFinanceiroV2State();
        limparFormFixa();
        renderizarFinanceiroMensalCompleto();
    });

    listaFixas?.addEventListener("click", evento=>{
        const pagar = evento.target.closest("[data-fixa-pagamento]");
        const editar = evento.target.closest("[data-fixa-editar]");
        const desativar = evento.target.closest("[data-fixa-desativar]");

        if(pagar){
            const id = pagar.dataset.fixaPagamento;

            financeiroV2State.fixedStatus[competenciaFinanceiraAtual] ||= {};
            financeiroV2State.fixedStatus[competenciaFinanceiraAtual][id] ||= {};

            const atual =
                Boolean(
                    financeiroV2State.fixedStatus[competenciaFinanceiraAtual][id].paid
                );

            financeiroV2State.fixedStatus[competenciaFinanceiraAtual][id] = {
                paid:!atual,
                paidAt:!atual ? new Date().toISOString() : null
            };

            salvarFinanceiroV2State();

            mostrarNotificacao(
                !atual
                    ? "Pagamento confirmado. O valor já foi descontado do faturamento líquido."
                    : "A despesa voltou para pendente e deixou de ser descontada do faturamento líquido.",
                "success",
                !atual ? "Despesa paga" : "Despesa pendente"
            );

            renderizarFinanceiroMensalCompleto();
            return;
        }

        if(editar){
            const id = editar.dataset.fixaEditar;
            const regra =
                financeiroV2State.fixedRules.find(item=>item.id===id);

            if(!regra) return;

            fixaEditandoId = id;

            document.getElementById("fixaDescricao").value =
                regra.description || "";

            document.getElementById("fixaValor").value =
                Number(regra.amount || 0);

            document.getElementById("fixaDia").value =
                Number(regra.dueDay || 1);

            document.getElementById("fixaCategoria").value =
                regra.category || "";

            if(salvarFixaBtn){
                salvarFixaBtn.textContent = "Salvar alterações";
            }

            fixaForm?.classList.add("active");
            fixaForm?.scrollIntoView({behavior:"smooth",block:"center"});
            return;
        }

        if(desativar){
            const id = desativar.dataset.fixaDesativar;

            const regra =
                financeiroV2State.fixedRules.find(item=>item.id===id);

            if(!regra) return;

            if(!confirm(
                `Desativar "${regra.description}"? Ela não aparecerá nos próximos meses.`
            )){
                return;
            }

            const foiPaga =
                Boolean(
                    financeiroV2State.fixedStatus?.[competenciaFinanceiraAtual]?.[id]?.paid
                );

            regra.endMonth =
                foiPaga
                    ? competenciaFinanceiraAtual
                    : deslocarCompetencia(competenciaFinanceiraAtual,-1);

            salvarFinanceiroV2State();
            renderizarFinanceiroMensalCompleto();
        }
    });

    novaAdicionalBtn?.addEventListener("click", ()=>{
        if(mesEstaFechado(competenciaFinanceiraAtual)) return;

        adicionalEditandoId = null;

        if(salvarAdicionalBtn){
            salvarAdicionalBtn.textContent = "Adicionar despesa";
        }

        adicionalForm?.classList.toggle("active");
    });

    cancelarAdicionalBtn?.addEventListener(
        "click",
        limparFormAdicional
    );

    salvarAdicionalBtn?.addEventListener("click", ()=>{
        if(mesEstaFechado(competenciaFinanceiraAtual)) return;

        const descricao =
            document.getElementById("adicionalDescricao")?.value.trim() || "";

        const valor =
            Number(document.getElementById("adicionalValor")?.value || 0);

        const categoria =
            document.getElementById("adicionalCategoria")?.value.trim() || "";

        if(!descricao || !valor || valor<=0){
            mostrarNotificacao(
                "Informe a descrição e um valor maior que zero.",
                "warning",
                "Revise a despesa adicional"
            );
            return;
        }

        financeiroV2State.additional[competenciaFinanceiraAtual] ||= [];

        if(adicionalEditandoId){
            const item =
                financeiroV2State.additional[competenciaFinanceiraAtual]
                    .find(item=>item.id===adicionalEditandoId);

            if(item){
                item.description = descricao;
                item.amount = valor;
                item.category = categoria || "Adicional";
                item.updatedAt = new Date().toISOString();
            }

            mostrarNotificacao(
                "A despesa adicional foi atualizada.",
                "success",
                "Despesa editada"
            );
        }else{
            financeiroV2State.additional[competenciaFinanceiraAtual].push({
                id:novaIdFinanceiro("adicional"),
                description:descricao,
                amount:valor,
                category:categoria || "Adicional",
                paid:false,
                paidAt:null,
                createdAt:new Date().toISOString()
            });

            mostrarNotificacao(
                "A despesa foi adicionada como pendente. Marque como paga quando o valor realmente sair do caixa.",
                "success",
                "Despesa adicionada"
            );
        }

        salvarFinanceiroV2State();
        limparFormAdicional();
        renderizarFinanceiroMensalCompleto();
    });

    listaAdicionais?.addEventListener("click", evento=>{
        const pagar =
            evento.target.closest("[data-adicional-pagamento]");

        const editar =
            evento.target.closest("[data-adicional-editar]");

        const remover =
            evento.target.closest("[data-adicional-remover]");

        const itens =
            financeiroV2State.additional[competenciaFinanceiraAtual] || [];

        if(pagar){
            const id = pagar.dataset.adicionalPagamento;
            const item = itens.find(item=>item.id===id);

            if(!item) return;

            item.paid = !Boolean(item.paid);
            item.paidAt =
                item.paid
                    ? new Date().toISOString()
                    : null;

            salvarFinanceiroV2State();

            mostrarNotificacao(
                item.paid
                    ? "Pagamento confirmado. O valor já foi descontado do faturamento líquido."
                    : "A despesa voltou para pendente e deixou de ser descontada do faturamento líquido.",
                "success",
                item.paid ? "Despesa paga" : "Despesa pendente"
            );

            renderizarFinanceiroMensalCompleto();
            return;
        }

        if(editar){
            const id = editar.dataset.adicionalEditar;
            const item = itens.find(item=>item.id===id);

            if(!item) return;

            adicionalEditandoId = id;

            document.getElementById("adicionalDescricao").value =
                item.description || "";

            document.getElementById("adicionalValor").value =
                Number(item.amount || 0);

            document.getElementById("adicionalCategoria").value =
                item.category || "";

            if(salvarAdicionalBtn){
                salvarAdicionalBtn.textContent = "Salvar alterações";
            }

            adicionalForm?.classList.add("active");
            adicionalForm?.scrollIntoView({behavior:"smooth",block:"center"});
            return;
        }

        if(remover){
            const id = remover.dataset.adicionalRemover;

            if(!confirm("Remover esta despesa adicional?")){
                return;
            }

            financeiroV2State.additional[competenciaFinanceiraAtual] =
                itens.filter(item=>item.id!==id);

            salvarFinanceiroV2State();
            renderizarFinanceiroMensalCompleto();
        }
    });

    fecharMesBtn?.addEventListener("click", ()=>{
        if(mesEstaFechado(competenciaFinanceiraAtual)) return;

        const resumo =
            resumoFinanceiroV2(competenciaFinanceiraAtual);

        const fixas =
            regrasFixasDaCompetencia(competenciaFinanceiraAtual);

        const adicionais =
            adicionaisDaCompetencia(competenciaFinanceiraAtual);

        const legadas =
            despesasLegadasDaCompetencia(competenciaFinanceiraAtual);

        const confirmou = confirm(
            `Fechar ${nomeCompetencia(competenciaFinanceiraAtual)}?\n\n` +
            `Receita bruta: ${dinheiro(resumo.gross)}\n` +
            `Despesas pagas: ${dinheiro(resumo.totalPaid)}\n` +
            `Despesas pendentes: ${dinheiro(resumo.totalPending)}\n` +
            `Faturamento líquido: ${dinheiro(resumo.net)}\n\n` +
            `Depois do fechamento, este mês ficará congelado no histórico.`
        );

        if(!confirmou) return;

        financeiroV2State.closings[competenciaFinanceiraAtual] = {
            competence:competenciaFinanceiraAtual,
            grossRevenue:resumo.gross,
            fixedPaid:resumo.fixedPaid,
            fixedPending:resumo.fixedPending,
            additionalPaid:resumo.additionalPaid,
            additionalPending:resumo.additionalPending,
            additional:resumo.additionalPaid,
            legacy:resumo.legacy,
            totalPaidExpenses:resumo.totalPaid,
            net:resumo.net,
            projected:resumo.projected,

            fixedItems:fixas.map(item=>({
                id:item.id,
                description:item.description,
                amount:Number(item.amount||0),
                dueDay:item.dueDay,
                category:item.category,
                paid:Boolean(item.paid)
            })),

            additionalItems:adicionais.map(item=>({
                ...item,
                paid:Boolean(item.paid)
            })),

            legacyItems:legadas.map(item=>({...item})),

            closedAt:new Date().toISOString()
        };

        /*
          Depois do fechamento, os adicionais ativos daquele mês
          saem da área operacional, mas continuam no snapshot fechado.
        */
        delete financeiroV2State.additional[competenciaFinanceiraAtual];

        salvarFinanceiroV2State();

        mostrarNotificacao(
            `O faturamento de ${nomeCompetencia(competenciaFinanceiraAtual)} foi fechado e arquivado.`,
            "success",
            "Mês fechado"
        );

        renderizarFinanceiroMensalCompleto();
    });
}


/*
  Movimentos locais usados pelo gráfico.
  O backend atual ainda não possui os campos específicos de recorrência/competência.
*/
function movimentosFinanceirosV2ParaGrafico(){
    /*
      Compatibilidade com código antigo:
      devolve APENAS despesas novas do Financeiro 3.x.
      Lançamentos legados da API /finance não entram aqui,
      evitando dupla contagem no gráfico.
    */
    return movimentosFinanceirosConsolidados()
        .filter(item=>
            item.type === "saida" &&
            item.source !== "legacy"
        )
        .map(item=>({
            date:item.date,
            amount:item.amount,
            description:item.description
        }));
}


function inicializarFinanceiroMensal(){

    document
        .querySelectorAll(".chart-period-btn")
        .forEach(btn=>{
            btn.classList.toggle(
                "active",
                btn.dataset.periodo === periodoGraficoAtual
            );
        });

    configurarFinanceiroMensalV2();
    renderizarFinanceiroMensalCompleto();
}


/* =====================================================
   INICIALIZAÇÃO
===================================================== */


async function solicitarLiberacaoAssinatura(){
    const btn=document.getElementById("subscriptionRequest");
    const statusEl=document.getElementById("subscriptionRequestStatus");
    if(btn) btn.disabled=true;
    if(statusEl){statusEl.className="subscription-request-status";statusEl.textContent="Enviando solicitação...";}
    try{
        const result=await Api.post("/subscriptions/request-activation",{});
        if(statusEl){statusEl.classList.add("ok");statusEl.textContent=result?.message || "Solicitação enviada. Aguarde a confirmação da Vynce.";}
    }catch(err){
        if(statusEl){statusEl.classList.add("error");statusEl.textContent=err?.message || "Não foi possível enviar a solicitação agora.";}
    }finally{if(btn) btn.disabled=false;}
}

async function verificarAssinatura(){
    try{
        const me=await Api.get("/users/me");
        const expira=me.subscription_expires_at ? new Date(me.subscription_expires_at) : null;
        const assinaturaValida=me.subscription_status==="active" && (!expira || expira.getTime()>Date.now());
        if(!assinaturaValida){
            const gate=document.getElementById("subscriptionGate"); if(gate) gate.hidden=false;
            const c=document.getElementById("subscriptionContact"); if(c){c.textContent="vyncetechnologies26@gmail.com";c.href="mailto:vyncetechnologies26@gmail.com";}
            document.getElementById("subscriptionRequest")?.addEventListener("click",solicitarLiberacaoAssinatura);
            document.getElementById("subscriptionLogout")?.addEventListener("click",()=>Auth.logout());
            return false;
        }
        return true;
    }catch(err){ mostrarErro(err); return false; }
}

const toggleNovoCliente=document.getElementById("toggleNovoCliente");
if(toggleNovoCliente){toggleNovoCliente.addEventListener("click",()=>{const p=document.getElementById("novoClientePanel"); if(p) p.hidden=!p.hidden;});}

async function iniciarSistema(){

    /*
      Acorda discretamente o backend do Render.
      Não bloqueia a tela.
    */
    if(
        typeof Api.warmup === "function"
    ){
        Api.warmup().catch(()=>{});
    }

    const abaSalva =
        localStorage.getItem(ABA_ATIVA_KEY);

    const abaInicial =
        abaSalva && document.getElementById(abaSalva)
            ? abaSalva
            : "dashboard";

    // Mostra a página e o tema imediatamente.
    abrirPagina(abaInicial);

    // Confirma a liberação comercial antes de carregar dados pagos.
    if(!(await verificarAssinatura())) return;

    // APIs carregam depois, sem trocar a aba nem o tema.
    await carregarTudo();

    if(typeof inicializarFinanceiroMensal === "function"){
        inicializarFinanceiroMensal();
    }

    if(typeof atualizarMarketingCompleto === "function"){
        atualizarMarketingCompleto();
        renderizarCampanhas();
    }

    pedirPermissaoNotificacao();
}


iniciarSistema();


})();