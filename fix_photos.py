import sqlite3

conn = sqlite3.connect('showroom.db')

# Fix Mercedes C200 - was wrongly set to Subaru files
conn.execute("UPDATE cars SET images='mercedes_1.png,mercedes_2.png,mercedes_3.png,mercedes_4.png' WHERE id=2")

# Fix Toyota Prado - was wrongly set to BMW files
conn.execute("UPDATE cars SET images='prado_1.png,prado_2.png,prado_3.png,prado_4.png' WHERE id=3")

# Fix Subaru Outback - files have a space, use correct names
conn.execute("UPDATE cars SET images='Subaru_1.png,Subaru_2.png,Subaru_3.png,Subaru_4.png' WHERE id=4")

# Fix BMW - give it the BMW files that are currently on Prado
conn.execute("UPDATE cars SET images='BMW_1.png,BMW_2.png,BMW_3.png,BMW_4.png' WHERE id=5")

# Fix Honda
conn.execute("UPDATE cars SET images='Honda_1.png,Honda_2.png,Honda_3.png,Honda_4.png,Honda_5.png' WHERE id=6")

conn.commit()

print("FIXED! Here is the result:")
for row in conn.execute("SELECT id, title, images FROM cars"):
    print(f"\n  ID={row[0]}: {row[1]}")
    print(f"  Images: {row[2]}")

conn.close()