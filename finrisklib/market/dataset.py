"""
Este módulo está enfocado en la creación de datasets, es decir objetos que contengan y ayuden a manejar la
información dentro de los mismos.
"""
from datetime import date
from finrisklib.enums import Currency
from finrisklib.enums import BusinessDay
from finrisklib.enums import Period
from finrisklib.enums import FinancialIndex
from finrisklib.enums import Locality
from finrisklib.market.fxrate import FxPair
from finrisklib.market.index import *
from finrisklib.market.curve import Curve
from finrisklib.market.tradingcalendar import TradingCalendar
from finrisklib.exceptions import DatasetException
from pandas.tseries.holiday import AbstractHolidayCalendar


class CalendarDataSet:
    """Set de Datos de Calendarios

    Clase especializada en el manejo de calendarios.
    """

    def __init__(self):
        default_calendar = AbstractHolidayCalendar(name='default', rules=[])
        self.calendars = {'default': {'calendar': TradingCalendar(calendar_name='default', holidays=[],
                                                                  base_calendar=default_calendar),
                                      'rules': [], 'holidays': []}}

    def add_calendar(self, locality: Locality, rules: list, holidays: list):
        """Agregar calendario

        Agrega un calendario asociado a una localidad especifica

        :param locality: Localidad asociada.
        :type locality: Locality
        :param rules: Reglas de feriados.
        :type rules: list
        :param holidays: Feriados específicos.
        :type holidays: list
        :return:
        """
        calendar_name = str(locality)
        base_calendar = AbstractHolidayCalendar(name=calendar_name, rules=rules)
        self.calendars[calendar_name] = {'calendar': TradingCalendar(calendar_name=calendar_name,
                                                                     holidays=holidays,
                                                                     base_calendar=base_calendar),
                                         'rules': rules, 'holidays': holidays}

    def get_calendar(self, localities: list) -> TradingCalendar:
        """Obtiene un calendario dada una lista de localidades

        :param localities: Listado de localidades
        :type localities: list

        :return: TradingCalendar
        """
        if type(localities) is list:
            localities_str = [str(locality) for locality in localities]
            calendar_name = '-'.join(localities_str)
        else:
            calendar_name = str(localities)

        if calendar_name not in self.calendars:
            if '-' in calendar_name:
                rules = []
                holidays = []
                for name in calendar_name.split('-'):
                    rules += self.get_rules([name])
                    holidays += self.get_holidays([name])

                base_calendar = AbstractHolidayCalendar(name=calendar_name, rules=rules)
                calendar = TradingCalendar(calendar_name=calendar_name, holidays=holidays, base_calendar=base_calendar)
                self.calendars[calendar_name] = {'calendar': calendar, 'rules': rules, 'holidays': rules}
            else:
                calendar_name = 'default'

        return self.calendars[calendar_name]['calendar']

    def get_rules(self, localities: list):
        """Obtiene las reglas de calendario dada una lista de localidades

        :param localities: Listado de localidades
        :type localities: list

        :return: Lista de Reglas
        """
        if type(localities) is list:
            localities_str = [str(locality) for locality in localities]
            calendar_name = '-'.join(localities_str)
        else:
            calendar_name = str(localities)

        if calendar_name not in self.calendars:
            calendar_name = 'default'

        return self.calendars[calendar_name]['rules']

    def get_holidays(self, localities: list):
        """Obtiene feriados específicos de calendario dada una lista de localidades

        :param localities: Listado de localidades
        :type localities: list

        :return: Lista de Reglas
        """
        if type(localities) is list:
            localities_str = [str(locality) for locality in localities]
            calendar_name = '-'.join(localities_str)
        else:
            calendar_name = str(localities)

        if calendar_name not in self.calendars:
            calendar_name = 'default'

        return self.calendars[calendar_name]['holidays']


