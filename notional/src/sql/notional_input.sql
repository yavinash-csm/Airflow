select cast(business_day as date) asofdate,notional_end
from dbo.jcpInvestmentsHistory
where
   jcpInvestmentsHistory.business_day >= {date_start} and
   jcpInvestmentsHistory.business_day <= {date_end} and
   jcpInvestmentsHistory.clientId = {client} and
   jcpInvestmentsHistory.stratId = {strategy}
order by jcpInvestmentsHistory.business_day