import sqlite3
conn = sqlite3.connect('poker.db')
c = conn.cursor()

game_ids = set() #set used to exclude duplicate game_ids

#create game_id using timestamp
def createGameID(game):
    conflict = False
    first_line_words = game[0].split(' ')
    date = first_line_words[3].strip('\n')
    date_vals = date.split('/')
    time = first_line_words[4].strip('\n')
    time_vals = time.split(':')
    
    #enforce consistent formatting (2016/9/26 -> 20160926)
    for i in range(3):
        if len(date_vals[i]) == 1:
            date_vals[i] = '0' + date_vals[i]
        if len(time_vals[i]) == 1:
            time_vals[i] = '0' + time_vals[i]
    game_id = ''.join(date_vals) + ''.join(time_vals)
    if game_id not in game_ids:
        game_ids.add(game_id)
    else:
        conflict = True
    return game_id, conflict

def parse_games(filename):
    lines = open(filename ,"r").readlines()
    games = []
    for line in lines:
        words = line.split(' ')
        if words[0] == "Game" and words[1] == "started":
            games.append([])
        if len(words) > 0:
            games[-1].append(line)

    # data information for Hands table
    player_IDs = []
    game_IDs = []
    card_1 = []
    card_2 = []
    bets = []
    net_gain = []
    chip_stack = []

    # parse game information and insert into Games table
    for game in games:
        game_id, conflict = createGameID(game)
        if conflict:
            continue
        stakes = game[1].split(' ')[3]
        big_blind = stakes.split("/")[1]
        cards = [None]*5
        for line in game:
            words = line.split(" ")
            # get info about the 5 cards on the board
            if words[0] == "Board:":
                cards_info = words[1:]
                for i in range(len(cards_info)):
                    cards[i] = cards_info[i].strip("[]\n")

        c.execute('''INSERT INTO Games VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', \
                (game_id, 'k', big_blind, cards[0], cards[1], cards[2], cards[3], cards[4], None, None, None, None))

    # parse hand information and insert into Hands table
        game_length = len(game)
        for line in game:
            words = line.split(' ')
            if words[0] == 'Seat' and len(words[1]) == 2:
                # get info on game_id
                game_IDs.append(game_id)
                # get info on player_id
                player_IDs.append(' '.join(words[2:-1]))
                # get info on chip stack
                chip_stack.append(float(words[-1].strip('().\r\n')))
            if line == '------ Summary ------\n':
                summary_index = game.index(line)
                for i in range(summary_index, game_length):
                    summary_words = game[i].split(' ')
                    summary_line_length = len(summary_words)
                    if summary_words[0] == 'Player' or summary_words[0] == '*Player':
                        if summary_words[2] == 'shows:':
                            for word in summary_words:
                                # get info on first card
                                if word.startswith('['):
                                    card_1.append(word.strip('['))
                                # get info on second card
                                if word.endswith('].'):
                                    card_2.append(word.strip('].'))
                        else:
                            card_1.append(None)
                            card_2.append(None)
                    for j in range(summary_line_length):
                        if summary_words[j].endswith('Bets:'):
                            # get info on bet
                            bet_index = summary_words.index(summary_words[j]) + 1
                            bet = float(summary_words[bet_index].strip('.'))
                            bets.append(bet)
                            # get info on net gain
                            collects_index = bet_index + 2
                            collect = float(summary_words[collects_index].strip('.'))
                            net_gain.append(collect - bet)

    # parse hand information and insert into Actions table
        round_k = 0 #0 pre-flop, 1 post-flop, 2 post-turn, 3 post-river
        pos_in_round = 0 #0 for first action in round, counting up
        for line in game:
            words = line.split(" ")
            if words[0] == "***":
                round_k += 1
                pos_in_round = 0
            if words[0] == "Player":
                player_id = words[1]
                action_word = words[2].strip("\n ")
                if action_word == 'folds':
                    pos_in_round += 1
                    c.execute('''INSERT INTO Actions VALUES (?, ?, ?, ?, ?, ?)''', \
                (game_id, 'k', player_id, round_k, pos_in_round, 'f'))
                if action_word == 'calls':
                    pos_in_round += 1
                    c.execute('''INSERT INTO Actions VALUES (?, ?, ?, ?, ?, ?)''', \
                (game_id, 'k', player_id, round_k, pos_in_round, 'c'))
                if action_word == 'raises':
                    pos_in_round += 1
                    c.execute('''INSERT INTO Actions VALUES (?, ?, ?, ?, ?, ?)''', \
                (game_id, 'k', player_id, round_k, pos_in_round, 'r'))
                if action_word == 'checks':
                    pos_in_round += 1
                    c.execute('''INSERT INTO Actions VALUES (?, ?, ?, ?, ?, ?)''', \
                (game_id, 'k', player_id, round_k, pos_in_round, 'k'))
                if action_word == 'bets':
                    pos_in_round += 1
                    c.execute('''INSERT INTO Actions VALUES (?, ?, ?, ?, ?, ?)''', \
                (game_id, 'k', player_id, round_k, pos_in_round, 'b'))
                if action_word == 'allin':
                    pos_in_round += 1
                    c.execute('''INSERT INTO Actions VALUES (?, ?, ?, ?, ?, ?)''', \
                (game_id, 'k', player_id, round_k, pos_in_round, 'A'))

    for pid, gid, c1, c2, b, ng, cs in zip(player_IDs, game_IDs, card_1, card_2, bets, net_gain, chip_stack):
        c.execute('''INSERT INTO Hands VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (gid, 'k' ,pid, c1, c2, b, ng, cs))

    conn.commit()

def main():
    for file_id in range(1, 10):
        filename = "kaggle-data/kaggle_file" + str(file_id) + ".txt"
        parse_games(filename)
    
if __name__ == '__main__':
    main()
