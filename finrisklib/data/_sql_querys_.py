# Módulo privado de almacenamiento de queries SQL

# region Consultas de curvas

# region Base Oficial

"""Curva Única Base Oficial"""
OFFICIAL_SINGLE_CURVE_QUERY = """SELECT fecha, codigocurva, tenor, mid_factor = POWER(1+ valormid/100, -tenor/360)
                                 FROM curvas 
                                 WHERE fecha = '{process_date}' and codigocurva = '{curve_name}'
                                 ORDER BY codigocurva, tenor"""

"""Curvas Base Oficial"""
OFFICIAL_CURVES_QUERY = """SELECT fecha, codigocurva, tenor, mid_factor = POWER(1+ valormid/100, -tenor/360)
                           FROM curvas 
                           WHERE fecha = '{process_date}' 
                           ORDER BY codigocurva, tenor"""

"""Nombre Curvas Oficiales"""
OFFICIAL_CURVES_NAMES_QUERY = """SELECT distinct codigocurva 
                                 FROM curvas 
                                 WHERE fecha = '{process_date}' 
                                 ORDER BY codigocurva"""

# endregion

# region Base Murex

"""Curva Única Murex"""
MUREX_SINGLE_CURVE_QUERY = """SELECT fecha_proceso, nombre_Curva, plazo, 
                              POWER(1+ZCOUPON_MID/100, -plazo/360) as Ds_fact_mid   
                              FROM MUREX_EOD_CURVAS 
                              WHERE [Fecha_proceso]= '{process_date}' 
                              and Nombre_Curva = '{curve_name}' 
                              and Ds_fact_mid <> 0
                              ORDER BY Nombre_Curva, plazo
                              """

"""Curvas Murex"""
MUREX_CURVES_QUERY = """SELECT fecha_proceso, nombre_Curva, plazo, 
                        POWER(1+ZCOUPON_MID/100, -plazo/360) as Ds_fact_mid   
                        FROM MUREX_EOD_CURVAS 
                        WHERE [Fecha_proceso]= '{process_date}' and nombre_Curva not in ('CLP ICP', 
                        'USD DAILY TERM SOFR') 
                        and Ds_fact_mid <> 0
                        ORDER BY Nombre_Curva, plazo
                        """

"""Nombre Curvas Murex"""
MUREX_CURVES_NAMES_QUERY = """SELECT distinct nombre_Curva 
                              FROM MUREX_EOD_CURVAS 
                              WHERE [Fecha_proceso]= '{process_date}' and nombre_Curva not in ('CLP ICP', 
                              'USD DAILY TERM SOFR')   
                              ORDER BY Nombre_Curva"""

# endregion

# region Sandbox

"""Curva Única Murex"""
SANDBOX_SINGLE_CURVE_QUERY = """SELECT fecha_proceso, nombreCurva, plazo, 
                                POWER(1+ZCOUPON_MID/100, -plazo/360) as Ds_fact_mid   
                                FROM EOD_MUREX_CURVAS 
                                WHERE [Fecha_proceso]= '{process_date}' and NombreCurva = '{curve_name}' 
                                and Ds_fact_mid <> 0
                                ORDER BY NombreCurva, plazo"""

"""Curvas Murex"""
SANDBOX_CURVES_QUERY = """SELECT fecha_proceso, UPPER(nombreCurva) as 'NombreCurva', plazo, 
                          POWER(1+ZCOUPON_MID/100, -plazo/360) as Ds_fact_mid 
                          FROM EOD_MUREX_CURVAS 
                          WHERE [Fecha_proceso]= '{process_date}' and nombreCurva not in ('CLP ICP', 
                          'USD DAILY TERM SOFR') 
                          and Ds_fact_mid <> 0
                          ORDER BY nombreCurva, plazo
                          """

"""Nombre Curvas Murex"""
SANDBOX_CURVES_NAMES_QUERY = """SELECT distinct nombreCurva 
                                FROM EOD_MUREX_CURVAS 
                                WHERE [Fecha_proceso]= '{process_date}' and nombreCurva not in ('CLP ICP', 
                                'USD DAILY TERM SOFR') 
                                ORDER BY NombreCurva"""


# endregion

# endregion

# region Consultas de Tipos de Cambio

# region Base Oficial

OFFICIAL_FX_QUERY = """SELECT valor
                       FROM tipocambio
                       WHERE fecha = '{process_date}'
                       AND localidad = '{primary_currency}'
                       AND moneda = '{secondary_currency}'"""