class CurveDataSet:
    """Set de Datos de Curvas

    Clase especializada en el almacenamiento y tratamiento de datos de curvas.

    :param process_date: Fecha de Proceso.
    :type process_date: date
    :param default_collateral_currency: Moneda de colateral (default: USD).
    :type default_collateral_currency: Currency
    """
    def __init__(self, process_date: date, default_collateral_currency: Currency = Currency.USD):
        self.process_date = process_date
        self.__default_collateral_currency = default_collateral_currency  # Variable privada de base para curvas.
        self.__discount_curves = {}  # Variable privada de almacenamiento de curvas de descuento.
        self.__projection_curves = {}  # Variable privada de almacenamiento de curvas de proyección.

    # region Funciones de configuración

    def set_default_collateral_currency(self, collateral_currency: Currency):
        """Asignar moneda default de colateral

        Asigna una moneda como colateral default para todos los calculos internos, incluyendo la generación de curvas
        sintéticas.

        :param collateral_currency: Moneda de Colateral
        :type collateral_currency: Currency
        """
        self.__default_collateral_currency = collateral_currency

    def get_default_collateral_currency(self):
        """Obtener moneda default de colateral

        Obtiene la moneda asignada como colateral default para todos los calculos internos.

        :return: Moneda de colateral default
        """
        return self.__default_collateral_currency

    # endregion

    # region Manejo de curvas de descuento

    def add_discount_curve(self, curve, associated_currency: Currency, associated_collateral: Currency = None):
        """Agregar curva de descuento

        Agrega una curva de descuento considerando una moneda y un colateral asociado

        :param curve: Curva.
        :type curve: Curve
        :param associated_currency: Moneda asociada a la Curva.
        :type associated_currency: Currency
        :param associated_collateral: Colateral asociado a la Curva.
        :type associated_collateral: Currency
        """
        if associated_collateral is None:
            associated_collateral = self.__default_collateral_currency
        if associated_collateral in self.__discount_curves.keys():
            self.__discount_curves[associated_collateral][associated_currency] = curve
        else:
            self.__discount_curves[associated_collateral] = {associated_currency: curve}

    def get_discount_curve(self, associated_currency: Currency, associated_collateral: Currency = None):
        """Obtener curva de descuento

        Obtiene una curva de descuento de acuerdo la moneda y colateral asociada. En caso la curva no exista se
        intentará construir una curva sintética tomando como base la moneda default de las curvas. Si no es posible
        obtener un sintético se levanta una excepción.

        :param associated_currency: Moneda asociada.
        :type associated_currency: Currency.
        :param associated_collateral: Colateral asociado.
        :type associated_collateral: Currency

        :raises DatasetException: En caso la curva no pueda ser obtenida

        :return: Objeto Curve
        """
        if associated_collateral is None:
            associated_collateral = self.__default_collateral_currency
        if associated_collateral in self.__discount_curves.keys():
            # Caso 1: La curva existe dentro del dataset
            if associated_currency in self.__discount_curves[associated_collateral].keys():
                return self.__discount_curves[associated_collateral][associated_currency]
            else:
                # Caso 2: Se construye una curva sintética
                try:

                    base_curve = self.get_discount_curve(associated_currency=associated_collateral,
                                                         associated_collateral=self.__default_collateral_currency)
                    collateral_curve = self.get_discount_curve(associated_currency=associated_collateral,
                                                               associated_collateral=associated_collateral)
                    currency_curve = self.get_discount_curve(associated_currency=associated_currency,
                                                             associated_collateral=self.__default_collateral_currency)

                    synth_curve = (currency_curve/base_curve)*collateral_curve
                    synth_curve.curve_name = f'Synth: {associated_currency} Col {associated_collateral}'
                    # Guardando la curva sintética para optimizar performance
                    self.add_discount_curve(curve=synth_curve, associated_currency=associated_currency,
                                            associated_collateral=associated_collateral)
                    return synth_curve
                except Exception:
                    message = f'Could not construct synthetic curve for {associated_currency} collateralized with ' \
                              f'{associated_collateral}.'
                    raise DatasetException(message)
        else:
            message = f'Could not construct synthetic curve for {associated_currency} collateralized with ' \
                      f'{associated_collateral}.'
            raise DatasetException(message)

    # endregion

    # region Manejo de curvas de proyección

    def add_projection_curve(self, curve: Curve, associated_index: FinancialIndex):
        """Agregar curva de proyección

        Agrega una curva de proyección

        :param curve: Curva
        :type curve: Curve
        :param associated_index: Indice asociado
        :param associated_index: Index
        """
        self.__projection_curves[associated_index.name] = curve

    def get_projection_curve(self, associated_index: Index) -> Curve:
        """Obtener curva de proyección

        Obtiene una curva de proyección para el índice señalado

        :param associated_index: Índice asociado.
        :type associated_index: Index

        :return: Curva de proyección
        """

        if str(associated_index) in self.__projection_curves.keys():
            return self.__projection_curves[associated_index.name]
        else:
            message = f'Could not find a projection curve associated to index {associated_index}'
            raise DatasetException(message)

    # endregion


