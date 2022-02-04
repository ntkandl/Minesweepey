import cv2
import numpy as np
import win32gui
from PIL import ImageGrab


class MineSweeperWindowFinder():
    hwnd_list = []

    def winEnumHandler(self, hwnd, ctx ):
        if win32gui.IsWindowVisible( hwnd ):
            if 'minesweeper arbiter' in win32gui.GetWindowText( hwnd ).lower():
                self.hwnd_list.append({"window_id" : hwnd , "window_title" : win32gui.GetWindowText( hwnd )})
            # print (hex(hwnd), win32gui.GetWindowText( hwnd ))

    def getMineSweeperWindowCandidateHandles(self):
        win32gui.EnumWindows( self.winEnumHandler, None )        
        return self.hwnd_list

    def getMineSweeperWindowHandle(self):
        hwnd_list = self.getMineSweeperWindowCandidateHandles()

        assert(len(hwnd_list) == 2)
        minesweeper_hwnd = None

        for window in hwnd_list:
            dimensions = win32gui.GetWindowRect(window['window_id'])
            if dimensions[0] != dimensions[2] and dimensions[1] != dimensions[3]:
                minesweeper_hwnd = window['window_id']
                #print(dimensions)

        assert(minesweeper_hwnd is not None)
        return minesweeper_hwnd

def window_rect_to_grid_rect(window_rect):
    """
    window_rect - tuple of (topleft_x, topleft_y, bottomright_x, bottomright_y)
    """
    grid_topleft = (window_rect[0] + 15, window_rect[1] + 101)
    grid_bottomright = (window_rect[2] - 15, window_rect[3] - 43)
    grid_rect = (grid_topleft[0], grid_topleft[1], grid_bottomright[0], grid_bottomright[1])

    image = ImageGrab.grab(grid_rect)
#    image.show()

    return grid_topleft, grid_bottomright, grid_rect

def window_rect_to_mine_count_rect(window_rect):
    """
    window_rect - tuple of (topleft_x, topleft_y, bottomright_x, bottomright_y)
    Trims window to just game board
    """
    grid_topleft = (window_rect[0] + 19, window_rect[1] + 62)
    grid_bottomright = (window_rect[0] + 58, window_rect[1] + 85)
    mine_count_rect = (grid_topleft[0], grid_topleft[1], grid_bottomright[0], grid_bottomright[1])

    return mine_count_rect
# def window_rect_to_smiley_rect(window_rect):
# def window_rect_to_scoreboard_rect(window_rect):


"""New"""


def read_mines(mine_count_rect):
    """Grabs images of 3 digits of mine counter and stores # values in an int"""  #Does not yet compare!
    digit_width = int((mine_count_rect[2] - mine_count_rect[0]) / 3)
    hundreds_rect = (mine_count_rect[0], mine_count_rect[1], mine_count_rect[0] + digit_width, mine_count_rect[3])
    tens_rect = (mine_count_rect[0]+ digit_width, mine_count_rect[1], mine_count_rect[0] + 2 * digit_width, mine_count_rect[3])
    ones_rect = (mine_count_rect[0]+ 2 * digit_width, mine_count_rect[1], mine_count_rect[0] + 3 * digit_width, mine_count_rect[3])


    mc_hundreds_image = ImageGrab.grab(hundreds_rect)
#    mc_hundreds_image.show()
    mc_tens_image = ImageGrab.grab(tens_rect)
#    mc_tens_image.show()
    mc_ones_image = ImageGrab.grab(ones_rect)
#    mc_ones_image.show()

    #Compare these 3 images with ref images to get individual values and convert to a single int

    mine_count = 0 #temp
    return mine_count

def get_tile_image(tile_image_coords):
    minesweeper_grid_pixel_width = int(16)
    tile_topleft = tile_image_coords[0] - int(minesweeper_grid_pixel_width / 2), tile_image_coords[1] - int(minesweeper_grid_pixel_width / 2)
    tile_botright = tile_image_coords[0] + int(minesweeper_grid_pixel_width / 2), tile_image_coords[1] + int(minesweeper_grid_pixel_width / 2)

    image_rect = [*tile_topleft, *tile_botright]
    tile_image = ImageGrab.grab(image_rect)

    tile_image.show()
    


