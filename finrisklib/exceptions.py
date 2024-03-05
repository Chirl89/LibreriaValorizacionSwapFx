"""
Las excepciones contenidas en este módulo fueron diseñadas para manejar los errores internos de la librería. Estos
errores pueden ser causados por multiples razones entre ellas: tipo equivocado de parámetros, operación inválida,
falta de información disponible, etc.
"""


class CalendarException(Exception):
    """Excepción de Calendario

    Maneja los errores en la aplicación de calendarios.

    :param message: Mensaje.
    :type message: str.
    """
    def __init__(self, message: str):
        super(CalendarException, self).__init__(f'Calendar error: {message}')


class CurrencyException(Exception):
    """Excepción de Moneda

    Maneja los errores asociados con Monedas.

    :param message: Mensaje.
    :type message: str.
    """

    def __init__(self, message: str, currency: str = ''):
        self.currency = currency
        super(CurrencyException, self).__init__(f'Currency Error: {message}')


class EnumException(Exception):
    """Excepción de Enumerador

    Maneja los errores asociados con enumeradores.

    :param message: Mensaje
    :type message: str
    """

    def __init__(self, message: str):
        super(EnumException, self).__init__(f'Enum Error: {message}')


class CurveException(Exception):
    """Excepción de Curva

    Maneja los errores en la construcción o utilización de curvas.

    :param curve_name: Nombre de la curva.
    :type curve_name: str.
    :param message: Mensaje.
    :type message: str.
    """

    def __init__(self, curve_name: str, message: str):
        super(CurveException, self).__init__(f'´CurveException in {curve_name}: {message}')


class QueryException(Exception):
    """Excepción de consulta

    Maneja los errores de queries en la base de datos.
    
    :param query: Consulta SQL.
    :type query: str.
    :param message: Mensaje.
    :type message: str
    """

    def __init__(self, query: str, message: str):
        self.query = query
        super(QueryException, self).__init__(message)


class FxRateException(Exception):
    """Excepción de tasa de cambio

    Maneja errores asociados a la tasa de cambio.

    :param fx_pair_name: Tasa de Cambio.
    :type fx_pair_name: str.
    :param message: Mensaje.
    :type message: str
    """

    def __init__(self, fx_pair_name: str, message: str):
        self.fx_pair_name = fx_pair_name
        super(FxRateException, self).__init__(f'´FxRateException in {fx_pair_name}: {message}')


class IndexException(Exception):
    """Excepción de Índice

    Maneja errores asociados a índices.

    :param idx_name: Nombre del Índice.
    :type idx_name: str.
    :param message: Mensaje.
    :type message: str.
    """

    def __init__(self, idx_name: str, message: str):
        self.idx_name = idx_name
        super(IndexException, self).__init__(f'´IndexException in {idx_name}: {message}')


class DatasetException(Exception):
    """Excepción de DataSet

    Maneja los errores en Datasets.

    :param message: Mensaje.
    :param message: str.
    """

    def __init__(self, message: str):
        super(DatasetException, self).__init__(f'Error in Dataset: {message}')


class PortfolioException(Exception):
    """Excepción de Portfolio

    Maneja los errores en Portafolios.

    :param message: Mensaje.
    :param message: str.
    """

    def __init__(self, message: str):
        super(PortfolioException, self).__init__(f'Error in Portfolio: {message}')


class FileReadException(Exception):
    """Excepción de Lectura de archivos

    Maneja los errores en la lectura de archivos.

    :param file_path: Localización del archivo.
    :type file_path: str
    :param file_alias: Nombre o Alias del archivo.
    :type file_alias: str.
    :param message: Mensaje.
    :type message: str.
    """

    def __init__(self, file_path: str, file_alias: str, message: str):
        self.file_path = file_path
        super(FileReadException, self).__init__(f'Error reading file {file_alias}: {message}')
