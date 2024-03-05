"""
Los enumeradores dentro de este módulo se utilizan para estandarizar la utilización de la librería entre los distintos
usuarios y asi evitar diferencias en los nombres, códigos o parametrización utilizada.
"""

from enum import Enum, auto
from finrisklib.exceptions import CurrencyException
from finrisklib.exceptions import IndexException
from finrisklib.exceptions import EnumException


class Locality(Enum):
    """Enumerador de localidades.

    Lista las principales localidades financieras siguiendo el ISO 3166, cada localización tiene representación
    abreviada (letras) y un código numérico.
    """

    NDL = 000
    """Localidad No Determinada (Non Determined Location)"""

    # region  Norteamérica

    IMF = 999
    """Fondo Monetario Internacional(NON - ISO CODE)"""
    USA = 840
    """Estados Unidos"""
    CAN = 124
    """Canada"""

    # endregion

    # region Sudamérica

    CHL = 152
    """Chile"""
    PER = 604
    """Peru"""
    COL = 170
    """Colombia"""
    VEN = 862
    """Venezuela"""
    ARG = 32
    """Argentina"""
    BRA = 76
    """Brasil"""

    # endregion

    # region Centroamérica

    MEX = 484
    """Mexico"""

    # endregion

    # region Europa

    # Union Europea(NON - ISO CODE)
    EUR = 998
    """Union Europea"""
    GBR = 826
    """Reino Unido"""
    CHE = 756
    """Suiza"""
    SWE = 752
    """Suecia"""
    DNK = 208
    """Dinamarca"""
    NOR = 578
    """Noruega"""

    # endregion

    # region Africa

    ZAF = 710
    """Sudáfrica"""

    # endregion

    # region Asia

    # China
    CN = 156
    """China"""
    HKG = 344
    """Hong Kong"""
    # Japón
    JPN = 392
    """Japón"""
    # Corea del Sur
    KOR = 410
    """Corea del sur"""

    # endregion

    # region Oceania

    AUS = 36
    """Australia"""
    NZL = 554
    """Nueva Zelanda"""

    # endregion

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Currency(Enum):
    """Enumerador de Moneda

    Lista las monedas utilizando un Mnemotécnico de 3 letras.
    """

    NDC = auto()
    """Non Determined Currency"""

    # region Norteamérica

    USD = auto(),
    """Dólar Estadounidense"""
    CAD = auto(),
    """Dólar Canadiense"""
    DEG = auto(),
    """Derecho Especial de Giro"""

    # endregion

    # region Sudamérica

    CLP = auto(),
    """Peso Chileno"""
    CLD = auto(),
    """Peso Chileno a Dólar Observado"""
    CLF = auto(),
    """Unidad de Fomento"""
    PEN = auto(),
    """Sol Peruano"""
    COP = auto(),
    """Peso Colombiano"""
    BRL = auto(),
    """Real Brasilero"""

    # endregion

    # region Centroamérica

    MXN = auto(),
    """Peso Mexicano"""

    # endregion

    # region Europa

    EUR = auto(),
    """Euro"""
    GBP = auto(),
    """Libra Británica"""
    CHF = auto(),
    """Franco Suizo"""
    SEK = auto(),
    """Corona Sueca"""
    DKK = auto(),
    """Corona Danesa"""
    NOK = auto(),
    """Corana Noruega"""

    # endregion

    # region Asia

    JPY = auto(),
    """Yen Japonés"""
    CNY = auto(),
    """Yuan Renminbi Chino"""
    CNH = auto(),
    """Yuan Renminbi Chino"""
    KRW = auto(),
    """Won Surcoreano"""
    HKD = auto(),
    """Dólar Hong Kong"""

    # endregion

    # region Oceania

    AUD = auto(),
    """Dólar Australiano"""
    NZD = auto(),
    """Dólar Neozelandés"""

    # endregion

    # region Africa

    ZAR = auto(),
    """Rand Sudafricano"""

    # endregion

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    @staticmethod
    def from_str(currency_str: str):
        """Convertir String a Currency

        Método estático que convierte un string en Currency

        :param currency_str: String de moneda

        :return: Enumerador de moneda
        """
        try:
            currency = Currency[currency_str.upper()]
            return currency
        except Exception:
            message = f'Parsing error, could not find {currency_str} in Currency Enum'
            raise CurrencyException(message=message, currency=currency_str)


