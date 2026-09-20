/*
 * CAMADA DE DADOS DO FRONTEND
 *
 * Hoje:
 *   usa o JSON local gerado pelo Python.
 *
 * Futuro:
 *   defina DATA_SOURCE = "api"
 *   e API_BASE_URL com a URL do FastAPI.
 *
 * Contrato esperado da futura API:
 *   GET /api/indicadores
 *   GET /api/indicadores/{codigo}
 */

const DATA_SOURCE = "local";

// Exemplo futuro:
// const API_BASE_URL = "http://localhost:8000";
const API_BASE_URL = "";


async function carregarDadosLocais() {
    const response = await fetch("data/indicadores.json");

    if (!response.ok) {
        throw new Error("Não foi possível carregar data/indicadores.json");
    }

    return await response.json();
}


async function carregarDadosAPI() {
    if (!API_BASE_URL) {
        throw new Error("API_BASE_URL não configurada.");
    }

    const response = await fetch(`${API_BASE_URL}/api/indicadores`);

    if (!response.ok) {
        throw new Error(`Erro na API: HTTP ${response.status}`);
    }

    const indicadores = await response.json();

    // A API futura pode retornar um array puro.
    // Adaptamos para o mesmo formato usado pelo frontend local.
    return {
        gerado_em: null,
        fonte_local: "FastAPI",
        temas: [...new Set(indicadores.map(item => item.tema).filter(Boolean))],
        indicadores
    };
}


export async function carregarDados() {
    if (DATA_SOURCE === "api") {
        return await carregarDadosAPI();
    }

    return await carregarDadosLocais();
}


export async function carregarIndicadorPorCodigo(codigo) {
    if (DATA_SOURCE === "api") {
        const response = await fetch(
            `${API_BASE_URL}/api/indicadores/${encodeURIComponent(codigo)}`
        );

        if (!response.ok) {
            throw new Error(`Indicador não encontrado na API: ${codigo}`);
        }

        return await response.json();
    }

    const dados = await carregarDadosLocais();

    return dados.indicadores.find(
        indicador => indicador.codigo === codigo
    ) || null;
}
