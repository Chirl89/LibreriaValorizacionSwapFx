"""
El módulo de índices se encarga de proveer la información y configuración de los principales índices de mercado.
"""

from finrisklib.enums import IndexType
from finrisklib.enums import Periodicity
from finrisklib.enums import DayCount
from finrisklib.enums import Compounding
from finrisklib.enums import FinancialIndex
from finrisklib.finriskconfig import index_config
from finrisklib.exceptions import IndexException

# region Indices


class Index:
    """Clase base Índice

    Representa un índice financiero

    :param name: Nombre.
    :type name: str
    :param idx_type: Tipo de índice.
    :type idx_type: IndexType
    :param periodicity: Periodicidad.
    :type periodicity: Periodicity
    :param day_count: Convención de conteo de días.
    :type day_count: day_count
    :param compounding: Convención de composición.
    :type compounding: Compounding
    """

    def __init__(self, name: str, idx_type: IndexType, periodicity: Periodicity,
                 day_count: DayCount, compounding: Compounding):
        """Constructor"""
        self.name = name
        self.idx_type = idx_type
        self.periodicity = periodicity
        self.day_count = day_count
        self.compounding = compounding

    def __hash__(self):
        return hash((self.name, self.idx_type))

    def __str__(self):
        """
        Sobrecarga de string

        :return:
        """
        return f'{self.name}'

    def __repr__(self):
        """
        Sobrecarga de representación

        :return:
        """
        return f'{self.name}'

    def __eq__(self, other):
        """
        Sobrecarga la comparación de igualdad entre dos objetos Índice

        :param other: Objeto.
        :return: Booleano con resultado de comparación
        """
        if isinstance(other, Index):
            return self.name == other.name and \
                   self.idx_type == other.idx_type
        return False

    def to_enum(self):
        return FinancialIndex.from_str(self.name)

    @staticmethod
    def generate(index_name: FinancialIndex, day_count: DayCount = None,
                 compounding: Compounding = None):

        if compounding is None:
            compounding = Compounding.from_str(index_config[index_name]['compound'])

        if day_count is None:
            day_count = DayCount.from_str(index_config[index_name]['count'])

        if type(index_name) != type(FinancialIndex):
            index_name = FinancialIndex.from_str(str(index_name))

        if index_name in index_config.keys():
            try:
                idx_type = IndexType.from_str(index_config[index_name]['type'])
                periodicity = Periodicity.from_str(index_config[index_name]['period'])

                return Index(name=str(index_name), idx_type=idx_type, periodicity=periodicity,
                             day_count=day_count, compounding=compounding)

            except Exception:
                message = f'Uncategorized exception occurred while generating {index_name} index'
                raise IndexException(idx_name=index_name, message=message)
        else:
            message = f'Could not generate Index object for {index_name} index'
            raise IndexException(idx_name=index_name, message=message)

# endregion
