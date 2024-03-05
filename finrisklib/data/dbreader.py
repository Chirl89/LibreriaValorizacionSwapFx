"""
Este módulo se encuentra enfocado en estandarizar la obtención de datos desde los servidores productivos.
"""

import pandas as pd

from finrisklib.data._sql_querys_ import *
from finrisklib.finriskconfig import index_bbg_codes
from finrisklib.enums import Source
from finrisklib.enums import FinancialIndex
from finrisklib.enums import Currency
from finrisklib.enums import Locality
from finrisklib.market.dataset import CurveDataSet
from finrisklib.market.dataset import CalendarDataSet
from finrisklib.market.dataset import FxDataSet
from finrisklib.market.dataset import IndexDataSet
from finrisklib.market.dataset import DataSet
from finrisklib.instruments.flow import Cash
from finrisklib.instruments.instrument import Derivative
from finrisklib.exceptions import QueryException
from finrisklib.market.curve import Curve
from finrisklib.data.dataparser import DataParser
from finrisklib.data.dbconnection import SQLConn
from finrisklib.instruments.portfolio import Portfolio
from pandas.tseries.holiday import Holiday, nearest_workday
from pandas.tseries.holiday import USMartinLutherKingJr, USPresidentsDay, GoodFriday
from pandas.tseries.holiday import USMemorialDay, USLaborDay, USThanksgivingDay

from datetime import date
from dateutil.relativedelta import relativedelta


