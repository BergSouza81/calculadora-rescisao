document.addEventListener('DOMContentLoaded', () => {
    const calculadoraForm = document.getElementById('calculadoraForm');
    const resultsSection = document.getElementById('resultsSection');
    const resultadosContainer = document.getElementById('resultados');
    const formSection = document.getElementById('formSection');
    const voltarFormBtn = document.getElementById('voltarForm');
    const addHoraExtraBtn = document.getElementById('addHoraExtra');
    const horasExtrasContainer = document.getElementById('horasExtrasContainer');

    // --- 1. Controle de Visibilidade ---
    const mostrarResultados = () => {
        formSection.style.display = 'none';
        resultsSection.style.display = 'block';
    };

    const mostrarFormulario = () => {
        formSection.style.display = 'block';
        resultsSection.style.display = 'none';
        resultadosContainer.innerHTML = ''; // Limpa resultados anteriores
    };

    voltarFormBtn.addEventListener('click', mostrarFormulario);
    
    // Inicia a aplicação mostrando o formulário
    mostrarFormulario(); 

    // --- 2. Funcionalidade de Horas Extras/Variáveis Dinâmicas ---
    let itemCounter = 3; // Começa após os meses 1 e 2 iniciais

    addHoraExtraBtn.addEventListener('click', () => {
        const novoItem = document.createElement('div');
        novoItem.classList.add('hora-extra-item');
        novoItem.innerHTML = `
            <div class="form-group">
                <label for="he-mes${itemCounter}">Valor Mês ${itemCounter} (R$)</label>
                <input type="number" id="he-mes${itemCounter}" name="he-mes${itemCounter}" placeholder="0.00" value="0.00" step="0.01" min="0">
            </div>
            <button type="button" class="btn-secondary removeHoraExtra">Remover</button>
        `;
        horasExtrasContainer.appendChild(novoItem);
        itemCounter++;

        // Adiciona evento de remoção
        novoItem.querySelector('.removeHoraExtra').addEventListener('click', () => {
            novoItem.remove();
        });
    });

    // --- 3. Processamento do Formulário e Comunicação com o Backend ---
    calculadoraForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // 1. Coleta dos dados do formulário
        const formData = new FormData(calculadoraForm);
        const data = {};
        
        // Coleta dados principais e converte números/booleanos
        for (const [key, value] of formData.entries()) {
            if (key === 'salario') {
                data[key] = parseFloat(value) || 0;
            } else if (key === 'isPcd' || key === 'feriasVencidas') {
                data[key] = (value === 'on'); 
            } else {
                data[key] = value;
            }
        }
        
        // Coleta de todas as verbas variáveis
        data.verbasVariaveis = [];
        const inputsVariaveis = horasExtrasContainer.querySelectorAll('input[type="number"]');
        inputsVariaveis.forEach(input => {
            if (parseFloat(input.value) > 0) {
                data.verbasVariaveis.push(parseFloat(input.value));
            }
        });

        try {
            const response = await fetch('/api/calcular_rescisao', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });
            
            if (!response.ok) {
                throw new Error(`Erro de rede ou servidor: ${response.statusText}`);
            }

            const resultadoCalculo = await response.json();
            renderizarResultados(resultadoCalculo);
            mostrarResultados();

        } catch (error) {
            console.error('Erro ao calcular rescisão:', error);
            alert(`Ocorreu um erro ao calcular. Por favor, verifique os dados e tente novamente.`);
        }
    });

    // --- 4. Função de Renderização ---
    function renderizarResultados(resultado) {
        resultadosContainer.innerHTML = '';
        
        const verbas = [
            { label: "Saldo de Salário", valor: resultado.saldo_salario, classe: "" },
            { label: "Aviso Prévio", valor: resultado.aviso_previo, classe: "" },
            { label: "Férias Proporcionais + 1/3", valor: resultado.ferias_proporcionais, classe: "" },
            { label: "Férias Vencidas + 1/3", valor: resultado.ferias_vencidas, classe: "" },
            { label: "13º Salário Proporcional", valor: resultado.decimo_terceiro, classe: "" },
            { label: "Multa FGTS", valor: resultado.multa_fgts, classe: "" },
            { label: "Total de Descontos", valor: resultado.total_descontos * -1 || 0, classe: "desconto" },
            { label: "TOTAL LÍQUIDO A RECEBER", valor: resultado.total_liquido, classe: "total" }
        ].filter(item => item.valor !== undefined && item.valor !== null);

        verbas.forEach(verba => {
            const item = document.createElement('div');
            item.classList.add('resultado-item');
            if (verba.classe) {
                item.classList.add(verba.classe);
            }
            
            const valorFormatado = verba.valor.toLocaleString('pt-BR', { 
                style: 'currency', 
                currency: 'BRL' 
            });

            const sinal = verba.classe === 'desconto' ? '(-)' : '';

            item.innerHTML = `
                <span class="resultado-label">${verba.label}</span>
                <span class="resultado-valor">${sinal} ${valorFormatado.replace('-', '')}</span>
            `;
            resultadosContainer.appendChild(item);
        });
    }

    // --- 5. Funcionalidade Imprimir ---
    document.getElementById('imprimirResultado').addEventListener('click', () => {
        window.print();
    });
});