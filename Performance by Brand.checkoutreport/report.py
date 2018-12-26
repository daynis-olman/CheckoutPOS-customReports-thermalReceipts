from api.reports import ExportStringType, ExportIntegerType, ExportCurrencyType, ExportNumericType
from api.reports import Database, db_result_cleanse

name = 'Performance By Brand'
version = '3.0'
description = 'Lists sales revenue, quantity, and percentage of total revenue per brand'
icon = 'icon.png'
isExportable = True
dateSelection = True

localizeHeader = True
exportColumnTypes = [ExportStringType, ExportIntegerType, ExportCurrencyType, ExportNumericType]
exportColumnWidths = [50, 50, 50, 50, 50]


def per_brand_performance(date_range):
    return db_result_cleanse(Database.execute("""
        SELECT
            util.value(ii.id_item,'brand') AS brand,
            COALESCE(SUM(ii.quantity),0) AS quantity,
            COALESCE(SUM(util.bankers_round(ii.price_ex)),0) AS revenue,
            round(
                COALESCE(
                    SUM(ii.price_ex),0) / COALESCE((
                                            SELECT GREATEST(
                                                SUM(ii2.price_ex),
                                                0.00001)
                                            FROM
                                                util.invoice_item AS ii2
                                            WHERE
                                                ii2.date::date BETWEEN :begin AND :end),
                                            1) * 100,1) AS percentage_revenue
        FROM
            util.invoice_item AS ii
        WHERE
            ii.date::date BETWEEN :begin AND :end
        GROUP BY
            brand
        ORDER BY
            percentage_revenue DESC;
        """, date_range).fetchall())


def performance_grand_totals(date_range):
    return Database.execute("""
        SELECT
            COALESCE(SUM(ii.quantity),0) AS quantity,
            COALESCE(SUM(util.bankers_round(ii.price_ex)),0) AS revenue
        FROM
            util.invoice_item AS ii
        WHERE
            ii.date::date BETWEEN :begin AND :end;
        """, date_range).fetchall()[0]


def per_brand_product_performance(brand, date_range):
    d = dict(date_range)
    d['brand'] = brand
    if brand is None:
        brand_query = 'IS NULL'
    else:
        brand_query = '= :brand'
    return db_result_cleanse(Database.execute("""
        SELECT
            util.value(ii.id_item,'name') AS name,
            COALESCE(SUM(ii.quantity),0) AS quantity,
            COALESCE(SUM(util.bankers_round(ii.price_ex)),0) AS revenue,
            round(COALESCE(SUM(ii.price_ex), 0) / GREATEST(
                (SELECT
                    SUM(ii2.price_ex)
                FROM
                    util.invoice_item AS ii2
                WHERE
                    ii2.date::date BETWEEN :begin AND :end AND
                    util.value(ii2.id_item,'brand') {brand_query}),
                0.00001) * 100,
                1) AS percentage_revenue
        FROM
            util.invoice_item AS ii
        WHERE
            ii.date::date BETWEEN :begin AND :end AND
            util.value(ii.id_item,'brand') {brand_query}
        GROUP BY
            ii.id_item,name
        ORDER BY
            percentage_revenue DESC;
        """.format(brand_query=brand_query), d).fetchall())


def top_5_grossing_brands(date_range):
    return db_result_cleanse(Database.execute("""
        SELECT
            util.value(ii.id_item,'brand') AS brand,
            COALESCE(SUM(ii.quantity),0) AS quantity,
            COALESCE(SUM(util.bankers_round(ii.price_ex)),0) AS revenue
        FROM
            util.invoice_item AS ii
        WHERE
            ii.date::date BETWEEN :begin AND :end
        GROUP BY
            brand
        ORDER BY
            revenue DESC
        LIMIT 5;
        """, date_range).fetchall())


def data(date_range):
    date_range = dict(date_range)
    top5 = top_5_grossing_brands(date_range)
    top5_products = []
    for brand in top5:
        top5_products.append(per_brand_product_performance(brand['brand'], date_range))

    per_brand_report = per_brand_performance(date_range)
    performance_totals = performance_grand_totals(date_range)
    return {
        'brands': per_brand_report,
        'top5_brands': top5,
        'top5_brand_products': top5_products,
        'performance_totals': performance_totals}


def fast_export_rows(exportData):
    per_brand_performance_data = exportData['brands']

    rows = [[u'Brand', u'Quantity Sold', u'Total', u'Percentage']]

    for row in per_brand_performance_data:
        rows.append([row[v] for v in ('brand', 'quantity', 'revenue', 'percentage_revenue')])

    return rows


def exportRows(date_range):

    return fast_export_rows(data(date_range))
