"""
Este módulo se encuentra enfocado en representar productos forward, para esto se cuenta con las siguientes
clases.

La clase Forward que representa un forward Vanilla.
"""

from datetime import date
from finrisklib.instruments.flow import Cash
from finrisklib.instruments.flow import Cashflow
from finrisklib.market.dataset import DataSet
from finrisklib.market.fxrate import FxPair
from finrisklib.enums import Currency
from finrisklib.instruments.instrument import Derivative


class Forward(Derivative):
    """Instrumento Forward

    Clase dedicada a la representación de forwards vanilla.

    :param start_date: Fecha de inicio.
    :type start_date: date
    :param end_date: Fecha de termino.
    :type end_date: date
    :param fixing_date: Fecha de fijación.
    :type fixing_date: date
    :param pay_date: Fecha de pago.
    :type pay_date: date
    :param active_notional: Nocional activo.
    :type active_notional: Cash
    :param passive_notional: Nocional pasivo.
    :type passive_notional: Cash
    :param associated_collateral: Colateral asociado.
    :type associated_collateral: Currency
    """

    def __init__(self, start_date: date, end_date: date, fixing_date: date, pay_date: date, active_notional: Cash,
                 passive_notional: Cash, associated_collateral: Currency, payment_currency: Currency = Currency.CLP):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.fixing_date = fixing_date
        self.pay_date = pay_date
        self.active_notional = active_notional
        self.passive_notional = passive_notional
        self.associated_collateral = associated_collateral
        self.payment_currency = payment_currency
        self.fx_pair = FxPair.generate(f'{str(active_notional.currency)}{str(passive_notional.currency)}')

        self.strike = self.passive_notional.amount / self.active_notional.amount

        active_cashflow = Cashflow(flow_date=pay_date, amount=active_notional.amount,
                                   currency=active_notional.currency)
        passive_cashflow = Cashflow(flow_date=pay_date, amount=passive_notional.amount,
                                    currency=passive_notional.currency)

        super().add_active_cashflow(active_cashflow)
        super().add_passive_cashflow(passive_cashflow)

    def valuate(self, dataset: DataSet):
        """Valorizar

        Obtiene el mtm, en caso no se especifique la fecha se utilizara la fecha del data set

        :param dataset: Dataset de mercado
        :type dataset: DataSet

        :return: Objeto Cash con valor presente del instrumento
        """

        valuation_currency = dataset.get_default_valuation_currency()

        # Caso fecha de valorización sea menor a fecha de pago
        if dataset.market_date >= self.pay_date:
            return Cash(amount=0, currency=valuation_currency)

        fx_pair = self.get_currency_pair()

        strike = self.get_strike()
        # fwd_price = dataset.get_fx_forward_rate(fx_pair=fx_pair, forward_date=self.end_date)
        fwd_price = dataset.get_fx_forward_rate(fx_pair=fx_pair, forward_date=self.fixing_date)

        payoff = (fwd_price-strike)*self.active_notional.amount

        payment_pair = FxPair.generate(f'{self.passive_notional.currency}{self.payment_currency}')
        valuation_pair = FxPair.generate(f'{self.payment_currency}{valuation_currency}')

        payoff_fwd_price = dataset.get_fx_forward_rate(fx_pair=payment_pair, forward_date=self.fixing_date)
        payoff_pay_currency = payoff*payoff_fwd_price

        discount_curve = dataset.get_discount_curve(associated_currency=self.payment_currency,
                                                    associated_collateral=self.associated_collateral)

        dt = (self.pay_date-dataset.market_date).days
        df = discount_curve.get_discount_factor(dt)

        spot = dataset.get_fx_rate(fx_pair=valuation_pair)

        value = payoff_pay_currency * df * spot

        return Cash(amount=value, currency=valuation_currency)

    def get_strike(self):
        """Obtener strike

        Obtiene el strike del forward

        :return: Strike
        """
        return self.strike

    def get_currency_pair(self):
        """Obtener par de moneda

        Obtiene el par de moneda asociada con el instrumento

        :return: FxPair
        """
        return self.fx_pair
