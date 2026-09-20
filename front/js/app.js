import { carregarDados } from "./data-provider.js";


const state = {
    indicadores: [],
    temas: [],
    temaSelecionado: "Todos",
    busca: "",
    selecionado: null,
};


const elementos = {
    tabs: document.querySelector("#tabs-temas"),
    busca: document.querySelector("#busca"),
    contador: document.querySelector("#contador"),
    lista: document.querySelector("#lista-indicadores"),
    detalhe: document.querySelector("#detalhe"),
    mensagem: document.querySelector("#mensagem"),
};


function normalizarTexto(valor) {
    return (valor || "")
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .trim();
}


function formatarNumero(valor) {
    if (valor === null || valor === undefined || Number.isNaN(Number(valor))) {
        return "—";
    }

    const numero = Number(valor);

    return numero.toLocaleString("pt-BR", {
        maximumFractionDigits: 2,
        minimumFractionDigits: Number.isInteger(numero) ? 0 : 2,
    });
}


function formatarValor(indicador, valor) {
    const unidade = normalizarTexto(indicador.unidade);

    if (valor === null || valor === undefined) {
        return "—";
    }

    if (unidade.includes("%")) {
        return `${formatarNumero(valor)}%`;
    }

    return `${formatarNumero(valor)}${indicador.unidade ? ` ${indicador.unidade}` : ""}`;
}


