import unittest
from datetime import datetime
from calculo import CalculadoraTrabalhista


class TestCalculadoraTrabalhista(unittest.TestCase):

    def test_salario_e_rescisao_basica(self):
        dados = {
            'salario': 3000,
            'data_admissao': '2023-01-15',
            'data_demissao': '2023-10-10',
            'motivo': 'pedido'
        }
        res = CalculadoraTrabalhista.calcular_rescisao_completa(dados)
        self.assertTrue(res['sucesso'])
        self.assertIn('verbas', res)
        v = res['verbas']
        # Checa algumas expectativas básicas
        self.assertAlmostEqual(v['saldo_salario'], 1000.00)
        self.assertGreater(v['total_geral'], 0)

    def test_admissao_no_mes_demissao(self):
        # Admissão e demissão no mesmo mês: dias trabalhados devem considerar admissão
        data_admissao = datetime(2023, 10, 5)
        data_demissao = datetime(2023, 10, 20)
        dias = CalculadoraTrabalhista.calcular_dias_trabalhados(
            data_admissao, data_demissao)
        self.assertEqual(dias, 16)  # 20 - 5 + 1

    def test_decimo_terceiro_limites(self):
        # Se admissão em janeiro e demissão em dezembro => 12 meses
        salario = 2400
        d_adm = datetime(2023, 1, 1)
        d_dem = datetime(2023, 12, 31)
        dec = CalculadoraTrabalhista.calcular_decimo_terceiro(
            salario, d_adm, d_dem)
        self.assertAlmostEqual(dec, salario)  # 12/12 * salario

        # Admissão depois da demissão (inválido) => meses sanear para 0
        d_adm2 = datetime(2024, 1, 1)
        d_dem2 = datetime(2023, 12, 31)
        dec2 = CalculadoraTrabalhista.calcular_decimo_terceiro(
            salario, d_adm2, d_dem2)
        self.assertAlmostEqual(dec2, 0)

    def test_fgts_calculation(self):
        salario = 3000
        meses = 6
        # Teste para dispensa sem justa causa (40%)
        multa = CalculadoraTrabalhista.calcular_fgts(
            salario, meses, "demissao-sem-justa-causa")
        self.assertAlmostEqual(multa, 576)  # 3000 * 0.08 * 6 * 0.4

        # Teste para pedido de demissão (0%)
        multa_pedido = CalculadoraTrabalhista.calcular_fgts(
            salario, meses, "pedido-demissao")
        self.assertAlmostEqual(multa_pedido, 0)

        # Teste para culpa recíproca (20%)
        multa_reciproca = CalculadoraTrabalhista.calcular_fgts(
            salario, meses, "culpa-reciproca")
        self.assertAlmostEqual(multa_reciproca, 288)  # 3000 * 0.08 * 6 * 0.2

        # Teste para término de contrato (40%)
        multa_termino = CalculadoraTrabalhista.calcular_fgts(
            salario, meses, "termino-contrato")
        self.assertAlmostEqual(multa_termino, 576)  # 3000 * 0.08 * 6 * 0.4

        # Teste para motivo não listado (0%)
        multa_outro = CalculadoraTrabalhista.calcular_fgts(
            salario, meses, "outro-motivo")
        self.assertAlmostEqual(multa_outro, 0)

    def test_saldo_salario_mes_parcial(self):
        salario = 3000
        data_admissao = datetime(2023, 10, 15)  # Admitido dia 15
        data_demissao = datetime(2023, 10, 25)  # Demitido dia 25
        saldo = CalculadoraTrabalhista.calcular_saldo_salario(
            salario, data_admissao, data_demissao)
        # 11 dias trabalhados (25 - 15 + 1)
        self.assertAlmostEqual(saldo, 1100.0)  # (3000/30) * 11

    def test_ferias_proporcionais_precisao(self):
        salario = 3000
        # Teste período incompleto com mais de 14 dias
        d_adm = datetime(2023, 1, 1)
        d_dem = datetime(2023, 3, 16)  # 2 meses + 16 dias
        ferias = CalculadoraTrabalhista.calcular_ferias_proporcionais(
            salario, d_adm, d_dem)
        # 3 meses (2 completos + 1 por ter mais de 14 dias)
        valor_esperado = (salario / 12 * 3) * 1.3333333
        self.assertAlmostEqual(ferias, valor_esperado, places=2)

        # Teste período incompleto com menos de 14 dias
        d_dem2 = datetime(2023, 3, 13)  # 2 meses + 13 dias
        ferias2 = CalculadoraTrabalhista.calcular_ferias_proporcionais(
            salario, d_adm, d_dem2)
        # 2 meses apenas (13 dias não conta novo mês)
        valor_esperado2 = (salario / 12 * 2) * 1.3333333
        self.assertAlmostEqual(ferias2, valor_esperado2, places=2)

    def test_horas_extras(self):
        # Teste cálculo de média de horas extras
        horas_extras = [
            {'mes': 1, 'quantidade': 10, 'valor': 500},
            {'mes': 2, 'quantidade': 15, 'valor': 750},
            {'mes': 3, 'quantidade': 5, 'valor': 250}
        ]
        media = CalculadoraTrabalhista.calcular_media_horas_extras(
            horas_extras)
        self.assertAlmostEqual(media, 500)  # (500 + 750 + 250) / 3

        # Teste reflexos em férias e 13º
        reflexos = CalculadoraTrabalhista.calcular_verbas_variaveis(500, 6)
        # Verifica se o retorno é um dicionário com as chaves corretas
        self.assertIsInstance(reflexos, dict)
        self.assertIn('ferias', reflexos)
        self.assertIn('decimo_terceiro', reflexos)

        # Verifica os valores calculados
        # Férias: (500 * 6/12) + (500 * 6/12 / 3)
        self.assertAlmostEqual(reflexos['ferias'], (500/2) + (500/2/3))
        # 13º: (500 * 6/12)
        self.assertAlmostEqual(reflexos['decimo_terceiro'], 500/2)

    def test_rescisao_pcd(self):
        # Teste indenização PCD em caso de dispensa sem justa causa
        salario = 3000
        data_admissao = datetime(2020, 1, 1)
        data_demissao = datetime(2023, 7, 1)
        motivo = "demissao-sem-justa-causa"

        indenizacao = CalculadoraTrabalhista.calcular_verbas_pcd(
            salario, data_admissao, data_demissao, motivo)
        # 3 anos trabalhados * salário
        self.assertEqual(indenizacao, 9000)

        # Teste PCD com pedido de demissão (não tem direito)
        indenizacao_pedido = CalculadoraTrabalhista.calcular_verbas_pcd(
            salario, data_admissao, data_demissao, "pedido-demissao")
        self.assertEqual(indenizacao_pedido, 0)

    def test_rescisao_completa_com_extras_e_pcd(self):
        dados = {
            'salario': 3000,
            'data_admissao': '2020-01-01',
            'data_demissao': '2023-07-01',
            'motivo': 'demissao-sem-justa-causa',
            'is_pcd': True,
            'horas_extras': [
                {'mes': 1, 'quantidade': 10, 'valor': 500},
                {'mes': 2, 'quantidade': 15, 'valor': 750},
                {'mes': 3, 'quantidade': 5, 'valor': 250}
            ]
        }
        res = CalculadoraTrabalhista.calcular_rescisao_completa(dados)
        self.assertTrue(res['sucesso'])
        self.assertIn('indenizacao_pcd', res['verbas'])
        self.assertIn('media_horas_extras', res['verbas'])
        self.assertGreater(res['verbas']['media_horas_extras'], 0)


if __name__ == '__main__':
    unittest.main()
