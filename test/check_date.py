from datetime import datetime

print(f"Current date: {datetime.now()}")
print(f"Current year-week: {datetime.now().strftime('%Y-%W')}")
print(f"Current ISO week: {datetime.now().isocalendar()}")
print(f"Current ISO year-week: {datetime.now().isocalendar()[0]}-{datetime.now().isocalendar()[1]}")