class FxDataSet:
    """Set de Datos de Pares de Moneda

    Clase especializada en el almacenamiento y tratamiento de pares de monedas.

    :param process_date: Fecha de Proceso.
    :type process_date: date
    """
    def __init__(self, process_date: date):
        self.process_date = process_date

        self.__fx_rates = {}
        self.__fx_volatility = {}

    # region Funciones

    def add_fx_rate(self, fx_pair: FxPair, fx_mid: float, discounted_fx: float = None):
        """Agregar tipo de cambio

        Agrega un objeto tipo de cambio al dataset.

        :param fx_pair: Par de monedas.
        :type fx_pair: FxPair
        :param fx_mid: Valor mid.
        :type fx_mid: float
        :param discounted_fx: Valor descontado (Opcional)
        :type discounted_fx: float
        """
        self.__fx_rates[fx_pair] = {'rate': fx_mid, 'discounted': discounted_fx, 'projections': {}}

    def contains(self, fx_pair: FxPair):
        """Verificar contención de fx pair

        Verifica si el dataset contiene un par de moneda especifico

        :param fx_pair: Par de moneda
        :type fx_pair: FxPair

        :return: bool
        """
        return fx_pair in self.__fx_rates

    def contains_projection(self, fx_pair: FxPair, projection_date: date):
        if self.contains(fx_pair=fx_pair):
            return projection_date in self.__fx_rates[fx_pair]['projections']
        else:
            return False

    def contains_discounted(self, fx_pair: FxPair):
        """Verificar si contiene Spot Descontado

        Verifica si el dataset contienen la moneda y el spot descontado respectivo

        :param fx_pair: Par de moneda
        :type fx_pair: FxPair

        :return: bool
        """
        if fx_pair in self.__fx_rates:
            return self.__fx_rates[fx_pair]['discounted'] is not None
        else:
            return False

    def set_fx_rate(self, fx_pair: FxPair, fx_rate: float):
        """Asigna nuevo valor a tasa de cambio

        Asigna nuevo valor a tasa de cambio

        :param fx_pair: Par de monedas.
        :type fx_pair: FxPair
        :param fx_rate: Valor mid.
        :type fx_rate: float
        """
        if fx_pair in self.__fx_rates:
            self.__fx_rates[fx_pair]['rate'] = fx_rate
        else:
            raise DatasetException(f'Could not find FxPair {fx_pair}')

    def get_fx_rate(self, fx_pair: FxPair):
        """Obtener valor de tasa de cambio

        Obtiene el valor almacenado de tasa de cambio

        :param fx_pair: Par de monedas.
        :type fx_pair: FxPair
        """
        if fx_pair.has_eq_currency():
            return 1
        elif fx_pair in self.__fx_rates:
            return self.__fx_rates[fx_pair]['rate']
        else:
            raise DatasetException(f'Could not find FxPair {fx_pair}')

    def set_discounted_fx_rate(self, fx_pair: FxPair, discounted_fx_rate: float):
        """Asigna nuevo valor a tasa de cambio

        Asigna nuevo valor a tasa de cambio

        :param fx_pair: Par de monedas.
        :type fx_pair: FxPair
        :param discounted_fx_rate: Valor descontado.
        :type discounted_fx_rate: float
        """
        if fx_pair in self.__fx_rates:
            self.__fx_rates[fx_pair]['discounted'] = discounted_fx_rate
        else:
            raise DatasetException(f'Could not find FxPair {fx_pair}')

    def get_discounted_fx_rate(self, fx_pair: FxPair):
        """Obtener valor descontado de tasa de cambio

        Obtiene el valor almacenado de tasa de cambio descontada

        :param fx_pair: Par de monedas.
        :type fx_pair: FxPair
        """
        if fx_pair.has_eq_currency():
            return 1
        if fx_pair in self.__fx_rates:
            return self.__fx_rates[fx_pair]['discounted']
        else:
            raise DatasetException(f'Could not find FxPair {fx_pair}')

    def set_projection(self, fx_pair: FxPair, projection_date: date, projected_rate: float):
        """Asigna nuevo valor a tasa de cambio

        Asigna nuevo valor a tasa de cambio

        :param fx_pair: Par de monedas.
        :type fx_pair: FxPair
        :param projection_date: Fecha de proyección
        :type projection_date: date
        :param projected_rate: Tasa Proyectada.
        :type projected_rate: float
        """
        if fx_pair in self.__fx_rates:
            self.__fx_rates[fx_pair]['projections'][projection_date] = projected_rate
        else:
            raise DatasetException(f'Could not find FxPair {fx_pair}')

    def get_projection(self, fx_pair: FxPair, projection_date: date):
        """Asigna nuevo valor a tasa de cambio

        Asigna nuevo valor a tasa de cambio

        :param fx_pair: Par de monedas.
        :type fx_pair: FxPair
        :param projection_date: Fecha de proyección
        :type projection_date: date
        """
        if self.contains_projection(fx_pair, projection_date):
            return self.__fx_rates[fx_pair]['projections'][projection_date]
        else:
            raise DatasetException(f'Could not find FxPair {fx_pair}')

    # endregion


