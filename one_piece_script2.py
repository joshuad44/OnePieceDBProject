import pandas as pd
import mysql.connector


chars_df = pd.read_csv('./Characters.csv', encoding='ISO-8859-1', usecols=['name', 'episode', 'note'])

chars_df['episode'].fillna('Unknown', inplace=True)  
chars_df['note'].fillna('No description available', inplace=True)

connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='one_piece_db'
)
cursor = connection.cursor()

for _, row in chars_df.iterrows():
    cursor.execute("SELECT episode_id FROM Episode WHERE episode_id = %s", (row['episode'],))
    result = cursor.fetchone()

    if result:
        first_episode_id = result[0]
        cursor.execute(
            "INSERT INTO OPCharacter (name, description, first_episode_id) VALUES (%s, %s, %s)",
            (row['name'], row['note'], first_episode_id)
        )
    else:
        print(f"Episode {row['episode']} not found, skipping character.")
    
connection.commit()
cursor.close()
connection.close()
