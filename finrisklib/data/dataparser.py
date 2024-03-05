"""
Este módulo está dedicado a la conversión de datos con formatos establecidos a objetos propios de la librería
financiera.
"""

import pandas as pd
import sys
from finrisklib.finriskconfig import index_codes
from finrisklib.finriskconfig import curve_config
from finrisklib.finriskconfig import csa_clients
from finrisklib.enums import CurveType
from finrisklib.enums import Currency
from finrisklib.enums import FinancialIndex
from finrisklib.enums import FinancialPosition
from finrisklib.enums import DayCount
from finrisklib.enums import Compounding
from finrisklib.exceptions import CurveException
from finrisklib.exceptions import IndexException
from finrisklib.instruments.instrument import Derivative
from finrisklib.instruments.flow import Cash
from finrisklib.instruments.forward import Forward
from finrisklib.instruments.swap import Coupon
from finrisklib.instruments.swap import Leg
from finrisklib.instruments.swap import Swap
from finrisklib.instruments.portfolio import Portfolio
from finrisklib.market.dataset import CurveDataSet
from finrisklib.market.dataset import FxDataSet
from finrisklib.market.dataset import IndexDataSet
from finrisklib.market.curve import Curve
from finrisklib.market.fxrate import FxPair
from finrisklib.market.index import Index
from datetime import date
from datetime import timedelta