def board_define(game_board):
    """Create list of dictionaries that include info such as image of space, adjacent spaces, and state/value of the space"""

    #game_board[0] contains general info: W and H of board, # of starting mines, mines left(?)
    #game_board[x] for x>0 contains the info for the x grid square starting 1 = top left, moving left to right
    #info includes:adjacent square ID's, value (0,1,2... U(nknown), M(ine)), current image, complete/done (boolean)(is this necessary? U would be only non-complete value)

    minesweeper_grid_pixel_width = 16
    W = int((grid_rect[2] - grid_rect[0]) / minesweeper_grid_pixel_width)
    H = int((grid_rect[3] - grid_rect[1]) / minesweeper_grid_pixel_width)

    #print(f"Game grid is {W} x {H}")

    TOTAL_MINES = read_mines(mine_count_rect)    #an initial read of the mine counter to tell the total number of mines in the game


    game_board[0] = {
        'W' : W,        #Game Board Width in grid squares
        'H' : H,        #Game Board Height in grid squares
        'Total Mines' : TOTAL_MINES,    #Total number of mines in the game, discovered or not
        'Remaining Mines' : TOTAL_MINES,  #Number of undiscovered mines (all of them at start)
        'Game State' : 1        #Game state variable, 1: in progress, 0: game over (win or lose) not sure if needed
    }

    tile = 0
    while tile < (W * H): #For each square in the game
        tile += 1
        
        #find coords of the square
        X_coord = tile%W                   #if x = 1, X = 1. if x=10, X = 10, if x=11, X = 1
        if X_coord == 0:
            X_coord = W
        Y_coord = int(tile/W)+1              #if x = 1, Y = 1. if x=10, Y = 1, if x=11, Y = 2

        print(f"Tile: {tile} {W} {X_coord}, {Y_coord}")

        tile_image_coords = [(grid_rect[0] + (X_coord-1)*minesweeper_grid_pixel_width + int(minesweeper_grid_pixel_width/2)),(grid_rect[1] + (Y_coord-1)*minesweeper_grid_pixel_width + int(minesweeper_grid_pixel_width/2))]
        


        #find ID's of adjacent squares
        if tile > W and tile < W*H and (tile%W != 0) and ((tile-1)%W != 0):     #non-edge squares have 8 adjacent
            adjacent_squares = ((tile-W)-1, (tile-W), (tile-W)+1, tile-1, tile+1, (tile+W)-1, (tile+W), (tile+W)+1)

        elif tile > 1 and tile < W: #top edge squares have 5 adjacent
            adjacent_squares = (tile-1, tile+1, (tile+W)-1, (tile+W), (tile+W)+1)

        elif tile > 1 and tile < W*(H-1)+1 and ((tile-1)%W == 0): #left edge squares have 5 adjacent
            adjacent_squares = ((tile-W), (tile-W)+1, tile+1, (tile+W), (tile+W)+1)

        elif tile > W and tile < W*H and (tile%W == 0): #right edge squares have 5 adjacent
            adjacent_squares = ((tile-W)-1, (tile-W), tile-1, (tile+W)-1, (tile+W))

        elif tile > W*(H-1)+1 and tile < W*H: #bottom edge squares have 5 adjacent
            adjacent_squares = (tile-1, tile+1, (tile+W)-1, (tile+W), (tile+W)+1)

        else:   #corner pieces have 3 adjacent, 
            if tile == 1:  #top left
                adjacent_squares = (tile+1, (tile+W), (tile+W)+1)
            
            elif tile == W:    #top right
                adjacent_squares = (tile-1, (tile+W)-1, (tile+W))

            elif tile == W*(H-1)+1: #bottom left
                adjacent_squares = ((tile-W), (tile-W)+1, tile+1)                

            elif tile == W*H:   #bottom right
                adjacent_squares = ((tile-W)-1, (tile-W), tile-1)

      
        


        new_square = {
            'Value' : 'U',
            'Adjacent' : adjacent_squares,
            'Image Coords' : tile_image_coords,
            'Image' : 'ImageGrab.grab(x_image_coords)'

        }

        game_board.append(new_square)


    return game_board


#def make_move():

#def board_update():
        #Only update non-complete spaces
    #if  



window_finder = MineSweeperWindowFinder()
minesweeper_hwnd = window_finder.getMineSweeperWindowHandle()

win32gui.SetForegroundWindow(minesweeper_hwnd)

image = ImageGrab.grab(win32gui.GetWindowRect(minesweeper_hwnd))
#image.show()
#image.save('Beginner.png')

window_rect = win32gui.GetWindowRect(minesweeper_hwnd)

grid_topleft, grid_bottomright, grid_rect = window_rect_to_grid_rect(window_rect)

image = ImageGrab.grab(grid_rect)
#image.show()

mine_count_rect = window_rect_to_mine_count_rect(window_rect)
image = ImageGrab.grab(mine_count_rect)



game_board = [0]

def main():
   
    board_define(game_board)

    print(f"game_board[0]: {game_board[0]}")
    print(f"game_board[1]: {game_board[1]}")
    print(f"game_board[2]: {game_board[2]}")

    print(game_board[1]['Image Coords'])
    image = get_tile_image(game_board[4]['Image Coords'])
    image.save('Beginner.png')
    image get_tile_image(game_board[2]['Image Coords'])
    get_tile_image(game_board[17]['Image Coords'])






    # http://timgolden.me.uk/pywin32-docs/win32gui__FindWindow_meth.html




    """
    - Need to grab images of each icon from minesweeper as pngs and put them in this dir
    - Need to write a function that converts game grid image to numpy array designating what's in each grid location using MSE or some other image processing
    """



if __name__ == '__main__':
    main()
