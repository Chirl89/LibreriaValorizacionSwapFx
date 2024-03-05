"""
Este módulo contiene los objetos necesarios para poder representar curvas de descuento y proyección.
"""
import math
import pandas as pd
from datetime import date
from datetime import timedelta
from finrisklib.exceptions import CurveException
from finrisklib.finmath.interpolator import Interpolator
from finrisklib.enums import InterpolationMethod
from finrisklib.enums import ExtrapolationMethod
from finrisklib.enums import Compounding
from finrisklib.enums import DayCount
from finrisklib.market.tradingcalendar import TradingCalendar


def generate_curve_config(interpolation_method=InterpolationMethod.LOG_LINEAR,
                          low_point_extrapolation_method=ExtrapolationMethod.FLAT_RATE,
                          high_point_extrapolation_method=ExtrapolationMethod.RATE_SLOPE,
                          rate_compounding=Compounding.YIELD,
                          rate_day_count=DayCount.DC_ACT_360):
    """Generar configuración de curvas

    Genera un diccionario con el formato adecuado para configurar la clase :class:`Curve <market.curve.Curve>`.

    :param interpolation_method: Método de interpolación. (default Log-Linear)
    :type interpolation_method: InterpolationMethod.
    :param low_point_extrapolation_method: Método de extrapolación en punto bajo. (default Flat Rate)
    :type low_point_extrapolation_method: ExtrapolationMethod.
    :param high_point_extrapolation_method: Método de extrapolación en punto alto. (default Rate Slope).
    :type high_point_extrapolation_method: ExtrapolationMethod.
    :param rate_compounding: Composición de tasa. (default Yield)
    :type rate_compounding: Compounding.
    :param rate_day_count: Conteo de días de la tasa. (default Act/360)
    :type rate_day_count: DayCount

    :return: Diccionario con configuración de curva
    """
    curve_config = {'interpolation': interpolation_method,
                    'low extrapolation': low_point_extrapolation_method,
                    'high extrapolation': high_point_extrapolation_method,
                    'associated_index compounding': rate_compounding,
                    'associated_index day count': rate_day_count}
    return curve_config


