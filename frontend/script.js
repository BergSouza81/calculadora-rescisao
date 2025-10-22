// Configuração da API
const API_URL = 'https://calculadora-rescisao.onrender.com/api/calcular';
const CACHE_KEY = 'calculadora_rescisao_cache';
const CACHE_DURATION = 1000 * 60 * 60; // 1 hora

// Elementos do DOM
const form = document.getElementById('calculadoraForm');
const resultsSection = document.getElementById('resultsSection');
const resultadosDiv = document.getElementById('resultados');
const voltarFormBtn = document.getElementById('voltarForm');
const addHoraExtraBtn = document.getElementById('addHoraExtra');
const horasExtrasContainer = document.getElementById('horasExtrasContainer');

// Criar elemento para mensagens
const messageContainer = document.createElement('div');
messageContainer.id = 'messageContainer';
form.insertBefore(messageContainer, form.firstChild);

// Criar overlay de carregamento
const loadingOverlay = document.createElement('div');
loadingOverlay.className = 'loading-overlay';
loadingOverlay.style.display = 'none';
loadingOverlay.innerHTML = '<div class="loading-spinner"></div>';
document.body.appendChild(loadingOverlay);

// Funções de utilidade
const formatMoney = (value) => {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
};

const showLoading = () => {
    loadingOverlay.style.display = 'flex';
    form.style.opacity = '0.5';
};

const hideLoading = () => {
    loadingOverlay.style.display = 'none';
    form.style.opacity = '1';
};

const showMessage = (text, type = 'error') => {
    messageContainer.innerHTML = `
        <div class="message ${type}">
            ${text}
        </div>
    `;
    messageContainer.scrollIntoView({ behavior: 'smooth' });
    setTimeout(() => {
        messageContainer.innerHTML = '';
    }, 5000);
};

// Funções de cache
const saveToCache = (key, data) => {
    const cacheItem = {
        data,
        timestamp: new Date().getTime()
    };
    localStorage.setItem(key, JSON.stringify(cacheItem));
};

const getFromCache = (key, formData) => {
    const cached = localStorage.getItem(key);
    if (!cached) return null;

    const { data, timestamp } = JSON.parse(cached);
    const age = new Date().getTime() - timestamp;

    if (age > CACHE_DURATION) {
        localStorage.removeItem(key);
        return null;
    }

    // Verificar se os dados do formulário são idênticos
    const cachedStr = JSON.stringify(data.formData);
    const currentStr = JSON.stringify(formData);
    return cachedStr === currentStr ? data.result : null;
};

// Adicionar campo de hora extra
const addHoraExtraField = () => {
    const horaExtraItem = document.createElement('div');
    horaExtraItem.className = 'hora-extra-item';
    
    const mes = new Date().getMonth() + 1;
    
    horaExtraItem.innerHTML = `
        <div class="form-group">
            <label>Mês:</label>
            <input type="number" name="hora_extra_mes" min="1" max="12" value="${mes}" required>
        </div>
        <div class="form-group">
            <label>Quantidade de Horas:</label>
            <input type="number" name="hora_extra_quantidade" min="0" step="1" required>
        </div>
        <div class="form-group">
            <label>Valor Total:</label>
            <input type="number" name="hora_extra_valor" min="0" step="0.01" required>
        </div>
        <button type="button" class="btn-secondary remover-hora-extra" onclick="this.parentElement.remove()">
            Remover
        </button>
    `;
    
    horasExtrasContainer.appendChild(horaExtraItem);
};

// Coletar dados das horas extras
const getHorasExtras = () => {
    const horasExtras = [];
    const items = horasExtrasContainer.getElementsByClassName('hora-extra-item');
    
    for (const item of items) {
        const inputs = item.getElementsByTagName('input');
        horasExtras.push({
            mes: parseInt(inputs[0].value),
            quantidade: parseInt(inputs[1].value),
            valor: parseFloat(inputs[2].value)
        });
    }
    
    return horasExtras;
};

