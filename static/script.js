let editIndex = null; // Índice do item sendo editado
const localStorageKey = 'nutrientes';

// Inicialização ao carregar o DOM
document.addEventListener('DOMContentLoaded', () => {
    initializeStorage();

    // Identifica a rota atual
    const currentPath = window.location.pathname;
    // Verifica se a rota é /nutrientes
    if (currentPath === '/nutrientes') {
        renderNutrients();
        updateItemCount();
    } else if(currentPath === '/formulador1'){
        loadNutrientList();
    } else if (currentPath === '/formulador2') {
        const cardResults = document.getElementById("cardResults");
        cardResults.style.opacity = 0;
        loadMateriasPrimas();
    }
});

// Inicializa o armazenamento local
function initializeStorage() {
    if (!localStorage.getItem(localStorageKey)) {
        fetch('/static/materias_primas.json')
            .then((response) => response.json())
            .then((data) => {
                localStorage.setItem(localStorageKey, JSON.stringify(data.data));
            });
    }
}

// Exibe feedback visual
function showFeedback(message, type) {
    const feedback = document.getElementById('feedback');
    feedback.textContent = message;
    feedback.className = `feedback ${type}`;
    feedback.style.display = 'block';

    setTimeout(() => {
        feedback.style.display = 'none';
    }, 3000);
}

// Cria um campo de nutriente (utilizado em várias funções)
function createNutrientField(nutrient = { name: '', percent: '' }) {
    const container = document.querySelector('#nutrientsContainer');

    const field = document.createElement('div');
    field.className = 'nutrient-field';

    const nutrientInput = document.createElement('input');
    nutrientInput.name = 'nutrientName';
    nutrientInput.type = 'text';
    nutrientInput.value = nutrient.name;
    nutrientInput.placeholder = 'Ex.: N';
    nutrientInput.required = true;
    nutrientInput.className = 'nutrient-input';

    const percentInput = document.createElement('input');
    percentInput.name = 'percent';
    percentInput.type = 'number';
    percentInput.value = nutrient.percent;
    percentInput.placeholder = '%';
    percentInput.min = 0;
    percentInput.max = 100;
    percentInput.required = true;
    percentInput.className = 'percent-input';

    const removeButton = document.createElement('button');
    removeButton.textContent = '-';
    removeButton.type = 'button';
    removeButton.className = 'remove-button';
    removeButton.onclick = () => field.remove();

    field.appendChild(nutrientInput);
    field.appendChild(percentInput);
    field.appendChild(removeButton);
    container.appendChild(field);
}

// Adiciona um novo campo vazio
function addNutrientField() {
    createNutrientField();
}

// Valida se a soma dos percentuais dos nutrientes não ultrapassa 100%
function validatePercentages(nutrientFields) {
    let totalPercent = 0;

    nutrientFields.forEach((field) => {
        const percent = parseFloat(field.querySelector('[name="percent"]').value);
        totalPercent += percent || 0;
    });

    if (totalPercent > 100) {
        showFeedback('Erro: A soma dos percentuais dos nutrientes não pode ultrapassar 100%.', 'error');
        throw new Error('Total percentual excede 100%.');
    }
}

// Salva ou edita um nutriente
function saveNutrient() {
    const name = document.getElementById('name').value;
    const isNutrient = document.getElementById('isNutrient').checked;
    const nutrientFields = document.querySelectorAll('.nutrient-field');

    if (!name) {
        showFeedback('Erro: O nome da matéria-prima é obrigatório!', 'error');
        return;
    }

    const nutrients = [];
    nutrientFields.forEach((field) => {
        const nutrientName = field.querySelector('[name="nutrientName"]').value;
        const percent = parseFloat(field.querySelector('[name="percent"]').value);

        if (nutrientName && percent) {
            nutrients.push({ name: nutrientName, percent });
        }
    });

    validatePercentages(nutrientFields);

    let nutrientsList = JSON.parse(localStorage.getItem(localStorageKey)) || [];
    const newEntry = { name, isNutrient, nutrient: nutrients };

    if (editIndex !== null) {
        nutrientsList[editIndex] = newEntry;
        editIndex = null;
    } else {
        nutrientsList.push(newEntry);
    }

    localStorage.setItem(localStorageKey, JSON.stringify(nutrientsList));
    renderNutrients();
    showFeedback(`${isNutrient ? 'Nutriente' : 'Enchimento'} salvo com sucesso!`, 'success');
    resetForm();
}

