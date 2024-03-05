from unittest import TestCase
from datetime import date
from finrisklib.instruments.flow import Cash
from finrisklib.instruments.flow import Cashflow
from finrisklib.enums import Currency
from finrisklib.exceptions import CurrencyException


class TestCash(TestCase):

    def test_str(self):
        """
        Prueba la conversión de objeto a string para la clase Cash
        """
        expected = "100.00 USD"

        cash_obj = Cash(amount=100, currency=Currency.USD)
        result = str(cash_obj)
        self.assertEqual(expected, result)

    def test_sum(self):
        """
        Prueba que se puedan sumar dos cajas de la misma moneda
        """
        cash_1 = Cash(100, Currency.USD)
        cash_2 = Cash(150, Currency.USD)

        sum_result = cash_1 + cash_2
        self.assertEqual(sum_result.amount, 250)

    def test_sum_type_exception(self):
        """
        Prueba que se levante una excepción al intentar sumar un tipo no soportado
        """
        try:
            cash_1 = Cash(100, Currency.USD)
            cash_2 = "150 USD"

            cash_1 + cash_2
            self.fail()
        except TypeError:
            pass

    def test_sum_currency_exception(self):
        """
        Prueba que se levante una excepción al intentar sumar dos flujos con monedas distintas
        """
        try:
            cash_1 = Cash(100, Currency.USD)
            cash_2 = Cash(150, Currency.EUR)

            cash_1 + cash_2
            self.fail()
        except CurrencyException:
            pass

    def test_eq(self):
        """
        Prueba que se asegurar que dos flujos son iguales
        """
        cash_1 = Cash(100, Currency.USD)
        cash_2 = Cash(100, Currency.USD)
        self.assertTrue(cash_1 == cash_2)


class TestCashflow(TestCase):

    def test_str(self):
        """
        Prueba la conversión de objeto a string para la clase Cashflow
        """
        cashflow_obj = Cashflow(flow_date=date(year=2022, month=1, day=30), amount=100, currency=Currency.USD)
        expected = "100.00 USD 2022/01/30"

        result = str(cashflow_obj)
        self.assertEqual(expected, result)

    def test_sum(self):
        """
        Prueba que se puedan sumar dos cajas de la misma moneda y fecha
        """
        cash_1 = Cashflow(flow_date=date(year=2022, month=1, day=30), amount=100, currency=Currency.USD)
        cash_2 = Cashflow(flow_date=date(year=2022, month=1, day=30), amount=150, currency=Currency.USD)
        cash_3 = Cashflow(flow_date=date(year=2022, month=1, day=30), amount=250, currency=Currency.USD)

        sum_result = cash_1 + cash_2
        self.assertEqual(sum_result, cash_3)

    def test_sum_type_exception(self):
        """
        Prueba que se levante una excepción al intentar sumar un tipo no soportado
        """
        try:
            cash_1 = Cashflow(flow_date=date(year=2022, month=1, day=30), amount=100, currency=Currency.USD)
            cash_2 = "150 USD"

            cash_1 + cash_2
            self.fail()
        except TypeError:
            pass

    def test_sum_currency_exception(self):
        """
        Prueba que se levante una excepción al intentar sumar dos flujos con monedas distintas
        """
        try:
            cash_1 = Cashflow(flow_date=date(year=2022, month=1, day=30), amount=100, currency=Currency.USD)
            cash_2 = Cashflow(flow_date=date(year=2022, month=1, day=30), amount=150, currency=Currency.EUR)

            cash_1 + cash_2
            self.fail()
        except CurrencyException:
            pass

    def test_sum_date_exception(self):
        """
        Prueba que se levante una excepción al intentar sumar dos flujos con fechas distintas
        """
        try:
            cash_1 = Cashflow(flow_date=date(year=2022, month=1, day=30), amount=100, currency=Currency.USD)
            cash_2 = Cashflow(flow_date=date(year=2022, month=4, day=30), amount=150, currency=Currency.USD)

            cash_1 + cash_2
            self.fail()
        except ValueError:
            pass
