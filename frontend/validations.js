// Validações
const validateForm = (formData) => {
    const errors = [];
    const today = new Date();

    // Validar salário
    if (formData.salario <= 0) {
        errors.push('O salário deve ser maior que zero');
    }

    // Validar datas
    const admissao = new Date(formData.data_admissao);
    const demissao = new Date(formData.data_demissao);

    if (admissao > demissao) {
        errors.push('A data de admissão não pode ser posterior à data de demissão');
    }

    if (demissao > today) {
        errors.push('A data de demissão não pode ser futura');
    }

    // Validar horas extras
    if (formData.horas_extras.length > 0) {
        const mesesUnicos = new Set();
        for (const he of formData.horas_extras) {
            if (he.valor <= 0) {
                errors.push('O valor das horas extras deve ser maior que zero');
            }
            if (he.quantidade <= 0) {
                errors.push('A quantidade de horas extras deve ser maior que zero');
            }
            mesesUnicos.add(he.mes);
        }
        if (mesesUnicos.size !== formData.horas_extras.length) {
            errors.push('Não pode haver horas extras duplicadas para o mesmo mês');
        }
    }

    return errors;
};