// Reseta o formulário para o estado inicial
function resetForm() {
    document.getElementById('name').value = '';
    document.getElementById('isNutrient').checked = true;
    document.querySelector('#nutrientsContainer').innerHTML = '';
    addNutrientField();
}

// Preenche o formulário para edição
function editNutrient(index) {
    const nutrientsList = JSON.parse(localStorage.getItem(localStorageKey)) || [];
    const item = nutrientsList[index];

    document.getElementById('name').value = item.name;
    document.getElementById('isNutrient').checked = item.isNutrient;

    const container = document.querySelector('#nutrientsContainer');
    container.innerHTML = '';
    item.nutrient.forEach((n) => createNutrientField(n));

    editIndex = index;

    const formContainer = document.querySelector('.form-container');
    formContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    document.getElementById('name').focus();
}

// Exclui um nutriente
function deleteNutrient(index) {
    const nutrientsList = JSON.parse(localStorage.getItem(localStorageKey)) || [];

    if (index >= 0 && index < nutrientsList.length) {
        nutrientsList.splice(index, 1);
        localStorage.setItem(localStorageKey, JSON.stringify(nutrientsList));
        renderNutrients();
        showFeedback('Nutriente removido com sucesso!', 'success');
    } else {
        showFeedback('Erro ao tentar remover o nutriente.', 'error');
    }
}

// Renderiza os cartões de nutrientes
function renderNutrients() {
    const nutrientCards = document.getElementById('nutrientCards');
    nutrientCards.innerHTML = '';

    const nutrientsList = JSON.parse(localStorage.getItem(localStorageKey)) || [];
    nutrientsList.forEach((item, index) => {
        const card = document.createElement('div');
        card.className = `card ${item.isNutrient ? 'nutrient-card' : 'enchimento-card'}`;

        card.innerHTML = `
            <h3 class="card-title">${item.name}</h3>
            <p class="card-description">${item.isNutrient 
                ? item.nutrient.map(n => `${n.name}: ${n.percent}%`).join(', ') 
                : 'Enchimento'}</p>
        `;

        const buttonsContainer = document.createElement('div');
        buttonsContainer.className = 'card-buttons';

        const editButton = document.createElement('button');
        editButton.className = 'edit-button';
        editButton.textContent = 'Editar';
        editButton.onclick = () => editNutrient(index);

        const deleteButton = document.createElement('button');
        deleteButton.className = 'remove-button';
        deleteButton.textContent = 'Excluir';
        deleteButton.onclick = () => deleteNutrient(index);

        buttonsContainer.appendChild(editButton);
        buttonsContainer.appendChild(deleteButton);
        card.appendChild(buttonsContainer);
        nutrientCards.appendChild(card);
    });

    updateInfoTable(nutrientsList);
    updateItemCount();
}

// Atualiza o total de itens exibidos na tela
function updateItemCount() {
    const nutrientsList = JSON.parse(localStorage.getItem(localStorageKey)) || [];
    document.getElementById('totalItems').textContent = nutrientsList.length;
}

// Atualiza a tabela informativa
function updateInfoTable(nutrientsList) {
    const totalNutrients = nutrientsList.filter((item) => item.isNutrient).length;
    const totalFillers = nutrientsList.filter((item) => !item.isNutrient).length;

    const nutrientBaseCounts = ['N', 'P', 'K'].map((base) =>
        nutrientsList.filter((item) => item.nutrient.some((n) => n.name === base)).length
    );

    document.getElementById('totalNutrients').textContent = totalNutrients;
    document.getElementById('totalFillers').textContent = totalFillers;
    document.getElementById('totalNBase').textContent = nutrientBaseCounts[0];
    document.getElementById('totalPBase').textContent = nutrientBaseCounts[1];
    document.getElementById('totalKBase').textContent = nutrientBaseCounts[2];
}


