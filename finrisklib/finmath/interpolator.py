"""
Clases dedicadas a la interpolación y extrapolación de vectores
"""

import math
from finrisklib.enums import InterpolationMethod
from finrisklib.enums import ExtrapolationMethod


class Interpolator:
    """
    Clase estática dedicada a la interpolación y extrapolación de vectores

    :note: La clase se encuentra enfocada en la practicidad de uso, ya que puede ser llamada directamente sin necesidad
           de alguna inicialización, además el método :func:`interpolate` se encarga de apuntar a la interpolación
           requerida basándose en el método de interpolación o extrapolación especificado. Sin embargo, esto tiene un
           coste en eficiencia si se requieren hacer gran cantidad de interpolaciones, porque el proceso realizará
           siempre chequeos de seguridad (largo de vectores) y búsqueda de índices en el vértice x. Si es que se
           requiere hacer miles de interpolaciones sobre un mismo vector, lo recomendable es generar un nuevo vector
           con todos los puntos interpolados para que estos sean mantenidos en memoria y se reduzca el tiempo de
           ejecución. Esta decisión se deja al usuario.
    """

    @staticmethod
    def interpolate(point, x_vector, y_vector, interpolation_method=InterpolationMethod.LINEAR,
                    extrapolation_method=ExtrapolationMethod.SLOPE) -> float:
        """Función de interpolación.

        :param point: Punto a interpolar.
        :type point: float
        :param x_vector: Eje x.
        :type x_vector: list[]
        :param y_vector: Eje y.
        :type y_vector: list[]
        :param interpolation_method: Método de interpolación (default: Lineal)
        :type interpolation_method: InterpolationMethod
        :param extrapolation_method: Método de extrapolación (default: Pendiente)
        :type extrapolation_method: ExtrapolationMethod

        :return: Punto interpolado

        :raises ValueException: Cuando la longitud de los vectores x e y no son iguales.
        """

        # Levanta excepción en caso los vectores no sean del mismo tamaño
        if len(x_vector) != len(y_vector):
            raise ValueError("x and y vector must be on equal length")
        # En caso el punto buscado ya existe en el vector X se obtiene índice y se devuelve valor correspondiente
        if point in x_vector:
            index = x_vector.index(point)
            return y_vector[index]
        # Si el punto es menor al minimo o mayor al máximo se usa una extrapolación
        if point < min(x_vector) or point > max(x_vector):
            if extrapolation_method == ExtrapolationMethod.SLOPE:
                return Interpolator.extrapolate_slope(point=point, x_vector=x_vector, y_vector=y_vector)
            if extrapolation_method == ExtrapolationMethod.LOG_SLOPE:
                return Interpolator.extrapolate_log_slope(point=point, x_vector=x_vector, y_vector=y_vector)
            if extrapolation_method == ExtrapolationMethod.RATE_SLOPE:
                return Interpolator.extrapolate_rate_slope(point=point, x_vector=x_vector, y_vector=y_vector)
            if extrapolation_method == ExtrapolationMethod.FLAT:
                return Interpolator.extrapolate_flat(point=point, x_vector=x_vector, y_vector=y_vector)
            if extrapolation_method == ExtrapolationMethod.FLAT_RATE:
                return Interpolator.extrapolate_flat_rate(point=point, x_vector=x_vector, y_vector=y_vector)
        else:  # Si el punto se encuentra entre el máximo y el minimo se aplica una interpolación
            if interpolation_method == InterpolationMethod.LINEAR:
                return Interpolator.interpolate_linear(point=point, x_vector=x_vector, y_vector=y_vector)
            if interpolation_method == InterpolationMethod.LOG_LINEAR:
                return Interpolator.interpolate_log_linear(point=point, x_vector=x_vector, y_vector=y_vector)

    @staticmethod
    def interpolate_linear(point, x_vector, y_vector) -> float:
        r"""Interpolación Lineal

        Genera una interpolación lineal para un punto especificado de acuerdo a la siguiente fórmula:

        .. math::

            y = y_2\cdot\alpha + y_1\cdot(1-\alpha)

        Donde:

        .. math::

            \alpha = \frac{(x - x_1)}{x_2-x_1}

        :param point: Punto a interpolar.
        :type point: float
        :param x_vector: Eje x.
        :type x_vector: List[]
        :param y_vector: Eje y.
        :type y_vector: List[]

        :return: Punto interpolado

        :raises ValueException: Cuando la longitud de los vectores x e y no son iguales.
        """

        Interpolator._validate_for_interpolation(point, x_vector, y_vector)

        # En caso el punto buscado ya existe en el vector X se obtiene índice y se devuelve valor correspondiente
        if point in x_vector:
            index = x_vector.index(point)
            return y_vector[index]

        # Buscamos indice del punto
        alpha, y_1, y_2 = Interpolator._get_vector_values(point, x_vector, y_vector)
        y = y_2*alpha + y_1*(1-alpha)

        return y

    @staticmethod
    def interpolate_log_linear(point, x_vector, y_vector) -> float:
        r"""Interpolación Log-lineal

        Genera una interpolación Log-Lineal para un punto especificado de acuerdo a la siguiente fórmula:

        .. math::

            y = y_2^{\alpha}\cdot y_1^{1-\alpha}

        Donde:

        .. math::

            \alpha = \frac{(x - x_1)}{x_2-x_1}

        :param point: Punto a interpolar.
        :type point: float
        :param x_vector: Eje x.
        :type x_vector: List[]
        :param y_vector: Eje y.
        :type y_vector: List[]

        :return: Punto interpolado

        :raises ValueException: Cuando la longitud de los vectores x e y no son iguales.
        """

        Interpolator._validate_for_interpolation(point, x_vector, y_vector)

        # En caso el punto buscado ya existe en el vector X se obtiene índice y se devuelve valor correspondiente
        if point in x_vector:
            index = x_vector.index(point)
            return y_vector[index]

        # Buscamos indice del punto
        alpha, y_1, y_2 = Interpolator._get_vector_values(point, x_vector, y_vector)
        y = math.pow(y_2, alpha)*math.pow(y_1, 1-alpha)
        return y

    @staticmethod
    def extrapolate_slope(point, x_vector, y_vector) -> float:
        r"""Extrapolación por pendiente

        Genera una extrapolación manteniendo la última pendiente para un punto especificado de acuerdo a la siguiente
        fórmula si el punto es mayor al último valor del eje x:

        .. math::

            y = y_n + (x - x_n)\frac{y_n-y_{n-1}}{x_n-x_{n-1}}

        En el caso en que el primer punto sea menor al primer punto del eje X se tiene la siguiente fórmula:

        .. math::

            y = y_1 - (x_1 - x)\frac{y_2-y_1}{x_2-x_1}

        :param point: Punto a extrapolar.
        :type point: float
        :param x_vector: Eje x.
        :type x_vector: List[]
        :param y_vector: Eje y.
        :type y_vector: List[]

        :return: Punto extrapolado

        :raises ValueException: Cuando la longitud de los vectores x e y no son iguales.
        """
        Interpolator._validate_for_extrapolation(point, x_vector, y_vector)

        # En caso el punto buscado ya existe en el vector X se obtiene índice y se devuelve valor correspondiente
        if point in x_vector:
            index = x_vector.index(point)
            return y_vector[index]

        if point < min(x_vector):
            y = y_vector[0] - (x_vector[0]-point)*((y_vector[1]-y_vector[0])/(x_vector[1]-x_vector[0]))
        else:
            n = len(y_vector)-1
            y = y_vector[n] + (point - x_vector[n]) * ((y_vector[n] - y_vector[n-1]) / (x_vector[n] - x_vector[n-1]))
        return y

    @staticmethod
    def extrapolate_log_slope(point, x_vector, y_vector) -> float:
        r"""Extrapolación por pendiente logarítmica

        Genera una extrapolación manteniendo la última pendiente logarítmica para un punto especificado de acuerdo a la
        siguiente fórmula si el punto es mayor al último valor del eje x:

        .. math::

            y = y_n\cdot e^{(x - x_n)\frac{ln(y_n)-ln(y_{n-1})}{x_n-x_{n-1}}}

        En el caso en que el primer punto sea menor al primer punto del eje X se tiene la siguiente fórmula:

        .. math::

            y = y_1\cdot e^{-(x_1 - x)\frac{ln(y_2)-ln(y_1)}{x_2-x_1}}

        :param point: Punto a extrapolar.
        :type point: float
        :param x_vector: Eje x.
        :type x_vector: List[]
        :param y_vector: Eje y.
        :type y_vector: List[]

        :return: Punto extrapolado

        :raises ValueException: Cuando la longitud de los vectores x e y no son iguales.
        """
        Interpolator._validate_for_extrapolation(point, x_vector, y_vector)

        # En caso el punto buscado ya existe en el vector X se obtiene índice y se devuelve valor correspondiente
        if point in x_vector:
            index = x_vector.index(point)
            return y_vector[index]

        if point < min(x_vector):
            y = y_vector[0]*math.exp(-(x_vector[0]-point)*((math.log(y_vector[1])-math.log(y_vector[0]))/(x_vector[1] -
                                                                                                          x_vector[0])))
        else:
            n = len(y_vector) - 1
            y = y_vector[n]*math.exp((point-x_vector[n]) * ((math.log(y_vector[n]) - math.log(y_vector[n-1])) /
                                                            (x_vector[n] - x_vector[n-1])))
        return y

    @staticmethod
    def extrapolate_flat(point, x_vector, y_vector) -> float:
        r"""Extrapolación plana

        Genera una extrapolación plana manteniendo el valor conocido más cercano.

        :param point: Punto a extrapolar.
        :type point: float
        :param x_vector: Eje x.
        :type x_vector: List[]
        :param y_vector: Eje y.
        :type y_vector: List[]

        :return: Punto extrapolado

        :raises ValueException: Cuando la longitud de los vectores x e y no son iguales.
        """

        Interpolator._validate_for_extrapolation(point, x_vector, y_vector)

        # En caso el punto buscado ya existe en el vector X se obtiene índice y se devuelve valor correspondiente
        if point in x_vector:
            index = x_vector.index(point)
            return y_vector[index]

        if point < min(x_vector):
            y = y_vector[0]
        else:
            n = len(y_vector) - 1
            y = y_vector[n]
        return y

    @staticmethod
    def extrapolate_flat_rate(point, x_vector, y_vector) -> float:
        r"""Extrapolación plana

        Genera una extrapolación plana manteniendo el valor conocido más cercano tratándolo como una tasa YIELD ACT/360.

        :param point: Punto a extrapolar.
        :type point: float
        :param x_vector: Eje x.
        :type x_vector: List[]
        :param y_vector: Eje y.
        :type y_vector: List[]

        :return: Punto extrapolado

        :raises ValueException: Cuando la longitud de los vectores x e y no son iguales.
        """

        Interpolator._validate_for_extrapolation(point, x_vector, y_vector)

        # En caso el punto buscado ya existe en el vector X se obtiene índice y se devuelve valor correspondiente
        if point in x_vector:
            index = x_vector.index(point)
            return y_vector[index]

        if point < min(x_vector):
            r = math.pow(1/y_vector[0], 360/x_vector[0])-1
            y = math.pow(1+r, -point/360)
        else:
            n = len(y_vector) - 1
            r = math.pow(1/y_vector[n], 360/x_vector[n])-1
            y = math.pow(1+r, -point/360)
        return y

    @staticmethod
    def extrapolate_rate_slope(point, x_vector, y_vector) -> float:
        r"""Extrapolación por tasa YIELD Act/360

        Genera una extrapolación manteniendo la última pendiente para un punto especificado bajo una tasa YIELD Act/360
        de acuerdo a la siguiente fórmula si el punto es mayor al último valor del eje x:

        .. math::

            r = r_n + (x - x_n)\frac{r_n-r_{n-1}}{x_n-x_{n-1}}

            y = (1+r)^{(-x/360)}

        En el caso en que el primer punto sea menor al primer punto del eje X se tiene la siguiente fórmula:

        .. math::

            r = r_1 - (x_1 - x)\frac{r_2-r_1}{x_2-x_1}

            y = (1+r)^{(-x/360)}

        :param point: Punto a extrapolar.
        :type point: float
        :param x_vector: Eje x.
        :type x_vector: List[]
        :param y_vector: Eje y.
        :type y_vector: List[]

        :return: Punto extrapolado

        :raises ValueException: Cuando la longitud de los vectores x e y no son iguales.
        """
        Interpolator._validate_for_extrapolation(point, x_vector, y_vector)

        # En caso el punto buscado ya existe en el vector X se obtiene índice y se devuelve valor correspondiente
        if point in x_vector:
            index = x_vector.index(point)
            return y_vector[index]

        if point < min(x_vector):
            r_0 = math.pow(1/y_vector[0], 360.00/x_vector[0])-1
            r_1 = math.pow(1 / y_vector[1], 360.00/x_vector[1]) - 1
            slope = ((r_1-r_0)/(x_vector[1]-x_vector[0]))

            r = r_0 - (x_vector[0]-point)*slope
            y = math.pow(1 + r, -point / 360.00)
        else:
            n = len(y_vector)-1

            r_n = math.pow(1 / y_vector[n], 360.00/x_vector[n]) - 1
            r_n_1 = math.pow(1 / y_vector[n-1], 360.00/x_vector[n-1]) - 1
            slope = ((r_n - r_n_1) / (x_vector[n] - x_vector[n-1]))

            r = r_n + (point - x_vector[n]) * slope
            y = math.pow(1 + r, -point / 360.00)
        return y

    @staticmethod
    def _validate_for_interpolation(point, x_vector, y_vector):
        """
        Función privada para validar los vectores utilizados en la interpolación
        """
        # Levanta excepción en caso los vectores no sean del mismo tamaño
        if len(x_vector) != len(y_vector):
            raise ValueError("x and y vector must be on equal length")

        # Si el punto es menor al minimo o mayor al máximo se usa una extrapolación
        if not (min(x_vector) < point < max(x_vector)):
            raise ValueError(f'Point {point} must be between the lowest and the highest value of the x Vector.')

    @staticmethod
    def _validate_for_extrapolation(point, x_vector, y_vector):
        """
        Función privada para validar los vectores utilizados en la extrapolación
        """
        # Levanta excepción en caso los vectores no sean del mismo tamaño
        if len(x_vector) != len(y_vector):
            raise ValueError("x and y vector must be on equal length")

        # Si el punto es menor al minimo o mayor al máximo se usa una interpolación
        if min(x_vector) < point < max(x_vector):
            raise ValueError(f'Point {point} must be between lower than the lowest value or higher than the highest '
                             f'value of the x Vector.')

    @staticmethod
    def _get_vector_values(point, x_vector, y_vector):
        """
        Función privada para la obtención de valores de los vectores
        """
        idx = next(x[0] for x in enumerate(x_vector) if x[1] > point)
        x_1 = x_vector[idx - 1]
        x_2 = x_vector[idx]
        y_1 = y_vector[idx - 1]
        y_2 = y_vector[idx]

        alpha = (point - x_1) / (x_2 - x_1)

        return alpha, y_1, y_2