class IndexType(Enum):
    """Enumerador de tipos de índices

    Enumera los distintos tipos de índices existentes
    """
    FIXED = auto()
    """Fijo"""
    MPR = auto()
    """Monetary Policy Rate"""
    ON = auto()
    """Tasa Overnight"""
    IBOR = auto()

    """Interbancarias"""
    CPI = auto()
    """Indices de inflación"""

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    @staticmethod
    def from_str(index_type_str: str):
        """Convertir String a IndexType

        Método estático que convierte un string en un enumerador de Tipo de Índice

        :param index_type_str: String de Tipo de Índice

        :return: Enumerador de tipo de índice
        """
        try:
            index_type = IndexType[index_type_str.upper()]
            return index_type
        except Exception:
            message = f'Parsing error, could not find {index_type_str} in IndexType Enum'
            raise EnumException(message=message)


class FinancialIndex(Enum):
    """Enumerador de Índices Financieros

    Lista los principales índices financieros.
    """
    FIX = auto(),
    """Fijo"""
    ICP = auto(),
    """Índice Camara Promedio"""
    ICP_REAL = auto(),
    """Índice Camara Real"""
    TAB1M = auto(),
    """TAB CLP 1M"""
    TAB3M = auto(),
    """TAB CLP 3M"""
    TAB6M = auto(),
    """TAB CLP 6M"""
    TAB1Y = auto(),
    """TAB CLP 1Y"""
    TABUF3M = auto(),
    """TAB UF 3M"""
    TABUF6M = auto(),
    """TAB UF 6M"""
    TABUF1Y = auto(),
    """TAB UF 1Y"""
    OIS = auto(),
    """OIS"""
    SOFR = auto(),
    """SOFR"""
    LIBOR1M = auto(),
    """LIBOR 1M"""
    LIBOR3M = auto(),
    """LIBOR 3M"""
    LIBOR6M = auto(),
    """LIBOR 6M"""
    LIBOR1Y = auto(),
    """LIBOR 1Y"""
    TERM_SOFR1M = auto(),
    """TERM SOFR 1M"""
    TERM_SOFR3M = auto(),
    """TERM SOFR 3M"""
    TERM_SOFR6M = auto(),
    """TERM SOFR 6M"""
    TERM_SOFR1Y = auto(),
    """TERM SOFR 1Y"""
    EONIA = auto(),
    """EONIA"""
    ESTR = auto(),
    """ESTR"""
    EURIBOR1M = auto(),
    """EURIBOR 1M"""
    EURIBOR3M = auto(),
    """EURIBOR 3M"""
    EURIBOR6M = auto(),
    """EURIBOR 6M"""
    EURIBOR1Y = auto(),
    """EURIBOR 1Y"""
    IBR = auto(),
    """Índice Bancario de Referencia"""
    TONA = auto(),
    """TONA Japonés"""
    BBSW_3M = auto(),
    """Bank Bill 3M Australiano"""
    SARON = auto(),
    """SARON Suizo"""
    AONIA = auto()
    """AONIA Australiano"""

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    @staticmethod
    def from_str(index_str: str):
        """Convertir String a Índice

        Método estático que convierte un string en Índice Financiero

        :param index_str: String de Índice Financiero

        :return: Enumerador de Índice Financiero

        :raises IndexException: En caso no se reconozca el string
        """
        try:
            idx = FinancialIndex[index_str.upper()]
            return idx
        except Exception:
            message = f'Parsing error, could not find {index_str} in FinancialIndex Enum'
            raise IndexException(idx_name=index_str, message=message)


