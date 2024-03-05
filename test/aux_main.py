import pandas as pd

# from data.dbreader import DBReader
from finrisklib.enums import Source
from finrisklib.data.dbreader import DBReader
from finrisklib.data.dbconnection import SQLConn
from finrisklib.data.filereader import XlsReader
from finrisklib.market.dataset import DataSet
from datetime import date
from dateutil.relativedelta import relativedelta

def valuate_portfolio(process_date, source):

    reader = DBReader()

    dataset = reader.get_dataset(process_date=process_date, source=source)
    portfolio = reader.get_portfolio(process_date=process_date, source=source)

    file_name = f"C:/Users/ECGL1495/Desktop/Replicas/replica_portafolio_{process_date.strftime('%Y%m%d')}.xlsx"
    portfolio.valuate_to_excel(dataset=dataset, file_name=file_name)

def valuate_single_operation(process_date, id_number, source):
    reader = DBReader()

    dataset = reader.get_dataset(process_date=process_date, source=source)

    official_operation = reader.get_operation(id_number=id_number, process_date=process_date)
    official_mtm = reader.get_official_mtm(id_number=id_number, process_date=process_date)

    findur_val = official_operation.valuate(dataset=dataset)
    details = official_operation.valuation_to_dataframe(dataset=dataset)
    details.to_excel(f"C:/Users/ECGL1495/Desktop/Replicas/replica_op_{str(id_number)}_{process_date.strftime('%Y%m%d')}.xlsx")
    print(f'Oficial: {official_mtm}')
    print(f'Replica: {findur_val}')
    print(f'diferencia {official_mtm.amount - findur_val.amount}')

if __name__ == "__main__":
    process_date_1 = date(year=2023, month=11, day=20)
    # process_date_2 = date(year=2023, month=10, day=5)
    # process_date_3 = date(year=2023, month=10, day=6)
    id_number = 3106

    valuate_single_operation(process_date=process_date_1, id_number=id_number, source=Source.OFFICIAL)
    # valuate_single_operation(process_date=process_date_2, id_number=id_number, source=Source.MUREX)
    # valuate_single_operation(process_date=process_date_3, id_number=id_number, source=Source.MUREX)
    # valuate_portfolio(process_date=process_date_1, source=Source.MUREX)
    # valuate_portfolio(process_date=process_date_1, source=Source.OFFICIAL)