OFFICIAL_FX_RATES_QUERY = """SELECT fecha, 
                                case when localidad = 'US' and moneda in ('AUD', 'EUR', 'GBP', 'NZD') then moneda
                                     when localidad = 'CL' and moneda in ('CLF') then moneda
                                     when localidad = 'US' then 'USD'
                                     else moneda end,		 
                                case when localidad = 'US' and moneda in ('AUD', 'EUR', 'GBP', 'NZD') then 'USD'
                                     when localidad = 'CL' and moneda in ('CLF') then 'CLP'
                                     when localidad = 'US' then moneda
                                     when localidad = 'CL' then 'CLP'
                                     else localidad end, 
                                valor --valor
                             FROM banco.dbo.tipocambio
                             WHERE
                                fecha = '{process_date}'
                             and localidad <> 'BR'
                             and moneda not in ('CLD', 'DEG')
                             and not (moneda = 'USD' and localidad = 'US')
                             ORDER BY 2,3"""

# endregion

# region Base Murex

MUREX_FX_QUERY = """SELECT MID
                    FROM MUREX_EOD_Paridades
                    WHERE fecha_proceso = '{process_date}'
                    AND primera_moneda = '{primary_currency}'
                    AND segunda_moneda = '{secondary_currency}'"""


MUREX_FX_RATES_QUERY = """SELECT Fecha_proceso, Primera_moneda, segunda_moneda, mid
                          FROM MUREX_EOD_Paridades
                          WHERE fecha_proceso = '{process_date}'
                          AND PARIDAD NOT IN ('AUD/CLP', 'BRL/CLP', 'BRL/BR', 'CAD/CLP',
                                              'CHF/CLP', 'CNH/CLP', 'CNY/CLP', 'COP/CLP',
                                              'DKK/CLP', 'EUR/CLP', 'GBP/CLP', 'CLP/HKD',
                                              'JPY/CLP', 'KRW/CLP', 'MXN/CLP', 'NOK/CLP',
                                              'NZD/CLP', 'PEN/CLP', 'SEK/CLP', 'ZAR/CLP')
                          ORDER BY primera_Moneda, Segunda_Moneda"""

# endregion

# region Sandbox

SANDBOX_FX_QUERY = """SELECT MID
                      FROM EOD_MUREX_MONEDAS
                      WHERE fecha_proceso = '{process_date}'
                      AND primeramoneda = '{primary_currency}'
                      AND segundamoneda = '{secondary_currency}'"""


SANDBOX_FX_RATES_QUERY = """SELECT Fecha_proceso, Primeramoneda, segundamoneda, mid
                            FROM EOD_MUREX_MONEDAS
                            WHERE fecha_proceso = '{process_date}'
                            AND PARIDAD NOT IN ('AUD/CLP', 'BRL/CLP', 'BRL/BR', 'CAD/CLP',
                                                'CHF/CLP', 'CNH/CLP', 'CNY/CLP', 'COP/CLP',
                                                'DKK/CLP', 'EUR/CLP', 'GBP/CLP', 'CLP/HKD',
                                                'JPY/CLP', 'KRW/CLP', 'MXN/CLP', 'NOK/CLP',
                                                'NZD/CLP', 'PEN/CLP', 'SEK/CLP', 'ZAR/CLP')
                            ORDER BY primeraMoneda, SegundaMoneda"""


# endregion

# endregion

# region Consultas de Indices

# region Base Oficial

INDEX_DATA_QUERY = """SELECT IIF(marketName = 'CLICP INDEX' 
                      OR marketName = 'CLICREAL INDEX', cast(Rate as numeric(10,5)), 
                      cast(Rate as numeric(10,5))/100.00) as 'Rate'
                      FROM Indices
                      WHERE marketName = '{bbg_code}' AND case when processDate = '{process_date}' 
                      ORDER BY rateId, processdate"""

INDEX_HISTORICAL_DATA_QUERY = """SELECT marketName, IIF(marketName = 'SOFRRATE INDEX', FixingDate, processdate), 
                                 IIF(marketName = 'CLICP INDEX' 
                                 OR marketName = 'CLICREAL INDEX', cast(Rate as numeric(10,5)), 
                                 cast(Rate as numeric(10,5))/100.00) as 'Rate'
                                 FROM Indices
                                 WHERE marketName = '{bbg_code}' AND processDate BETWEEN '{start_date}' 
                                      AND '{end_date}'
                                 ORDER BY rateId, processdate"""