class MaxMin(Enum):
    """Determinante de Máximo y Mínimo

    Determina el Máximo (+1) y Minimo (-1)
    """

    MAX = +1,
    """Máximo"""
    MIN = -1
    """Minimo"""

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class FinancialPosition(Enum):
    """Enumerador de posición financiera

    Lista las posibles posiciones financieras, Long (1) y Short (-1)
    """

    LONG = 1
    """Largo"""
    SHORT = -1
    """Corto"""

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class CashflowType(Enum):
    """Enumerador de tipo de flujo de Caja

    Lista los tipos de flujo de caja: Activo (1) y Pasivo (-1)
    """

    ACTIVE = 1
    """Activo"""
    PASSIVE = -1
    """Pasivo"""

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Source(Enum):
    """Enumerador de Fuente de Información

    Enumera las distintas fuentes de información
    """

    OFFICIAL = auto()
    """Oficial"""
    MUREX = auto()
    """Murex"""
    SANDBOX = auto()
    """Sandbox"""

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class CurveType(Enum):
    """Enumerador de Tipos de Curva

    Enumera los distintos tipos de curva.
    """

    DISCOUNT = auto()
    """Curva de Descuento"""
    PROJECTION = auto()
    """Curva de Proyección"""
    DUAL = auto()
    """Curva de Descuento y Proyección"""
    CREDIT_RISK = auto()
    """Curva de Riesgo de Crédito"""
    FIXED_INCOME = auto()
    """Curva de Renta Fija"""
    FUNDING_COST = auto()
    """Curva de Costo de Fondo"""
    NOT_USED = auto()
    """Curva no usada"""

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Period(Enum):
    """Enumerador de periodos

    Enumera y estandariza la representación de los distintos tipos de periodo.
    """
    DAY = auto()
    """Día"""
    MONTH = auto()
    """Mes"""
    QUARTER = auto()
    """Trimestre"""
    SEMESTER = auto()
    """Semestre"""
    YEAR = auto()
    """Año"""

    def __str__(self):
        return self.name


class Periodicity(Enum):
    """Enumerador de periodicidad

    Enumera y estandariza la representación de las periodicidades.
    """

    UNIQUE = 0
    """Pago unico"""
    ANNUAL = 1
    """Anual"""
    BIANNUAL = 2
    """Semestral"""
    QUARTERLY = 4
    """Trimestral"""
    MONTHLY = 12
    """Mensual"""
    WEEKLY = 52
    """Semanal"""
    TN = 182
    """Cada dos días"""
    OVERNIGHT = 365
    """Pago diario"""
    ON = 365
    """Pago diario"""
    TAILOR_MADE = 999
    """Pagos hechos a la medida"""

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    @staticmethod
    def from_str(periodicity_str: str):
        """Convertir String a Periodicity

        Método estático que convierte un string en una Periodicidad

        :param periodicity_str: String de periodicidad

        :return: Enumerador de periodicidad
        """
        try:
            periodicity = Periodicity[periodicity_str.upper()]
            return periodicity
        except Exception:
            message = f'Parsing error, could not find {periodicity_str} in Periodicity Enum'
            raise EnumException(message=message)


class BusinessDay(Enum):
    """Enumerador de redondeo de días hábiles

    Enumera las distintas convenciones de redondeo de días hábiles.
    """
    UNADJUSTED = auto()
    """Sin ajuste por fecha"""
    FOLLOWING = auto()
    """Convención Following"""
    MODIFIED_FOLLOWING = auto()
    """Convención Modified Following"""
    PRECEDING = auto()
    """Convención Preceding"""
    MODIFIED_PRECEDING = auto()
    """Convención Modified Preceding"""
    END_OF_MONTH = auto()
    """Fin de mes"""
    PUBLISH_UF = auto()
    """Convención UF"""

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    @staticmethod
    def from_str(business_day_str: str):
        """Convertir String a Business Day Convention

        Método estático que convierte un string en un enumerador de convención de días laborales

        :param business_day_str: String de Convención de días laborales

        :return: Enumerador de BusinessDay
        """
        try:
            business_day = BusinessDay[business_day_str.upper()]
            return business_day
        except Exception:
            message = f'Parsing error, could not find {business_day_str} in BusinessDay Enum'
            raise EnumException(message=message)


