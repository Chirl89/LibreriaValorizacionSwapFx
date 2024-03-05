from unittest import TestCase
from finrisklib.data.filereader import XlsReader
from finrisklib.enums import Currency


class TestCurve(TestCase):

    def test_get_discount_factor(self):
        """
        Prueba de obtención de factor de descuento.
        """

        file_name = 'testdata/curve_test_data.xlsx'

        curve_dataset = XlsReader.read_curve_data(file_name)
        clp_curve = curve_dataset.get_discount_curve(associated_currency=Currency.CLP,
                                                     associated_collateral=Currency.USD)

        # Prueba 1 (Interpolación)

        t = 35
        p_expected = 0.99309569481
        p_real = clp_curve.get_discount_factor(t)
        self.assertAlmostEqual(p_expected, p_real, places=10)

        # Prueba 2 (extrapolación punto menor)

        t = 2
        p_expected = 0.999564928651727
        p_real = clp_curve.get_discount_factor(t)
        self.assertAlmostEqual(p_expected, p_real, places=10)

        # Prueba 3 (extrapolación punto mayor)

        t = 15000
        p_expected = 0.183846447315592
        p_real = clp_curve.get_discount_factor(t)
        self.assertAlmostEqual(p_expected, p_real, places=10)

    def test_curve_div(self):
        """
        Prueba de división de curvas
        """

        file_name = 'testdata/filereader_test_curve_data.xlsx'

        curve_data = XlsReader.read_curve_data(file_name)
        clp_curve = curve_data.get_discount_curve(associated_currency=Currency.CLP,
                                                  associated_collateral=Currency.USD)
        cam_curve = curve_data.get_discount_curve(associated_currency=Currency.CLP,
                                                  associated_collateral=Currency.CLP)

        div_curve = clp_curve/cam_curve

        self.assertEqual(27, len(div_curve.tenors))
        self.assertAlmostEqual(1.00430530569116, div_curve.get_discount_factor(186), 10)

    def test_mul_div(self):
        """
        Prueba de multiplicación de curvas
        """

        file_name = 'testdata/filereader_test_curve_data.xlsx'

        curve_data = XlsReader.read_curve_data(file_name)
        clp_curve = curve_data.get_discount_curve(associated_currency=Currency.CLP,
                                                  associated_collateral=Currency.USD)
        cam_curve = curve_data.get_discount_curve(associated_currency=Currency.CLP,
                                                  associated_collateral=Currency.CLP)

        div_curve = clp_curve*cam_curve

        self.assertEqual(27, len(div_curve.tenors))
        self.assertAlmostEqual(0.91358857464463, div_curve.get_discount_factor(186), 10)
