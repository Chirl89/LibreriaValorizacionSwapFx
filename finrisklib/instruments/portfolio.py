"""
Este módulo se encuentra enfocado en representar portafolios de productos.
"""

import sys
import pandas as pd
from finrisklib.exceptions import PortfolioException
from finrisklib.instruments.instrument import Derivative
from finrisklib.market.dataset import DataSet


class Portfolio:
    """Portafolio

    Clase enfocada en la representación de un portafolio de productos genérico.

    :param portfolio_name: Nombre del portafolio
    :type portfolio_name: str
    """
    def __init__(self, portfolio_name: str):
        self.portfolio_name = portfolio_name
        self.operations = {}

    def add_operation(self, id_number: float, instrument: Derivative):
        """Agregar Operación

        Agrega una operación al portafolio

        :param id_number: Numero de identificación
        :type id_number: float
        :param instrument: Instrumento
        :type instrument: Derivative
        """
        self.operations[id_number] = instrument

    def valuate(self, dataset: DataSet) -> dict:
        """Valorizar

        Valoriza el portafolio utilizando el dataset provisto

        :param dataset: Dataset
        :type dataset: DataSet
        """
        valuation = {}
        i = 1
        n = len(self.operations.keys())
        for id_number in self.operations.keys():
            try:
                valuation[id_number] = self.operations[id_number].valuate(dataset=dataset)
                sys.stdout.write('\r')
                percent = round((i / n) * 100, 2)
                sys.stdout.write(f'Valuating {i} of  {n} - Progress: {percent}%')
                sys.stdout.flush()
                i += 1
            except Exception:
                message = f'Error while valuating operation {id_number}'
                raise PortfolioException(message=message)
        return valuation

    def valuate_to_excel(self, dataset: DataSet, file_name: str):
        """Valorizar a Excel

        Valoriza el portafolio y muestra los resultados en formato excel

        :param dataset: Dataset.
        :type dataset: DataSet
        :param file_name: Nombre del archivo (debe incluir terminación .xlsx)
        :type file_name: str
        :return:
        """
        valuation_dict = self.valuate(dataset=dataset)

        data = {'Operation Number': [], 'Amount': [], 'Currency': []}
        for op in valuation_dict:
            data['Operation Number'].append(int(op))
            data['Amount'].append(valuation_dict[op].amount)
            data['Currency'].append(valuation_dict[op].currency)

        df = pd.DataFrame.from_dict(data)
        df.to_excel(file_name, index=False)

    def merge(self, other_portfolio):
        """Combinar Portafolios

        Combina dos portafolios en uno

        :param other_portfolio: Otro Portafolio
        :type other_portfolio: Portfolio
        """
        other_operations = other_portfolio.operations
        for op in other_operations:
            self.add_operation(op, other_operations[op])
