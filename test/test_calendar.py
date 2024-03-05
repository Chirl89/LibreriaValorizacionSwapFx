from unittest import TestCase
from finrisklib.market.tradingcalendar import TradingCalendar
from datetime import date
from finrisklib.enums import DayCount


class TestCalendar(TestCase):

    def test_get_year_fraction(self):
        date_1 = date(year=2021, month=1, day=1)
        date_2 = date(year=2022, month=1, day=1)

        expected = 1
        real = TradingCalendar.get_year_fraction(start_date=date_1, end_date=date_2, day_count=DayCount.DC_ACT_365)

        self.assertEqual(expected, real)

        expected = 365/360
        real = TradingCalendar.get_year_fraction(start_date=date_1, end_date=date_2, day_count=DayCount.DC_ACT_360)

        self.assertEqual(expected, real)
