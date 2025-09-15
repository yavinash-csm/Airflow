select c.date AS asofdate, isnull(t.comm, 0) commsn
from dbo.calendar c left join (
select  '20'+substring(trade_id, 1, 2)+'-'+substring(trade_id, 3, 2)+'-'+substring(trade_id, 5, 2) asofdate, 
sum(commission_broker+commission_exchange) comm
from jam_trades  
where
   canceled = 0 and
   trade_id like '2506%' and
   trader_changed_orig = {client}
group by '20'+substring(trade_id, 1, 2)+'-'+substring(trade_id, 3, 2)+'-'+substring(trade_id, 5, 2)
)t on c.date = t.asofdate
where
   c.business_day = 1 and
   c.date >= {date_start} and
   c.date <= {date_end}
order by c.date