"""
Este módulo cuenta con una clase abstract base para los instrumentos derivados
"""
import pandas as pd

from finrisklib.market.dataset import DataSet
from finrisklib.enums import CashflowType
from finrisklib.instruments.flow import Cashflow


class Derivative:

    def __init__(self):
        self.__cashflows = {CashflowType.ACTIVE: [],
                            CashflowType.PASSIVE: []}
        self.__metadata = {}

    def add_metadata(self, parameter, value):
        """Agregar Metadata

        Agrega un parámetro y valor a la metadata del instrumento.

        :param parameter: Nombre del parámetro.
        :type parameter: str
        :param value: Valor del parámetro.
        :type value: Any
        :return:
        """
        if self.__metadata is None:
            self.__metadata = {}
        else:
            self.__metadata[parameter] = value

    def get_metadata(self, parameter):
        """Obtener Metadata

        Obtiene un parámetro de la metadata del instrumento.

        :param parameter: Nombre del parámetro.
        :type parameter: str

        :return: valor de la metadata
        """
        return self.__metadata[parameter]

    def add_active_cashflow(self, active_cashflow: Cashflow):
        """Agregar flujo de caja activo

        Agrega un flujo de caja activo.

        :param active_cashflow: Flujo de caja
        :type active_cashflow: Cashflow
        """
        self.__cashflows[CashflowType.ACTIVE].append(active_cashflow)

    def add_passive_cashflow(self, passive_cashflow: Cashflow):
        """Agregar flujo de caja pasivo

        Agrega un flujo de caja pasivo.

        :param passive_cashflow: Flujo de caja
        :type passive_cashflow: Cashflow
        """
        self.__cashflows[CashflowType.PASSIVE].append(passive_cashflow)

    def get_active_cashflows(self):
        """Obtener flujos de caja activos

        Obtiene los flujos de caja activos.
        """
        return self.__cashflows[CashflowType.ACTIVE]

    def get_passive_cashflows(self):
        """Obtener flujos de caja pasivos

        Obtiene los flujos de caja pasivos.
        """
        return self.__cashflows[CashflowType.PASSIVE]

    def get_cashflows(self):
        """Obtener flujos de caja

        Obtiene los flujos de caja.
        """
        return self.__cashflows

    def calculate_cashflows(self):
        """Calcular flujos de caja (Abstracto)

        Método abstracto para el cálculo de flujos de caja
        """
        pass

    def get_valuated_cashflows(self, dataset: DataSet):
        """Valorizar flujos de caja (Abstracto)

        Método abstracto para la valorización de flujos de caja
        """
        pass

    def valuate(self, dataset: DataSet):
        """Valorizar (Abstracto)

        Método abstracto para la valorización del instrumento
        """
        pass

    def valuation_to_dataframe(self, dataset: DataSet) -> pd.DataFrame:
        pass
