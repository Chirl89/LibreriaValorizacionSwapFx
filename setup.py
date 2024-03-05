from setuptools import setup

setup(
    name='finrisklib',
    version='2.0.0',
    packages=['finrisklib', 'finrisklib.data', 'finrisklib.finmath', 'finrisklib.instruments',
              'finrisklib.market'],
    install_requires=['pandas', 'openpyxl', 'pyodbc', 'sqlalchemy', 'IPython', 'python-dateutil',
                      'kaleido', 'plotly', 'matplotlib'],
    author='Gerencia de Riesgo Financiero',
    description='Librería de Funciones de Riesgo Financiero',
    python_requires=">=3.6"
)
