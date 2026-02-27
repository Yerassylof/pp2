from datetime import datetime, timedelta, timezone
import math

def parse_line(line):
    date_part, tz_part = line.split()
    
  
    dt = datetime.strptime(date_part, "%Y-%m-%d")
    
    
    sign = 1 if '+' in tz_part else -1
    hh, mm = map(int, tz_part[3:].split(':'))
    offset = timedelta(hours=hh, minutes=mm) * sign
    
    return dt.replace(tzinfo=timezone(offset))

line1 = input().strip()
line2 = input().strip()

dt1 = parse_line(line1).astimezone(timezone.utc)
dt2 = parse_line(line2).astimezone(timezone.utc)

delta_seconds = abs((dt1 - dt2).total_seconds())

print(int(delta_seconds // 86400))