class IndexDataSet:
    """Set de Datos de Índices Financieros

    Clase especializada en el almacenamiento y tratamiento de índices financieros.
    """
    def __init__(self):
        self.__indexes = {}
        self.__idx_volatility = {}

    # region Manejo de índices

    def set_index_data(self, index, historical_data):
        """Asignar data de índices

        Asigna la información histórica correspondiente a un índice.

        :param index: Indice.
        :type index: Index
        :param historical_data: Data histórica.
        :type historical_data: dict
        """
        self.__indexes[index] = historical_data

    def get_index_data(self, index: FinancialIndex, idx_date: date):
        """Obtener data de índices

        Obtiene la data de un índice a una fecha especificada.

        :param index: Indice.
        :type index: Index
        :param idx_date: Fecha requerida.
        :type idx_date: date

        :raises DatasetException: En caso no se cuente con la información requerida.

        :return: Información del índice a la fecha especificada.
        """
        if index in self.__indexes.keys():
            idx_data = self.__indexes[index]
            if idx_date in idx_data:
                return self.__indexes[index][idx_date]
            else:
                dates = [t for t in idx_data.keys() if t < idx_date]
                if len(dates) == 0:
                    raise DatasetException(f'Could not find data for {index} in date {idx_date}')
                dates.sort(reverse=True)
                idx_date = dates[0]
                idx_value = self.__indexes[index][idx_date]
                self.__indexes[index][idx_date] = idx_value
                return self.__indexes[index][idx_date]
        else:
            raise DatasetException(f'Could not find historical data for index {index}')

    def get_index_data_between(self, index: FinancialIndex, start_date: date, end_date: date) -> dict:
        """Obtener data de índices entre las fechas

        :param index: Indice.
        :type index: FinancialIndex
        :param start_date: Fecha de inicio.
        :type start_date: date
        :param end_date: Fecha de fin.
        :type end_date: date

        :return: Información entre las fechas designadas
        """
        if index in self.__indexes.keys():
            idx_data = self.__indexes[index]
            selected_data = dict(filter(lambda x: start_date <= x[0] <= end_date, idx_data.items()))
            selected_data = dict(sorted(selected_data.items()))
            # if len(selected_data.keys()) < 1:
            #    raise DatasetException(f'Could not find data for {index} between {start_date} and {end_date}')
            return selected_data
        else:
            raise DatasetException(f'Could not find historical data for index {index}')

    # endregion