class DBReader:
    """Lector de base de datos

    Clase dedicada a la lectura de información desde las bases de datos.

    :param conn: Conexión a BD. (Default: B08)
    :type conn: SQLConn
    """

    def __init__(self, conn: SQLConn = SQLConn.get_b08_conn()):
        """Inicializador"""
        self.__B08conn = conn

    def __get_query_data(self, query_name: str, query: str, parameters: dict) -> pd.DataFrame:
        """Función privada de obtención de datos

        Maneja de manera general las solicitudes de datos

        :param query_name: Nombre de la query.
        :param query: Cadena de texto con query.
        :param parameters: Parámetros a ser utilizados.

        :return: Dataframe con información solicitada

        :raises: QueryException cuando no se retornan datos
        """
        formatted_query = query.format(**parameters)
        query_data = self.__B08conn.execute_query(query=formatted_query)

        row_number = len(query_data.index)
        if row_number == 0:
            message = f'Could not find data for {query_name} with parameters {parameters}.'
            raise QueryException(formatted_query, message)

        return query_data

    # region Ejecución de Queries

    def execute_query(self, query: str):
        """Ejecutar Query

        Ejecuta la query solicitada

        :param query: Query

        :return: Dataframe con datos de query ejecutada
        """
        return self.__B08conn.execute_query(query=query)

    # endregion

    # region Extracción de Curvas

    def get_curve_names(self, process_date: date, source: Source = Source.OFFICIAL) -> list:
        """Obtener nombre de curvas

        Obtiene una lista con los nombres de curvas disponibles.

        :param process_date: fecha de proceso.
        :type process_date: date
        :param source: Fuente de información (Default = OFFICIAL).
        :type source: Source

        :return: Lista con nombres de curvas.
        :raises QueryException: Cuando no se retorna valores con la query realizada.
        """

        if source == Source.OFFICIAL:
            query = OFFICIAL_CURVES_NAMES_QUERY
        elif source == Source.MUREX:
            query = MUREX_CURVES_NAMES_QUERY
        elif source == Source.SANDBOX:
            query = SANDBOX_CURVES_NAMES_QUERY
        else:
            raise QueryException('get_curve_names', f'Unrecognized source {source} requested')

        query_data = self.__get_query_data(query_name='get_curve_names', query=query,
                                           parameters={'process_date': process_date.strftime('%Y%m%d')})
        curve_names = query_data.iloc[:, 0].tolist()
        return curve_names

    def get_single_curve_data(self, curve_name: str, process_date: date, source: Source = Source.OFFICIAL) -> Curve:
        """Obtener Curva

        Obtiene un objeto curva en específico.

        :param curve_name: Nombre de la curva.
        :type curve_name: str
        :param process_date: fecha de proceso.
        :type process_date: date
        :param source: Fuente de información (Default = OFFICIAL).
        :type source: Source


        :return: Objeto Curva con la información del servidor.
        :raises QueryException: Cuando no se retorna valores con la query realizada.
        """

        if source == Source.OFFICIAL:
            query = OFFICIAL_SINGLE_CURVE_QUERY
        elif source == Source.MUREX:
            query = MUREX_SINGLE_CURVE_QUERY
        elif source == Source.SANDBOX:
            query = SANDBOX_SINGLE_CURVE_QUERY
        else:
            raise QueryException('get_single_curve', f'Unrecognized source {source} requested')

        curve_data = self.__get_query_data(query_name='get_single_curve', query=query,
                                           parameters={'process_date': process_date.strftime('%Y%m%d'),
                                                       'curve_name': curve_name})

        curve_obj = Curve(curve_name=curve_name, process_date=process_date, tenors=curve_data.iloc[:, 2].tolist(),
                          discount_factors=curve_data.iloc[:, 3].tolist())

        return curve_obj

    def get_curve_dataset(self, process_date: date, source: Source = Source.OFFICIAL) -> CurveDataSet:
        """Obtener todas las Curvas

        Obtiene un diccionario con todas las curvas disponibles a una fecha determinada.

        :param process_date: Fecha de las curvas.
        :type process_date: date.
        :param source: Fuente de información (Default = OFFICIAL).
        :type source: Source

        :return: Diccionario con objetos Curva con la información del servidor.

        :raises QueryException: Cuando no se retorna valores con la query realizada.
        """

        if source == Source.OFFICIAL:
            query = OFFICIAL_CURVES_QUERY
            default_collateral_currency = Currency.CLP
        elif source == Source.MUREX:
            query = MUREX_CURVES_QUERY
            default_collateral_currency = Currency.USD
        elif source == Source.SANDBOX:
            query = SANDBOX_CURVES_QUERY
            default_collateral_currency = Currency.USD
        else:
            raise QueryException('get_curves', f'Unrecognized source {source} requested')

        curve_data = self.__get_query_data(query_name='get_curve_dataset', query=query,
                                           parameters={'process_date': process_date.strftime('%Y%m%d')})

        curve_dataset = DataParser.parse_curve_data(curve_data=curve_data)
        curve_dataset.set_default_collateral_currency(default_collateral_currency)
        return curve_dataset

    # endregion

    # region Extracción de tipos de cambio

    def get_fx_rate(self, primary_currency: str, secondary_currency: str, process_date: date,
                    source: Source = Source.MUREX) -> float:
        """Obtener tasa de cambio

        Retorna el tipo de cambio solicitado para la fecha especificada

        :param primary_currency: Nombre de la moneda primaria.
        :type primary_currency: str.
        :param secondary_currency: Nombre de la moneda secundaria.
        :type secondary_currency: str.
        :param process_date: Fecha de proceso.
        :type process_date: date.
        :param source: Fuente de Información (Default = MUREX).
        :type source: Source

        :return: Valor de la moneda
        """
        if source == Source.OFFICIAL:
            if primary_currency == 'CLP':
                primary_currency = 'CL'
            elif primary_currency == 'USD':
                primary_currency = 'US'
            elif primary_currency == 'BRL':
                primary_currency = 'BR'
            else:
                raise QueryException('get_fx_rate', f'Unrecognized primary currency {primary_currency} '
                                                    f'for Official Source')
            query = OFFICIAL_FX_QUERY
        elif source == Source.MUREX:
            query = MUREX_FX_QUERY
        elif source == Source.SANDBOX:
            query = SANDBOX_FX_QUERY
        else:
            raise QueryException('get_fx_rate', f'Unrecognized source {source} requested')

        fx_data = self.__get_query_data(query_name='get_fx_rate', query=query,
                                        parameters={'primary_currency': primary_currency,
                                                    'secondary_currency': secondary_currency,
                                                    'process_date': process_date.strftime('%Y%m%d')})

        value = float(fx_data.values)

        return value

    def get_fx_dataset(self, process_date: date, source: Source = Source.MUREX) -> FxDataSet:
        """Obtener todas las tasas de cambio

        Retorna los tipos de cambio para la fecha especificada

        :param process_date: Fecha de proceso.
        :type process_date: date
        :param source: Fuente de Información (Default = MUREX).
        :type source: Source

        :return: Dataset de tipo de cambio
        """

        if source == Source.OFFICIAL:
            fx_data = self.__get_query_data(query_name='get_fx_dataset', query=OFFICIAL_FX_RATES_QUERY,
                                            parameters={'process_date': process_date.strftime('%Y%m%d')})
        elif source == Source.MUREX:
            fx_data = self.__get_query_data(query_name='get_fx_dataset', query=MUREX_FX_RATES_QUERY,
                                            parameters={'process_date': process_date.strftime('%Y%m%d')})
        elif source == Source.SANDBOX:
            fx_data = self.__get_query_data(query_name='get_fx_dataset', query=SANDBOX_FX_RATES_QUERY,
                                            parameters={'process_date': process_date.strftime('%Y%m%d')})
        else:
            raise QueryException('get_fx_dataset', f'Unrecognized source {source} requested')

        fx_dataset = DataParser.parse_fx_data(fx_data=fx_data)

        return fx_dataset

    # endregion

    # region Extracción de datos Indices

    def get_index_rate(self, index: FinancialIndex, process_date: date) -> float:
        """Obtener valor de Índice Financiero

        Obtiene el valor de un índice financiero a una fecha determinada

        :param index: Índice Financiero.
        :type index: FinancialIndex
        :param process_date: fecha de proceso.
        :type process_date: date

        :return: valor del índice.

        :raise QueryException: En caso no se encuentre data o el índice no se reconozca.
        """
        if index in index_bbg_codes.keys():
            bbg_code = index_bbg_codes[index]
            index_value = self.__get_query_data(query_name='get_index_data', query=INDEX_DATA_QUERY,
                                                parameters={'bbg_code': bbg_code,
                                                            'process_date': process_date.strftime('%Y%m%d')})
            value = float(index_value.values)

            return value
        else:
            raise QueryException('get_index_data', f'Unrecognized Financial Index {index}')

    def get_single_index_dataset(self, index: FinancialIndex, start_date: date, end_date: date) -> IndexDataSet:
        """Obtener Valores Históricos de Índice Financiero

        Obtiene el valor histórico de un índice financiero entre las fechas determinadas

        :param index: Índice Financiero.
        :type index: FinancialIndex
        :param start_date: fecha de inicio.
        :type start_date: date
        :param end_date: fecha de término.
        :type end_date: date

        :return: IndexDataSet con datos solicitados

        :raise QueryException: En caso no se encuentre data o el índice no se reconozca.
        """
        if index in index_bbg_codes.keys():
            bbg_code = index_bbg_codes[index]
            index_values = self.__get_query_data(query_name='get_index_historical_data',
                                                 query=INDEX_HISTORICAL_DATA_QUERY,
                                                 parameters={'bbg_code': bbg_code,
                                                             'start_date': start_date.strftime('%Y%m%d'),
                                                             'end_date': end_date.strftime('%Y%m%d')})

            return DataParser.parse_index_data(index_data=index_values)
        else:
            raise QueryException('get_index_data', f'Unrecognized Financial Index {index}')

    def get_index_dataset(self, start_date: date, end_date: date) -> IndexDataSet:
        """Obtener Valores Históricos de todos los Índices Financiero

        Obtiene el valor histórico de todos los índices financieros entre las fechas determinadas

        :param start_date: Fecha de inicio.
        :type start_date: date.
        :param end_date: fecha de término.
        :type end_date: date.

        :return: IndexDataSet con datos solicitados

        :raise QueryException: En caso no se encuentre data o el índice no se reconozca.
        """
        index_values = self.__get_query_data(query_name='get_all_index_historical_data',
                                             query=ALL_INDEX_HISTORICAL_DATA_QUERY,
                                             parameters={'start_date': start_date.strftime('%Y%m%d'),
                                                         'end_date': end_date.strftime('%Y%m%d')})

        return DataParser.parse_index_data(index_data=index_values)

    # endregion

    # region Extracción de Calendarios

    def get_calendar_dataset(self) -> CalendarDataSet:
        """Obtener Dataset de Calendarios

        Obtiene un dataset de Calendarios con los calendarios default
        """

        calendar_data = {Locality.CHL: {'rules': [Holiday('AñoNuevo', month=1, day=1),  # ley 2977
                                                  GoodFriday,  # ley 2977
                                                  Holiday('DiaDelTrabajo', month=5, day=1),  # ley 19973
                                                  Holiday('GloriasNavales', month=5, day=21),  # ley 2977
                                                  Holiday('SanPedroSanPablo', month=6, day=29),  # ley 2977
                                                  Holiday('VirgenDelCarmen', month=7, day=16),  # Ley 20148
                                                  Holiday('AsuncionVirgen', month=8, day=15),  # ley 2977
                                                  Holiday('IndependenciaNacional', month=9, day=18),  # ley 2977
                                                  Holiday('GloriasDelEjercito', month=9, day=19),  # ley 2977
                                                  Holiday('EncuentroDosMundos', month=10, day=9),
                                                  Holiday('DiaIglesiasEvangélicas', month=10, day=31),
                                                  Holiday('TodosLosSantos', month=11, day=1),  # ley 2977
                                                  Holiday('InmaculadaConcepción', month=12, day=8),  # ley 2977
                                                  Holiday('Navidad', month=12, day=25),  # ley 2977
                                                  Holiday('FinAño', month=12, day=31)],
                                        'holidays': []},
                         Locality.USA: {'rules': [USMartinLutherKingJr, USPresidentsDay, GoodFriday,
                                                  USMemorialDay, USLaborDay, USThanksgivingDay,
                                                  Holiday('NewYearsDay', month=1, day=1, observance=nearest_workday),
                                                  Holiday('USIndependenceDay', month=7, day=4,
                                                          observance=nearest_workday),
                                                  Holiday('VeteransDay', month=11, day=11),
                                                  Holiday('Christmas', month=12, day=25, observance=nearest_workday)],
                                        'holidays': []}}

        calendar_dataset = CalendarDataSet()

        for locality in calendar_data:
            calendar_dataset.add_calendar(locality=locality,
                                          rules=calendar_data[locality]['rules'],
                                          holidays=calendar_data[locality]['holidays'])

        return calendar_dataset

    # endregion

    # region Extracción de dataset

    def get_dataset(self, process_date: date, source: Source = Source.OFFICIAL) -> DataSet:
        """Obtener Dataset

        Obtiene la información de mercado provista en los distintos archivos.

        :param process_date: Fecha del dataset.
        :type process_date: date.
        :param source: Fuente (Default: OFFICIAL)
        :type source: Source

        :return: Objeto Dataset.
        """

        curve_dataset = self.get_curve_dataset(process_date=process_date, source=source)
        fx_dataset = self.get_fx_dataset(process_date=process_date, source=source)
        index_dataset = self.get_index_dataset(start_date=process_date - relativedelta(years=5),
                                               end_date=process_date)

        calendar_dataset = self.get_calendar_dataset()

        dataset = DataSet(process_date=process_date,
                          curve_dataset=curve_dataset,
                          fx_dataset=fx_dataset,
                          index_dataset=index_dataset,
                          calendar_dataset=calendar_dataset)
        return dataset

    # endregion

    # region Obtención datos de Operaciones

    def get_operation(self, id_number: int, process_date: date) -> Derivative:
        """Obtener operación

        Obtiene una operación desde la base de datos a partir del número de operación y la fecha de proceso

        :param id_number: Número de operación.
        :type id_number: int
        :param process_date: Fecha de proceso.
        :type process_date: date

        :return: Derivative
        """
        operation_data = self.__get_query_data(query_name='get_operation_data', query=OPERATION_DATA_QUERY,
                                               parameters={'process_date': process_date.strftime('%Y%m%d'),
                                                           'id_number': id_number})

        return DataParser.parse_operation_data(operation_data=operation_data)

    def get_grf_fwd_operation(self, id_number: int, process_date: date) -> Derivative:
        """Obtener operación forward desde la interfaz GRF

        Obtiene una operación desde la base de datos a partir del número de operación y la fecha de proceso

        :param id_number: Número de operación.
        :type id_number: int
        :param process_date: Fecha de proceso.
        :type process_date: date

        :return: Derivative
        """
        operation_data = self.__get_query_data(query_name='get_grf_fwd_operation', query=GRF_FWD_OPERATION_DATA_QUERY,
                                               parameters={'process_date': process_date.strftime('%Y%m%d'),
                                                           'id_number': id_number})

        compensation_currency = self.__get_query_data(query_name='get_grf_fwd_operation',
                                                      query=GRF_COMPENSATION_CURRENCY,
                                                      parameters={'process_date': process_date.strftime('%Y%m%d')})

        return DataParser.parse_grf_fwd_operation_data(operation_data=operation_data,
                                                       compensation_currency=compensation_currency)

    def get_official_mtm(self, id_number: int, process_date) -> Cash:
        """Obtener Mark to Market Oficial

        Obtiene el Mark to Market oficial de una operación

        :param id_number: Número de operación.
        :type id_number: int
        :param process_date: Fecha de proceso.
        :type process_date: date

        :return: Cash
        """
        mtm_data = self.__get_query_data(query_name='get_official_mtm', query=OPERATION_MTM_QUERY,
                                         parameters={'process_date': process_date.strftime('%Y%m%d'),
                                                     'id_number': id_number})

        mtm = Cash(amount=mtm_data.iloc[0]['mtm'], currency=Currency.CLP)

        return mtm

    # endregion

    # region Obtención de Portafolios

    def get_forward_portfolio(self, process_date: date, source: Source = Source.OFFICIAL) -> Portfolio:
        """Obtener portafolio forward

        Obtiene todos los forwards de la cartera

        :param process_date: Fecha de Proceso.
        :type process_date: date
        :param source: Fuente de Información (Default: Official)
        :type source: Source

        :return: Portfolio
        """
        if source == Source.OFFICIAL:
            portfolio_data = self.__get_query_data(query_name='get_forward_portfolio', query=FORWARD_DATA_QUERY,
                                                   parameters={'process_date': process_date.strftime('%Y%m%d')})
            return DataParser.parse_portfolio_data(portfolio_data=portfolio_data)
        else:
            portfolio_data = self.__get_query_data(query_name='get_grf_forward_portfolio', query=GRF_FORWARD_QUERY,
                                                   parameters={'process_date': process_date.strftime('%Y%m%d')})

            compensation_currency = self.__get_query_data(query_name='get_grf_fwd_operation',
                                                          query=GRF_COMPENSATION_CURRENCY,
                                                          parameters={'process_date': process_date.strftime('%Y%m%d')})

            return DataParser.parse_grf_fwd_portfolio_data(portfolio_data=portfolio_data,
                                                           compensation_currency=compensation_currency)

    def get_swap_portfolio(self, process_date: date, source: Source = Source.OFFICIAL) -> Portfolio:
        """Obtener portafolio swap

        Obtiene todos los swaps de la cartera

        :param process_date: Fecha de Proceso.
        :type process_date: date
        :param source: Fuente de Información (Default: Official)
        :type source: Source

        :return: Portfolio
        """
        if source == Source.OFFICIAL:
            portfolio_data = self.__get_query_data(query_name='get_swap_portfolio', query=SWAP_DATA_QUERY,
                                                   parameters={'process_date': process_date.strftime('%Y%m%d')})

            return DataParser.parse_portfolio_data(portfolio_data=portfolio_data)
        else:
            portfolio_data = self.__get_query_data(query_name='get_swap_portfolio', query=GRF_SWAP_QUERY,
                                                   parameters={'process_date': process_date.strftime('%Y%m%d')})

            return DataParser.parse_grf_swap_portfolio_data(portfolio_data=portfolio_data)

    def get_portfolio(self, process_date: date, source: Source = Source.OFFICIAL) -> Portfolio:
        """Obtener el portafolio completo

        Obtiene todos los productos de la cartera

        :param process_date: Fecha de Proceso.
        :type process_date: date
        :param source: Fuente de Información (Default: Official)
        :type source: Source

        :return: Portfolio
        """
        if source == Source.OFFICIAL:
            portfolio_data = self.__get_query_data(query_name='get_portfolio', query=DERIVADOS_DATA_QUERY,
                                                   parameters={'process_date': process_date.strftime('%Y%m%d')})

            return DataParser.parse_portfolio_data(portfolio_data=portfolio_data)
        else:
            fwd_portfolio = self.get_forward_portfolio(process_date=process_date, source=source)
            swap_portfolio = self.get_swap_portfolio(process_date=process_date, source=source)
            fwd_portfolio.merge(other_portfolio=swap_portfolio)
            return fwd_portfolio

    # endregion

    # region Murex Swap

    def get_grf_swap_operation(self, id_number: int, process_date: date) -> Derivative:
        """Obtener operación Swap desde la interfaz GRF

        Obtiene una operación desde la base de datos a partir del número de operación y la fecha de proceso

        :param id_number: Número de operación.
        :type id_number: int
        :param process_date: Fecha de proceso.
        :type process_date: date

        :return: Derivative
        """
        operation_data = self.__get_query_data(query_name='get_grf_swap_operation', query=SWAP_OPERATION_DATA_QUERY,
                                               parameters={'process_date': process_date.strftime('%Y%m%d'),
                                                           'id_number': id_number})

        return DataParser.parse_grf_swap_operation_data(operation_data=operation_data)

    # endregion
    