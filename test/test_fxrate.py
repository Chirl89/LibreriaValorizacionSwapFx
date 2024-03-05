from unittest import TestCase
from finrisklib.market.fxrate import FxPair
from finrisklib.enums import Currency


class TestFxRateData(TestCase):

    def test_eq_rate(self):
        usd_1 = FxPair.generate('USDCLP')
        usd_2 = FxPair(primary_currency=Currency.USD, secondary_currency=Currency.CLP, discount_days=1)

        cop_1 = FxPair.generate(('USDCOP'))

        self.assertEqual(usd_1, usd_2)
        self.assertNotEqual(usd_1, cop_1)

    def test_str_fx(self):
        usd_1 = FxPair.generate('USDCLP')

        expected = "USD-CLP"
        real = str(usd_1)
        self.assertEqual(real, expected)

        usd_1 = FxPair.generate('usdclp')

        expected = "USD-CLP"
        real = str(usd_1)
        self.assertEqual(real, expected)