class DataParser:
    """
    Clase estática dedicada a la conversión de datos (DataFrames) con estructuras definidas en objetos propios de la
    librería financiera
    """

    # region Convertir datos de Curvas

    @staticmethod
    def parse_curve_data(curve_data: pd.DataFrame) -> CurveDataSet:
        """ Convertir data de curvas

        Convierte un DataFrame con los datos

        .. list-table:: **Formato Tabla de Curvas**
           :widths: 25 25 25 25
           :header-rows: 1

           * - Fecha Proceso
             - Código Curva
             - Tenor
             - Factor de descuento
           * - 2022/01/03
             - CURVA_CLP_CL
             - 1
             - 0.998

        :param curve_data: Data de curvas
        :type curve_data: DataFrame

        :return: CurveDataSet
        """
        process_date = curve_data.iloc[:, 0].iloc[0].date()

        curve_dataset = CurveDataSet(process_date=process_date)

        curve_names = curve_data.iloc[:, 1].unique()

        for curve_name in curve_names:

            if curve_name.upper() in curve_config.keys():
                config_data = curve_config[curve_name.upper()]
            else:
                raise CurveException(curve_name=curve_name, message=f'Curve not recognized while reading data.')

            curve_type = config_data['type']

            current_curve_data = curve_data.loc[curve_data.iloc[:, 1] == curve_name]
            tenors = current_curve_data.iloc[:, 2].tolist()
            mid_factor = current_curve_data.iloc[:, 3].tolist()

            curve_obj = Curve(curve_name=curve_name, process_date=process_date, tenors=tenors,
                              discount_factors=mid_factor)

            if curve_type == CurveType.DISCOUNT:

                associated_currency = config_data['currency']
                associated_collateral = config_data['colateral']

                curve_dataset.add_discount_curve(curve=curve_obj, associated_currency=associated_currency,
                                                 associated_collateral=associated_collateral)
            elif curve_type == CurveType.PROJECTION:

                associated_index = config_data['index']
                curve_dataset.add_projection_curve(curve=curve_obj, associated_index=associated_index)

            elif curve_type == CurveType.DUAL:

                associated_currency = config_data['currency']
                associated_collateral = config_data['colateral']
                associated_index = config_data['index']

                curve_dataset.add_discount_curve(curve=curve_obj, associated_currency=associated_currency,
                                                 associated_collateral=associated_collateral)

                curve_dataset.add_projection_curve(curve=curve_obj, associated_index=associated_index)

                if associated_index == FinancialIndex.SOFR:

                    curve_dataset.add_projection_curve(curve=curve_obj, associated_index=FinancialIndex.TERM_SOFR1M)
                    curve_dataset.add_projection_curve(curve=curve_obj, associated_index=FinancialIndex.TERM_SOFR3M)
                    curve_dataset.add_projection_curve(curve=curve_obj, associated_index=FinancialIndex.TERM_SOFR6M)
                    curve_dataset.add_projection_curve(curve=curve_obj, associated_index=FinancialIndex.TERM_SOFR1Y)

        return curve_dataset

    # endregion

    # region Convertir datos de Tipo de Cambio

    @staticmethod
    def parse_fx_data(fx_data: pd.DataFrame) -> FxDataSet:
        """ Convertir data de tipos de cambio

        Convierte un DataFrame con los datos

        .. list-table:: **Formato Tabla de Tipo de Cambio**
           :widths: 25 25 25 25
           :header-rows: 1

           * - Fecha Proceso
             - Moneda Primaria
             - Moneda Secundaria
             - Tipo de Cambio
           * - 2022/01/03
             - USD
             - CLP
             - 850

        :param fx_data: Data de curvas
        :type fx_data: DataFrame

        :return: FxDataSet
        """
        process_date = fx_data.iloc[:, 0].iloc[0].date()

        fx_dataset = FxDataSet(process_date=process_date)

        for index, row in fx_data.iterrows():
            primary_currency = row.iloc[1]
            secondary_currency = row.iloc[2]

            fx_pair = FxPair.generate(primary_currency+secondary_currency)
            fx_mid = row.iloc[3]

            fx_dataset.add_fx_rate(fx_pair=fx_pair, fx_mid=fx_mid)

        return fx_dataset

    # endregion

    # region Convertir Datos de Índices

    @staticmethod
    def parse_index_data(index_data: pd.DataFrame) -> IndexDataSet:
        """ Convertir data de índices financieros

        Convierte un DataFrame con los datos

        .. list-table:: **Formato Tabla de Índices Financieros**
           :widths: 25 25 25
           :header-rows: 1

           * - Código Índice
             - Fecha Proceso
             - Valor
           * - ICP REAL
             - 2022/01/03
             - 17854.15

        :param index_data: Data de índices
        :type index_data: DataFrame

        :return: IndexDataSet
        """

        idx_dataset = IndexDataSet()

        idx_codes = index_data.iloc[:, 0].unique()

        for code in idx_codes:

            if code.upper() not in index_codes.keys():
                message = f'Could not find Financial Index for code {code}'
                raise IndexException(idx_name=code, message=message)

            idx = index_codes[code.upper()]

            idx_data = index_data.loc[index_data.iloc[:, 0] == code]

            dates = idx_data.iloc[:, 1].dt.date
            values = idx_data.iloc[:, 2]

            hist_data = dict(zip(dates, values))

            idx_dataset.set_index_data(index=idx, historical_data=hist_data)

        return idx_dataset

    # endregion

    # region Convertir Datos Operaciones Cartera Derivados

    @staticmethod
    def parse_portfolio_data(portfolio_data: pd.DataFrame) -> Portfolio:
        """ Convertir data de portafolio

        Convierte un dataframe con la estructura de cartera en un objeto Portfolio

        :param portfolio_data: Data de portfolio
        :type portfolio_data: DataFrame

        :return: Portfolio
        """
        operation_numbers = portfolio_data['numerooperacion'].unique()

        portfolio = Portfolio(portfolio_name='Portfolio')

        n = len(operation_numbers)
        i = 1

        for id_number in operation_numbers:

            operation_data = portfolio_data.loc[portfolio_data['numerooperacion'] == id_number]
            instrument = DataParser.parse_operation_data(operation_data=operation_data)
            portfolio.add_operation(id_number=id_number, instrument=instrument)

            sys.stdout.write('\r')
            sys.stdout.write(f'Reading {i} of  {n} - Progress: {((i/n)*100):.2f}%')
            sys.stdout.flush()
            i += 1

        return portfolio

    @staticmethod
    def parse_operation_data(operation_data: pd.DataFrame) -> Derivative:
        """ Convertir data de operación

        Convierte un dataframe con la estructura de la cartera en un objeto de instrumento.

        :param operation_data: Data de la operación
        :type operation_data: DataFrame

        :return: Derivative
        """

        operation_type = operation_data['tipoproducto'].iat[0]
        product_type = operation_data['ProductoOriginal'].iat[0]

        if operation_type.upper() == 'FORWARD':
            if product_type.upper() == 'SEGURO DE CAMBIO_NEM' or\
                    product_type.upper() == 'SEGURO DE INFLACIÓN_ENM':
                pass
            else:
                return DataParser.__parse_ndf(operation_data=operation_data)
        elif operation_type.upper() == 'SWAP':
            return DataParser.__parse_swap(operation_data=operation_data)
        else:
            pass

    #  region Forwards

    @staticmethod
    def __parse_ndf(operation_data: pd.DataFrame):
        """Método Privado de Conversión de NDF"""

        active_leg = operation_data.loc[operation_data['tipoflujo'] == 'ACT']
        passive_leg = operation_data.loc[operation_data['tipoflujo'] == 'PAS']

        cliente_id = active_leg.iloc[0]['cliente']

        associated_collateral = Currency.USD if cliente_id in csa_clients.keys() else Currency.CLP

        active_currency = Currency[active_leg.iloc[0]['moneda']]
        active_notional = Cash(amount=active_leg.iloc[0]['amortizacion'], currency=active_currency)

        passive_currency = Currency[passive_leg.iloc[0]['moneda']]
        passive_notional = Cash(amount=passive_leg.iloc[0]['amortizacion'], currency=passive_currency)

        start_date = active_leg.iloc[0]['fechainiciflujo'].to_pydatetime().date()
        end_date = active_leg.iloc[0]['fechavenciminetoflujo'].to_pydatetime().date()
        pay_date = active_leg.iloc[0]['fechapago'].to_pydatetime().date()

        pair = f'{active_currency}{passive_currency}'

        if pair == 'USDCLF' or pair == 'CLFUSD':
            fixing_date = active_leg.iloc[0]['fechafijacion'].to_pydatetime().date()
            payment_currency = Currency.USD
        elif pair == 'CLPCLF' or pair == 'CLFCLP':
            fixing_date = active_leg.iloc[0]['fechafijacion'].to_pydatetime().date()
            payment_currency = Currency.CLP
        else:
            fixing_date = active_leg.iloc[0]['fechavenciminetoflujo'].to_pydatetime().date()
            payment_currency = Currency.CLP

        return Forward(start_date=start_date, end_date=end_date, fixing_date=fixing_date, pay_date=pay_date,
                       active_notional=active_notional, passive_notional=passive_notional,
                       associated_collateral=associated_collateral, payment_currency=payment_currency)

    # endregion

    # region Swaps

    @staticmethod
    def __parse_swap(operation_data: pd.DataFrame):
        """Método Privado de conversión de Swap"""

        active_leg_data = operation_data.loc[operation_data['tipoflujo'] == 'ACT']
        passive_leg_data = operation_data.loc[operation_data['tipoflujo'] == 'PAS']

        cliente_id = active_leg_data.iloc[0]['cliente']

        associated_collateral = Currency.USD if str(cliente_id) in csa_clients.keys() else Currency.CLP

        active_leg = DataParser.__parse_leg(dataframe=active_leg_data, position=FinancialPosition.LONG,
                                            associated_collateral=associated_collateral)
        passive_leg = DataParser.__parse_leg(dataframe=passive_leg_data, position=FinancialPosition.SHORT,
                                             associated_collateral=associated_collateral)
        swap = Swap(active_leg=active_leg, passive_leg=passive_leg, associated_collateral=associated_collateral)

        return swap

    @staticmethod
    def __parse_leg(dataframe: pd.DataFrame, position: FinancialPosition, associated_collateral: Currency):
        """Método Privado de conversión de Legs"""
        leg = Leg(position=position, associated_collateral=associated_collateral)

        for index, row in dataframe.iterrows():
            coupon = DataParser.__parse_coupon(row=row, associated_collateral=associated_collateral)
            leg.add_coupon(coupon)

        return leg

    @staticmethod
    def __parse_coupon(row: pd.Series, associated_collateral):
        """Método Privado de conversión de Cupones"""

        rate_name = row['tasanombre'].replace(" ", "")
        rate_value = row['tasa'] / 100

        spread = row['spread']/100
        start_date = row['fechainiciflujo'].to_pydatetime().date()
        if start_date.weekday() == 5:
            start_date = start_date + timedelta(days=-1)
        elif start_date.weekday() == 6:
            start_date = start_date + timedelta(days=-2)

        end_date = row['fechavenciminetoflujo'].to_pydatetime().date()
        start_fixing_date = row['fechainiciflujo'].to_pydatetime().date()
        if start_fixing_date.weekday() == 5:
            start_fixing_date = start_fixing_date + timedelta(days=-1)
        elif start_fixing_date.weekday() == 6:
            start_fixing_date = start_fixing_date + timedelta(days=-2)

        end_fixing_date = row['fechavenciminetoflujo'].to_pydatetime().date()
        # if
        interest_payment_date = row['fechapago'].to_pydatetime().date()
        principal_payment_date = row['fechapago'].to_pydatetime().date()
        currency = Currency.from_str(row['moneda'])
        amortization = Cash(amount=row['amortizacion'], currency=currency)
        outstanding_notional = Cash(amount=row['saldoresidual'], currency=currency) + amortization
        conventions = row['basenombre']

        if rate_name.upper() == 'ICP':
            rate_enum = FinancialIndex.ICP_REAL if currency == Currency.CLF else FinancialIndex.ICP
        elif rate_name.upper() == 'TAB90':
            rate_enum = FinancialIndex.TABUF3M if currency == Currency.CLF else FinancialIndex.TAB3M
        elif rate_name.upper() == 'TAB180':
            rate_enum = FinancialIndex.TABUF6M if currency == Currency.CLF else FinancialIndex.TAB6M
        elif rate_name.upper() == 'TAB360':
            rate_enum = FinancialIndex.TABUF1Y if currency == Currency.CLF else FinancialIndex.TAB1Y
        else:
            rate_enum = index_codes[rate_name.upper()]  # Falta control de errores

        if conventions == 'YLD 30/360':
            day_count = DayCount.DC_30_360
            compounding = Compounding.YIELD
        elif conventions == 'LIN 30/360' or conventions == 'LIN 30/360 ISM':
            day_count = DayCount.DC_30_360
            compounding = Compounding.LINEAR
        elif conventions == 'LIN 30E/360':
            day_count = DayCount.DC_30E_360
            compounding = Compounding.LINEAR
        elif conventions == 'YLD ACT/365' or conventions == 'L ACT/ACT_A/365':
            day_count = DayCount.DC_ACT_365
            compounding = Compounding.YIELD
        elif conventions == 'YLD ACT/360':
            day_count = DayCount.DC_ACT_360
            compounding = Compounding.YIELD
        else:
            day_count = DayCount.DC_ACT_360
            compounding = Compounding.LINEAR

        rate = Index.generate(rate_enum, day_count, compounding)

        coupon = Coupon(associated_index=rate, reference_rate=rate_value, spread=spread,
                        start_date=start_date, end_date=end_date,
                        start_fixing_date=start_fixing_date,
                        end_fixing_date=end_fixing_date, interest_payment_date=interest_payment_date,
                        principal_payment_date=principal_payment_date, amortization=amortization,
                        outstanding_notional=outstanding_notional, associated_collateral=associated_collateral)
        return coupon

    # endregion

    # endregion

    # region Convertir Datos Operaciones Cartera GRF

    # region GRF Forward

    @staticmethod
    def parse_grf_fwd_operation_data(operation_data: pd.DataFrame, compensation_currency: pd.DataFrame) -> Derivative:
        """ Convertir data de operación forward desde interfaz GRF

        Convierte un dataframe con la estructura de la cartera en un objeto de instrumento.

        :param operation_data: Data de la operación
        :type operation_data: DataFrame
        :param compensation_currency: Moneda de Compensación
        :type compensation_currency: DataFrame

        :return: Derivative
        """
        return DataParser.__parse_grf_forward(operation_data=operation_data,
                                              compensation_currency=compensation_currency)

    @staticmethod
    def parse_grf_fwd_portfolio_data(portfolio_data: pd.DataFrame, compensation_currency: pd.DataFrame) -> Portfolio:
        """ Convertir data de portafolio

        Convierte un dataframe con la estructura de cartera en un objeto Portfolio

        :param portfolio_data: Data de portfolio
        :type portfolio_data: DataFrame
        :param compensation_currency: Moneda de compensación
        :type compensation_currency: DataFrame

        :return: Portfolio
        """
        operation_numbers = portfolio_data['Numero Operacion'].unique()

        portfolio = Portfolio(portfolio_name='Portfolio Fwd GRF')

        n = len(operation_numbers)
        i = 1

        for id_number in operation_numbers:
            operation_data = portfolio_data.loc[portfolio_data['Numero Operacion'] == id_number]

            instrument = DataParser.__parse_grf_forward(operation_data=operation_data,
                                                        compensation_currency=compensation_currency)

            portfolio.add_operation(id_number=id_number, instrument=instrument)

            sys.stdout.write('\r')
            sys.stdout.write(f'Reading {i} of  {n} - Progress: {((i / n) * 100):.2f}%')
            sys.stdout.flush()
            i += 1

        return portfolio

    @staticmethod
    def __parse_grf_forward(operation_data: pd.DataFrame, compensation_currency: pd.DataFrame):
        """Método Privado de Conversión de NDF"""

        active_leg = operation_data.loc[operation_data['Tipo Flujo'] == 'Act']
        passive_leg = operation_data.loc[operation_data['Tipo Flujo'] == 'Pas']

        typology = operation_data.iloc[0]['TYPOLOGY']
        # strategy = operation_data.iloc[0]['TP_STRTGY']

        cliente_id = active_leg.iloc[0]['Rut Cliente']
        gid = active_leg.iloc[0]['Numero Operacion']

        compensation_data = compensation_currency.loc[compensation_currency['Gid'] == gid]

        associated_collateral = Currency.USD if cliente_id in csa_clients.keys() else Currency.CLP

        active_currency = Currency[active_leg.iloc[0]['Moneda']]
        active_notional = Cash(amount=active_leg.iloc[0]['Saldo Residual'], currency=active_currency)

        passive_currency = Currency[passive_leg.iloc[0]['Moneda']]
        passive_notional = Cash(amount=passive_leg.iloc[0]['Saldo Residual'], currency=passive_currency)

        start_date = active_leg.iloc[0]['Fecha Inicio'].to_pydatetime().date()
        end_date = active_leg.iloc[0]['Fecha Vencimiento'].to_pydatetime().date()
        pay_date = active_leg.iloc[0]['Fecha Pago'].to_pydatetime().date()

        if typology == 'Cross Forward':
            fixing_date = active_leg.iloc[0]['Fecha Vencimiento'].to_pydatetime().date()
            payment_currency = Currency.CLP
        elif typology == 'Cross NDF':
            fixing_date = active_leg.iloc[0]['Fecha Vencimiento'].to_pydatetime().date()
            payment_currency = Currency.CLP
        elif typology == 'Cross NDF UF':
            fixing_date = active_leg.iloc[0]['Fecha Fijacion Indice'].to_pydatetime().date()
            payment_currency = Currency.USD
        elif typology == 'Forward':
            fixing_date = active_leg.iloc[0]['Fecha Pago'].to_pydatetime().date()
            payment_currency = Currency.CLP
        elif typology == 'Forward FX':
            fixing_date = active_leg.iloc[0]['Fecha Pago'].to_pydatetime().date()
            payment_currency = Currency.CLP
        elif typology == 'NDF':
            fixing_date = active_leg.iloc[0]['Fecha Vencimiento'].to_pydatetime().date()
            payment_currency = Currency.CLP
            if len(compensation_data) > 0:
                compensation_currency = compensation_data.iloc[0]['moneda_de_pago']
                if compensation_currency == 'USD':
                    payment_currency = Currency.USD
                else:
                    payment_currency = Currency.CLP
        elif typology == 'NDF FX':
            fixing_date = active_leg.iloc[0]['Fecha Vencimiento'].to_pydatetime().date()
            payment_currency = Currency.USD
        elif typology == 'NDF UF':
            fixing_date = active_leg.iloc[0]['Fecha Fijacion Indice'].to_pydatetime().date()
            payment_currency = Currency.CLP
        else:
            fixing_date = active_leg.iloc[0]['Fecha Vencimiento'].to_pydatetime().date()
            payment_currency = Currency.CLP

        return Forward(start_date=start_date, end_date=end_date, fixing_date=fixing_date, pay_date=pay_date,
                       active_notional=active_notional, passive_notional=passive_notional,
                       associated_collateral=associated_collateral, payment_currency=payment_currency)

    # endregion

    # region GRF Swaps

    @staticmethod
    def parse_grf_swap_operation_data(operation_data: pd.DataFrame) -> Derivative:
        """ Convertir data de operación forward desde interfaz GRF

        Convierte un dataframe con la estructura de la cartera en un objeto de instrumento.

        :param operation_data: Data de la operación
        :type operation_data: DataFrame

        :return: Derivative
        """
        return DataParser.__parse_grf_swap(operation_data=operation_data)

    @staticmethod
    def parse_grf_swap_portfolio_data(portfolio_data: pd.DataFrame) -> Portfolio:
        """ Convertir data de portafolio

        Convierte un dataframe con la estructura de cartera en un objeto Portfolio

        :param portfolio_data: Data de portfolio
        :type portfolio_data: DataFrame

        :return: Portfolio
        """
        operation_numbers = portfolio_data['GID'].unique()

        portfolio = Portfolio(portfolio_name='Portfolio Swap GRF')

        n = len(operation_numbers)
        i = 1

        for id_number in operation_numbers:
            operation_data = portfolio_data.loc[portfolio_data['GID'] == id_number]

            instrument = DataParser.__parse_grf_swap(operation_data=operation_data)

            portfolio.add_operation(id_number=id_number, instrument=instrument)

            sys.stdout.write('\r')
            sys.stdout.write(f'Reading {i} of  {n} - Progress: {((i / n) * 100):.2f}%')
            sys.stdout.flush()
            i += 1

        return portfolio

    @staticmethod
    def __parse_grf_swap(operation_data: pd.DataFrame):
        """Método Privado de conversión de Swap"""

        active_leg_data = operation_data.loc[operation_data['tipo_flujo'] == 'ACT']
        passive_leg_data = operation_data.loc[operation_data['tipo_flujo'] == 'PAS']

        cliente_id = active_leg_data.iloc[0]['cliente']

        associated_collateral = Currency.USD if str(cliente_id) in csa_clients.keys() else Currency.CLP

        active_leg = DataParser.__parse_grf_leg(dataframe=active_leg_data, position=FinancialPosition.LONG,
                                                associated_collateral=associated_collateral)
        passive_leg = DataParser.__parse_grf_leg(dataframe=passive_leg_data, position=FinancialPosition.SHORT,
                                                 associated_collateral=associated_collateral)
        swap = Swap(active_leg=active_leg, passive_leg=passive_leg, associated_collateral=associated_collateral)

        return swap

    @staticmethod
    def __parse_grf_leg(dataframe: pd.DataFrame, position: FinancialPosition, associated_collateral: Currency):
        """Método Privado de conversión de Legs"""
        leg = Leg(position=position, associated_collateral=associated_collateral)

        for index, row in dataframe.iterrows():
            coupon = DataParser.__parse_grf_coupon(row=row, associated_collateral=associated_collateral)
            leg.add_coupon(coupon)

        return leg

    @staticmethod
    def __parse_grf_coupon(row: pd.Series, associated_collateral):
        """Método Privado de conversión de Cupones"""

        strategy = row['strategy']

        rate_name = row['tasa_nombre']
        rate_value = row['tasa'] / 100

        spread = row['spread'] / 100
        start_date = row['fecha_inicio_flujo'].to_pydatetime().date()
        end_date = row['fecha_vencimiento_flujo'].to_pydatetime().date()

        default_date = date(year=1900, day=1, month=1)
        fixing_date = row['fecha_fijacion'].to_pydatetime().date()
        if fixing_date != default_date and strategy == 'IRS USD':
            start_fixing_date = fixing_date
        else:
            start_fixing_date = start_date

        end_fixing_date = end_date
        interest_payment_date = row['fecha_pago'].to_pydatetime().date()
        principal_payment_date = row['fecha_pago'].to_pydatetime().date()
        currency = Currency.from_str(row['moneda'])
        if row['tipo_flujo'] == 'PAS':
            amortization = Cash(amount=-1.00*row['amortizacion'], currency=currency)
        else:
            amortization = Cash(amount=row['amortizacion'], currency=currency)
        outstanding_notional = Cash(amount=row['saldo_residual'], currency=currency)
        conventions = row['base_nombre']

        rate_enum = index_codes[rate_name.upper()]  # Falta control de errores

        if conventions == 'YLD 30/360':
            day_count = DayCount.DC_30_360
            compounding = Compounding.YIELD
        elif conventions == 'LIN 30/360':
            day_count = DayCount.DC_30_360
            compounding = Compounding.LINEAR
        elif conventions == 'LIN 30E/360':
            day_count = DayCount.DC_30E_360
            compounding = Compounding.LINEAR
        elif conventions == 'LIN ACT/360':
            day_count = DayCount.DC_ACT_360
            compounding = Compounding.LINEAR
        elif conventions == 'YLD ACT/360':
            day_count = DayCount.DC_ACT_360
            compounding = Compounding.YIELD
        elif conventions == 'YLD ACT/365':
            day_count = DayCount.DC_ACT_365
            compounding = Compounding.YIELD
        else:
            day_count = DayCount.DC_ACT_360
            compounding = Compounding.LINEAR

        rate = Index.generate(rate_enum, day_count, compounding)

        coupon = Coupon(associated_index=rate, reference_rate=rate_value, spread=spread,
                        start_date=start_date, end_date=end_date,
                        start_fixing_date=start_fixing_date,
                        end_fixing_date=end_fixing_date, interest_payment_date=interest_payment_date,
                        principal_payment_date=principal_payment_date, amortization=amortization,
                        outstanding_notional=outstanding_notional, associated_collateral=associated_collateral)
        return coupon

    # end region

    # endregion
