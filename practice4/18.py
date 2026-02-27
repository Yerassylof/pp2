x1, y1 = map(float, input().split())
x2, y2 = map(float, input().split())

xr = (x2 * y1 + x1 * y2) / (y1 + y2)
yr = 0.0

print(f"{xr:.10f} {yr:.10f}")