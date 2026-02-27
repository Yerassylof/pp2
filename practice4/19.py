import math

r = float(input())
x1, y1 = map(float, input().split())
x2, y2 = map(float, input().split())

dx = x2 - x1
dy = y2 - y1

d = math.hypot(dx, dy)

d1 = math.hypot(x1, y1)
d2 = math.hypot(x2, y2)
t = -(x1*dx + y1*dy) / (dx*dx + dy*dy)
if t < 0:
     closest_dist = d1
elif t > 1:
     closest_dist = d2
else:
     px = x1 + t*dx
     py = y1 + t*dy
     closest_dist = math.hypot(px, py)

if closest_dist >= r:
     print(f"{d:.10f}")
else:
     theta = math.acos((x1*x2 + y1*y2)/(d1*d2))
     alpha = theta - math.acos(r/d1) - math.acos(r/d2)
     length = math.sqrt(d1*d1 - r*r) + math.sqrt(d2*d2 - r*r) + r*alpha
     print(f"{length:.10f}")
