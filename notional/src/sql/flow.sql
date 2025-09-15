-- select c.date AS asofdate, isnull(f.flow, 0) flow
-- from dbo.calendar c left join (
-- select jcpInvestments.resetDate asofdate,flow
-- from dbo.jcpInvestments
-- where
--    jcpInvestments.clientId = :client and
--    jcpInvestments.stratId = :strategy and
--    jcpInvestments.canceled = 0
-- )f on
--    f.asofdate = c.date
-- where
--    c.business_day = 1 and
--    c.date >= :date_start and
--    c.date <= :date_end
-- order by c.date;
SELECT
    c.date AS asofdate,
    ISNULL(f.flow, 0) AS flow
FROM dbo.calendar c
LEFT JOIN (
    SELECT
        jcpInvestments.resetDate AS asofdate,
        flow
    FROM dbo.jcpInvestments
    WHERE
        jcpInvestments.clientId = {client} AND
        jcpInvestments.stratId = {strategy} AND
        jcpInvestments.canceled = 0
) f ON f.asofdate = c.date
WHERE
    c.business_day = 1 AND
    c.date >= {date_start} AND
    c.date <= {date_end}
ORDER BY
    c.date;
