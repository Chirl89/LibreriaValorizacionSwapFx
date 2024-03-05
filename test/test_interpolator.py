from unittest import TestCase
from finrisklib.finmath.interpolator import Interpolator


class TestInterpolator(TestCase):

    def test_interpolate_linear(self):
        """
        Prueba Función de interpolación lineal
        """
        x_vector = [1, 3, 5, 7, 9]
        y_vector = [10, 30, 50, 70, 90]

        point = 4.7542154
        y_expected = 47.542154

        y_real = Interpolator.interpolate_linear(point=point, x_vector=x_vector, y_vector=y_vector)

        self.assertEqual(y_real, y_expected)

        point = 5.000
        y_expected = 50

        y_real = Interpolator.interpolate_linear(point=point, x_vector=x_vector, y_vector=y_vector)

        self.assertEqual(y_real, y_expected)

    def test_interpolate_log_linear(self):
        """
        Prueba Función de interpolación log-lineal
        """

        x_vector = [1, 3, 5, 7, 9]
        y_vector = [10, 30, 50, 70, 90]

        point = 4.75
        y_expected = 46.9071352993

        y_real = Interpolator.interpolate_log_linear(point=point, x_vector=x_vector, y_vector=y_vector)

        self.assertAlmostEqual(y_real, y_expected, places=10)

    def test_extrapolate_slope(self):
        """
        Prueba Función de extrapolación por pendiente
        """
        x_vector = [3, 5, 7]
        y_vector = [30, 50, 70]

        point = 8
        y_expected = 80

        y_real = Interpolator.extrapolate_slope(point=point, x_vector=x_vector, y_vector=y_vector)

        self.assertAlmostEqual(y_real, y_expected, places=10)

        point = 1
        y_expected = 10

        y_real = Interpolator.extrapolate_slope(point=point, x_vector=x_vector, y_vector=y_vector)

        self.assertAlmostEqual(y_real, y_expected, places=10)

    def test_extrapolate_log_slope(self):
        """
        Prueba Función de extrapolación por pendiente
        """
        x_vector = [3, 5, 7]
        y_vector = [30, 50, 70]

        point = 8
        y_expected = 82.8251169633946

        y_real = Interpolator.extrapolate_log_slope(point=point, x_vector=x_vector, y_vector=y_vector)

        self.assertAlmostEqual(y_real, y_expected, places=10)

        point = 1
        y_expected = 18

        y_real = Interpolator.extrapolate_log_slope(point=point, x_vector=x_vector, y_vector=y_vector)

        self.assertAlmostEqual(y_real, y_expected, places=10)

    def test_extrapolate_flat(self):
        """
        Prueba Función de extrapolación plana
        """
        x_vector = [3, 5, 7]
        y_vector = [30, 50, 70]

        point = 1
        y_expected = 30

        y_real = Interpolator.extrapolate_flat(point=point, x_vector=x_vector, y_vector=y_vector)

        self.assertAlmostEqual(y_real, y_expected, places=10)

        point = 8
        y_expected = 70

        y_real = Interpolator.extrapolate_flat(point=point, x_vector=x_vector, y_vector=y_vector)

        self.assertAlmostEqual(y_real, y_expected, places=10)

    def test_extrapolate_flat_rate(self):
        """
        Prueba Función de extrapolación plana en tasa yield act 360
        """
        x_vector = [30, 60, 90]
        y_vector = [0.995942407351067, 0.991116234762077, 0.985538361687288]

        point = 10
        y_expected = 0.998645635642314

        y_real = Interpolator.extrapolate_flat_rate(point=point, x_vector=x_vector, y_vector=y_vector)

        self.assertAlmostEqual(y_real, y_expected, places=10)

        point = 100
        y_expected = 0.9839444784982

        y_real = Interpolator.extrapolate_flat_rate(point=point, x_vector=x_vector, y_vector=y_vector)

        self.assertAlmostEqual(y_real, y_expected, places=10)

    def test_extrapolate_rate_slope(self):
        """
        Prueba Función de extrapolación con pendiente en tasa yield act 360
        """
        x_vector = [30, 60, 90]
        y_vector = [0.995942407351067, 0.991116234762077, 0.985074032530535]

        point = 10
        y_expected = 0.998733843607

        y_real = Interpolator.extrapolate_rate_slope(point=point, x_vector=x_vector, y_vector=y_vector)

        self.assertAlmostEqual(y_real, y_expected, places=10)

        point = 100
        y_expected = 0.982830050373

        y_real = Interpolator.extrapolate_rate_slope(point=point, x_vector=x_vector, y_vector=y_vector)

        self.assertAlmostEqual(y_real, y_expected, places=10)