class Curve:
    """Curva

    Clase dedicada a la representación de curvas de descuento y de proyección

    :param curve_name: Identificador de la curva.
    :type curve_name: str
    :param process_date: Fecha de proceso de la curva actual.
    :type process_date: date
    :param tenors: Lista de tenors asignados.
    :type tenors: list[int]
    :param discount_factors: Lista de factores de descuento mid.
    :type discount_factors: list[float]
    :param curve_config: Diccionario con configuración de curva (Default: None)
    :type curve_config: dict
    """

    # region Inicializador

    def __init__(self, curve_name: str, process_date: date, tenors: list, discount_factors: list,
                 curve_config: dict = None):

        if curve_config is None:
            self.curve_config = generate_curve_config()
        else:
            self.curve_config = curve_config

        if tenors != sorted(tenors):
            raise CurveException(curve_name, 'Vector tenor must be sorted.')

        if len(tenors) != len(discount_factors):
            raise CurveException(curve_name, f'Vectors tenors (length {len(tenors)}) and '
                                             f'discount factors (length {len(discount_factors)}) '
                                             f'must be of equal length.')

        self.curve_name = curve_name
        self.process_date = process_date
        self.tenors = tenors
        self.discount_factors = discount_factors

    # endregion

    # region Overload de Representación

    def __repr__(self):
        """Sobrecarga de Representación

        Devuelve el nombre de la curva

        :return: Nombre de curva
        """
        return self.curve_name

    # endregion

    # region Obtención de factores de descuento

    def get_discount_factor(self, t: int) -> float:
        """Obtener factor de descuento

        Obtiene el factor de descuento al tenor especificado

        :param t: tenor especificado.
        :type t: int

        :return: Factor de descuento
        """
        if t < min(self.tenors):
            return Interpolator.interpolate(point=t, x_vector=self.tenors, y_vector=self.discount_factors,
                                            interpolation_method=self.curve_config['interpolation'],
                                            extrapolation_method=self.curve_config['low extrapolation'])
        else:
            return Interpolator.interpolate(point=t, x_vector=self.tenors, y_vector=self.discount_factors,
                                            interpolation_method=self.curve_config['interpolation'],
                                            extrapolation_method=self.curve_config['high extrapolation'])

    def get_cap_factor(self, t: int) -> float:
        """Obtener factor de capitalización

        Obtiene el factor de capitalización a un tenor especificado

        :param t: tenor especificado
        :type t: int

        :return: Factor de capitalización
        """
        return 1/self.get_discount_factor(t)

    def get_forward_factor(self, t_start, t_end):
        """Obtener Factor Forward

        Obtiene el factor forward entre los tenors especificados

        :param t_start: tenor de inicio
        :param t_end: tenor de final

        :return: Factor Forward
        """

        p_start = self.get_discount_factor(t_start)
        p_end = self.get_discount_factor(t_end)
        return p_end/p_start

    def get_rate(self, t: int) -> float:
        """Obtener tasa de descuento

        Obtiene la tasa de descuento del tenor especificado

        :param t: tenor especificado.
        :type t: int

        :return: Tasa de descuento
        """
        df = self.get_discount_factor(t)
        end_date = self.process_date + timedelta(days=t)
        rate = Curve.df_to_rate(discount_factor=df, start_date=self.process_date, end_date=end_date,
                                rate_compounding=self.curve_config['associated_index compounding'],
                                rate_day_count=self.curve_config['associated_index day count'])
        return rate

    # endregion

    # region Obtención de tasas

    def get_rate_curve(self):
        """Obtener curva de tasas

        Obtiene la curva expresada en tasa

        :return: Tuple con tenors y tasa.
        """
        rates = []
        for i in range(len(self.tenors)):
            t = self.tenors[i]
            df = self.discount_factors[i]
            end_date = self.process_date + timedelta(days=t)
            rate = Curve.df_to_rate(discount_factor=df, start_date=self.process_date, end_date=end_date,
                                    rate_compounding=self.curve_config['associated_index compounding'],
                                    rate_day_count=self.curve_config['associated_index day count'])
            rates.append(rate)

        return self.tenors, rates

    # endregion

    # region funciones de conversión de datos

    def to_dict(self):
        """Convertir en diccionario

        Convierte los datos de la curva en un diccionario

        :return: Diccionario con datos de la curva
        """
        return dict(zip(self.tenors, self.discount_factors))

    def rates_to_dict(self):
        """Convertir a un diccionario de tasas

        Convierte la curva en un diccionario de tasas

        :return: Diccionario de tasas
        """
        tenors, rates = self.get_rate_curve()
        return dict(zip(tenors, rates))

    def to_dataframe(self):
        """Convertir a dataframe

        Convierte los datos de la curva a un dataframe

        :return: Dataframe con datos de la curva
        """
        curve_dict = self.to_dict()
        df = pd.DataFrame(curve_dict.items(), columns=['Tenor', 'Discount Factor'])
        return df

    def rates_to_dataframe(self):
        """Convertir tasas a dataframe

        Convierte las tasas de la curva a un dataframe

        :return: Dataframe con tasas de la curva
        """
        curve_dict = self.rates_to_dict()
        df = pd.DataFrame(curve_dict.items(), columns=['Tenor', 'Rates'])
        return df

    # endregion

    # region Funciones Estáticas

    @staticmethod
    def df_to_rate(discount_factor, start_date, end_date, rate_compounding, rate_day_count):
        """Convertir Factor de Descuento a Tasa

        Convierte el factor de descuento provisto a una tasa utilizando las convenciones de composición y
        conteo de días provistas.

        :param discount_factor: Factor de descuento.
        :type discount_factor: float.
        :param start_date: fecha de inicio.
        :type start_date: date.
        :param end_date: fecha de fin.
        :type end_date: date.
        :param rate_compounding: Convención de composición de Tasa.
        :type rate_compounding: Compounding.
        :param rate_day_count: Convención de conteo de días.
        :type rate_day_count: DayCount.

        :return: Tasa de interés.
        """
        yf = TradingCalendar.get_year_fraction(start_date=start_date, end_date=end_date, day_count=rate_day_count)

        if rate_compounding == Compounding.LINEAR:
            return ((1 / discount_factor) - 1)/yf
        elif rate_compounding == Compounding.YIELD:
            return math.pow(1/discount_factor, 1/yf)-1
        elif rate_compounding == Compounding.EXPONENTIAL:
            return -math.log(discount_factor)/yf
        else:
            raise NotImplemented()

    @staticmethod
    def rate_to_df(annual_rate: float, start_date: date, end_date: date, rate_compounding: Compounding,
                   rate_day_count: DayCount):
        """Convertir Tasa a Factor de Descuento

        Convierte la tasa a factor de descuento utilizando las convenciones de composición y conteo de días
        provisto.

        :param annual_rate: Tasa Anual.
        :param start_date: fecha de inicio.
        :type start_date: date.
        :param end_date: fecha de fin.
        :type end_date: date.
        :param rate_compounding: Convención de composición de Tasa.
        :type rate_compounding: Compounding.
        :param rate_day_count: Convención de conteo de días.
        :type rate_day_count: DayCount.

        :return: Factor de descuento
        """
        yf = TradingCalendar.get_year_fraction(start_date=start_date, end_date=end_date, day_count=rate_day_count)

        if rate_compounding == Compounding.LINEAR:
            return 1/(1+annual_rate*yf)
        elif rate_compounding == Compounding.YIELD:
            return math.pow(1+annual_rate, -yf)
        elif rate_compounding == Compounding.EXPONENTIAL:
            return math.exp(-annual_rate*yf)
        else:
            raise NotImplemented()

    @staticmethod
    def rate_to_cap_factor(annual_rate, start_date, end_date, rate_compounding, rate_day_count):
        """Convertir Tasa a Factor de Capitalización

        Convierte la tasa a factor de capitalización utilizando las convenciones de composición y conteo de días
        provisto.

        :param annual_rate: Tasa Anual.
        :param start_date: fecha de inicio.
        :type start_date: date
        :param end_date: fecha de fin.
        :type end_date: date
        :param rate_compounding: Convención de composición de Tasa.
        :type rate_compounding: Compounding
        :param rate_day_count: Convención de conteo de días.
        :type rate_day_count: DayCount

        :return: Factor de capitalización
        """
        return 1/Curve.rate_to_df(annual_rate, start_date, end_date, rate_compounding, rate_day_count)

    # endregion

    # region Sobrecarga de operadores

    def __truediv__(self, other):
        """Sobrecarga de división

        :param other: Otro objeto
        :return: Curva Dividida
        """
        if isinstance(other, Curve):
            tenors = self.tenors.copy()
            tenors.extend(x for x in other.tenors if x not in tenors)
            tenors.sort()
            discount_factors = []
            for t in tenors:
                df = self.get_discount_factor(t)/other.get_discount_factor(t)
                discount_factors.append(df)
            curve_name = f'Synth: {self.curve_name} div {other.curve_name}'
            new_curve = Curve(curve_name=curve_name, process_date=self.process_date, tenors=tenors,
                              discount_factors=discount_factors)
            return new_curve
        else:
            message = f'Can not divide Curve objet and {type(other)}.'
            raise CurveException(self.curve_name, message)

    def __mul__(self, other):
        """Sobrecarga de multiplicación

        :param other: Otro objeto
        :return: Curva Multiplicada
        """
        if isinstance(other, Curve):
            tenors = self.tenors.copy()
            tenors.extend(x for x in other.tenors if x not in tenors)
            tenors.sort()
            discount_factors = []
            for t in tenors:
                df = self.get_discount_factor(t)*other.get_discount_factor(t)
                discount_factors.append(df)
            curve_name = f'Synth: {self.curve_name} times {other.curve_name}'
            new_curve = Curve(curve_name=curve_name, process_date=self.process_date, tenors=tenors,
                              discount_factors=discount_factors)
            return new_curve
        else:
            message = f'Can not multiply Curve objet and {type(other)}.'
            raise CurveException(self.curve_name, message)

    # endregion
