"""
Este módulo se encuentra enfocado en representar productos swap.
"""

from finrisklib.instruments.flow import Cash
from finrisklib.instruments.flow import Cashflow
from finrisklib.instruments.instrument import Derivative
from finrisklib.market.index import Index
from finrisklib.enums import FinancialPosition, Locality
from finrisklib.enums import FinancialIndex
from finrisklib.enums import Currency
from finrisklib.enums import IndexType
from finrisklib.enums import Period
from finrisklib.enums import BusinessDay
from finrisklib.market.dataset import DataSet
from finrisklib.market.fxrate import FxPair
from finrisklib.market.curve import Curve
from datetime import date
import pandas as pd


class Coupon:
    """Cupón

    Clase enfocada en la representación de cupones con interés y/o amortizaciones.

    :param associated_index: Índice Asociado.
    :type associated_index: Index
    :param reference_rate: Tasa de referencia.
    :type reference_rate: float
    :param spread: Spread sobre la tasa de interés.
    :type spread: float
    :param start_date: Fecha de inicio del cupón.
    :type start_date: date
    :param end_date: Fecha de término del cupón.
    :type end_date: date
    :param start_fixing_date: Fecha de inicio de fijación del cupón.
    :type start_fixing_date: date
    :param end_fixing_date: Fecha de término de fijación del cupón.
    :type end_fixing_date: date
    :param interest_payment_date: Fecha de pago del interés.
    :type interest_payment_date: date
    :param principal_payment_date: Fecha de pago de la amortización.
    :type principal_payment_date: date
    :param outstanding_notional: Nocional remanente.
    :type outstanding_notional: Cash
    :param amortization: Amortización.
    :type amortization: Cash
    :param associated_collateral: Colateral asociado.
    :type associated_collateral: Currency
    """

    def __init__(self, associated_index: Index, reference_rate: float, spread: float, start_date: date, end_date: date,
                 start_fixing_date: date, end_fixing_date: date, interest_payment_date: date,
                 principal_payment_date: date, outstanding_notional: Cash, amortization: Cash,
                 associated_collateral: Currency):

        self.associated_index = associated_index
        self.reference_rate = reference_rate
        self.spread = spread
        self.start_fixing_date = start_fixing_date
        self.end_fixing_date = end_fixing_date
        self.start_date = start_date
        self.end_date = end_date
        self.interest_payment_date = interest_payment_date
        self.principal_payment_date = principal_payment_date
        self.outstanding_notional = outstanding_notional
        self.amortization = amortization
        self.associated_collateral = associated_collateral

    def __repr__(self):
        """
        Sobrecarga de representación

        :return: Descripción del flujo
        """
        return f's: {self.start_date} - e: {self.end_date}: {str(self.associated_index)} {self.reference_rate} + ' \
               f'{self.spread}'

    def __get_annual_rate(self, dataset: DataSet) -> float:
        """Obtener tasa de índice anual

        Obtiene la tasa anualizada de un índice en un periodo de tiempo determinado

        :return: Tasa anualizada del periodo
        """
        if self.associated_index.to_enum() == FinancialIndex.FIX:
            annual_rate = self.reference_rate
        elif self.start_fixing_date < dataset.market_date:

            index_curve = dataset.get_projection_curve(associated_index=self.associated_index)

            dt = (self.end_fixing_date - self.start_fixing_date).days
            t = (self.end_fixing_date - dataset.market_date).days

            if self.associated_index.to_enum() == FinancialIndex.ICP:
                start_index = dataset.get_index_data(self.associated_index.to_enum(), self.start_fixing_date)
                end_index = dataset.get_index_data(self.associated_index.to_enum(), dataset.market_date)

                cap_factor = index_curve.get_cap_factor(t)
                end_index = end_index * cap_factor

                annual_rate = round(((end_index / start_index) - 1) * 360 / dt, 6)
            elif self.associated_index.to_enum() == FinancialIndex.ICP_REAL:

                index_curve = dataset.get_discount_curve(associated_currency=Currency.CLF,
                                                         associated_collateral=Currency.CLP)
                start_index = dataset.get_index_data(self.associated_index.to_enum(), self.start_fixing_date)
                end_index = dataset.get_index_data(self.associated_index.to_enum(), dataset.market_date)

                cap_factor = index_curve.get_cap_factor(t)
                end_index = end_index * cap_factor

                annual_rate = round(((end_index / start_index) - 1) * 360 / dt, 6)
            elif self.associated_index.idx_type == IndexType.ON:

                hist = dataset.get_index_data_between(index=self.associated_index.to_enum(),
                                                      start_date=self.start_fixing_date,
                                                      end_date=dataset.market_date)
                compounded_rate = 1

                base_calendar = dataset.get_calendar([Locality.USA])
                end_date = dataset.market_date
                dates_hist = list(hist.keys())
                n = len(dates_hist)
                for i in range(1, n):
                    end_date = dates_hist[i]
                    key = dates_hist[i-1]
                    yf = (end_date-key).days / 360
                    associated_index = hist[key]
                    compounded_rate = compounded_rate * (1 + associated_index * yf)

                t1 = (end_date - dataset.market_date).days
                t2 = (self.end_fixing_date - dataset.market_date).days
                cap_factor = 1/index_curve.get_forward_factor(t_start=0, t_end=t2)
                compounded_rate = compounded_rate*cap_factor

                annual_rate = (compounded_rate-1)*360/dt

            else:
                annual_rate = dataset.get_index_data(self.associated_index.to_enum(), self.start_fixing_date)
        else:
            if self.associated_index.to_enum() == FinancialIndex.ICP_REAL:
                index_curve = dataset.get_discount_curve(associated_currency=Currency.CLF,
                                                         associated_collateral=Currency.CLP)
            else:
                index_curve = dataset.get_projection_curve(associated_index=self.associated_index)

            t_start = (self.start_fixing_date - dataset.market_date).days
            t_end = (self.end_fixing_date - dataset.market_date).days
            fd = index_curve.get_forward_factor(t_start=t_start, t_end=t_end)

            if t_start == t_end:
                annual_rate = 0
            else:
                annual_rate = Curve.df_to_rate(discount_factor=fd, start_date=self.start_fixing_date,
                                               end_date=self.end_fixing_date,
                                               rate_compounding=self.associated_index.compounding,
                                               rate_day_count=self.associated_index.day_count)
            if self.associated_index.to_enum() == FinancialIndex.ICP or \
               self.associated_index.to_enum() == FinancialIndex.ICP_REAL:

                annual_rate = round(annual_rate, 6)

        return annual_rate + self.spread

    def to_dict(self):
        """
        Convertir a diccionario

        Convierte el cupón a un diccionario

        :return: Diccionario con valores del cupón
        """
        # date_format = '%Y-%m-%d'
        values_dict = {'Rate Type': str(self.associated_index.to_enum()),
                       'Start Date': self.start_date,  # .strftime(date_format),
                       'End Date': self.end_date,  # .strftime(date_format),
                       'Fixing Start Date': self.start_fixing_date,  # .strftime(date_format),
                       'Fixing End Date': self.end_fixing_date,  # .strftime(date_format),
                       'Interest Pay Date': self.interest_payment_date,  # .strftime(date_format),
                       'Principal Pay Date': self.principal_payment_date,  # .strftime(date_format),
                       'Outstanding Notional Amount': self.outstanding_notional.amount,
                       'Outstanding Notional Currency': self.outstanding_notional.currency,
                       'Amortization Amount': self.amortization.amount,
                       'Amortization Currency': self.amortization.currency,
                       'Associated Collateral': self.associated_collateral}

        return values_dict

    def get_valuation_details(self, dataset: DataSet) -> dict:
        """Detalle de valorización

        Valoriza y detalla el instrumento utilizando la información de mercado provista

        :param dataset: Información de mercado.
        :type dataset: DataSet

        :return: Diccionario de datos
        """
        coupon_dict = self.to_dict()

        valuation_currency = dataset.get_default_valuation_currency()

        annual_rate = self.__get_annual_rate(dataset)

        cap_factor = Curve.rate_to_cap_factor(annual_rate=annual_rate, start_date=self.start_date,
                                              end_date=self.end_date,
                                              rate_compounding=self.associated_index.compounding,
                                              rate_day_count=self.associated_index.day_count)

        interest_amount = self.outstanding_notional.amount*(cap_factor-1)
        interest = Cashflow(flow_date=self.interest_payment_date, amount=interest_amount,
                            currency=self.outstanding_notional.currency)
        principal = Cashflow(flow_date=self.principal_payment_date, amount=self.amortization.amount,
                             currency=self.amortization.currency)

        discount_curve = dataset.get_discount_curve(associated_currency=self.outstanding_notional.currency,
                                                    associated_collateral=self.associated_collateral)

        val_pair = FxPair.generate(f'{principal.currency}{valuation_currency}')

        fx_val = dataset.get_fx_rate(val_pair)

        if dataset.market_date >= interest.flow_date:
            disc_int = Cash(amount=0, currency=valuation_currency)
            disc_prin = Cash(amount=0, currency=valuation_currency)
            mtm_int = Cash(amount=0, currency=valuation_currency)
            mtm_prin = Cash(amount=0, currency=valuation_currency)
        else:
            dt_int = (self.interest_payment_date - dataset.market_date).days
            df_int = discount_curve.get_discount_factor(dt_int)

            dt_prin = (self.principal_payment_date - dataset.market_date).days
            df_prin = discount_curve.get_discount_factor(dt_prin)

            disc_int = interest.amount * df_int
            disc_prin = principal.amount * df_prin

            mtm_int = Cash(amount=disc_int*fx_val, currency=valuation_currency)
            mtm_prin = Cash(amount=disc_prin*fx_val, currency=valuation_currency)

        mtm = mtm_int + mtm_prin

        coupon_dict['Anual Rate'] = annual_rate
        coupon_dict['Interest'] = interest.amount
        coupon_dict['Principal'] = principal.amount
        coupon_dict['Discounted Interest'] = disc_int
        coupon_dict['Discounted Principal'] = disc_prin
        coupon_dict['MtM Interest'] = mtm_int.amount
        coupon_dict['MtM Principal'] = mtm_prin.amount
        coupon_dict['MtM'] = mtm.amount
        coupon_dict['Valuation Currency'] = valuation_currency

        return coupon_dict

    def valuate(self, dataset: DataSet):
        """Valorizar

        Valoriza el instrumento utilizando la información de mercado provista

        :param dataset: Información de mercado.
        :type dataset: DataSet

        :return: Objeto Cash con valor presente del instrumento
        """
        valuation_details = self.get_valuation_details(dataset=dataset)
        mtm = Cash(amount=valuation_details['MtM'], currency=dataset.get_default_valuation_currency())
        return mtm

    def to_dataframe(self):
        """
        Convertir a dataframe

        Convierte a Dataframe

        :return: DataFrame con valores del cupón
        """
        coupon_dict = self.to_dict()
        return pd.DataFrame.from_dict(coupon_dict)