ALL_INDEX_HISTORICAL_DATA_QUERY = """SELECT marketName, 
                                     IIF(marketName = 'SOFRRATE INDEX', FixingDate, processdate), 
                                     IIF(marketName = 'CLICP INDEX' 
                                     OR marketName = 'CLICREAL INDEX', cast(Rate as numeric(10,5)), 
                                     cast(Rate as numeric(10,5))/100.00) as 'Rate'
                                     FROM Indices
                                     WHERE iif(marketName = 'SOFRRATE INDEX',FixingDate,processdate) 
                                        BETWEEN '{start_date}' AND '{end_date}'
                                     ORDER BY rateId, processdate"""

# endregion

# endregion

# region Consultas de Operaciones

# region Base Oficial

OPERATION_DATA_QUERY = """SELECT * FROM carteraderivados
                          WHERE fechaproceso = '{process_date}' AND numerooperacion = '{id_number}'
                          ORDER BY tipoflujo, numeroflujo"""

OPERATION_MTM_QUERY = """SELECT SUM(IIF(tipoflujo = 'ACT', mtm, -mtm)) as 'mtm' FROM carteraderivados
                         WHERE fechaproceso = '{process_date}' and numerooperacion = '{id_number}'
                         GROUP BY numerooperacion"""

# endregion

# region Base Murex

GRF_FWD_OPERATION_DATA_QUERY = """SELECT * FROM Murex_GRF_Cartera_Spot_FWD
                                  WHERE [fecha proceso] = '{process_date}'
                                  AND tp_strtgy NOT IN ('Spot_NEM','Spot FX_NEM', 'Spot')
                                  AND prod_fmly NOT IN ('FXspot', 'SwpSpotCov', 'FxForward_NEM')
                                  AND [Numero Operacion] = '{id_number}'
                                  ORDER BY [numero operacion], [tipo flujo]"""

SWAP_OPERATION_DATA_QUERY = """SELECT * FROM [MUREX_GRF_CARTERA_SWAP]
                               WHERE FECHA_PROCESO ='{process_date}'
                               AND GID = '{id_number}'
                               and moneda <> ''
                               ORDER BY GID, tipo_flujo, plazo_residual"""

GRF_COMPENSATION_CURRENCY = """SELECT distinct [Gid], [moneda_de_pago] 
                               FROM MUREX_POSCA_DERIVADOS
                               WHERE [Fecha_proceso] = '{process_date}'"""

# endregion

# endregion

# region Consultas de Portafolios

# region Base Oficial

FORWARD_DATA_QUERY = """SELECT * FROM carteraderivados
                        WHERE fechaproceso = '{process_date}' AND tipoproducto = 'FORWARD'
                        AND productooriginal <> 'Seguro de Cambio_Nem'
                        AND productooriginal <> 'Seguro de Inflación_Nem'                    
                        ORDER BY numerooperacion, tipoflujo, numeroflujo"""

SWAP_DATA_QUERY = """SELECT * FROM carteraderivados
                     WHERE fechaproceso = '{process_date}' AND tipoproducto = 'SWAP'
                     ORDER BY numerooperacion, tipoflujo, numeroflujo"""

DERIVADOS_DATA_QUERY = """SELECT * FROM carteraderivados
                          WHERE fechaproceso = '{process_date}'
                          AND productooriginal <> 'Seguro de Cambio_Nem'
                          AND productooriginal <> 'Seguro de Inflación_Nem'  
                          ORDER BY numerooperacion, tipoflujo, numeroflujo"""

# endregion

# region Base Murex

GRF_FORWARD_QUERY = """SELECT * FROM banco.dbo.Murex_GRF_Cartera_Spot_FWD
                       WHERE [fecha proceso] = '{process_date}'
                       AND tp_strtgy NOT IN ('Spot_NEM','Spot FX_NEM', 'Spot')
                       AND prod_fmly NOT IN ('FXspot', 'SwpSpotCov', 'FxForward_NEM')
                       ORDER BY [numero operacion], [tipo flujo]"""


GRF_SWAP_QUERY = """SELECT * FROM [MUREX_GRF_CARTERA_SWAP]
                    WHERE FECHA_PROCESO = '{process_date}'
                    AND moneda <> ''
                    ORDER BY GID, tipo_flujo, plazo_residual"""

# endregion

# endregion
