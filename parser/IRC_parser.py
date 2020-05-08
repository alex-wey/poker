import os
import tarfile
import shutil
import sqlite3

conn = sqlite3.connect('../poker.db')
c = conn.cursor()

files = os.listdir('.')

for file in files:
    if file.startswith('holdem.'):
        try:
            if os.path.isdir('./tmp'):
                print('Deleting existing tmp directory...')
                shutil.rmtree('./tmp')
            path = os.path.join('.', file)
            tar = tarfile.open(path, 'r:gz')
            print(f'Extracting {file}...')
            tar.extractall('./tmp')
            game_dir = os.path.join('./tmp/holdem', file.split('.')[1])
            print('Processing hdb...')
            hdb = open(os.path.join(game_dir, 'hdb'), 'r')
            for line in hdb.readlines():
                fields = line.split()
                cards = [None] * 5
                if len(fields) > 8:
                    for i in range(8, len(fields)):
                        cards[i - 8] = fields[i]
                for i in range(4, 8):
                    fields[i] = fields[i].split('/')[1]
                game = (fields[0] + 'i', 20, cards[0], cards[1], cards[2], cards[3], cards[4], float(fields[4]), float(fields[5]), float(fields[6]), float(fields[7]))
                c.execute('''INSERT INTO Games VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', game)
                # print(game)


            pdbs = os.listdir(os.path.join(game_dir, 'pdb'))
            for count, pdb_file in enumerate(pdbs):
                if count % 100 == 0:
                    print(f'Processing pdbs... ({count} / {len(pdbs)})')
                player_id = pdb_file[4:]
                pdb = open(os.path.join(game_dir, 'pdb', pdb_file))
                for line in pdb.readlines():
                    fields = line.split()
                    cards = [None] * 2
                    if len(fields) > 11:
                        cards = fields[11:]
                    hand = (fields[1] + 'i', player_id, cards[0], cards[1], float(fields[9]), float(fields[10]) - float(fields[9]), float(fields[8]))
                    c.execute('''INSERT INTO Hands VALUES (?, ?, ?, ?, ?, ?, ?)''', hand)
                    # print(hand)
                    for i in range(4, 8):
                        action_field = fields[i]
                        if action_field == '-':
                            continue
                        for j in range(len(action_field)):
                            action = (fields[1] + 'i', player_id, i - 4, j * 10 + int(fields[3]), action_field[j:j + 1])
                            c.execute('''INSERT INTO Actions VALUES (?, ?, ?, ?, ?)''', action)
                        # print(action)
            print('Saving to database...')
            conn.commit()
            print()
        except Exception as e:
            print(f'Error on file {file}')
            print(e)