function escaparHtml(texto) {
    return String(texto ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function indicadoresFiltrados() {
    const busca = normalizarTexto(state.busca);

    return state.indicadores.filter(indicador => {
        const pertenceAoTema =
            state.temaSelecionado === "Todos" ||
            indicador.tema === state.temaSelecionado;

        if (!pertenceAoTema) {
            return false;
        }

        if (!busca) {
            return true;
        }

        const textoPesquisa = normalizarTexto([
            indicador.codigo,
            indicador.nome,
            indicador.tema,
            indicador.definicao,
            indicador.uso,
        ].join(" "));

        return textoPesquisa.includes(busca);
    });
}


function renderTabs() {
    const todos = `
        <button
            class="tab ${state.temaSelecionado === "Todos" ? "ativo" : ""}"
            type="button"
            data-tema="Todos"
            aria-pressed="${state.temaSelecionado === "Todos"}"
        >
            Todos
        </button>
    `;

    const abas = state.temas.map(tema => `
        <button
            class="tab ${state.temaSelecionado === tema ? "ativo" : ""}"
            type="button"
            data-tema="${escaparHtml(tema)}"
            aria-pressed="${state.temaSelecionado === tema}"
        >
            ${escaparHtml(tema)}
        </button>
    `).join("");

    elementos.tabs.innerHTML = todos + abas;

    elementos.tabs
        .querySelectorAll(".tab")
        .forEach(botao => {
            botao.addEventListener("click", () => {
                state.temaSelecionado = botao.dataset.tema;
                renderTabs();
                renderLista();
            });
        });
}


function renderLista() {
    const filtrados = indicadoresFiltrados();

    elementos.contador.textContent =
        `${filtrados.length} indicador(es) encontrado(s)`;

    if (!filtrados.length) {
        elementos.lista.innerHTML = `
            <div class="estado-vazio">
                <h2>Nenhum indicador encontrado</h2>
                <p>
                    Tente outro termo de busca ou selecione a aba "Todos".
                </p>
            </div>
        `;
        return;
    }

    elementos.lista.innerHTML = filtrados.map(indicador => {
        const temDados = indicador.dados && indicador.dados.length > 0;

        return `
            <button
                class="card-indicador"
                type="button"
                data-codigo="${escaparHtml(indicador.codigo)}"
            >
                <span class="card-tema">${escaparHtml(indicador.tema)}</span>
                <span class="card-titulo">${escaparHtml(indicador.nome)}</span>

                <span class="card-valor">
                    ${
                        indicador.ultimo_valor !== null
                            ? formatarValor(indicador, indicador.ultimo_valor)
                            : "Sem dados"
                    }
                </span>

                <span class="card-meta">
                    ${
                        indicador.ultimo_ano !== null
                            ? `Último dado: ${indicador.ultimo_ano}`
                            : "Não há dados disponíveis"
                    }
                </span>

                <span class="card-estado">
                    ${temDados ? "Ver histórico →" : "Sem dados correspondentes para o período"}
                </span>
            </button>
        `;
    }).join("");

    elementos.lista
        .querySelectorAll(".card-indicador")
        .forEach(card => {
            card.addEventListener("click", () => {
                abrirDetalhe(card.dataset.codigo);
            });
        });
}


function abrirDetalhe(codigo) {
    const indicador = state.indicadores.find(item => item.codigo === codigo);

    if (!indicador) {
        return;
    }

    state.selecionado = indicador;

    renderDetalhe();

    elementos.detalhe.scrollIntoView({
        behavior: "smooth",
        block: "start",
    });
}


function calcularVariacao(indicador) {
    if (!indicador.dados || indicador.dados.length < 2) {
        return null;
    }

    const atual = indicador.dados[indicador.dados.length - 1];
    const anterior = indicador.dados[indicador.dados.length - 2];

    if (!anterior || anterior.valor === null || anterior.valor === 0) {
        return {
            tipo: "indisponivel",
            texto: "Comparação indisponível",
        };
    }

    const variacao = ((atual.valor - anterior.valor) / anterior.valor) * 100;

    return {
        tipo: variacao >= 0 ? "alta" : "baixa",
        texto: `${variacao >= 0 ? "+" : ""}${variacao.toFixed(2)}%`,
        anoAnterior: anterior.ano,
        valorAnterior: anterior.valor,
    };
}


function renderGrafico(indicador) {
    const dados = indicador.dados || [];

    if (!dados.length) {
        return `
            <div class="grafico-vazio">
                Sem dados correspondentes para o período.
            </div>
        `;
    }

    const largura = 900;
    const altura = 320;
    const margem = {
        esquerda: 70,
        direita: 30,
        topo: 30,
        base: 55,
    };

    const valores = dados.map(item => Number(item.valor));
    const min = Math.min(...valores);
    const max = Math.max(...valores);

    const intervalo = max - min || 1;

    const x = index => {
        if (dados.length === 1) {
            return (largura - margem.direita + margem.esquerda) / 2;
        }

        return margem.esquerda +
            (index / (dados.length - 1)) *
            (largura - margem.esquerda - margem.direita);
    };

    const y = valor => {
        return margem.topo +
            (1 - ((valor - min) / intervalo)) *
            (altura - margem.topo - margem.base);
    };

    const pontos = dados.map((item, index) => ({
        x: x(index),
        y: y(Number(item.valor)),
        ano: item.ano,
        valor: item.valor,
    }));

    const path = pontos
        .map((ponto, index) => {
            return `${index === 0 ? "M" : "L"} ${ponto.x.toFixed(2)} ${ponto.y.toFixed(2)}`;
        })
        .join(" ");

    const pontosSvg = pontos.map(ponto => `
        <circle
            cx="${ponto.x}"
            cy="${ponto.y}"
            r="4"
            class="ponto-grafico"
        >
            <title>
                ${ponto.ano}: ${formatarValor(indicador, ponto.valor)}
            </title>
        </circle>
    `).join("");

    const primeiroAno = dados[0].ano;
    const ultimoAno = dados[dados.length - 1].ano;

    return `
        <div class="grafico-container">
            <svg
                viewBox="0 0 ${largura} ${altura}"
                role="img"
                aria-label="Histórico de ${escaparHtml(indicador.nome)}"
            >
                <line
                    x1="${margem.esquerda}"
                    y1="${altura - margem.base}"
                    x2="${largura - margem.direita}"
                    y2="${altura - margem.base}"
                    class="eixo"
                />

                <line
                    x1="${margem.esquerda}"
                    y1="${margem.topo}"
                    x2="${margem.esquerda}"
                    y2="${altura - margem.base}"
                    class="eixo"
                />

                <path
                    d="${path}"
                    class="linha-grafico"
                    fill="none"
                />

                ${pontosSvg}

                <text
                    x="${margem.esquerda}"
                    y="${altura - 18}"
                    class="rotulo-grafico"
                >
                    ${primeiroAno}
                </text>

                <text
                    x="${largura - margem.direita}"
                    y="${altura - 18}"
                    text-anchor="end"
                    class="rotulo-grafico"
                >
                    ${ultimoAno}
                </text>

                <text
                    x="18"
                    y="${margem.topo + 6}"
                    class="rotulo-grafico"
                >
                    ${formatarNumero(max)}
                </text>

                <text
                    x="18"
                    y="${altura - margem.base}"
                    class="rotulo-grafico"
                >
                    ${formatarNumero(min)}
                </text>
            </svg>
        </div>
    `;
}


function renderTabela(indicador) {
    const dados = indicador.dados || [];

    if (!dados.length) {
        return `
            <div class="tabela-vazia">
                Sem dados correspondentes para o período.
            </div>
        `;
    }

    const linhas = [...dados].reverse().map(item => `
        <tr>
            <td>${item.ano}</td>
            <td>${formatarValor(indicador, item.valor)}</td>
        </tr>
    `).join("");

    return `
        <div class="tabela-scroll">
            <table>
                <thead>
                    <tr>
                        <th scope="col">Ano</th>
                        <th scope="col">Valor</th>
                    </tr>
                </thead>
                <tbody>
                    ${linhas}
                </tbody>
            </table>
        </div>
    `;
}


function renderDetalhe() {
    const indicador = state.selecionado;

    if (!indicador) {
        elementos.detalhe.innerHTML = `
            <div class="detalhe-vazio">
                <p>Selecione um indicador para visualizar os detalhes.</p>
            </div>
        `;
        return;
    }

    const comparacao = calcularVariacao(indicador);

    elementos.detalhe.innerHTML = `
        <div class="detalhe-cabecalho">
            <div>
                <span class="detalhe-tema">
                    ${escaparHtml(indicador.tema)}
                </span>

                <h2>${escaparHtml(indicador.nome)}</h2>

                <p class="codigo-indicador">
                    Código: ${escaparHtml(indicador.codigo)}
                </p>
            </div>

            <button
                type="button"
                class="botao-fechar"
                id="fechar-detalhe"
                aria-label="Fechar detalhes do indicador"
            >
                ×
            </button>
        </div>

        <div class="resumo-grid">
            <div class="kpi">
                <span class="kpi-label">Último dado</span>
                <strong>
                    ${
                        indicador.ultimo_valor !== null
                            ? formatarValor(indicador, indicador.ultimo_valor)
                            : "Sem dados"
                    }
                </strong>
            </div>

            <div class="kpi">
                <span class="kpi-label">Último ano</span>
                <strong>
                    ${indicador.ultimo_ano ?? "—"}
                </strong>
            </div>

            <div class="kpi">
                <span class="kpi-label">Variação</span>
                <strong>
                    ${
                        comparacao
                            ? comparacao.texto
                            : "—"
                    }
                </strong>
                ${
                    comparacao && comparacao.anoAnterior
                        ? `<small>vs. ${comparacao.anoAnterior}</small>`
                        : ""
                }
            </div>
        </div>

        <section class="detalhe-secao">
            <h3>Histórico</h3>
            ${renderGrafico(indicador)}
            ${renderTabela(indicador)}
        </section>

        <section class="detalhe-secao">
            <h3>Sobre o indicador</h3>

            <dl class="metadados">
                <div>
                    <dt>Definição</dt>
                    <dd>
                        ${
                            indicador.definicao
                                ? escaparHtml(indicador.definicao)
                                : "Informação ainda não cadastrada."
                        }
                    </dd>
                </div>

                <div>
                    <dt>Uso</dt>
                    <dd>
                        ${
                            indicador.uso
                                ? escaparHtml(indicador.uso)
                                : "Informação ainda não cadastrada."
                        }
                    </dd>
                </div>

                <div>
                    <dt>Unidade</dt>
                    <dd>
                        ${
                            indicador.unidade
                                ? escaparHtml(indicador.unidade)
                                : "Informação ainda não cadastrada."
                        }
                    </dd>
                </div>

                <div>
                    <dt>Periodicidade</dt>
                    <dd>
                        ${
                            indicador.periodicidade
                                ? escaparHtml(indicador.periodicidade)
                                : "Informação ainda não cadastrada."
                        }
                    </dd>
                </div>

                <div>
                    <dt>Fonte</dt>
                    <dd>
                        ${
                            indicador.fonte
                                ? escaparHtml(indicador.fonte)
                                : "Informação ainda não cadastrada."
                        }
                    </dd>
                </div>

                <div>
                    <dt>Metodologia</dt>
                    <dd>
                        ${
                            indicador.metodologia
                                ? escaparHtml(indicador.metodologia)
                                : "Informação ainda não cadastrada."
                        }
                    </dd>
                </div>
            </dl>
        </section>
    `;

    document.querySelector("#fechar-detalhe")
        .addEventListener("click", () => {
            state.selecionado = null;
            renderDetalhe();
        });
}


async function iniciar() {
    elementos.mensagem.textContent = "Carregando indicadores...";

    try {
        const dados = await carregarDados();

        state.indicadores = dados.indicadores || [];
        state.temas = dados.temas || [];

        elementos.mensagem.textContent = "";

        renderTabs();
        renderLista();
        renderDetalhe();
    } catch (erro) {
        console.error(erro);

        elementos.mensagem.textContent =
            "Não foi possível carregar os dados. Execute o servidor local pelo script scripts/exibir_front.py.";
    }
}


elementos.busca.addEventListener("input", event => {
    state.busca = event.target.value;
    renderLista();
});

iniciar();
