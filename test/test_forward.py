from unittest import TestCase

from finrisklib.instruments.flow import Cash
from finrisklib.instruments.forward import Forward
from finrisklib.enums import Currency
from finrisklib.data.filereader import XlsReader
from datetime import date


class TestForward(TestCase):

    def test_valuate(self):

        market_date = date(year=2022, month=5, day=25)
        curve_file = 'testdata/datasetreader_test_curve_data.xlsx'
        fx_file = 'testdata/datasetreader_test_fxrate_data.xlsx'
        index_file = 'testdata/filereader_test_index_data.xlsx'

        dataset = XlsReader.read_dataset_data(process_date=market_date, curve_file=curve_file, fx_file=fx_file,
                                              index_file=index_file)

        # Prueba 1: operación 6699677

        start_date = date(year=2022, month=5, day=5)
        end_date = date(year=2022, month=6, day=6)
        fixing_date = end_date
        pay_date = end_date
        active_notional = Cash(150000, Currency.EUR)
        passive_notional = Cash(157769.7225, Currency.USD)

        associated_collateral = Currency.USD

        fwd = Forward(start_date=start_date, end_date=end_date, fixing_date=fixing_date,
                      pay_date=pay_date, active_notional=active_notional,
                      passive_notional=passive_notional, associated_collateral=associated_collateral)

        real = fwd.valuate(dataset=dataset).amount
        expected = 1759012.895

        self.assertAlmostEqual(real, expected, 2)