function loadNutrientList() {
    const nutrients = JSON.parse(localStorage.getItem('nutrientes')) || [];
    const container = document.getElementById('nutrientList');
    container.innerHTML = '';

    document.getElementById('remainingKg').textContent = 1000;

    nutrients.forEach(mp => {
        // Criação do card
        const card = document.createElement('div');
        card.className = 'nutrient-card';

        // Título do nutriente
        const title = document.createElement('h3');
        title.textContent = mp.name;

        // Descrição com os teores de nutrientes
        const description = document.createElement('p');
        description.innerHTML = `
            <strong>N:</strong> ${mp.nutrient
                .filter(n => n.name === 'N')
                .reduce((sum, n) => sum + n.percent, 0)}% | 
            <strong>P₂O₅:</strong> ${mp.nutrient
                .filter(n => n.name.startsWith('P'))
                .reduce((sum, n) => sum + n.percent, 0)}% | 
            <strong>K₂O:</strong> ${mp.nutrient
                .filter(n => n.name.startsWith('K'))
                .reduce((sum, n) => sum + n.percent, 0)}%`;

        // Campo de entrada para quantidade
        const input = document.createElement('input');
        input.type = 'number';
        input.placeholder = 'KG';
        input.className = 'nutrient-input';
        input.dataset.id = mp.id;
        input.dataset.name = mp.name;
        input.dataset.isNutrient = mp.isNutrient;
        input.dataset.teor_n = mp.nutrient
            .filter(n => n.name.startsWith('N'))
            .reduce((sum, n) => sum + n.percent, 0);
        input.dataset.teor_p2o5 = mp.nutrient
            .filter(n => n.name.startsWith('P'))
            .reduce((sum, n) => sum + n.percent, 0);
        input.dataset.teor_k2o = mp.nutrient
            .filter(n => n.name.startsWith('K'))
            .reduce((sum, n) => sum + n.percent, 0);
        input.oninput = updateRealTimeCalculation; // Atualiza o cálculo em tempo real

        // Adiciona elementos ao card
        card.appendChild(title);
        card.appendChild(description);
        card.appendChild(input);

        // Adiciona o card ao container
        container.appendChild(card);
    });
}


function updateRealTimeCalculation() {
    const nutrientInputs = document.querySelectorAll('.nutrient-input');

    let totalKg = 0; // Total de KG das matérias-primas
    let totalN = 0; // Total de Nitrogênio (N)
    let totalP = 0; // Total de Fósforo (P₂O₅)
    let totalK = 0; // Total de Potássio (K₂O)
    const materiasPrimas = []; // Lista de matérias-primas selecionadas
    const enchimentos = []; // Lista de enchimentos

    // Calcula os valores com base nos inputs
    nutrientInputs.forEach(input => {
        const kg = parseFloat(input.value) || 0; // Quantidade informada (em KG)
        const teorN = parseFloat(input.dataset.teor_n) || 0; // Teor de N
        const teorP = parseFloat(input.dataset.teor_p2o5) || 0; // Teor de P₂O₅
        const teorK = parseFloat(input.dataset.teor_k2o) || 0; // Teor de K₂O

        if (kg > 0) {

            if (input.dataset.isNutrient === 'true') {
                materiasPrimas.push({ name: input.dataset.name, kg, isNutrient: input.dataset.isNutrient });
            } else {
                enchimentos.push({ name: input.dataset.name, kg, isNutrient: input.dataset.isNutrient });
            }
        }

        // Calcula os totais
        totalKg += kg;
        totalN += (kg * teorN) / 100;
        totalP += (kg * teorP) / 100;
        totalK += (kg * teorK) / 100;
    });


    // Calcula o enchimento necessário
    const enchimentoKg = Math.max(1000 - totalKg, 0);
    if (enchimentoKg > 0) {
        enchimentos.push({ name: 'Enchimento', kg: enchimentoKg });
    }

    // Atualiza a indicação de KG restantes
    const remainingKg = Math.max(1000 - totalKg, 0).toFixed(2);
    document.getElementById('remainingKg').textContent = remainingKg;

    // Atualiza o card de resumo
    updateSummaryCard(totalN, totalP, totalK, materiasPrimas, enchimentos, totalKg + enchimentoKg);
}

