import sqlite3

conn = sqlite3.connect('showroom.db')

# Update all cars that have Nairobi to Mombasa
conn.execute("UPDATE cars SET location='Mombasa' WHERE location='Nairobi' OR location='' OR location IS NULL")
conn.commit()

print("Updated! Current locations:")
for row in conn.execute("SELECT id, title, location FROM cars"):
    print(f"  ID={row[0]}: {row[1]} → {row[2]}")

conn.close()