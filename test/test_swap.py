from unittest import TestCase
from finrisklib.enums import Currency, Source
from finrisklib.instruments.flow import Cash
from finrisklib.instruments.flow import Cashflow
from finrisklib.data.dbreader import DBReader
from finrisklib.market.index import Index
from finrisklib.enums import FinancialIndex
from finrisklib.enums import IndexType
from finrisklib.enums import Periodicity
from finrisklib.enums import Compounding
from finrisklib.enums import DayCount
from datetime import date
from finrisklib.instruments.swap import Coupon


class TestCoupon(TestCase):

    def test_get_flow_fix_rate(self):
        # Obtención de dataset

        process_date = date(year=2022, month=7, day=29)
        reader = DBReader()
        dataset = reader.get_dataset(process_date=process_date, source=Source.SANDBOX)

        # region Prueba 1

        # Operación 6651513 Flujo 1 Activo

        # Definición de Cupón

        rate = Index(name=str(FinancialIndex.FIX), idx_type=IndexType.FIXED, periodicity=Periodicity.ANNUAL,
                     day_count=DayCount.DC_ACT_360, compounding=Compounding.LINEAR)
        spread = 0
        start_date = date(year=2022, month=4, day=20)
        start_fixing_date = date(year=2022, month=4, day=20)
        end_date = date(year=2025, month=5, day=27)
        end_fixing_date = date(year=2025, month=5, day=27)
        interest_payment_date = date(year=2025, month=5, day=27)
        principal_payment_date = date(year=2025, month=5, day=27)
        outstanding_notional = Cash(amount=2750000, currency=Currency.USD)
        amortization = Cash(amount=2750000, currency=Currency.USD)
        associated_collateral = Currency.CLP

        coupon = Coupon(associated_index=rate, reference_rate=0, spread=spread, start_date=start_date, end_date=end_date,
                        start_fixing_date=start_fixing_date, end_fixing_date=end_fixing_date,
                        interest_payment_date=interest_payment_date, principal_payment_date=principal_payment_date,
                        outstanding_notional=outstanding_notional, amortization=amortization,
                        associated_collateral=associated_collateral)

        valuation_details = coupon.get_valuation_details(dataset=dataset)

        self.assertEqual(valuation_details['Interest'], 0)
        self.assertEqual(valuation_details['Principal'], 2750000.000000)

        # endregion

        # region Prueba 2

        # Operación 4892674 Flujo 2 Activo

        # Definición de Cupón

        rate = Index(name=str(FinancialIndex.FIX), idx_type=IndexType.FIXED, periodicity=Periodicity.ANNUAL,
                     day_count=DayCount.DC_ACT_360, compounding=Compounding.LINEAR)
        spread = 0
        start_date = date(year=2022, month=5, day=3)
        start_fixing_date = date(year=2022, month=5, day=3)
        end_date = date(year=2022, month=11, day=3)
        end_fixing_date = date(year=2022, month=11, day=3)
        interest_payment_date = date(year=2022, month=11, day=4)
        principal_payment_date = date(year=2022, month=11, day=4)
        outstanding_notional = Cash(amount=300000.000000, currency=Currency.CLF)
        amortization = Cash(amount=0, currency=Currency.CLF)
        associated_collateral = Currency.CLP

        coupon = Coupon(associated_index=rate, reference_rate=0.0091, spread=spread, start_date=start_date,
                        end_date=end_date,
                        start_fixing_date=start_fixing_date, end_fixing_date=end_fixing_date,
                        interest_payment_date=interest_payment_date, principal_payment_date=principal_payment_date,
                        outstanding_notional=outstanding_notional, amortization=amortization,
                        associated_collateral=associated_collateral)

        valuation_details = coupon.get_valuation_details(dataset)

        self.assertAlmostEqual(valuation_details['Interest'], 1395.333333, 5)
        self.assertEqual(valuation_details['Principal'], 0)

        # endregion

    def test_get_flow_float(self):

        process_date = date(year=2022, month=7, day=29)
        reader = DBReader()

        dataset = reader.get_dataset(process_date=process_date, source=Source.OFFICIAL)

        # region Prueba 1

        # Operación 4892674 Flujo 2 Activo

        # Definición de Cupón

        rate = Index.generate(FinancialIndex.EURIBOR6M)
        spread = 0
        start_date = date(year=2022, month=6, day=27)
        start_fixing_date = date(year=2022, month=6, day=23)
        end_date = date(year=2022, month=12, day=27)
        end_fixing_date = date(year=2022, month=12, day=27)
        interest_payment_date = date(year=2022, month=12, day=27)
        principal_payment_date = date(year=2022, month=12, day=27)
        outstanding_notional = Cash(amount=5000000.000000, currency=Currency.EUR)
        amortization = Cash(amount=0, currency=Currency.EUR)
        associated_collateral = Currency.USD

        coupon = Coupon(associated_index=rate, reference_rate=0, spread=spread, start_date=start_date,
                        end_date=end_date,
                        start_fixing_date=start_fixing_date, end_fixing_date=end_fixing_date,
                        interest_payment_date=interest_payment_date, principal_payment_date=principal_payment_date,
                        outstanding_notional=outstanding_notional, amortization=amortization,
                        associated_collateral=associated_collateral)

        valuation_details = coupon.get_valuation_details(dataset=dataset)

        self.assertAlmostEqual(valuation_details['Interest'], 7396.250000, 5)
        self.assertEqual(valuation_details['Principal'], 0)

        # endregion
