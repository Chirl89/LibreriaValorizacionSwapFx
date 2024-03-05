from unittest import TestCase
from finrisklib.data.filereader import XlsReader
from datetime import date
from finrisklib.enums import Currency


class TestFileReader(TestCase):

    def test_read_curve_data(self):
        file_name = 'testdata/filereader_test_curve_data.xlsx'
        curve_dataset = XlsReader.read_curve_data(file_name)
        clp_cl = curve_dataset.get_discount_curve(associated_currency=Currency.CLP,
                                                  associated_collateral=Currency.CLP)

        self.assertEqual(1, 1)

    def test_read_fx_pair_data(self):
        file_name = 'testdata/filereader_test_fxrate_data.xlsx'
        fx_data = XlsReader.read_fx_pair_data(file_name)

        self.assertEqual(1, 1)

    def test_read_index_data(self):
        file_name = 'testdata/filereader_test_index_data.xlsx'
        idx_data = XlsReader.read_index_data(file_name)

        self.assertEqual(1, 1)

    def test_read_dataset_data(self):
        process_date = date(year=2022, month=5, day=25)
        curve_file = 'testdata/datasetreader_test_curve_data.xlsx'
        fx_file = 'testdata/datasetreader_test_fxrate_data.xlsx'
        index_file = 'testdata/filereader_test_index_data.xlsx'

        dataset = XlsReader.read_dataset_data(process_date=process_date, curve_file=curve_file, fx_file=fx_file,
                                              index_file=index_file)
        self.assertEqual(1, 1)

    def test_read_operation_data(self):
        file_name = 'testdata/filereader_test_swap_data.xlsx'
        instrument = XlsReader.read_derivados_data(file_name)

        self.assertTrue(1 == 1)