class Leg:
    """Swap Leg

    Clase enfocada en la representación de Swap Legs.

    :param position: Posición financiera.
    :type position: FinancialPosition
    :param associated_collateral: Colateral asociado.
    :type associated_collateral: Currency
    """

    def __init__(self, position: FinancialPosition, associated_collateral):
        self.position = position
        self.associated_collateral = associated_collateral
        self.__metadata = {}
        self.__coupons = []

    def add_coupon(self, coupon: Coupon):
        """Agregar Cupón

        Agrega una cupón al swap leg.

        :param coupon: Cupón
        :type coupon: Coupon
        """
        self.__coupons.append(coupon)

    def get_coupon(self, i: int):
        """Obtener cupón

        Obtiene el cupón en la posición i

        :param i: Posición
        :type i: int
        :return: Coupon
        """
        return self.__coupons[i]

    def to_dict(self):
        values_dict = {'Financial Position': [],
                       'Coupon N°': [],
                       'Rate Type': [],
                       'Start Date': [],
                       'End Date': [],
                       'Fixing Start Date': [],
                       'Fixing End Date': [],
                       'Interest Pay Date': [],
                       'Principal Pay Date': [],
                       'Outstanding Notional Amount': [],
                       'Outstanding Notional Currency': [],
                       'Amortization Amount': [],
                       'Amortization Currency': [],
                       'Associated Collateral': []}
        i = 0
        for coupon in self.__coupons:
            coupon_dict = coupon.to_dict()
            values_dict['Coupon N°'].append(i)
            values_dict['Financial Position'].append(self.position.name)
            for key in coupon_dict:
                values_dict[key].append(coupon_dict[key])
            i += 1

        return values_dict

    def get_valuation_details(self, dataset: DataSet):
        values_dict = {'Financial Position': [],
                       'Coupon N°': [],
                       'Rate Type': [],
                       'Start Date': [],
                       'End Date': [],
                       'Fixing Start Date': [],
                       'Fixing End Date': [],
                       'Interest Pay Date': [],
                       'Principal Pay Date': [],
                       'Outstanding Notional Amount': [],
                       'Outstanding Notional Currency': [],
                       'Amortization Amount': [],
                       'Amortization Currency': [],
                       'Associated Collateral': [],
                       'Anual Rate': [],
                       'Interest': [],
                       'Principal': [],
                       'Discounted Interest': [],
                       'Discounted Principal': [],
                       'MtM Interest': [],
                       'MtM Principal': [],
                       'MtM': [],
                       'Valuation Currency': []}
        i = 0
        for coupon in self.__coupons:
            coupon_dict = coupon.get_valuation_details(dataset=dataset)
            values_dict['Coupon N°'].append(i)
            values_dict['Financial Position'].append(self.position.name)
            for key in coupon_dict:
                values_dict[key].append(coupon_dict[key])
            i += 1

        return values_dict

    def to_dataframe(self):
        """Convertir a dataframe

        Convierte a Dataframe

        :return: DataFrame con valores del cupón
        """
        coupon_dict = self.to_dict()
        return pd.DataFrame.from_dict(coupon_dict)

    def valuation_to_dataframe(self, dataset: DataSet):
        valuation_details = self.get_valuation_details(dataset=dataset)
        return pd.DataFrame.from_dict(valuation_details)

    def valuate(self, dataset: DataSet):
        """Valorizar

        Valoriza el instrumento utilizando la información de mercado provista

        :param dataset: Información de mercado.
        :type dataset: DataSet

        :return: Objeto Cash con valor presente del instrumento
        """
        valuation_currency = dataset.get_default_valuation_currency()
        value = Cash(amount=0, currency=valuation_currency)
        e = self.position.value
        for coupon in self.__coupons:
            coupon_value = e*coupon.valuate(dataset=dataset)
            value += coupon_value

        return value


