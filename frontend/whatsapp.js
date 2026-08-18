// frontend/whatsapp.js

/**
 * INTEGRAÇÃO EVOLUTION API - WhatsApp
 * 
 * Este módulo gerencia a integração com Evolution API
 * para enviar mensagens via WhatsApp de forma nativa.
 */

const whatsappModule = (function() {

    const configApiKey = document.getElementById("configApiKey");
    const configBaseUrl = document.getElementById("configBaseUrl");
    const configInstanceName = document.getElementById("configInstanceName");
    const salvarEvolutionBtn = document.getElementById("salvarEvolutionBtn");
    const testarConexaoBtn = document.getElementById("testarConexaoBtn");
    const statusEvolution = document.getElementById("statusEvolution");

    const campaignMessage = document.getElementById("campaignMessage");
    const clientesPara = document.getElementById("clientesPara");
    const enviarCampanhaBtn = document.getElementById("enviarCampanhaBtn");
    const progressoCampanha = document.getElementById("progressoCampanha");

    // Carregar configuração salva
    function carregarConfiguracao() {
        return Api.get("/evolution/config").catch(() => null);
    }

    // Salvar configuração
    if (salvarEvolutionBtn) {
        salvarEvolutionBtn.onclick = async function() {
            const apiKey = configApiKey.value.trim();
            const baseUrl = configBaseUrl.value.trim();
            const instanceName = configInstanceName.value.trim() || "default";

            if (!apiKey || !baseUrl) {
                alert("Preencha API Key e Base URL");
                return;
            }

            try {
                await Api.post("/evolution/config", {
                    api_key: apiKey,
                    base_url: baseUrl,
                    instance_name: instanceName
                });

                alert("✅ Configuração salva com sucesso!");
                configApiKey.value = "";
                configBaseUrl.value = "";
                configInstanceName.value = "default";

            } catch (err) {
                alert(`❌ Erro ao salvar: ${err.message}`);
            }
        };
    }

    // Testar conexão
    if (testarConexaoBtn) {
        testarConexaoBtn.onclick = async function() {
            statusEvolution.innerHTML = "⏳ Testando conexão...";
            statusEvolution.className = "status-info";

            try {
                const result = await Api.post("/evolution/test-connection");

                if (result.success) {
                    statusEvolution.innerHTML = "✅ Conectado ao WhatsApp com sucesso!";
                    statusEvolution.className = "status-success";
                } else {
                    statusEvolution.innerHTML = `❌ Erro: ${result.error}`;
                    statusEvolution.className = "status-error";
                }
            } catch (err) {
                statusEvolution.innerHTML = `❌ Erro: ${err.message}`;
                statusEvolution.className = "status-error";
            }
        };
    }

    // Enviar campanha via WhatsApp
    if (enviarCampanhaBtn) {
        enviarCampanhaBtn.onclick = async function() {
            const mensagem = campaignMessage.value.trim();
            const clientesSelect = clientesPara.value;

            if (!mensagem) {
                alert("Digite a mensagem para enviar");
                return;
            }

            let clientIds = null;

            if (clientesSelect === "selecionados") {
                const checkboxes = document.querySelectorAll(".cliente-checkbox:checked");
                if (checkboxes.length === 0) {
                    alert("Selecione pelo menos um cliente");
                    return;
                }
                clientIds = Array.from(checkboxes).map(cb => Number(cb.value));
            }

            try {
                progressoCampanha.innerHTML = "⏳ Enviando campanha...";
                progressoCampanha.className = "status-info";

                const result = await Api.post("/evolution/send-campaign-whatsapp", {
                    message: mensagem,
                    client_ids: clientIds
                });

                const taxa_sucesso = ((result.total_enviados / result.total_destinatarios) * 100).toFixed(1);

                progressoCampanha.innerHTML = `
                    ✅ Campanha enviada!
                    <br>
                    Enviados: ${result.total_enviados} / ${result.total_destinatarios}
                    <br>
                    Taxa de sucesso: ${taxa_sucesso}%
                    ${result.total_falhas > 0 ? `<br>Falhas: ${result.total_falhas}` : ""}
                `;
                progressoCampanha.className = "status-success";

                campaignMessage.value = "";

            } catch (err) {
                progressoCampanha.innerHTML = `❌ Erro: ${err.message}`;
                progressoCampanha.className = "status-error";
            }
        };
    }

    return {
        carregarConfiguracao
    };

})();

// Carregar configuração ao iniciar
setTimeout(() => whatsappModule.carregarConfiguracao(), 500);
