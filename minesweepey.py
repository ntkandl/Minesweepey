import cv2
import numpy as np
import win32gui
import os
from PIL import ImageGrab
from random import randrange
import pyautogui
import matplotlib.pyplot as plt
from skimage.metrics import structural_similarity as ssim

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5


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


def read_mines(mine_count_rect):
    """Grabs images of 3 digits of mine counter and stores # values in an int"""  #Does not yet compare!
    digit_width = int((mine_count_rect[2] - mine_count_rect[0]) / 3)
    hundreds_rect = (mine_count_rect[0], mine_count_rect[1], mine_count_rect[0] + digit_width, mine_count_rect[3])
    tens_rect = (mine_count_rect[0]+ digit_width, mine_count_rect[1], mine_count_rect[0] + 2 * digit_width, mine_count_rect[3])
    ones_rect = (mine_count_rect[0]+ 2 * digit_width, mine_count_rect[1], mine_count_rect[0] + 3 * digit_width, mine_count_rect[3])

    #Read Hundreds Value
    mc_hundreds_image = ImageGrab.grab(hundreds_rect)
    mc_hundreds_val = int(image_compare(mc_hundreds_image, 'Mine Count')[0])

    #Read Tens Value
    mc_tens_image = ImageGrab.grab(tens_rect)
    mc_tens_val = int(image_compare(mc_tens_image, 'Mine Count')[0])

    #Read Ones Value
    mc_ones_image = ImageGrab.grab(ones_rect)
    mc_ones_val = int(image_compare(mc_ones_image, 'Mine Count')[0])

    mine_count = 100 * mc_hundreds_val + 10 * mc_tens_val + mc_ones_val

    return mine_count

def image_compare(image,image_type,output = False):
    """
    Compares 'image' with the reference images of image_type (tile or mine count)
    Returns best image key (string)
    """
    #import images of image type to ref_images
    img_dir = "ref_images"
    ref_images = {}
    if image_type == 'Mine Count':
        for i in range(10):
            ref_images[f"{i}"] = cv2.imread(os.path.join(img_dir, f"MineCountRef{i}.png"))

    if image_type == 'Tiles':
        for i in range(9):
            ref_images[f"{i}"] = cv2.imread(os.path.join(img_dir, f"{i}_ref.png"))
        ref_images['F'] = cv2.imread(os.path.join(img_dir, "F_ref.png"))
        ref_images['M'] = cv2.imread(os.path.join(img_dir, "Mine_ref.png"))
        ref_images['U'] = cv2.imread(os.path.join(img_dir, "U_ref.png"))
        
    best_err = np.inf
    best_img_key = None 
    
    for image_key in ref_images:
        imageA = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
        imageA = imageA * (255.0/imageA.max())

        imageB = cv2.cvtColor(ref_images[image_key], cv2.COLOR_BGR2GRAY)
        imageB = imageB * (255.0/imageB.max())

        err = mse(imageA, imageB)

        if output == True:
            # setup the figure
            fig = plt.figure("MSE comparison")
            plt.suptitle("MSE: %.2f" % (err))
            # # show first image
            ax = fig.add_subplot(1, 2, 1)
            # plt.imshow(imageA, cmap = plt.cm.gray)
            plt.imshow(imageA)
            plt.axis("off")
            # show the second image
            ax = fig.add_subplot(1, 2, 2)
            # plt.imshow(imageB, cmap = plt.cm.gray)
            plt.imshow(imageB)
            plt.axis("off")
            # show the images
            plt.show()

        #print(f"{image_key=} {err=}")
        if err < best_err:
            best_err = err
            best_img_key = image_key

        #print(f"Best Image: {best_img_key}, Best Err: {best_err}")
    
    return best_img_key , best_err

def mse(imageA, imageB):
	# the 'Mean Squared Error' between the two images is the
	# sum of the squared difference between the two images;
	# NOTE: the two images must have the same dimension
	err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
	err /= float(imageA.shape[0] * imageA.shape[1])
	
	# return the MSE, the lower the error, the more "similar"
	# the two images are
	return err