// Exibir resultados
const displayResults = (data) => {
    if (!data.sucesso) {
        alert('Erro ao calcular: ' + data.erro);
        return;
    }

    const verbas = data.verbas;
    const resultadosHTML = `
        <div class="resultado-item">
            <h3>Saldo de Salário</h3>
            <div class="resultado-valor">${formatMoney(verbas.saldo_salario)}</div>
        </div>
        <div class="resultado-item">
            <h3>Férias Proporcionais</h3>
            <div class="resultado-valor">${formatMoney(verbas.ferias_proporcionais)}</div>
        </div>
        <div class="resultado-item">
            <h3>13º Salário</h3>
            <div class="resultado-valor">${formatMoney(verbas.decimo_terceiro)}</div>
        </div>
        <div class="resultado-item">
            <h3>Aviso Prévio</h3>
            <div class="resultado-valor">${formatMoney(verbas.aviso_previo)}</div>
        </div>
        <div class="resultado-item">
            <h3>Multa FGTS</h3>
            <div class="resultado-valor">${formatMoney(verbas.multa_fgts)}</div>
        </div>
        ${verbas.indenizacao_pcd ? `
        <div class="resultado-item">
            <h3>Indenização PCD</h3>
            <div class="resultado-valor">${formatMoney(verbas.indenizacao_pcd)}</div>
        </div>
        ` : ''}
        <div class="resultado-item">
            <h3>Média Horas Extras</h3>
            <div class="resultado-valor">${formatMoney(verbas.media_horas_extras)}</div>
        </div>
        <div class="resultado-item total-geral">
            <h3>Total Geral</h3>
            <div class="resultado-valor">${formatMoney(verbas.total_geral)}</div>
        </div>
    `;

    resultadosDiv.innerHTML = resultadosHTML;
    form.style.display = 'none';
    resultsSection.style.display = 'block';
};

// Event Listeners
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    messageContainer.innerHTML = '';
    
    const formData = {
        salario: parseFloat(document.getElementById('salario').value),
        data_admissao: document.getElementById('dataAdmissao').value,
        data_demissao: document.getElementById('dataDemissao').value,
        motivo: document.getElementById('motivo').value,
        aviso_previo: document.getElementById('avisoPrevio').value,
        is_pcd: document.getElementById('isPcd').checked,
        horas_extras: getHorasExtras()
    };

    // Validar formulário
    const errors = validateForm(formData);
    if (errors.length > 0) {
        errors.forEach(error => showMessage(error, 'error'));
        return;
    }

    // Verificar cache
    const cacheKey = `${CACHE_KEY}_${JSON.stringify(formData)}`;
    const cachedResult = getFromCache(cacheKey, formData);
    if (cachedResult) {
        displayResults(cachedResult);
        showMessage('Dados carregados do cache', 'success');
        return;
    }

    try {
        showLoading();
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.erro || 'Erro ao processar a requisição');
        }

        // Salvar no cache
        saveToCache(cacheKey, {
            formData,
            result: data
        });

        displayResults(data);
        showMessage('Cálculo realizado com sucesso!', 'success');
    } catch (error) {
        console.error('Erro:', error);
        showMessage(error.message || 'Erro ao comunicar com o servidor', 'error');
    } finally {
        hideLoading();
    }
});

voltarFormBtn.addEventListener('click', () => {
    resultsSection.style.display = 'none';
    form.style.display = 'block';
});

addHoraExtraBtn.addEventListener('click', addHoraExtraField);

// Validação das datas
document.getElementById('dataDemissao').addEventListener('change', function() {
    const admissao = new Date(document.getElementById('dataAdmissao').value);
    const demissao = new Date(this.value);
    
    if (admissao > demissao) {
        alert('A data de demissão não pode ser anterior à data de admissão');
        this.value = '';
    }
});