from datetime import datetime
from dateutil.relativedelta import relativedelta


class CalculadoraTrabalhista:

    @staticmethod
    def calcular_dias_trabalhados(data_admissao, data_demissao):
        """Calcula dias trabalhados no mês da demissão"""
        dias_no_mes = 30  # Padrão trabalhista
        # Se admissão no mesmo mês da demissão, dias trabalhados começam na data de admissão
        if data_admissao.year == data_demissao.year and data_admissao.month == data_demissao.month:
            dias_trabalhados = max(
                0, min(data_demissao.day - data_admissao.day + 1, dias_no_mes))
        else:
            dias_trabalhados = min(data_demissao.day, dias_no_mes)
        return dias_trabalhados

    @staticmethod
    def calcular_saldo_salario(salario, data_admissao, data_demissao):
        """Calcula saldo de salário, considerando admissão no mesmo mês"""
        dias_no_mes = 30  # Padrão trabalhista
        # Se admissão no mesmo mês, considera apenas dias trabalhados
        if data_admissao.year == data_demissao.year and data_admissao.month == data_demissao.month:
            dias_trabalhados = max(
                0, min(data_demissao.day - data_admissao.day + 1, dias_no_mes))
        else:
            dias_trabalhados = min(data_demissao.day, dias_no_mes)
        return (salario / dias_no_mes) * dias_trabalhados

    @staticmethod
    def calcular_ferias_proporcionais(salario, data_admissao, data_demissao):
        """Calcula férias proporcionais + 1/3 constitucional"""
        if data_admissao > data_demissao:
            return 0

        # Encontra início do último período aquisitivo
        anos_completos = relativedelta(data_demissao, data_admissao).years
        inicio_ultimo_periodo = data_admissao
        if anos_completos > 0:
            inicio_ultimo_periodo = data_admissao + \
                relativedelta(years=anos_completos)

        # Calcula meses no período aquisitivo atual
        meses_periodo_atual = relativedelta(
            data_demissao, inicio_ultimo_periodo)
        meses_trabalhados = meses_periodo_atual.months

        # Adiciona mês quando tem mais de 14 dias trabalhados
        if meses_periodo_atual.days > 14:
            meses_trabalhados += 1

        # Calcula valor proporcional + 1/3
        valor_ferias = (salario / 12) * meses_trabalhados
        um_terco = valor_ferias / 3

        return valor_ferias + um_terco

    @staticmethod
    def calcular_decimo_terceiro(salario, data_admissao, data_demissao):
        """Calcula 13º salário proporcional"""
        # Data inválida: admissão após demissão => proporcional 0
        if data_admissao > data_demissao:
            meses_trabalhados = 0
        # Calcula meses trabalhados no ano da demissão
        elif data_admissao.year == data_demissao.year:
            meses_trabalhados = data_demissao.month - data_admissao.month + 1
        else:
            meses_trabalhados = data_demissao.month

        # Saneamento: garantir 0..12
        meses_trabalhados = max(0, min(meses_trabalhados, 12))

        return (salario / 12) * meses_trabalhados

    @staticmethod
    def calcular_fgts(salario, meses_trabalhados, motivo):
        """Calcula multa do FGTS conforme motivo padronizado"""
        total_fgts = salario * 0.08 * meses_trabalhados

        # Padronizar com os valores que virão do frontend
        motivos_com_multa = {
            'demissao-sem-justa-causa': 0.40,
            'rescisao-indireta': 0.40,
            'culpa-reciproca': 0.20,
            'pedido-demissao': 0.0,
            'demissao-com-justa-causa': 0.0,
            'termino-contrato': 0.40
        }

        # Usar get() com fallback para caso de motivos diferentes
        percentual_multa = motivos_com_multa.get(motivo, 0.0)
        return total_fgts * percentual_multa

    @staticmethod
    def calcular_media_horas_extras(horas_extras_12_meses):
        """Calcula média de horas extras dos últimos 12 meses"""
        if not horas_extras_12_meses:
            return 0

        total_horas = sum(he['quantidade'] for he in horas_extras_12_meses)
        total_valor = sum(he['valor'] for he in horas_extras_12_meses)
        return total_valor / len(horas_extras_12_meses) if horas_extras_12_meses else 0

    @staticmethod
    def calcular_verbas_variaveis(media_horas_extras, meses_trabalhados):
        """Calcula reflexo das horas extras em 13º e férias"""
        if media_horas_extras <= 0:
            return {'decimo_terceiro': 0, 'ferias': 0}

        # 13º proporcional
        valor_13 = (media_horas_extras / 12) * meses_trabalhados

        # Férias proporcionais + 1/3
        valor_ferias_base = (media_horas_extras / 12) * meses_trabalhados
        valor_ferias_terco = valor_ferias_base / 3
        valor_ferias_total = valor_ferias_base + valor_ferias_terco

        return {
            'decimo_terceiro': valor_13,
            'ferias': valor_ferias_total
        }

    @staticmethod
    def calcular_verbas_pcd(salario, data_admissao, data_demissao, motivo):
        """Calcula verbas específicas para PCD (Pessoa com Deficiência)"""
        # PCD tem direito a indenização se demitido sem justa causa
        if motivo in ['demissao-sem-justa-causa', 'rescisao-indireta']:
            # Calcula tempo total em anos
            anos_trabalhados = relativedelta(
                data_demissao, data_admissao).years
            # Indenização = salário * anos trabalhados (mínimo 1 ano)
            return salario * max(1, anos_trabalhados)
        return 0

    @staticmethod
    def calcular_aviso_previo(salario, tipo_aviso, anos_trabalhados=0):
        """Calcula aviso prévio considerando tempo de serviço"""
        # Base: 30 dias + 3 dias por ano trabalhado (até máximo de 90 dias)
        # Limite de 60 dias adicionais
        dias_adicionais = min(60, anos_trabalhados * 3)

        if tipo_aviso == "indenizado":
            return salario * ((30 + dias_adicionais) / 30)
        elif tipo_aviso == "trabalhado":
            return 0
        else:
            # Reduzido pela metade
            return (salario * ((30 + dias_adicionais) / 30)) / 2

    @staticmethod
    def calcular_rescisao_completa(dados):
        """Calcula todas as verbas rescisórias"""
        try:
            salario = float(dados['salario'])
            data_admissao = datetime.strptime(
                dados['data_admissao'], '%Y-%m-%d')
            data_demissao = datetime.strptime(
                dados['data_demissao'], '%Y-%m-%d')
            motivo = dados['motivo']
            aviso_previo = dados.get('aviso_previo', 'indenizado')
            is_pcd = dados.get('is_pcd', False)
            horas_extras = dados.get('horas_extras', [])

            # Cálculos individuais
            saldo_salario = CalculadoraTrabalhista.calcular_saldo_salario(
                salario, data_admissao, data_demissao)

            # Calcula média de horas extras
            media_he = CalculadoraTrabalhista.calcular_media_horas_extras(
                horas_extras)

            # Férias e 13º considerando horas extras
            ferias_proporcionais = CalculadoraTrabalhista.calcular_ferias_proporcionais(
                salario, data_admissao, data_demissao
            )
            decimo_terceiro = CalculadoraTrabalhista.calcular_decimo_terceiro(
                salario, data_admissao, data_demissao
            )

            # Reflexos de horas extras em férias e 13º
            diferenca = relativedelta(data_demissao, data_admissao)
            meses_trabalhados = diferenca.years * 12 + diferenca.months
            verbas_variaveis = CalculadoraTrabalhista.calcular_verbas_variaveis(
                media_he, meses_trabalhados
            )

            # Calcula verbas específicas para PCD
            verbas_pcd = 0
            if is_pcd:
                verbas_pcd = CalculadoraTrabalhista.calcular_verbas_pcd(
                    salario, data_admissao, data_demissao, motivo
                )

            # Aviso prévio considerando tempo de serviço
            anos_trabalhados = diferenca.years
            aviso_previo_valor = CalculadoraTrabalhista.calcular_aviso_previo(
                salario, aviso_previo, anos_trabalhados)

            # FGTS
            multa_fgts = CalculadoraTrabalhista.calcular_fgts(
                # FGTS inclui média de horas extras
                salario + media_he, meses_trabalhados, motivo)

            # Total
            totais = {
                'saldo_salario': round(saldo_salario, 2),
                'ferias_proporcionais': round(ferias_proporcionais + verbas_variaveis['ferias'], 2),
                'decimo_terceiro': round(decimo_terceiro + verbas_variaveis['decimo_terceiro'], 2),
                'aviso_previo': round(aviso_previo_valor, 2),
                'multa_fgts': round(multa_fgts, 2),
                'media_horas_extras': round(media_he, 2)
            }

            if verbas_pcd > 0:
                totais['indenizacao_pcd'] = round(verbas_pcd, 2)

            totais['total_geral'] = round(sum(totais.values()), 2)

            return {
                'sucesso': True,
                'verbas': totais,
                'detalhes': {
                    'meses_trabalhados': meses_trabalhados,
                    'dias_trabalhados_mes': data_demissao.day
                }
            }

        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }
