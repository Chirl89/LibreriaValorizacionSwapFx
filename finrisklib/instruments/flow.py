"""
Las clases en este módulo están dedicadas a la representación de cajas y flujos de caja.
"""

from finrisklib.enums import Currency
from finrisklib.exceptions import CurrencyException
from finrisklib.market.fxrate import FxPair
from finrisklib.market.dataset import DataSet
from datetime import date
from math import isclose


class Cash:
    r"""Clase Cash

    Representa una caja con moneda y monto específico. La clase soporta la suma de otro instrumento cash y su
    comparación.

    :param amount: Monto
    :type amount: float
    :param currency: Numerario o Moneda
    :type currency: Currency

    :raises TypeError: Cuando se intenta sumar con un objeto no Cash
    :raises CurrencyException: Cuando se intenta sumar con un objeto Cash con moneda distinta

    :Ejemplo de uso:

    .. highlight:: python
    .. code-block:: python

        from finlib.instruments.flow import Cash
        from finlib.enums import Currency

        cash_1 = Cash(amount = 100, currency = Currency.USD)
        cash_2 = Cash(amount = 150, currency = Currency.CLP)
        cash_3 = Cash(amount = 100, currency = Currency.USD)

        cash_fail = cash_1 + "100 USD" # Genera una excepción TypeError
        cash_fail = cash_1 + cash_2 # Genera una excepción CurrencyException
        cash_4 = cash_1 + cash_3 # Cash(200, Currency.USD)

        result = cash_1 == "100 USD" # false
        result = cash_1 == cash_2 # false
        result = cash_1 == cash3 # true

    """

    def __init__(self, amount: float, currency: Currency):
        """Inicializador"""
        self.amount = amount
        self.currency = currency

    # region overload de operadores

    def __str__(self):
        """
        Sobrecarga el string del flujo

        :return: monto y moneda del Cash
        """
        return f'{self.amount:,.2f} {self.currency if isinstance(self.currency, str) else self.currency.name }'

    def __repr__(self):
        """
        Sobrecarga de representación de flujo

        :return: monto, moneda y fecha del Cashflow
        """
        return f'{self.amount:,.2f} {self.currency if isinstance(self.currency, str) else self.currency.name } '

    def __add__(self, other):
        """
        Sobrecarga la suma de dos objetos Cash

        :param other: Objeto cash
        :return: objeto Cash sumado
        """
        if isinstance(other, Cash):
            if other.currency == self.currency:
                new_amount = self.amount + other.amount
                return Cash(amount=new_amount, currency=self.currency)
            raise CurrencyException(f'Can not add {str(self)} to {str(other)}. Currencies must coincide')
        else:
            raise TypeError(f'Can not add {type(other)} to Cash')

    def __sub__(self, other):
        """
        Sobrecarga la resta de dos objetos Cash

        :param other: Numero a substraer.
        :return: Objeto Cash restado.
        """
        if isinstance(other, Cash):
            if other.currency == self.currency:
                new_amount = self.amount - other.amount
                return Cash(amount=new_amount, currency=self.currency)
            raise CurrencyException(f'Can not subtract {str(self)} to {str(other)}. Currencies must coincide')
        else:
            raise TypeError(f'Can not subtract {type(other)} to Cash')

    def __mul__(self, other):
        """
        Sobrecarga de multiplicación a objeto Cash

        :param other: Numero a multiplicar
        :return: Objeto Cash multiplicado
        """
        if isinstance(other, float) or isinstance(other, int):
            value = self.amount*other
            return Cash(amount=value, currency=self.currency)
        else:
            raise TypeError(f'Can not multiply {type(other)} to Cash')

    def __rmul__(self, other):
        """
        Sobrecarga de multiplicación a objeto Cash

        :param other: Numero a multiplicar
        :return: Objeto Cash multiplicado
        """
        if isinstance(other, float) or isinstance(other, int):
            value = self.amount * other
            return Cash(amount=value, currency=self.currency)
        else:
            raise TypeError(f'Can not multiply {type(other)} to Cash')

    def __eq__(self, other):
        """
        Sobrecarga la comparación de igualdad entre dos objetos Cash

        :param other: Objeto
        :return: Booleano con resultado de comparación
        """
        if isinstance(other, Cash):
            return isclose(self.amount, other.amount) and self.currency == other.currency
        return False

    # endregion


class Cashflow:
    r"""Clase Cashflow

    Representa un flujo futuro con moneda, monto y fecha determinada. La clase soporta la suma de otro instrumento
    cashflow, al igual que su comparación.

    :param flow_date: Fecha del flujo
    :type flow_date: date
    :param amount: Monto
    :type amount: float
    :param currency: Numerario o Moneda
    :type currency: Currency

    :raises TypeError: Cuando se intenta sumar con un objeto no Cashflow
    :raises CurrencyException: Cuando se intenta sumar con un objeto Cashflow con moneda distinta
    :raises ValueError: Cuando se intenta sumar con un objeto Cashflow con fecha distinta

    .. highlight:: python
    .. code-block:: python

        from finlib.instruments.flow import Cashflow
        from finlib.enums import Currency
        from datetime import date

        cashflow_1 = Cashflow(flow_date=date(year=2022, month=1, day=30), amount = 100, currency = Currency.USD)
        cashflow_2 = Cashflow(flow_date=date(year=2022, month=1, day=30), amount = 150, currency = Currency.CLP)
        cashflow_3 = Cashflow(flow_date=date(year=2022, month=1, day=30), amount = 100, currency = Currency.USD)
        cashflow_4 = Cashflow(flow_date=date(year=2022, month=3, day=30), amount = 100, currency = Currency.USD)

        cashflow_fail = cashflow_1 + "100 USD" # Genera una excepción TypeError
        cashflow_fail = cashflow_1 + cashflow_2 # Genera una excepción CurrencyException
        cashflow_fail = cashflow_1 + cashflow_4 # Genera una excepción ValueError

        cash_5 = cash_1 + cash_3 # Cashflow(flow_date=date(year=2022, month=1, day=30), 200, Currency.USD)

        result = cash_1 == "100 USD" # false
        result = cash_1 == cash_2 # false
        result = cash_1 == cash3 # true

    """

    def __init__(self, flow_date: date, amount: float, currency: Currency):
        self.flow_date = flow_date
        self.amount = amount
        self.currency = currency

    # region sobrecarga de operadores

    def __str__(self):
        """
        Sobrecarga el string del flujo

        :return: monto, moneda y fecha del Cashflow
        """
        return f'{self.amount:,.2f} {self.currency if isinstance(self.currency, str) else self.currency.name } ' \
               f'{self.flow_date.strftime("%Y/%m/%d")}'

    def __repr__(self):
        """
        Sobrecarga de representación de flujo

        :return: monto, moneda y fecha del Cashflow
        """
        return f'{self.amount:,.2f} {self.currency if isinstance(self.currency, str) else self.currency.name } ' \
               f'{self.flow_date.strftime("%Y/%m/%d")}'

    def __add__(self, other):
        """
        Sobrecarga la suma de dos objetos Cashflow

        :param other: Objeto cashflow
        :return: objeto Cash sumado
        """
        if isinstance(other, Cashflow):
            if other.currency == self.currency and other.flow_date == self.flow_date:
                new_amount = self.amount + other.amount
                return Cashflow(flow_date=self.flow_date, amount=new_amount, currency=self.currency)
            elif other.currency != self.currency:
                raise CurrencyException(f'Can not add {str(self)} to {str(other)}. Currencies must coincide')
            else:
                raise ValueError(f'Can not add {str(self)} to {str(other)}. Dates must coincide')
        else:
            raise TypeError(f'Can not add {type(other)} to Cashflow')

    def __mul__(self, other):
        """
        Sobrecarga de multiplicación a objeto Cashflow

        :param other: Numero a multiplicar
        :return: Objeto Cashflow multiplicado
        """
        if isinstance(other, float) or isinstance(other, int):
            value = self.amount * other
            return Cashflow(amount=value, currency=self.currency, flow_date=self.flow_date)
        else:
            raise TypeError(f'Can not multiply {type(other)} to Cashflow')

    def __rmul__(self, other):
        """
        Sobrecarga de multiplicación a objeto Cashflow

        :param other: Numero a multiplicar
        :return: Objeto Cash multiplicado
        """
        if isinstance(other, float) or isinstance(other, int):
            value = self.amount * other
            return Cashflow(amount=value, currency=self.currency, flow_date=self.flow_date)
        else:
            raise TypeError(f'Can not multiply {type(other)} to Cashflow')

    def __eq__(self, other):
        """
        Sobrecarga la comparación de igualdad entre dos objetos Cashflow

        :param other: Objeto
        :return: Booleano con resultado de comparación
        """
        if isinstance(other, Cashflow):
            return isclose(self.amount, other.amount) and self.currency == other.currency \
                   and other.flow_date == self.flow_date
        return False

    def valuate(self, dataset: DataSet,
                associated_collateral: Currency = Currency.USD,
                valuation_currency: Currency = None) -> Cash:

        if valuation_currency is None:
            valuation_currency = dataset.get_default_valuation_currency()

        # Caso fecha de valorización sea menor a fecha de pago
        if dataset.market_date >= self.flow_date:
            return Cash(amount=0, currency=valuation_currency)

        fx_pair = FxPair.generate(f'{self.currency}{valuation_currency}')

        discount_curve = dataset.get_discount_curve(associated_currency=self.currency,
                                                    associated_collateral=associated_collateral)

        dt = (self.flow_date - dataset.market_date).days
        df = discount_curve.get_discount_factor(dt)

        value = self.amount * df

        valuation_spot = dataset.get_fx_rate(fx_pair)

        return Cash(amount=value * valuation_spot, currency=valuation_currency)

    # endregion