class Swap(Derivative):
    """Instrumento Swap

    Clase base dedicada a la representación de instrumentos Swap.

    :param associated_collateral: Colateral asociado.
    :type associated_collateral: Currency
    """

    def __init__(self, active_leg, passive_leg, associated_collateral):
        super().__init__()
        self.__legs = []
        self.__metadata = {}
        self.add_leg(active_leg)
        self.add_leg(passive_leg)
        self.associated_collateral = associated_collateral

    def get_swap_type(self):
        pass

    def add_leg(self, leg: Leg):
        """Agregar Leg

        Agrega un objeto Leg al Swap

        :param leg: Swap Leg
        :param leg: Leg
        """
        self.__legs.append(leg)

    def to_dict(self):
        swap_dict = {}
        for leg in self.__legs:
            leg_dict = leg.to_dict()
            for key in leg_dict:
                if key not in swap_dict:
                    swap_dict[key] = []
                leg_values = leg_dict[key]
                for val in leg_values:
                    swap_dict[key].append(val)

        return swap_dict

    def to_dataframe(self):
        """Convertir a dataframe

        Convierte a Dataframe

        :return: DataFrame con valores del cupón
        """
        swap_dict = self.to_dict()
        return pd.DataFrame.from_dict(swap_dict)

    def get_valuation_details(self, dataset: DataSet):
        valuation_details = {}
        for leg in self.__legs:
            leg_dict = leg.get_valuation_details(dataset=dataset)
            for key in leg_dict:
                if key not in valuation_details:
                    valuation_details[key] = []
                leg_values = leg_dict[key]
                for val in leg_values:
                    valuation_details[key].append(val)

        return valuation_details

    def valuation_to_dataframe(self, dataset: DataSet):
        valuation_details = self.get_valuation_details(dataset=dataset)
        return pd.DataFrame.from_dict(valuation_details)

    def get_flow(self, dataset: DataSet):
        """Obtener Flujo

        Obtiene los flujos proyectados a la fecha de pago

        :param dataset: Set de datos de mercado.
        :type dataset: DataSet

        :return: Lista de Cashflow a la fecha de pago.
        """
        flows = []
        for leg in self.__legs:
            flows += leg.get_flow(dataset)

        return flows

    def valuate(self, dataset: DataSet):
        """Valorizar

        Valoriza el instrumento utilizando la información de mercado provista

        :param dataset: Información de mercado.
        :type dataset: DataSet

        :return: Objeto Cash con valor presente del instrumento
        """

        valuation_currency = dataset.get_default_valuation_currency()
        value = Cash(amount=0, currency=valuation_currency)

        for leg in self.__legs:
            value += leg.valuate(dataset=dataset)

        return value

    def valuate_by_leg(self, dataset: DataSet):
        """Valorizar por leg

        Valoriza las legs del instrumento utilizando la información de mercado provista

        :param dataset: Información de mercado.
        :type dataset: DataSet

        :return: lista con objetos Cash con valor presente de las legs del instrumento
        """
        leg_values = []

        for leg in self.__legs:
            leg_values.append(leg.valuate(dataset=dataset))

        return leg_values

    """

    @staticmethod
    def generate_irs_cam(contract_date: date,  notional_amount: float, fix_rate: float,
                         financial_position: FinancialPosition, n_periods: int,
                         associated_collateral: Currency, is_offshore: bool = True):
        Genera IRS CAM Onshore

        Genera un Swap IRS Fix - CAM

        :param contract_date: Fecha del contrato
        :type contract_date: date
        :param notional_amount: Monto del nocional
        :type notional_amount: float
        :param fix_rate: Tasa Fija
        :type fix_rate: float
        :param financial_position: Posición financiera
        :type financial_position: FinancialPosition
        :param n_periods: Numero de periodos
        :type n_periods: int
        :param associated_collateral: Colateral asociado
        :type associated_collateral: Currency
        :param is_offshore: Derivado offshore
        :param is_offshore: bool

        :return: Objeto Swap
        

        notional = Cash(amount=notional_amount, currency=Currency.CLP)
        fix_rate = FixedRate(value=fix_rate, day_count=DayCount.DC_ACT_360, compounding=Compounding.LINEAR)
        float_rate = ICP()

        if financial_position == FinancialPosition.LONG:
            fixed_leg_position = FinancialPosition.LONG
            float_leg_position = FinancialPosition.SHORT
        else:
            fixed_leg_position = FinancialPosition.SHORT
            float_leg_position = FinancialPosition.LONG

        spread = 0
        periodicity = Periodicity.BIANNUAL
        start_lag = 2
        fixing_lag = 0
        interest_pay_lag = 1
        notional_pay_lag = 1
        initial_exchange = False
        notional_exchange = False
        business_day_convention = BusinessDay.MODIFIED_FOLLOWING

        associated_calendar = STGCalendar(holidays=[])

        if is_offshore:
            associated_calendar = associated_calendar.merge(other_calendar=NYSECalendar(holidays=[]))

        fix_leg = Leg.create_leg(contract_date=contract_date, associated_index=fix_rate, spread=spread,
                                 periodicity=periodicity, n_periods=n_periods,
                                 notional=notional, start_lag=start_lag, fixing_lag=fixing_lag,
                                 interest_pay_lag=interest_pay_lag,
                                 notional_pay_lag=notional_pay_lag, initial_exchange=initial_exchange,
                                 notional_exchange=notional_exchange,
                                 financial_position=fixed_leg_position, associated_collateral=associated_collateral,
                                 associated_calendar=associated_calendar,
                                 business_day_convention=business_day_convention)

        float_leg = Leg.create_leg(contract_date=contract_date, associated_index=float_rate, spread=spread,
                                   periodicity=periodicity, n_periods=n_periods,
                                   notional=notional, start_lag=start_lag, fixing_lag=fixing_lag,
                                   interest_pay_lag=interest_pay_lag,
                                   notional_pay_lag=notional_pay_lag, initial_exchange=initial_exchange,
                                   notional_exchange=notional_exchange,
                                   financial_position=float_leg_position, associated_collateral=associated_collateral,
                                   associated_calendar=associated_calendar,
                                   business_day_convention=business_day_convention)

        swap = Swap(active_leg=fix_leg, passive_leg=float_leg, associated_collateral=associated_collateral)

        return swap

    """