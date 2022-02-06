



game_board = []
for i in range(10):
    game_board[i] = {'Adjacent' : [i+1], }

for Tile in game_board[1:]:    #Updates the adjacent unknowns counter for every tile that has >0 adjacent unknowns
        print(f"{Tile=}") 
        #if len(Tile['Adjacent Unknowns']) > 0:
            #adjacent_count = len(Tile['Adjacent'])  #Count of adjacent tiles
        for adjacent_unkown in Tile['Adjacent Unknowns']:  #steps through every adjacent tile to the tile whose count is being updated
            if game_board[adjacent_unkown]['Value'] != 'U':
                ga