// Atualiza o conteúdo do card de resumo
function updateSummaryCard(totalN, totalP, totalK, materiasPrimas, enchimentos, totalKg) {
    const summaryContainer = document.getElementById('summaryCard');
    summaryContainer.innerHTML = `
        <h3>Resumo da Fórmula</h3>
        <div class="npk-info">N-P-K: ${(totalN/10).toFixed(0)}-${(totalP/10).toFixed(0)}-${(totalK/10).toFixed(0)}</div>
        <ul>
            <li><strong>Matérias-primas:</strong></li>
            ${materiasPrimas.map(mp => `<li>• ${mp.name}: ${mp.kg.toFixed(0)} kg</li>`).join('')}
            <li><strong>Enchimentos:</strong></li>
            ${enchimentos.map(e => `<li>• ${e.name}: ${e.kg.toFixed(0)} kg</li>`).join('')}
        </ul>
        <div class="nutrient-summary">
                <h4>Nutrientes Disponibilizados:</h4>
                <ul>
                    <li>• N: ${totalN.toFixed(0)} kg</li>
                    <li>• P: ${totalP.toFixed(0)} kg</li>
                    <li>• K: ${totalK.toFixed(0)} kg</li>
                </ul>
            </div>
        <div class="total">Total: ${totalKg.toFixed(0)} kg</div>
    `;

    console.log(materiasPrimas)
    console.log(enchimentos)
}

function calculateFormula_old() {
    const formulado = document.getElementById('formulado').value.trim();
    const selectedInputs = Array.from(document.querySelectorAll('#materiasPrimasTable input[type="checkbox"]:checked'));

    if (!formulado) {
        alert("Por favor, informe o formulado desejado (ex.: 04-20-20).");
        return;
    }

    if (selectedInputs.length === 0) {
        alert("Selecione pelo menos uma matéria-prima.");
        return;
    }

    const selectedMateriasPrimas = selectedInputs.map(input => ({
        name: input.dataset.name,
        nutrients: JSON.parse(input.dataset.nutrients)
    }));

    fetch('/formulador2/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            formulado: formulado,
            materiasPrimas: selectedMateriasPrimas
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            displayResults(data.results);
        }
    })
    .catch(error => {
        console.error("Erro ao calcular a fórmula:", error);
        alert("Ocorreu um erro ao calcular a fórmula.");
    });
}

function calculateFormula() {
    const formulado = document.getElementById('formulado').value.trim();
    const selectedInputs = Array.from(document.querySelectorAll('#materiasPrimasTable input[type="checkbox"]:checked'));
    const limite_enchimento = document.getElementById('limite_enchimento').value.trim();
    const margem = document.getElementById('margem').value.trim();
    const step = document.getElementById('step').value.trim();


    if (!formulado) {
        alert("Por favor, informe o formulado desejado (ex.: 04-20-20).");
        return;
    }

    if (selectedInputs.length === 0) {
        alert("Selecione pelo menos uma matéria-prima.");
        return;
    }

    if (!limite_enchimento || limite_enchimento < 0 || limite_enchimento > 1000) {
        alert("Por favor, informe o limite de enchimento correto");
        return;
    }

    if (!margem) {
        alert("Por favor, informe a margem.");
        return;
    }

    if (!step) {
        alert("Por favor, informe intervalo de variação.");
        return;
    }

    const selectedMateriasPrimas = selectedInputs.map(input => ({
        name: input.dataset.name,
        nutrients: JSON.parse(input.dataset.nutrients),
        isNutrient: input.dataset.isnutrient === "true"
    }));

    loadCalculate(true);

    console.log("Conectando API..")
    fetch('/formulador2/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            formulado: formulado,
            materiasPrimas: selectedMateriasPrimas,
            limiteEnchimento: limite_enchimento,
            margem: margem,
            step: step,
            incompatibility: document.getElementById('incompatibility').checked
        })
    })
    .then(response => response.json())
    .then(data => exibirResultados(data)) // ✅ Chama a função para exibir os resultados
    .catch(error => {
        loadCalculate(false);
        console.error("Erro ao calcular a fórmula:", error);
        alert("Ocorreu um erro ao calcular a fórmula.");
    });
}