def get_tile_image(tile_coords):
    minesweeper_grid_pixel_width = int(16)
    tile_topleft = tile_coords[0] - int(minesweeper_grid_pixel_width / 2), tile_coords[1] - int(minesweeper_grid_pixel_width / 2)
    tile_botright = tile_coords[0] + int(minesweeper_grid_pixel_width / 2), tile_coords[1] + int(minesweeper_grid_pixel_width / 2)

    image_rect = [*tile_topleft, *tile_botright]
    tile_image = ImageGrab.grab(image_rect)

    return tile_image
    


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
    remaining_mines = TOTAL_MINES

    game_board[0] = {
        'W' : W,        #Game Board Width in grid squares
        'H' : H,        #Game Board Height in grid squares
        'Total Tiles' : W * H,
        'Total Mines' : TOTAL_MINES,    #Total number of mines in the game, discovered or not
        'Remaining Mines' : remaining_mines,  #Number of undiscovered mines (all of them at start)
        'Remaining Unknowns' : W * H,
        'Move History' : [],
        'Game State' : 1        #Game state variable, 1: in progress, 0: game over (win or lose) not sure if needed
    }

    tile = 0
    while tile < (W * H): #For each square in the game
        tile += 1
        
        #find coords of the square
        X_coord = tile%W                   #if x = 1, X = 1. if x=10, X = 10, if x=11, X = 1
        if X_coord == 0:
            X_coord = W
        Y_coord = int((tile-1)/W)+1              #if x = 1, Y = 1. if x=10, Y = 1, if x=11, Y = 2

        tile_coords = [(grid_rect[0] + (X_coord-1)*minesweeper_grid_pixel_width + int(minesweeper_grid_pixel_width/2)),(grid_rect[1] + (Y_coord-1)*minesweeper_grid_pixel_width + int(minesweeper_grid_pixel_width/2))]
    

        #find ID's of adjacent squares
        edge = True
        if tile > W and tile < W*(H-1) and (tile%W != 0) and ((tile-1)%W != 0):     #non-edge squares have 8 adjacent
            adjacent_squares = ((tile-W)-1, (tile-W), (tile-W)+1, tile-1, tile+1, (tile+W)-1, (tile+W), (tile+W)+1)
            edge = False

        elif tile > 1 and tile < W: #top edge squares have 5 adjacent
            adjacent_squares = (tile-1, tile+1, (tile+W)-1, (tile+W), (tile+W)+1)

        elif tile > 1 and tile < W*(H-1)+1 and ((tile-1)%W == 0): #left edge squares have 5 adjacent
            adjacent_squares = ((tile-W), (tile-W)+1, tile+1, (tile+W), (tile+W)+1)

        elif tile > W and tile < W*H and (tile%W == 0): #right edge squares have 5 adjacent
            adjacent_squares = ((tile-W)-1, (tile-W), tile-1, (tile+W)-1, (tile+W))

        elif tile > W*(H-1)+1 and tile < W*H: #bottom edge squares have 5 adjacent
            adjacent_squares = (tile-1, tile+1, (tile-W)-1, (tile-W), (tile-W)+1)

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
            'Adjacent Unknowns' : list(adjacent_squares),       
            'Edge' : edge,
            'Tile Coords' : tile_coords,
            'Image' : get_tile_image(tile_coords)
            }

        game_board.append(new_square)


    return game_board


def rand_move(game_board):
    """Make a random, non-edge move  (might need a case for if only things left are edges)"""
    new_tile = 0
        
    # W = game_board[0]['W']
    # H = game_board[0]['H']
    edge = True
    value = '0'
    while (edge == True) or (value != 'U'):
        new_tile = randrange(1,game_board[0]['Total Tiles'])
        edge = game_board[new_tile]['Edge']
        value = game_board[new_tile]['Value']
        print(f"looped new random tile: {new_tile}\n {edge=}\n{value=}")
    print(f"Selected new tile: {new_tile}")
    return new_tile

def mouse_click(tile_attributes,click_type = 'L'):
    X = tile_attributes['Tile Coords'][0]
    Y = tile_attributes['Tile Coords'][1]
    pyautogui.moveTo(X,Y,0.5)
    if click_type == 'L':
        pyautogui.click(X,Y)
    elif click_type == 'R':
        pyautogui.rightClick(X,Y)
    


