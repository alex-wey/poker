import sqlite3

# Import Kaggle and CPRG data here:

conn = sqlite3.connect("poker.db")
c = conn.cursor()

# Delete tables if they exist
c.execute('DROP TABLE IF EXISTS "Games";')
c.execute('DROP TABLE IF EXISTS "Hands";')
c.execute('DROP TABLE IF EXISTS "Actions";')

# Create tables in the database and add data to it.
c.execute('''CREATE TABLE Games(
    game_ID VARCHAR(256) PRIMARY KEY, 
    data_source CHAR(1),
    big_blind FLOAT, 
    card1 CHAR(2), 
    card2 CHAR(2), 
    card3 CHAR(2), 
    card4 CHAR(2), 
    card5 CHAR(2), 
    pre_flop_pot FLOAT, 
    post_flop_pot FLOAT, 
    post_turn_pot FLOAT, 
    post_river_pot FLOAT)''')

c.execute('''CREATE TABLE Hands(
    game_ID VARCHAR(256) NOT NULL, 
    data_source CHAR(1),
    player_ID VARCHAR(256) NOT NULL, 
    card1 CHAR(2), 
    card2 CHAR(2), 
    bets FLOAT, 
    net_gain FLOAT, 
    chips_at_beginning FLOAT, 
    PRIMARY KEY(player_ID, game_ID))''')

c.execute('''CREATE TABLE Actions(
    game_ID VARCHAR(256) NOT NULL, 
    data_source CHAR(1),
    player_ID VARCHAR(256) NOT NULL, 
    round_k TINYINT NOT NULL, 
    pos_in_round TINYINT NOT NULL, 
    action_id CHAR(1), 
    PRIMARY KEY(player_ID, game_ID, round_k, pos_in_round))''')

conn.commit()