function displayResults(results) {
    const container = document.getElementById('resultsContainer');
    container.innerHTML = '';

    if (results.length === 0) {
        container.innerHTML = '<p>Não foi possível encontrar uma combinação com as matérias-primas selecionadas.</p>';
        return;
    }

    results.forEach((result, index) => {
        const div = document.createElement('div');
        div.className = 'result-card';
        div.innerHTML = `
            <h3>Opção ${index + 1}</h3>
            <p><strong>Formulado (NPK):</strong> ${result.formulado}</p>
            <ul>
                <li><strong>Matérias-Primas:</strong></li>
                ${result.materiasPrimas.map(mp => `<li>• ${mp.name}: ${mp.kg.toFixed(2)} kg</li>`).join('')}
                <li><strong>Enchimentos:</strong></li>
                ${result.enchimentos.map(e => `<li>• ${e.name}: ${e.kg.toFixed(2)} kg</li>`).join('')}
            </ul>
            <p><strong>Total:</strong> 1000 kg</p>
        `;
        container.appendChild(div);
    });
}

// Função para prever o total de combinações possíveis
function preverTotalCombinacoes_old(formulado, materiasPrimas, step = 10) {
    // Extrai os valores do formulado (N-P-K)
    const [targetN, targetP, targetK] = formulado.split('-').map(parseFloat);

    // Filtra matérias-primas relevantes com base no formulado
    const nutrientesRelevantes = {
        N: targetN > 0,
        P: targetP > 0,
        K: targetK > 0
    };

    const materiasPorNutriente = {
        N: materiasPrimas.filter(mp =>
            nutrientesRelevantes.N &&
            mp.nutrients.some(n => n.name === 'N' && parseFloat(n.percent) > 0)
        ),
        P: materiasPrimas.filter(mp =>
            nutrientesRelevantes.P &&
            mp.nutrients.some(n => n.name.startsWith('P') && parseFloat(n.percent) > 0)
        ),
        K: materiasPrimas.filter(mp =>
            nutrientesRelevantes.K &&
            mp.nutrients.some(n => n.name.startsWith('K') && parseFloat(n.percent) > 0)
        )
    };

    // Calcula as possibilidades para cada nutriente
    const possibilidadesPorNutriente = Object.keys(nutrientesRelevantes).map(nutriente => {
        const materias = materiasPorNutriente[nutriente];
        if (!nutrientesRelevantes[nutriente] || materias.length === 0) {
            return 1; // Se não houver matérias-primas para o nutriente, ignora
        }
        const possibilidadesPorMateria = Math.floor(100 / step) + 1; // Quantas opções por MP (0, step, ..., 100)
        return Math.pow(possibilidadesPorMateria, materias.length);
    });

    // Calcula o total de combinações possíveis
    const totalCombinacoes = possibilidadesPorNutriente.reduce((total, comb) => total * comb, 1);

    return totalCombinacoes;
}

// Evento para atualizar a previsão quando o formulado é alterado
document.getElementById('formulado').addEventListener('input', atualizarPrevisaoCombinacoes);

