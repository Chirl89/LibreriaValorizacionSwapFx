from unittest import TestCase

from finrisklib.data.dbreader import DBReader
from datetime import date
from finrisklib.enums import Source
from finrisklib.enums import Currency
from finrisklib.market.fxrate import FxPair
from finrisklib.instruments.flow import Cash
from finrisklib.market.index import *


class TestDBReader(TestCase):

    # region Pruebas obtención de curvas

    def test_get_curve_names(self):
        """
        Prueba la obtención de nombres de todas las curvas desde fuente murex y fuente oficial
        """

        reader = DBReader()
        curve_date = date(year=2022, month=5, day=16)
        curve_murex = reader.get_curve_names(process_date=curve_date, source=Source.SANDBOX)

        n_curves = len(curve_murex)

        self.assertTrue(n_curves > 0)

    def test_get_single_curve_data(self):
        """
        Prueba la obtención de datos de una curva
        """

        reader = DBReader()

        curve_date = date(year=2022, month=5, day=16)
        mx_clp = reader.get_single_curve_data(curve_name='CLP FX', process_date=curve_date, source=Source.SANDBOX)

        official_clp = reader.get_single_curve_data(curve_name='CURVA_CLP_CL', process_date=curve_date,
                                                    source=Source.OFFICIAL)

        self.assertEqual(1, 1)

    def test_get_curve_data(self):
        """
        Prueba la obtención de datos de todas las curvas desde las distintas fuentes
        """
        reader = DBReader()
        curve_date = date(year=2022, month=5, day=16)

        curve_murex = reader.get_curve_dataset(process_date=curve_date, source=Source.SANDBOX)
        curve_data = reader.get_curve_dataset(process_date=curve_date, source=Source.OFFICIAL)

        self.assertEqual(1, 1)

    # endregion

    # region pruebas de obtención de tipos de cambio

    def test_get_fx_dataset(self):
        """
        Prueba la obtención de todos los tipos de cambio
        """

        reader = DBReader()

        fx_date = date(year=2022, month=5, day=16)
        fx_dataset = reader.get_fx_dataset(process_date=fx_date, source=Source.SANDBOX)
        usd_clp = FxPair.generate('USDCLP')

        real = fx_dataset.get_fx_rate(usd_clp)

        expected = 860.185000000000

        self.assertEqual(real, expected)

    def test_get_fx_rate(self):
        # Prueba 1

        reader = DBReader()

        fx_date = date(year=2022, month=5, day=16)
        real = reader.get_fx_rate(primary_currency='USD', secondary_currency='CLP', process_date=fx_date,
                                  source=Source.SANDBOX)

        expected = 860.185000000000

        self.assertEqual(real, expected)

        real = reader.get_fx_rate(primary_currency='CLP', secondary_currency='USD', process_date=fx_date,
                                  source=Source.OFFICIAL)

        self.assertEqual(real, expected)

    # endregion

    # region Pruebas de obtención de data indices

    def test_get_index_data(self):
        reader = DBReader()

        process_date = date(year=2022, month=7, day=7)

        # test 1

        index_value = reader.get_index_rate(index=FinancialIndex.ICP, process_date=process_date)

        expected = 19859.90000000000

        self.assertEqual(expected, index_value)

    def test_get_single_index_dataset(self):
        reader = DBReader()

        start_date = date(year=2022, month=7, day=1)
        mid_date = date(year=2022, month=7, day=7)
        end_date = date(year=2022, month=7, day=15)

        # test 1
        idx_dataset = reader.get_single_index_dataset(index=FinancialIndex.ICP, start_date=start_date,
                                                      end_date=end_date)

        expected = 19859.90000000000
        idx_value = idx_dataset.get_index_data(index=FinancialIndex.ICP, idx_date=mid_date)

        self.assertEqual(expected, idx_value)

    def test_get_index_dataset(self):
        reader = DBReader()

        start_date = date(year=2022, month=7, day=1)
        mid_date = date(year=2022, month=7, day=7)
        end_date = date(year=2022, month=7, day=15)

        # test 1
        idx_dataset = reader.get_index_dataset(start_date=start_date, end_date=end_date)

        expected = 19859.90000000000
        idx_value = idx_dataset.get_index_data(index=FinancialIndex.ICP, idx_date=mid_date)

        self.assertEqual(expected, idx_value)

    # endregion

    # region Obtención de Dataset

    def test_get_dataset(self):
        reader = DBReader()

        process_date = date(year=2022, month=5, day=16)
        dataset = reader.get_dataset(process_date=process_date, source=Source.SANDBOX)

        self.assertEqual(1, 1)

    # endregion

    # region Pruebas de obtención de data de operaciones

    def test_get_operation_mtm(self):
        reader = DBReader()

        process_date = date(year=2022, month=7, day=28)
        id_number = 1001268
        real = reader.get_official_mtm(id_number=id_number, process_date=process_date)

        expected = Cash(amount=-406751286.000000, currency=Currency.CLP)

        self.assertEqual(real, expected)

    # endregion

