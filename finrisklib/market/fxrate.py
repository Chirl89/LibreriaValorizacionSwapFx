"""
El módulo de tipos de cambio permite la estandarización en la representación de los distintos pares de moneda.
"""
from finrisklib.enums import Currency
from finrisklib.enums import Locality
from finrisklib.finriskconfig import fx_pair_config
from finrisklib.exceptions import CurrencyException
from finrisklib.exceptions import FxRateException

# region Tipos de Cambio

# region Clase Base


class FxPair:
    """ Representación de un par de mondas

    Cuenta con una moneda primaria y otra moneda secundaria, siendo el tipo de cambio la cantidad de unidades de la
    moneda secundaria que se requieren para adquirir una unidad de la moneda primaria.

    :param primary_currency: Moneda primaria.
    :type primary_currency: Currency.
    :param secondary_currency: Moneda secundaria.
    :type secondary_currency: Currency.
    :param discount_days: Cantidad de días de descuento (default: 2).
    :type discount_days: Int.
    :param calendar_locations: Lista de localizaciones.
    :type calendar_locations: List
    """

    def __init__(self, primary_currency: Currency, secondary_currency: Currency,
                 discount_days: int = 2, calendar_locations=None):
        self.primary_currency = primary_currency
        self.secondary_currency = secondary_currency
        self.discount_days = discount_days
        if calendar_locations is None:
            calendar_locations = [Locality.USA]
        self.calendar_locations = calendar_locations

    def __hash__(self):
        return hash((self.primary_currency, self.secondary_currency))

    def __str__(self):
        """
        Sobrecarga de string
        :return:
        """
        return f'{self.primary_currency.name}-{self.secondary_currency.name}'

    def __repr__(self):
        """
        Sobrecarga de string
        :return:
        """
        return f'{self.primary_currency.name}-{self.secondary_currency.name}'

    def __eq__(self, other):
        """
        Sobrecarga la comparación de igualdad entre dos objetos Fx

        :param other: Objeto.
        :return: Booleano con resultado de comparación
        """
        if isinstance(other, FxPair):
            return self.primary_currency == other.primary_currency and \
                   self.secondary_currency == other.secondary_currency
        return False

    def inverse_pair(self):
        """Obtener par inverso

        Invierte el par de monedas y retorna un nuevo par de monedas

        :return: FxPair con monedas invertidas
        """
        return FxPair(primary_currency=self.secondary_currency, secondary_currency=self.primary_currency,
                      discount_days=self.discount_days)

    def has_eq_currency(self):
        """Monedas Iguales

        Verifica si las monedas primarias y secundarias sean iguales

        :return: Booleano
        """
        return self.primary_currency == self.secondary_currency

    @staticmethod
    def generate(pair: str):

        if type(pair) != str:
            pair = str(pair)

        pair = pair.upper()

        if pair in fx_pair_config.keys():
            try:
                primary_curr = Currency.from_str(fx_pair_config[pair]['primary'])
                secondary_curr = Currency.from_str(fx_pair_config[pair]['secondary'])
                discount_days = fx_pair_config[pair]['discount days']
                calendar_locations = fx_pair_config[pair]['calendar']

                return FxPair(primary_currency=primary_curr, secondary_currency=secondary_curr,
                              discount_days=discount_days, calendar_locations=calendar_locations)
            except CurrencyException as e:
                currency = e.currency
                message = f'Could not parse currency {currency} while generating {pair} pair'
                raise FxRateException(fx_pair_name=pair, message=message)
            except Exception:
                message = f'Uncategorized exception occurred while generating {pair} pair'
            raise FxRateException(fx_pair_name=pair, message=message)
        else:
            try:
                primary_curr = Currency.from_str(pair[:3])
                secondary_curr = Currency.from_str(pair[-3:])
                discount_days = 2
                calendar_locations = [Locality.USA]

                return FxPair(primary_currency=primary_curr, secondary_currency=secondary_curr,
                              discount_days=discount_days, calendar_locations=calendar_locations)
            except Exception:
                message = f'Could not generate FxPair object for {pair} pair'
                raise FxRateException(fx_pair_name=pair, message=message)

# endregion
