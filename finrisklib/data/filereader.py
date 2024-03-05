"""
Este módulo está enfocado en la lectura de archivos que puedan ser entendidos y procesados
por la librería. Los archivos deben tener un formato específico, el cual será especificado en la
documentación de cada función.
"""

import pandas as pd
from datetime import date

from finrisklib.market.dataset import CurveDataSet
from finrisklib.market.dataset import FxDataSet
from finrisklib.market.dataset import IndexDataSet
from finrisklib.market.dataset import DataSet
from finrisklib.data.dataparser import DataParser
from finrisklib.data.dbreader import DBReader


class XlsReader:
    """
    Clase dedicada a la lectura de datos en formato Excel.
    """

    # region Lectura de Curvas

    @staticmethod
    def read_curve_data(file_name: str) -> CurveDataSet:
        """ Leer de archivo de curvas

        Lee un archivo excel con datos de una o más curvas y devuelve un diccionario con los nombres y las curvas
        inicializadas. El formato aceptado es:

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

        :param file_name: Nombre del archivo a leer.
        :type file_name: str

        :return: CurveDataSet
        """

        curve_data = pd.read_excel(io=file_name)

        return DataParser.parse_curve_data(curve_data=curve_data)

    # endregion

    # region Lectura de Tipos de cambio

    @staticmethod
    def read_fx_pair_data(file_name: str) -> FxDataSet:
        """ Lector de archivo Excel de Tipos de cambio

        Lee un archivo excel con datos de uno o más tipos de cambio para un día específico y devuelve una lista de
        objetos FxPair. El formato aceptado es:

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

        :param file_name: Nombre del archivo a leer.
        :type file_name: str

        :return: Diccionario de objetos FxPair
        """

        fx_data = pd.read_excel(file_name)

        return DataParser.parse_fx_data(fx_data=fx_data)

    # endregion

    # region Lectura de datos de índices

    @staticmethod
    def read_index_data(file_name: str) -> IndexDataSet:
        """Lector de archivo Excel de Data de índices

        Lee un archivo excel con datos de uno o más índices con información histórica y devuelve un diccionario con
        llave de objeto Index y valores históricos. El formato aceptado es:

        .. list-table:: **Formato Tabla de Índices Financieros**
           :widths: 25 25 25
           :header-rows: 1

           * - Código Indice
             - Fecha Proceso
             - Valor
           * - ICP REAL
             - 2022/01/03
             - 17854.15

        :param file_name: Nombre del archivo a leer.
        :type file_name: str

        :return: Diccionario de objetos Index
        """

        index_data = pd.read_excel(file_name)
        return DataParser.parse_index_data(index_data=index_data)

    # endregion

    # region Lectura de dataset

    @staticmethod
    def read_dataset_data(process_date: date, curve_file: str, fx_file: str, index_file: str) -> DataSet:
        """ Lector de dataset

        Lee la información de mercado provista en los distintos archivos.

        :param process_date: Fecha del dataset.
        :type process_date: date.
        :param curve_file: Nombre del archivo con información de curvas.
        :type curve_file: str.
        :param fx_file: Nombre del archivo con información de tipo de cambio.
        :type fx_file: str.
        :param index_file: Nombre del archivo con información de índices.
        :type index_file: str.

        :return: Objeto Dataset.
        """

        curve_dataset = XlsReader.read_curve_data(file_name=curve_file)
        fx_dataset = XlsReader.read_fx_pair_data(file_name=fx_file)
        index_dataset = XlsReader.read_index_data(file_name=index_file)
        reader = DBReader()
        calendar_dataset = reader.get_calendar_dataset()

        dataset = DataSet(process_date=process_date,
                          curve_dataset=curve_dataset,
                          fx_dataset=fx_dataset,
                          index_dataset=index_dataset, calendar_dataset=calendar_dataset)
        return dataset

    # endregion

    # region Lectura de Operaciones

    @staticmethod
    def read_derivados_data(portfolio_file: str):
        """Leer Archivo de Operaciones

        Lee un archivo con el formato de Cartera Derivados

        :param portfolio_file: Dirección de archivo de portafolio

        :return: Portafolio
        """

        portfolio_data = pd.read_excel(portfolio_file)
        return DataParser.parse_portfolio_data(portfolio_data=portfolio_data)

    @staticmethod
    def read_derivados_operation_data(operation_file: str):
        """Leer Archivo de Operación Individual

        Lee un archivo con el formato de Cartera Derivados de una sola operación.

        :param operation_file: Dirección de archivo de portafolio

        :return: Derivative
        """

        operation_data = pd.read_excel(operation_file)
        return DataParser.parse_operation_data(operation_data=operation_data)

    @staticmethod
    def read_portfolio_data(portfolio_file: str):
        """Leer archivo de portafolio completo

        Obtiene todos los productos de la cartera

        :param portfolio_file: Dirección de archivo de portafolio

        :return: Portfolio
        """
        portfolio_data = pd.read_excel(portfolio_file)

        return DataParser.parse_portfolio_data(portfolio_data=portfolio_data)

    # endregion