// Máscara para o campo do formulado
function aplicarMascaraFormulado(input) {
    let valor = input.value.replace(/\D/g, ""); // Remove qualquer caractere não numérico
    if (valor.length > 6) valor = valor.slice(0, 6); // Limita o comprimento a 6 dígitos

    const formatado = valor
        .replace(/^(\d{2})(\d{0,2})(\d{0,2})$/, (_, n, p, k) => {
            return `${n}-${p}${p.length > 0 ? '-' : ''}${k}`;
        });

    input.value = formatado;
}

// Função para aplicar a máscara no input ao digitar
document.getElementById('formulado').addEventListener('input', (event) => {
    aplicarMascaraFormulado(event.target);
    atualizarPrevisaoCombinacoes(); // Recalcula automaticamente ao inserir o formulado
});

// Função para atualizar a seleção com base em um critério
function selecionar(tipo) {
    const checkboxes = document.querySelectorAll('#materiasPrimasTable input[type="checkbox"]');

    checkboxes.forEach(checkbox => {
        const isNutrient = JSON.parse(checkbox.dataset.nutrients).length > 0; // Verifica se tem nutrientes
        if (tipo === "tudo" || (tipo === "nutrientes" && isNutrient) || (tipo === "enchimentos" && !isNutrient)) {
            checkbox.checked = true;
        }
    });

    atualizarPrevisaoCombinacoes(); // Atualiza a previsão após a seleção
}

