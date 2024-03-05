"""
El módulo de calendarios se encarga de generar clases que contengan la información de los días laborales de una
localidad específica, al igual que permitir generar calculos relacionados con fechas.
"""

from finrisklib.enums import DayCount
from finrisklib.enums import BusinessDay
from finrisklib.enums import Period
from finrisklib.exceptions import CalendarException
from datetime import date
from pandas.tseries.offsets import CustomBusinessDay
from pandas.tseries.offsets import CustomBusinessMonthEnd
from pandas.tseries.offsets import DateOffset
from pandas.tseries.holiday import AbstractHolidayCalendar


class TradingCalendar:
    """Calendarios

    Clase dedicada al almacenamiento de calendarios

    :param calendar_name: Nombre del Calendario
    :type calendar_name: str
    :param holidays: listado de feriados.
    :type holidays: list
    :param base_calendar: Calendario base.
    :type base_calendar: AbstractHolidayCalendar
    """

    def __init__(self, calendar_name: str, holidays: list, base_calendar: AbstractHolidayCalendar):
        """Constructor"""
        self.calendar_name = calendar_name
        self.cbd = CustomBusinessDay(calendar=base_calendar, holidays=holidays)
        self.cbm = CustomBusinessMonthEnd(calendar=base_calendar, holidays=holidays)

    def adjust_workday(self, workday: date, business_day_convention: BusinessDay):
        """Ajustar día laborable

        Ajusta el día laborable provisto de acuerdo a la convención solicitada.

        :param workday: Día laborable inicial.
        :type workday: date
        :param business_day_convention: Convención de ajuste.
        :type business_day_convention: BusinessDay

        :return: Fecha ajustada
        """
        if business_day_convention == BusinessDay.UNADJUSTED:
            return workday
        elif business_day_convention == BusinessDay.FOLLOWING:
            adjusted_workday = (workday+0*self.cbd).to_pydatetime().date()
            return adjusted_workday
        elif business_day_convention == BusinessDay.MODIFIED_FOLLOWING:
            adjusted_workday = (workday+0*self.cbd).to_pydatetime().date()
            if adjusted_workday.month > workday.month:
                adjusted_workday = (workday - 1 * self.cbd).to_pydatetime().date()
            return adjusted_workday
        elif business_day_convention == BusinessDay.PRECEDING:
            adjusted_workday = (workday+0*self.cbd).to_pydatetime().date()
            if adjusted_workday > workday:
                adjusted_workday = (workday - 1 * self.cbd).to_pydatetime().date()
            return adjusted_workday
        elif business_day_convention == BusinessDay.MODIFIED_PRECEDING:
            adjusted_workday = (workday+0*self.cbd).to_pydatetime().date()
            if adjusted_workday > workday:
                adjusted_workday = (workday - 1 * self.cbd).to_pydatetime().date()
                if adjusted_workday.month < workday.month:
                    adjusted_workday = (workday + 1 * self.cbd).to_pydatetime().date()
            return adjusted_workday
        elif business_day_convention == BusinessDay.END_OF_MONTH:
            adjusted_workday = (workday + 0 * self.cbm).to_pydatetime().date()
            return adjusted_workday
        elif business_day_convention == BusinessDay.PUBLISH_UF:
            day = workday.day
            if day == 9:
                adjusted_workday = (workday + 0 * self.cbd).to_pydatetime().date()
                return adjusted_workday
            elif day < 9:
                uf_date = date(day=9, month=workday.month, year=workday.month)
                adjusted_workday = (uf_date + 0 * self.cbd).to_pydatetime().date()
                return adjusted_workday
            else:
                month = workday.month + 1 if workday.month < 12 else 1
                year = workday.year if workday.month < 12 else workday.year+1
                uf_date = date(day=9,  month=month, year=year)
                adjusted_workday = (uf_date + 0 * self.cbd).to_pydatetime().date()
                return adjusted_workday
        else:
            message = f'Business day Convention {business_day_convention} not recognized'
            raise CalendarException(message=message)

    def offset_date(self, start_date: date, n_periods: int, period: Period, convention: BusinessDay) -> date:
        """Mover fecha

        Mueve una fecha dentro de un periodo específico.

        :param start_date: fecha de inicio.
        :type start_date: date
        :param n_periods: número de periodos.
        :type n_periods: int
        :param period: Periodo
        :type period: Period
        :param convention: Convención.
        :type convention: BusinessDay

        :return: Fecha con offset
        """
        if period == Period.DAY:
            new_date = (start_date + n_periods*DateOffset()).to_pydatetime().date()
        elif period == Period.MONTH:
            new_date = (start_date + n_periods*DateOffset(months=1)).to_pydatetime().date()
        elif period == Period.QUARTER:
            new_date = (start_date + n_periods*DateOffset(months=3)).to_pydatetime().date()
        elif period == Period.SEMESTER:
            new_date = (start_date + n_periods*DateOffset(months=6)).to_pydatetime().date()
        elif period == Period.YEAR:
            new_date = (start_date + n_periods*DateOffset(months=12)).to_pydatetime().date()
        else:
            message = f'Period {period} not recognized'
            raise CalendarException(message=message)
        return self.adjust_workday(workday=new_date, business_day_convention=convention)

    @staticmethod
    def is_weekend(selected_date):
        """Fin de Semana

        Verifica si la fecha propuesta es un fin de semana (sábado y domingo).

        :param selected_date: Fecha.
        :type selected_date: date

        :return: Booleano
        """
        return selected_date.weekday() > 4

    @staticmethod
    def get_year_fraction(start_date: date, end_date: date, day_count: DayCount):
        """Obtener Fracción de Año

        Obtiene la fracción de año entre las fechas provistas utilizando la convención de conteo de días provista

        :param start_date: Fecha de inicio.
        :type start_date: date
        :param end_date: Fecha de fin.
        :type end_date: date
        :param day_count: Convención de conteo de días.
        :type day_count: DayCount

        :return: fracción de año
        """
        if day_count == DayCount.DC_ACT_360 or day_count == DayCount.DC_ACT_365:
            dt = (end_date-start_date).days
            return dt/360 if day_count == DayCount.DC_ACT_360 else dt/365
        elif day_count == DayCount.DC_30_360 or day_count == DayCount.DC_30_365:
            d1 = start_date.day
            m1 = start_date.month
            y1 = start_date.year

            d2 = end_date.day
            m2 = end_date.month
            y2 = end_date.year

            d1 = (30 if m1 == 2 and d1 >= 27 else d1)  # corrección febrero fecha inicio
            d2 = (30 if m2 == 2 and d2 >= 27 else d2)  # corrección febrero fecha final
            d2 = (30 if d2 == 31 and d1 >= 30 else d2)  # corrección fin de mes
            d1 = (30 if d1 == 31 else d1)  # corrección fin de mes fecha inicial

            dt = (360*(y2-y1)+30*(m2-m1)+(d2-d1))

            return dt/360 if day_count == DayCount.DC_30_360 else dt/365

        elif day_count == DayCount.DC_30E_360 or day_count == DayCount.DC_30E_365:

            d1 = start_date.day
            m1 = start_date.month
            y1 = start_date.year

            d2 = end_date.day
            m2 = end_date.month
            y2 = end_date.year

            d1 = (30 if d1 == 31 else d1)  # corrección fecha inicio
            d2 = (30 if d2 == 31 else d2)  # corrección fecha final

            dt = (360*(y2-y1)+30*(m2-m1)+(d2-d1))
            return dt/360 if day_count == DayCount.DC_30E_360 else dt/365
        elif day_count == DayCount.DC_30E_360_ISDA or day_count == DayCount.DC_30E_365_ISDA:

            d1 = start_date.day
            m1 = start_date.month
            y1 = start_date.year

            d2 = end_date.day
            m2 = end_date.month
            y2 = end_date.year

            d1 = (30 if d1 == 31 else d1)  # corrección fecha inicial
            d1 = (31 if d1 == 27 and m2 == 2 else d1)  # corrección febrero fecha inicio
            d2 = (30 if d2 == 31 else d2)  # corrección fecha final

            dt = (360*(y2-y1)+30*(m2-m1)+(d2-d1))
            return dt/360 if day_count == DayCount.DC_30E_360_ISDA else dt/365
        else:
            message = f'Day Count Convention {day_count} not recognized'
            raise CalendarException(message=message)
