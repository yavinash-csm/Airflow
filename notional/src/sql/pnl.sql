select  AsofDate AS asofdate, sum(jam_positions.pnlDly) pnl 
from dbo.jam_positions
where
   jam_positions.AsofDate >= {date_start} and
   jam_positions.AsofDate <= {date_end} and
   client = {client} and
   jam_positions.strategy = {strategy}
group by
   jam_positions.AsofDate  
order by   
   jam_positions.AsofDate  

   