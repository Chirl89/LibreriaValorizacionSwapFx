from unittest import TestCase
from finrisklib.market.index import Index
from finrisklib.enums import FinancialIndex


class TestIndex(TestCase):

    def test_str(self):
        """
        Test de conversión a cadena de texto
        """
        tab1m = Index.generate('TAB1M')
        tab3m = Index.generate(FinancialIndex.TAB3M)

        self.assertEqual('TAB1M', str(tab1m))
        self.assertEqual('TAB3M', str(tab3m))

    def test_to_enum(self):

        expected = FinancialIndex.FIX
        index = Index.generate(expected)
        real = index.to_enum()

        self.assertEqual(expected, real)