// Função para remover todas as seleções
function removerTudo() {
    const checkboxes = document.querySelectorAll('#materiasPrimasTable input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });

    atualizarPrevisaoCombinacoes(); // Atualiza a previsão após a remoção
}

// Carrega as matérias-primas na tabela e adiciona eventos de seleção
function loadMateriasPrimas() {
    const materiasPrimas = JSON.parse(localStorage.getItem('nutrientes')) || [];
    const tableBody = document.getElementById('materiasPrimasTable');
    tableBody.innerHTML = '';

    materiasPrimas.forEach(mp => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>
                <input 
                    type="checkbox" 
                    data-name="${mp.name}" 
                    data-nutrients='${JSON.stringify(mp.nutrient)}' 
                    data-isNutrient='${mp.isNutrient}'
                />
            </td>
            <td>${mp.name}</td>
            <td>${mp.nutrient.map(n => `${n.name}: ${n.percent}%`).join(', ')}</td>
        `;
        tableBody.appendChild(tr);
    });
    // Adiciona evento de cálculo automático na seleção
    tableBody.querySelectorAll('input[type="checkbox"]').forEach(input => {
        input.addEventListener('change', atualizarPrevisaoCombinacoes);
    });
}

// Função para validar matérias-primas selecionadas de acordo com o formulado
function validarMateriasPrimas(formulado, materiasPrimasSelecionadas) {
    const [targetN, targetP, targetK] = formulado.split('-').map(parseFloat);

    // Nutrientes exigidos pelo formulado
    const nutrientesNecessarios = {
        N: targetN > 0,
        P: targetP > 0,
        K: targetK > 0
    };

    // Verifica se há matérias-primas que forneçam cada nutriente necessário
    const nutrientesSelecionados = {
        N: materiasPrimasSelecionadas.some(mp =>
            mp.nutrients.some(n => n.name.startsWith('N') && parseFloat(n.percent) > 0)
        ),
        P: materiasPrimasSelecionadas.some(mp =>
            mp.nutrients.some(n => n.name.startsWith('P') && parseFloat(n.percent) > 0)
        ),
        K: materiasPrimasSelecionadas.some(mp =>
            mp.nutrients.some(n => n.name.startsWith('K') && parseFloat(n.percent) > 0)
        )
    };

    // Identifica nutrientes faltantes
    const erros = [];
    Object.keys(nutrientesNecessarios).forEach(nutriente => {
        if (nutrientesNecessarios[nutriente] && !nutrientesSelecionados[nutriente]) {
            erros.push(`Por favor, selecione pelo menos uma matéria-prima que forneça ${nutriente}.`);
        }
    });

    return erros;
}

// Atualiza automaticamente a previsão de combinações e validação na interface
function atualizarPrevisaoCombinacoes() {
    const formulado = document.getElementById('formulado').value.trim();
    const selectedInputs = Array.from(document.querySelectorAll('#materiasPrimasTable input[type="checkbox"]:checked'));

    // Elementos para exibição
    const previsaoContainer = document.getElementById('combinacoesPrevisao');
    const erroContainer = document.getElementById('erroContainer');

    // Reseta mensagens
    previsaoContainer.textContent = "";
    erroContainer.textContent = "";

    if (!formulado || !/^\d{2}-\d{2}-\d{2}$/.test(formulado)) {
        previsaoContainer.textContent = "Informe o formulado no formato XX-XX-XX.";
        return;
    }

    if (selectedInputs.length === 0) {
        previsaoContainer.textContent = "Selecione pelo menos uma matéria-prima.";
        return;
    }

    const materiasPrimasSelecionadas = selectedInputs.map(input => ({
        name: input.dataset.name,
        nutrients: JSON.parse(input.dataset.nutrients)
    }));

    // Valida as matérias-primas selecionadas
    const erros = validarMateriasPrimas(formulado, materiasPrimasSelecionadas);
    if (erros.length > 0) {
        erroContainer.innerHTML = erros.map(erro => `<p class="error-message">${erro}</p>`).join('');
        return;
    }

    // Calcula a previsão de combinações
    const step = 10; // Step fixo (pode ser dinâmico, se necessário)
    //const totalCombinacoes = preverTotalCombinacoes_old(formulado, materiasPrimasSelecionadas, step);
    const totalCombinacoes = preverTotalCombinacoes(formulado, materiasPrimasSelecionadas, step);
    console.log("Total estimado de combinações possíveis:", totalCombinacoes.toLocaleString());

    // Atualiza o conteúdo da previsão
    previsaoContainer.textContent = `Total estimado de combinações possíveis: ${totalCombinacoes.toLocaleString()}`;
}


function exibirResultados(data) {
    console.log("Sucesso API..")
    loadCalculate(false);
    const container = document.getElementById('resultsContainer');
    container.innerHTML = ''; // Limpa resultados anteriores

    if (data.error) {
        container.innerHTML = `<p class="error-message">${data.error}</p>`;
        return;
    }

    const {
        tempo_processamento,
        formulado_exigido,
        descartados,
        formulados_incompativeis,
        enchimentos_incompativeis,
        limite_enchimentos,
        total_combinacoes,
        aceitos
    } = data.results;

    // Criando o cabeçalho do resultado
    const header = document.createElement('div');
    header.className = 'results-header';
    header.innerHTML = `
        <h3>Formulado: ${formulado_exigido}</h3>
        <p><strong>Limite de enchimento:</strong> ${limite_enchimentos} kg</p>
        <p><strong>Tempo necessário:</strong> ${tempo_processamento}</p>
        <p><strong>Total de combinações:</strong> ${total_combinacoes}</p>
        <p><strong>Descartados:</strong> ${descartados}</p>
        <p><strong>Formulados Incompatíveis:</strong> ${formulados_incompativeis}</p>
        <p><strong>Enchimentos Incompatíveis:</strong> ${enchimentos_incompativeis}</p>
        <p><strong>Aceitos:</strong> ${aceitos.length}</p>
    `;
    container.appendChild(header);

    if (!data.results || data.results.aceitos.length === 0) {
        const sem_resultados = document.createElement('div');
        sem_resultados.innerHTML = '<p class="no-results">Nenhuma combinação foi encontrada.</p>';
        container.appendChild(sem_resultados);
        return;
    }


    // Criando cards para cada combinação aceita
    aceitos.forEach((comb, index) => {
        const card = document.createElement('div');
        card.className = 'result-card';

        // Título do card
        const title = document.createElement('h3');
        title.innerHTML = `Opção ${index + 1}`;
        card.appendChild(title);

        // Criando lista de materiais usados na combinação
        const materialsList = document.createElement('ul');
        comb.materiais.forEach(mat => {
            if (mat.isNutrient !== false) {
                const item = document.createElement('li');
                item.innerHTML = `<strong>${mat.name}</strong>: ${mat.kg} kg ${formatarNutrientes(mat.nutrients, mat.kg)}`;
                materialsList.appendChild(item);
            } else {
                const item = document.createElement('li');
                item.innerHTML = `<strong>${mat.name}</strong>: ${mat.kg} kg ${formatarNutrientes(mat.nutrients, mat.kg)}`;
                item.className = 'li-enchimento'
                materialsList.appendChild(item);
            }
        });


        // Exibir insumos
        const insumos = document.createElement('p');
        insumos.innerHTML = `<strong>Insumos:</strong> ${comb.total_insumos.toFixed(2)} kg`;

        // Exibir Enchimentos
        const enchimentos = document.createElement('p');
        enchimentos.innerHTML = `<strong>Enchimentos:</strong> ${comb.filler.toFixed(2)} kg`;

        // Exibir compatibilidade
        const compatibility = document.createElement('p');
        let legend = ''
        if (comb.compatibility) {
            legend = "✅ Sim"
        } else if (comb.limited) {
            legend = "⚠️ Possui limitação"
        } else {
            legend = "❌ Incompátivel"
        }
        compatibility.innerHTML = `<strong>Compatibilidade:</strong> ${legend}`;

        // Exibir mensagem de validação
        const message = document.createElement('p');
        message.className = 'validation-message';
        message.textContent = comb.message;

        card.appendChild(materialsList);
        card.appendChild(insumos);
        card.appendChild(enchimentos);
        card.appendChild(compatibility);
        card.appendChild(message);

        container.appendChild(card);
    });
}

// Formatar exibição de nutrientes
function formatarNutrientes_old(nutrients, kg) {
    return Object.entries(nutrients)
        .map(([key, value]) => `${key}: ${value.toFixed(2)} kg`)
        .join(', ');
}

// Função para formatar a exibição dos nutrientes, calculando a quantidade disponibilizada
function formatarNutrientes(nutrients, kg) {
    if (nutrients.length > 0) {
        return nutrients.map(nutrient => {
            // Converte o percent para número (caso venha como string)
            const percent = parseFloat(nutrient.percent);
            // Calcula a quantidade de nutriente: kg * (percent / 100)
            const quantidade = kg * (percent / 100);
            // Retorna a string formatada com duas casas decimais
            return `<br>${nutrient.name}: ${quantidade.toFixed(2)} kg`;
        }).join(', ');
    } else {
        return `(material inerte)`;
    }
}

function loadCalculate(option) {

    // Option: booleano

    // Option == true -> desativa button calcular Fórmula id=buttonCalculate e escreve: "Calculando.."
    // Option == true -> card id=cardResults é limpado e escondido

    // Option == false -> ativa button calcular Fórmula id=buttonCalculate e escreve: "Calcular Fórmula"
    // Option == true -> card id=cardResults é apresendado

    // Se possível adicionar efeito css leve

    const btnCalculate = document.getElementById("buttonCalculate");
    const cardResults = document.getElementById("cardResults");
    const resultsContainer = document.getElementById("resultsContainer");

  // Configura transição suave se ainda não tiver
  if (!cardResults.style.transition) {
    cardResults.style.transition = "opacity 0.5s ease";
  }

  if (option) {
    // Desativa o botão e muda o texto
    btnCalculate.disabled = true;
    btnCalculate.textContent = "Calculando..";

    // Limpa o card e esconde com efeito fade-out
    resultsContainer.innerHTML = "";
    cardResults.style.opacity = 0;
  } else {
    // Ativa o botão e reseta o texto
    btnCalculate.disabled = false;
    btnCalculate.textContent = "Calcular Fórmula";

    // Exibe o card com efeito fade-in
    cardResults.style.opacity = 1;
  }
}




