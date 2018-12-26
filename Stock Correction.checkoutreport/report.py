from api.reports import ExportDateTimeType, ExportStringType, ExportNumericType, ExportCurrencyType
from api.reports import Database, and_, timedelta
from db.transaction import CorrectTransaction as Correction

name = 'Stock Correction'
version = '1.0'
description = ''
icon = 'icon.png'
isExportable = False
dateSelection = True

localizeHeader = True

exportColumnTypes = [
    ExportDateTimeType,
    ExportStringType,
    ExportStringType,
    ExportStringType,
    ExportStringType,
    ExportStringType,
    ExportNumericType,
    ExportCurrencyType,
    # taxes will be inserted here
    ExportCurrencyType,
    ExportStringType,
    ExportStringType]

exportColumnWidths = [
    70,
    50,
    50,
    40,
    40,
    60,
    35,
    40,
    # taxes will be inserted here
    40,
    35,
    50]


def data(dateRange):

    allInvoices = Database.query(Correction).filter(and_(
        Correction.date >= dateRange['begin'],
        Correction.date <= dateRange['end'] + timedelta(days=1),
        Correction.id_parent == None)).order_by(Correction.id.desc())  # noqa

    return {
        'allInvoices': allInvoices,
        'grandTotalCost': sum([c.totalCost() for c in allInvoices])
        }


def exportRows(dateRange):

    return exportRows
