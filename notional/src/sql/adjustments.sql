 SELECT
    c.date AS asofdate,
    SUM(CASE WHEN f.adjust_type = 'COM' THEN ISNULL(f.adjust_dly, 0) ELSE 0 END) AS com_adj,
    SUM(CASE WHEN f.adjust_type = 'INT' THEN ISNULL(f.adjust_dly, 0) ELSE 0 END) AS int_adj
FROM dbo.calendar c
LEFT JOIN (
    SELECT
        jcpPnlAdjustments.business_day AS asofdate,
        jcpPnlAdjustments.adjust_dly,
        jcpPnlAdjustments.adjust_type
    FROM dbo.jcpPnlAdjustments
    WHERE
        jcpPnlAdjustments.clientId = {client} AND
        jcpPnlAdjustments.stratId = {strategy} AND
        jcpPnlAdjustments.canceled = 0 AND
        jcpPnlAdjustments.adjust_type IN ('COM', 'INT')
) f ON f.asofdate = c.date
WHERE
    c.business_day = 1 AND
    c.date >= {date_start} AND
    c.date <= {date_end}
GROUP BY
    c.date
ORDER BY
    c.date;