class DayCount(Enum):
    """Enumerador de convenciones de conteo de días

    Enumera las distintas convenciones de conteo de días.
    """

    DC_30_360 = auto()
    """Convención 30/360"""
    DC_30_365 = auto()
    """Convención 30/365"""
    DC_30E_360 = auto()
    """Convención 30/360 Europeo"""
    DC_30E_365 = auto()
    """Convención 30/365 Europeo"""
    DC_30E_360_ISDA = auto()
    """Convención 30/360 Europeo ISDA"""
    DC_30E_365_ISDA = auto()
    """Convención 30/365 Europeo ISDA"""
    DC_ACT_360 = auto()
    """Convención Act/360"""
    DC_ACT_365 = auto()
    """Convención Act/365"""

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    @staticmethod
    def from_str(day_count_str: str):
        """Convertir String a DayCount

        Método estático que convierte un string en un enumerador de conteo de días

        :param day_count_str: String de Conteo de días

        :return: Enumerador de conteo de días
        """
        try:
            day_count = DayCount[day_count_str.upper()]
            return day_count
        except Exception:
            message = f'Parsing error, could not find {day_count_str} in DayCount Enum'
            raise EnumException(message=message)


class Compounding(Enum):
    """Enumerador para composición de tasas

    Enumera las distintas convenciones de composición de tasas
    """

    LINEAR = auto()
    """Lineal"""
    YIELD = auto()
    """Compuesta"""
    EXPONENTIAL = auto()
    """Exponencial"""

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    @staticmethod
    def from_str(compounding_str: str):
        """Convertir String a IndexType

        Método estático que convierte un string en un enumerador de Tipo de Índice

        :param compounding_str: String de Tipo de Índice

        :return: Enumerador de Compounding
        """
        try:
            compounding = Compounding[compounding_str.upper()]
            return compounding
        except Exception:
            message = f'Parsing error, could not find {compounding_str} in Compounding Enum'
            raise EnumException(message=message)


class InterpolationMethod(Enum):
    """Enumerador para métodos de interpolación

    Enumera los métodos de interpolación implementados.
    """

    LINEAR = auto()
    """Lineal"""
    LOG_LINEAR = auto()
    """Log Lineal"""

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    @staticmethod
    def from_str(interpolation_str: str):
        """Convertir String a InterpolationMethod

        Método estático que convierte un string en un enumerador de método de interpolación

        :param interpolation_str: String de Método de interpolación

        :return: Enumerador de método de interpolación
        """
        try:
            interpolation_method = InterpolationMethod[interpolation_str.upper()]
            return interpolation_method
        except Exception:
            message = f'Parsing error, could not find {interpolation_str} in InterpolationMethod Enum'
            raise EnumException(message=message)


class ExtrapolationMethod(Enum):
    """Enumerador para métodos de extrapolación

    Enumera los métodos de extrapolación implementados
    """

    SLOPE = auto()
    """Mantiene la pendiente"""
    LOG_SLOPE = auto()
    """Mantiene la pendiente del logaritmo"""
    RATE_SLOPE = auto()
    """Mantiene la pendiente convirtiendo a una tasa convención Yield ACT/360"""
    FLAT = auto()
    """Mantiene el valor mas cercano"""
    FLAT_RATE = auto()
    """Mantiene el valor mas cercano tratándolo como tasa"""

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    @staticmethod
    def from_str(extrapolation_str: str):
        """Convertir String a InterpolationMethod

        Método estático que convierte un string en un enumerador de método de interpolación

        :param extrapolation_str: String de Método de interpolación

        :return: Enumerador de método de extrapolación
        """
        try:
            extrapolation_method = ExtrapolationMethod[extrapolation_str.upper()]
            return extrapolation_method
        except Exception:
            message = f'Parsing error, could not find {extrapolation_str} in ExtrapolationMethod Enum'
            raise EnumException(message=message)
