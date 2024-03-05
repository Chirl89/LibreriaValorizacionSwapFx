from unittest import TestCase

from finrisklib.market.fxrate import *
from finrisklib.data.filereader import XlsReader
from finrisklib.data.dbreader import DBReader
from finrisklib.market.index import *
from finrisklib.enums import Source
from datetime import date


class TestDataSet(TestCase):

    def test_get_fx_rate(self):
        market_date = date(year=2022, month=5, day=25)
        curve_file = 'testdata/datasetreader_test_curve_data.xlsx'
        fx_file = 'testdata/datasetreader_test_fxrate_data.xlsx'
        index_file = 'testdata/filereader_test_index_data.xlsx'

        dataset = XlsReader.read_dataset_data(process_date=market_date, curve_file=curve_file, fx_file=fx_file,
                                              index_file=index_file)

        # Prueba 1: USDCLP

        fx_pair = FxPair.generate('USDCLP')
        real = dataset.get_fx_rate(fx_pair=fx_pair)
        expected = 835.785730902442

        self.assertAlmostEqual(real, expected, 5)

        # Prueba 2: CLFCLP

        fx_pair = FxPair.generate('CLFCLP')
        real = dataset.get_fx_rate(fx_pair=fx_pair)
        expected = 32591.72

        self.assertAlmostEqual(real, expected, 5)

        # Prueba 3: EURUSD

        fx_pair = FxPair.generate('EURUSD')
        real = dataset.get_fx_rate(fx_pair=fx_pair)
        expected = 1.06531529996011

        self.assertAlmostEqual(real, expected, 5)

        # Prueba 4: USDEUR

        fx_pair = FxPair(Currency.USD, Currency.EUR)
        real = dataset.get_fx_rate(fx_pair=fx_pair)
        expected = 1 / 1.06531529996011

        self.assertAlmostEqual(real, expected, 5)

    def test_get_fx_discounted(self):

        fx_pair = FxPair.generate('USDCLP')

        reader = DBReader()

        # Prueba 1

        market_date = date(year=2023, month=5, day=2)
        dataset = reader.get_dataset(process_date=market_date, source=Source.SANDBOX)

        expected = 810.214429908013
        real = dataset.get_fx_rate(fx_pair=fx_pair)

        self.assertAlmostEqual(expected, real, 5)

        # Prueba 2

        market_date = date(year=2023, month=4, day=21)
        dataset = reader.get_dataset(process_date=market_date, source=Source.SANDBOX)

        expected = 796.080004664212
        real = dataset.get_fx_rate(fx_pair=fx_pair)

        self.assertAlmostEqual(expected, real, 5)

        # Prueba 3

        market_date = date(year=2023, month=4, day=28)
        dataset = reader.get_dataset(process_date=market_date, source=Source.SANDBOX)

        expected = 806.208959643895
        real = dataset.get_fx_rate(fx_pair=fx_pair)

        self.assertAlmostEqual(expected, real, 5)

    def test_get_fx_forward_rate(self):
        market_date = date(year=2022, month=5, day=25)
        curve_file = 'testdata/datasetreader_test_curve_data.xlsx'
        fx_file = 'testdata/datasetreader_test_fxrate_data.xlsx'
        index_file = 'testdata/filereader_test_index_data.xlsx'

        dataset = XlsReader.read_dataset_data(process_date=market_date, curve_file=curve_file,
                                              fx_file=fx_file, index_file=index_file)

        fx_pair = FxPair.generate('USDCLP')

        # Prueba 1: USDCLP 1 dia

        forward_date = date(year=2022, month=5, day=26)
        real = dataset.get_fx_forward_rate(fx_pair=fx_pair, forward_date=forward_date)
        expected = 835.95

        self.assertAlmostEqual(real, expected, 10)

        # Prueba 1: USDCLP 125 días

        forward_date = date(year=2022, month=9, day=27)
        real = dataset.get_fx_forward_rate(fx_pair=fx_pair, forward_date=forward_date)
        expected = 855.2000043835

        self.assertAlmostEqual(real, expected, 5)

    def test_get_index_data(self):
        market_date = date(year=2022, month=7, day=28)

        reader = DBReader()

        dataset = reader.get_dataset(process_date=market_date, source=Source.SANDBOX)

        # Prueba 1: Obtención de Libor
        libor3m = FinancialIndex.LIBOR3M
        index_date = date(year=2021, month=7, day=28)

        libor_rate = dataset.get_index_data(index=libor3m, idx_date=index_date)

        self.assertAlmostEqual(0.001285, libor_rate, 3)

    def test_get_index_data_between(self):

        market_date = date(year=2022, month=7, day=29)

        reader = DBReader()

        dataset = reader.get_dataset(process_date=market_date, source=Source.SANDBOX)

        # Prueba: Obtención de SOFR
        idx = FinancialIndex.SOFR

        start_date = date(year=2022, month=1, day=1)
        end_date = date(year=2022, month=7, day=1)

        data = dataset.get_index_data_between(index=idx, start_date=start_date, end_date=end_date)

        n = len(data)
        self.assertTrue(n > 1)
