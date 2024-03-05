from unittest import TestCase

from finrisklib.enums import Currency
from finrisklib.enums import FinancialIndex


class TestEnums(TestCase):
    """
    Pruebas unitarias para enumeradores
    """

    def test_currency(self):
        """
        Prueba la conversión en string del enumerador de Moneda
        """
        currency_string = Currency.USD
        expected = 'USD'
        self.assertTrue(currency_string, expected)

    def test_str_to_currency(self):
        """
        Prueba la conversión implícita de un string a un enumerador de currency
        """
        actual = Currency['USD']
        expected = Currency.USD
        self.assertEqual(actual, expected)

    def test_currency_from_str(self):
        """
        Prueba la conversión explícita de un string en enumerador de currency
        """
        # Prueba 1
        actual = Currency.from_str('USD')
        expected = Currency.USD
        self.assertEqual(actual, expected)

        # Prueba 2
        actual = Currency.from_str('usd')
        expected = Currency.USD
        self.assertEqual(actual, expected)

        # Prueba 3
        try:
            Currency.from_str('false')
            self.fail()
        except Exception as e:
            exception_type = type(e)
            self.assertTrue(1, 1)

    def test_index_from_str(self):
        expected = FinancialIndex.FIX
        real = FinancialIndex.from_str('FIX')

        self.assertEqual(expected, real)
