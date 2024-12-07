import pandas as pd
import mysql.connector

arcs_df = pd.read_csv('./one_piece_arcs.csv', encoding='ISO-8859-1', usecols=['Arc Name', 'Arc Type', 'Total Episodes'])
episodes_df = pd.read_csv('./one_piece_episodes.csv', encoding='ISO-8859-1', usecols=['Episode Name', 'Episode Type', 'Year', 'Arc Name'])

connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='topher14',
    database='one_piece_db'
)
cursor = connection.cursor()

for _, row in arcs_df.iterrows():
    cursor.execute(
        "INSERT INTO Arc (arc_name, arc_type, total_episodes) VALUES (%s, %s, %s)",
        (row['Arc Name'], row['Arc Type'], row['Total Episodes'])
    )

for _, row in episodes_df.iterrows():
    cursor.execute(
        "INSERT INTO Episode (episode_name, episode_type, year, arc_name) VALUES (%s, %s, %s, %s)",
        (row['Episode Name'], row['Episode Type'], row['Year'], row['Arc Name'])
    )

connection.commit()
cursor.close()
connection.close()


