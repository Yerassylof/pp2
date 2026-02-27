from datetime import datetime, timedelta

def parse(line):
    dt_part, tz_part = line.rsplit(' ', 1)
    dt = datetime.strptime(dt_part, "%Y-%m-%d %H:%M:%S")
    sign = 1 if tz_part[3] == '+' else -1
    hh, mm = map(int, tz_part[4:].split(':'))
    offset = sign * (hh*3600 + mm*60)
    return dt - timedelta(seconds=offset)

start = parse(input().strip())
end = parse(input().strip())

duration = int((end - start).total_seconds())
print(duration)