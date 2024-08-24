import sqlite3
import time
from datetime import date
import seaborn
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import io

total_work_hours = 4
work_chunk_hours = 1

def countdown(t): 
    while t: 
        mins, secs = divmod(t, 60) 
        timer = '{:02d}:{:02d}'.format(mins, secs) 
        print(timer, end="\r") 
        time.sleep(1) 
        t -= 1
    print('You may rest now!') 

print("Streaks: work timer and log - 4 hours of works in 1 hour chunks!\n")

conn = sqlite3.connect('main.db')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS streaks (
                date DATE PRIMARY KEY,
                hours_worked INTEGER
                )''')
conn.commit()

today = date.today().strftime('%Y-%m-%d')
query = """
SELECT hours_worked
FROM streaks
WHERE date = ?
"""
cur.execute(query, (today,))
hours_worked = cur.fetchone()

if not hours_worked or ( hours_worked[0] < total_work_hours):
    print("Ctrl+C to stop timer")
    if hours_worked:
        print(f"You have worked {hours_worked[0]} hour(s) already!")
    countdown(int(work_chunk_hours * 3600))

    cur.execute("SELECT hours_worked FROM streaks WHERE date = ?", (today,))
    result = cur.fetchone()
    if result:
        new_hours = result[0] + 1
    else:
        new_hours = 1

    query = """
      INSERT OR REPLACE INTO streaks (date, hours_worked)
      VALUES (?, ?)
      """
    cur.execute(query, (today, new_hours))
    conn.commit()

    cur.execute("SELECT date, hours_worked from streaks")
    res = cur.fetchall()

    df = pd.DataFrame(res, columns=['date', 'hours_worked'])
    df['date'] = pd.to_datetime(df['date'])
    df['day'] = df['date'].dt.day
    df['year_month'] = df['date'].dt.strftime('%Y-%B')

    grid = df.pivot(index='year_month', columns='day', values='hours_worked')    
    plt.figure(figsize=(15, 8))
    sns.heatmap(grid, annot=True, fmt='g', cmap='coolwarm', cbar=False, linewidths=.5)

    plt.xlabel('Day of Month')
    plt.ylabel('Year-Month')
    plt.title('Hours Worked by Day and Year-Month')
    plt.savefig('hours_worked.png')
    
    print(f"Hours worked for {today} incremented to {new_hours}.")
else:
    print("You have worked 4 hours")
    
conn.close()