class DataSet:
    """
    Clase dedicada al almacenamiento de información de mercado.

    :param process_date: Fecha de la información de mercado.
    :type process_date: date
    :param curve_dataset: (Opcional) Set de datos de Curvas.
    :type curve_dataset: CurveDataSet
    :param fx_dataset: (Opcional) Set de datos de Tasas de Cambio.
    :type fx_dataset: FxDataSet
    :param index_dataset: (Opcional) Set de datos de Índices Financieros.
    :type index_dataset: IndexDataSet
    """

    def __init__(self, process_date: date, curve_dataset: CurveDataSet, fx_dataset: FxDataSet,
                 index_dataset: IndexDataSet, calendar_dataset: CalendarDataSet = None):
        self.market_date = process_date
        self.__curve_dataset = curve_dataset  # Set de datos de curvas
        if calendar_dataset is None:
            calendar_dataset = CalendarDataSet()
        self.__calendar_dataset = calendar_dataset  # Set de datos de calendario
        self.__fx_dataset = fx_dataset  # Set de datos de tipos de cambio
        self.__index_dataset = index_dataset  # Set de datos de indices
        self.__default_valuation_currency = Currency.CLP  # Variable privada de configuración para valorización.
        self.__discounted_spot = True

    # region Funciones de configuración

    def set_default_valuation_currency(self, valuation_currency):
        """Asigna la moneda default de valorización

        Asigna una moneda default para generar los calculos de valorización

        :param valuation_currency: Moneda de valorización.
        :type valuation_currency: Currency
        """
        self.__default_valuation_currency = valuation_currency

    def get_default_valuation_currency(self):
        """Obtener la moneda default de valorización

        Obtiene la moneda asignada como moneda default para generar los calculos de valorización
        """
        return self.__default_valuation_currency

    def set_curve_dataset(self, curve_dataset: CurveDataSet):
        """Asignar dataset de Curvas

        Asigna un dataset de curvas

        :param curve_dataset: dataset de curvas
        :type curve_dataset: CurveDataSet
        """
        curve_dataset.process_date = self.market_date
        self.__curve_dataset = curve_dataset

    def set_fx_dataset(self, fx_dataset: FxDataSet):
        """Asignar dataset de Tipos de Cambio

        Asigna un dataset de Tipos de Cambio

        :param fx_dataset: dataset de tipos de cambio
        :type fx_dataset: CurveDataSet
        """
        fx_dataset.process_date = self.market_date
        self.__fx_dataset = fx_dataset

    def set_index_dataset(self, index_dataset: IndexDataSet):
        """Asignar dataset de Índices

        Asigna un dataset de Índices

        :param index_dataset: dataset de Índices
        :type index_dataset: CurveDataSet
        """
        index_dataset.process_date = self.market_date
        self.__index_dataset = index_dataset

    # region Funciones de configuración

    def disable_discounted_spot(self):
        """
        Desactiva el uso de spot descontado.
        """
        self.__discounted_spot = False

    def enable_discounted_spot(self):
        """
        Activa el uso de spot descontado.
        """
        self.__discounted_spot = True

    # endregion

    # region Funciones de obtención de datos

    def get_fx_rate(self, fx_pair: FxPair):
        """Obtener tipo de cambio

        Obtiene tipo de cambio a la fecha del dataset.

        :param fx_pair: Nombre de la tasa de cambio.
        :type fx_pair: FxPair

        :raises DatasetException: En caso no encuentre datos.

        :return: Tipo de Cambio
        """
        fx_rate = 1
        if fx_pair.primary_currency == fx_pair.secondary_currency:
            return fx_rate
        elif self.__fx_dataset.contains(fx_pair):
            if not self.__discounted_spot:
                return self.__fx_dataset.get_fx_rate(fx_pair=fx_pair)
            else:
                if self.__fx_dataset.contains_discounted(fx_pair=fx_pair):
                    return self.__fx_dataset.get_discounted_fx_rate(fx_pair=fx_pair)

                # Paso 1: Se obtienen las curvas de las monedas asociadas al fx pair
                primary_curve = self.__curve_dataset.get_discount_curve(associated_currency=fx_pair.primary_currency)
                sec_curve = self.__curve_dataset.get_discount_curve(associated_currency=fx_pair.secondary_currency)

                calendar = self.__calendar_dataset.get_calendar(fx_pair.calendar_locations)

                end_date = calendar.offset_date(start_date=self.market_date, n_periods=fx_pair.discount_days,
                                                period=Period.DAY, convention=BusinessDay.FOLLOWING)

                t = (end_date - self.market_date).days

                # Paso 2: Se interpola ambas curvas a la cantidad de días de descuento indicadas en el fx pair
                primary_factor = primary_curve.get_discount_factor(t)
                secondary_factor = sec_curve.get_discount_factor(t)

                # Paso 3: Descontamos el Spot
                fx_rate = self.__fx_dataset.get_fx_rate(fx_pair=fx_pair)
                discounted_spot = fx_rate * secondary_factor / primary_factor

                self.__fx_dataset.set_discounted_fx_rate(fx_pair=fx_pair, discounted_fx_rate=discounted_spot)

                return discounted_spot
        elif self.__fx_dataset.contains(fx_pair.inverse_pair()):
            # Busca la inversa de la moneda
            fx_rate = 1 / self.get_fx_rate(fx_pair=fx_pair.inverse_pair())
        else:
            pivot_currency = Currency.USD
            if fx_pair.primary_currency == Currency.USD or fx_pair.secondary_currency == Currency.USD:
                pivot_currency = Currency.CLP

            # Busca el arbitraje con moneda pivote

            active_pair = FxPair.generate(f'{fx_pair.primary_currency}{pivot_currency}')
            passive_pair = FxPair.generate(f'{pivot_currency}{fx_pair.secondary_currency}')

            passive_fx = 1
            if self.__fx_dataset.contains(active_pair) or self.__fx_dataset.contains(active_pair.inverse_pair()):
                active_fx = self.get_fx_rate(fx_pair=active_pair) if self.__fx_dataset.contains(active_pair) \
                            else 1/self.get_fx_rate(fx_pair=active_pair.inverse_pair())
                if self.__fx_dataset.contains(passive_pair) or self.__fx_dataset.contains(passive_pair.inverse_pair()):
                    passive_fx = self.get_fx_rate(fx_pair=passive_pair) if self.__fx_dataset.contains(passive_pair) \
                                 else 1/self.get_fx_rate(fx_pair=passive_pair.inverse_pair())
            else:
                raise DatasetException(f'Could not find information for FxPair {fx_pair}')

            fx_rate = active_fx * passive_fx

        discounted_fx = fx_rate if self.__discounted_spot else None
        self.__fx_dataset.add_fx_rate(fx_pair=fx_pair, fx_mid=fx_rate, discounted_fx=discounted_fx)

        return fx_rate

    def get_fx_forward_rate(self, fx_pair: FxPair, forward_date: date):
        r"""Obtener tipo de cambio forward

        Obtiene el tipo de cambio a una fecha futura, utilizando la siguiente fórmula:

        .. math::

           S_t^{C_1-C_2} = S_0^{C_1-C_2}\cdot \frac{P_0^{C_1}}{P_0^{C_2}}

        :param fx_pair: Tasa de Cambio.
        :type fx_pair: FxPair
        :param forward_date: Fecha Futura.
        :type forward_date: date

        :raises DatasetException: En caso no se pueda realizar el cálculo solicitado.

        :return: Tipo de cambio a fecha futura
        """
        if fx_pair.has_eq_currency():
            return 1
        try:
            # Paso 0: Verifica si la información existe en memoria
            if self.__fx_dataset.contains_projection(fx_pair=fx_pair, projection_date=forward_date):
                return self.__fx_dataset.get_projection(fx_pair=fx_pair, projection_date=forward_date)
            # Paso 1: Se obtiene el spot asociado al fx pair
            spot = self.get_fx_rate(fx_pair=fx_pair)
            # Paso 2: Se obtienen las curvas de las monedas asociadas al fx pair
            primary_curve = self.__curve_dataset.get_discount_curve(associated_currency=fx_pair.primary_currency)
            secondary_curve = self.__curve_dataset.get_discount_curve(associated_currency=fx_pair.secondary_currency)
            # Paso 3: Interpolamos al plazo estipulado
            t = (forward_date - self.market_date).days
            primary_factor = primary_curve.get_discount_factor(t)
            secondary_factor = secondary_curve.get_discount_factor(t)
            # Paso 4: calculamos spot forward
            fwd = spot * primary_factor / secondary_factor
            # Paso 5: Guardar resultado en memoria
            self.__fx_dataset.set_projection(fx_pair=fx_pair, projection_date=forward_date, projected_rate=fwd)
            return fwd
        except Exception:
            raise DatasetException(f'Could not calculate forward price at date {forward_date} for FxPair {fx_pair}')

    def get_discount_curve(self, associated_currency: Currency, associated_collateral: Currency = None) -> Curve:
        """Obtener curva de descuento

        Obtiene una curva de descuento de acuerdo la moneda y colateral asociada. En caso la curva no exista se
        intentará construir una curva sintética tomando como base la moneda default de las curvas. Si no es posible
        obtener un sintético se levanta una excepción.

        :param associated_currency: Moneda asociada.
        :type associated_currency: Currency.
        :param associated_collateral: Colateral asociado.
        :type associated_collateral: Currency

        :raises DatasetException: En caso la curva no pueda ser obtenida

        :return: Objeto Curve
        """
        return self.__curve_dataset.get_discount_curve(associated_currency=associated_currency,
                                                       associated_collateral=associated_collateral)

    def get_projection_curve(self, associated_index: Index):
        """Obtener curva de proyección

        Obtiene una curva de proyección para el índice señalado

        :param associated_index: Índice asociado.
        :type associated_index: Index

        :return: Curva de proyección
        """

        return self.__curve_dataset.get_projection_curve(associated_index=associated_index)

    def get_index_data(self, index: FinancialIndex, idx_date: date):
        """Obtener data de índices

        Obtiene la data de un índice a una fecha especificada.

        :param index: Indice.
        :type index: Index
        :param idx_date: Fecha requerida.
        :type idx_date: date

        :raises DatasetException: En caso no se cuente con la información requerida.

        :return: Información del índice a la fecha especificada.
        """
        return self.__index_dataset.get_index_data(index=index, idx_date=idx_date)

    def get_index_data_between(self, index: FinancialIndex, start_date: date, end_date: date):
        """Obtener data de índices entre las fechas

        :param index: Índice.
        :type index: FinancialIndex
        :param start_date: Fecha de inicio.
        :type start_date: date
        :param end_date: Fecha de fin.
        :type end_date: date

        :return: Información entre las fechas designadas
        """
        return self.__index_dataset.get_index_data_between(index=index, start_date=start_date, end_date=end_date)

    def get_calendar(self, localities: list):
        """Obtiene un calendario dada una lista de localidades

        :param localities: Listado de localidades
        :type localities: list

        :return: TradingCalendar
        """
        return self.__calendar_dataset.get_calendar(localities=localities)

    # endregion