def update_board(game_board):
    tile = 0 
    while tile < (game_board[0]['Total Tiles']):
        tile += 1
         
        if game_board[tile]['Value'] == 'U': #Only update non-complete spaces

            #Update Value with image compare
            new_tile_img = get_tile_image(game_board[tile]['Tile Coords']) #Get updated image of tile
            new_tile_val, error = image_compare(new_tile_img, 'Tiles') #compare new image with refs to get val

            #print(f"{tile=} {new_tile_val}  {error}")

            if new_tile_val == 'U':
                continue
            else:
                game_board[tile]['Value'] = new_tile_val
                game_board[0]['Remaining Unknowns'] -= 1
                if game_board[tile]['Value'] == 'M':
                    game_board[0]['Game State'] = 0



    for Tile in game_board[1:]:    #Updates the adjacent unknowns counter for every tile that has >0 adjacent unknowns
        print(f"{Tile=}") 
        #if len(Tile['Adjacent Unknowns']) > 0:
            #adjacent_count = len(Tile['Adjacent'])  #Count of adjacent tiles
        for adjacent_unkown in Tile['Adjacent Unknowns']:  #steps through every adjacent tile to the tile whose count is being updated
            if game_board[adjacent_unkown]['Value'] != 'U':
                Tile['Adjacent Unknowns'].remove(adjacent_unkown)
                #remove that value from the list of unkowns
            





def show_board(game_board):
    tile = 0 
    x = 1
    output = []
    while tile < (game_board[0]['W']*game_board[0]['H']):
        tile += 1
        x += 1
        output.append(game_board[tile]['Value'])
        if x > game_board[0]['W']:
            x = 1
            print(output)
            output = []


def debug(game_board):
    #Can add options to ask for input to request info about certain things
    from IPython import embed; embed()

    #Sample Input:
    #   tile = 
    #   image_compare(game_board[tile]['Image'],'Tiles',output = True)
    #   game_board[tile]




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
   
    board_define(game_board)    #intial board definition

    #Starting moves
    while game_board[0]['Remaining Unknowns'] > 2/3 * game_board[0]['Total Tiles'] and game_board[0]['Game State'] == 1:
        #click on random tiles until at least 1/3 of board is revealed  
        new_tile = rand_move(game_board)    
        mouse_click(game_board[new_tile],click_type = 'L')  
        game_board[0]['Move History'].append(new_tile)
        update_board(game_board)

    if game_board[0]['Game State'] == 0:
        print("Game Over")

    #mouse_click(game_board[new_tile],click_type = 'L')
    #update_board(game_board)

    # print(f"1 {game_board[1]}")
    # print(f"2 {game_board[2]}")
    # print(f"4 {game_board[4]}")
    # print(f"5 {game_board[5]}")
    # print(f"6 {game_board[6]}")
    # print(f"18 {game_board[18]}")
    # print(f"55 {game_board[55]}")
    # print(f"88 {game_board[88]}")
    # print(f"99 {game_board[99]}")
    # print(f"100 {game_board[100]}")

    print(f"Game Stats: {game_board[0]}")


    #grid display output
    show_board(game_board)

    debug(game_board)

    # image = game_board[1]['Image']
    #image.show()


"""To do"""
"""
- Need to check for game over in game update
- Update random move to not move to adjacents
    -only move to tile that has 8 adjacent unknowns (takes care of edge case and non adjacency)
        -if none, move to 7 adjacent unknowns, and so on

- Something that keeps track of number of adjacent unknowns?
    -How to keep it updated?
-Add done/completed boolean for each tile (when number of adjacent unknowns = 0)


________Later Features_________
- Add option to start over when game is over
    -find smiley location to click





"""
    






    # http://timgolden.me.uk/pywin32-docs/win32gui__FindWindow_meth.html

    #from IPython import embed; embed()


"""
    - Need to grab images of each icon from minesweeper as pngs and put them in this dir
    - Need to write a function that converts game grid image to numpy array designating what's in each grid location using MSE or some other image processing
"""



if __name__ == '__main__':
    main()
