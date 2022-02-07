import cv2
import numpy as np
import win32gui
import os
from PIL import ImageGrab
from random import randrange
import pyautogui
import matplotlib.pyplot as plt
import time
#from skimage.metrics import structural_similarity as ssim

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1




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




def read_mines(mine_count_rect):
    """Grabs images of 3 digits of mine counter and stores # values in an int"""  
    digit_width = int((mine_count_rect[2] - mine_count_rect[0]) / 3)
    hundreds_rect = (mine_count_rect[0], mine_count_rect[1], mine_count_rect[0] + digit_width, mine_count_rect[3])
    tens_rect = (mine_count_rect[0]+ digit_width, mine_count_rect[1], mine_count_rect[0] + 2 * digit_width, mine_count_rect[3])
    ones_rect = (mine_count_rect[0]+ 2 * digit_width, mine_count_rect[1], mine_count_rect[0] + 3 * digit_width, mine_count_rect[3])

    #Import Mine Count Reference Images
    MC_ref_images = import_reference_images('Mine Count')

    #Read Hundreds Value
    mc_hundreds_image = np.array(ImageGrab.grab(hundreds_rect))
    mc_hundreds_val = int(image_compare(mc_hundreds_image, MC_ref_images)[0])
    
    #Read Tens Value
    mc_tens_image = np.array(ImageGrab.grab(tens_rect))
    mc_tens_val = int(image_compare(mc_tens_image, MC_ref_images)[0])

    #Read Ones Value
    mc_ones_image = np.array(ImageGrab.grab(ones_rect))
    mc_ones_val = int(image_compare(mc_ones_image, MC_ref_images)[0])

    mine_count = 100 * mc_hundreds_val + 10 * mc_tens_val + mc_ones_val
    
    return mine_count




def import_reference_images(image_type):
    """Imports reference images of type 'Tiles' or 'Mine Count' and returns a list of those images"""
    ref_img_map = cv2.imread(os.path.join("ref_images", "Reference_Images.png"))
    ref_images = {}
    #Tile reference image extraction
    if image_type == 'Tiles':
        for i in range(9):  #extract ref images of tile states
            y_top = 23
            y_bot = 39
            x_left = 0 + 16*i
            x_right = 16 + 16*i
        
            ref_images[f"{i}"] = ref_img_map[y_top:y_bot, x_left:x_right]
            
        y_top = 39
        y_bot = 55
        ref_images['F'] = ref_img_map[y_top:y_bot, 0:16]
        ref_images['M'] = ref_img_map[y_top:y_bot, 16:32]
        ref_images['U'] = ref_img_map[y_top:y_bot, 32:48]

    elif image_type == 'Mine Count':
        for i in range(10): #extract ref images of mine count digits
            y_top = 0
            y_bot = 23
            x_left = 0 + (13*i)
            x_right = 13 + (13*i)
        
            ref_images[f"{i}"] = ref_img_map[y_top:y_bot, x_left:x_right]
 
    return ref_images





def image_compare(image,ref_images,output = False):
    """
    Compares 'image' with the reference images of image_type (tile or mine count)
    Returns best image key (string)
    """
    #import images of image type to ref_images
    #img_dir = "ref_images"
    # ref_images = {}
    

    # if image_type == 'Mine Count':
    #     for i in range(10):
    #         ref_images[f"{i}"] = cv2.imread(os.path.join(img_dir, f"MineCountRef{i}.png"))

    # if image_type == 'Tiles':
    #     for i in range(9):
    #         ref_images[f"{i}"] = cv2.imread(os.path.join(img_dir, f"{i}_ref.png"))
    #     ref_images['F'] = cv2.imread(os.path.join(img_dir, "F_ref.png"))
    #     ref_images['M'] = cv2.imread(os.path.join(img_dir, "Mine_ref.png"))
    #     ref_images['U'] = cv2.imread(os.path.join(img_dir, "U_ref.png"))

    # if first_time == True:
    #     ref_images_MC = {}
    #     ref_images_T = {}
    #     for i in range(10):
    #         ref_images_MC[f"{i}"] = cv2.imread(os.path.join(img_dir, f"MineCountRef{i}.png"))
    #     for i in range(9):
    #         ref_images_T[f"{i}"] = cv2.imread(os.path.join(img_dir, f"{i}_ref.png"))
    #     ref_images_T['F'] = cv2.imread(os.path.join(img_dir, "F_ref.png"))
    #     ref_images_T['M'] = cv2.imread(os.path.join(img_dir, "Mine_ref.png"))
    #     ref_images_T['U'] = cv2.imread(os.path.join(img_dir, "U_ref.png"))
   
    # if image_type == 'Mine Count':
    #     ref_images = ref_images_MC
    # else:
    #     ref_images = ref_images_T
    
     
    
    best_err = np.inf
    best_img_key = None 
    
    for image_key in ref_images:
        #imageA = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
        #imageA = np.array(image)
        #imageA = imageA * (255.0/imageA.max())
        imageA = image  #np.array necessary, but done when grab is done

        #imageB = cv2.cvtColor(ref_images[image_key], cv2.COLOR_BGR2GRAY)
        imageB =cv2.cvtColor(ref_images[image_key], cv2.COLOR_RGB2BGR)
        #imageB = imageB * (255.0/imageB.max())
        
        

        err = mse(imageA, imageB)
        
        #from IPython import embed; embed()
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




def get_tile_image(tile_coords,grid_image,grid_rect):
    minesweeper_grid_pixel_width = int(16)

    x_min = tile_coords[0] - grid_rect[0] - int(minesweeper_grid_pixel_width / 2)
    x_max = tile_coords[0] - grid_rect[0] + int(minesweeper_grid_pixel_width / 2)
    y_min = tile_coords[1] - grid_rect[1] - int(minesweeper_grid_pixel_width / 2)
    y_max = tile_coords[1] - grid_rect[1] + int(minesweeper_grid_pixel_width / 2)

    # tile_topleft = tile_coords[0] - int(minesweeper_grid_pixel_width / 2), tile_coords[1] - int(minesweeper_grid_pixel_width / 2)
    # tile_botright = tile_coords[0] + int(minesweeper_grid_pixel_width / 2), tile_coords[1] + int(minesweeper_grid_pixel_width / 2)

    # image_rect = [*tile_topleft, *tile_botright]
    # from IPython import embed; embed()
    tile_image = grid_image[y_min:y_max, x_min:x_max]
    
    return tile_image
    
# def window_rect_to_smiley_center(window_rect):
#     mine_count_rect = (window_rect[0] + 19, window_rect[1] + 62, window_rect[0] + 58, window_rect[1] + 85)

# def window_rect_to_grid_rect(window_rect):
#     """
#     window_rect - tuple of (topleft_x, topleft_y, bottomright_x, bottomright_y)
#     """
#     grid_topleft = (window_rect[0] + 15, window_rect[1] + 101)
#     grid_bottomright = (window_rect[2] - 15, window_rect[3] - 43)
#     grid_rect = (grid_topleft[0], grid_topleft[1], grid_bottomright[0], grid_bottomright[1])

# #    image = ImageGrab.grab(grid_rect)
# #    image.show()

#     return grid_rect

# def window_rect_to_mine_count_rect(window_rect):
#     """
#     window_rect - tuple of (topleft_x, topleft_y, bottomright_x, bottomright_y)
#     Trims window to just game board
#     """
#     grid_topleft = (window_rect[0] + 19, window_rect[1] + 62)
#     grid_bottomright = (window_rect[0] + 58, window_rect[1] + 85)
#     mine_count_rect = (grid_topleft[0], grid_topleft[1], grid_bottomright[0], grid_bottomright[1])

#     return mine_count_rect



def window_to_key_features(window_rect):
    """
    window_rect - tuple of (topleft_x, topleft_y, bottomright_x, bottomright_y)
    Trims window to key features
    """
    #Find game grid rectangle
    trim_top_gg = 101
    trim_left_gg = 15
    trim_right_gg = 15
    trim_bottom_gg = 43

    grid_rect = (
        window_rect[0] + trim_left_gg,
        window_rect[1] + trim_top_gg,
        window_rect[2] - trim_right_gg,
        window_rect[3] - trim_bottom_gg
    )

    #Find mine counter rectangle
    trim_top_mc = 62
    trim_left_mc = 19
    mc_width = 39
    mc_height = 23

    mine_count_rect = (
        window_rect[0] + trim_left_mc,
        window_rect[1] + trim_top_mc,
        window_rect[0] + trim_left_mc + mc_width,
        window_rect[1] + trim_top_mc + mc_height
    )

    #Find center of smiley
    smiley_center = (
        (window_rect[0] + window_rect[2]) / 2,
        (mine_count_rect[1] + mine_count_rect[3]) / 2
    )
        
    return grid_rect, mine_count_rect, smiley_center

#This was never used
# def get_image_opencv(rectangle):
#     """Captures image on screen, and converts to opencv compatible image."""
#     image = ImageGrab.grab(rectangle)
#     image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
#     image_cv = image_cv * (255.0/image_cv.max())

#     return image_cv


def board_define(game_board):
    """Create list of dictionaries that include info such as image of space, adjacent spaces, and state/value of the space"""

    #game_board[0] contains general info: W and H of board, # of starting mines, mines left(?)
    #game_board[x] for x>0 contains the info for the x grid square starting 1 = top left, moving left to right
    #info includes:adjacent square ID's, value (0,1,2... U(nknown), M(ine)), current image, complete/done (boolean)(is this necessary? U would be only non-complete value)

    window_finder = MineSweeperWindowFinder()
    minesweeper_hwnd = window_finder.getMineSweeperWindowHandle()
    win32gui.SetForegroundWindow(minesweeper_hwnd)
    window_rect = win32gui.GetWindowRect(minesweeper_hwnd)
    
    # grid_rect = window_rect_to_grid_rect(window_rect)
    # mine_count_rect = window_rect_to_mine_count_rect(window_rect)
    # smiley_center = window_rect_to_smiley_center(window_rect)

    grid_rect, mine_count_rect, smiley_center = window_to_key_features(window_rect)

    #grid_image = get_image_opencv(grid_rect)
    grid_image = np.array(ImageGrab.grab(grid_rect))

    # cv2.imshow('grid image',grid_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows
    # from IPython import embed;  embed()

    minesweeper_grid_pixel_width = 16
    W = int((grid_rect[2] - grid_rect[0]) / minesweeper_grid_pixel_width)
    H = int((grid_rect[3] - grid_rect[1]) / minesweeper_grid_pixel_width)

    #print(f"Game grid is {W} x {H}")
    mine_count_tic = time.perf_counter()
    TOTAL_MINES = read_mines(mine_count_rect)    #an initial read of the mine counter to tell the total number of mines in the game
    remaining_mines = TOTAL_MINES
    mine_count_toc = time.perf_counter()
    print(f"Time to find Mine Count: {mine_count_toc - mine_count_tic:0.4f}s")
    game_board[0] = {
        'W' : W,        #Game Board Width in grid squares
        'H' : H,        #Game Board Height in grid squares
        'Total Tiles' : W * H,
        'Total Mines' : TOTAL_MINES,    #Total number of mines in the game, discovered or not
        'Remaining Mines' : remaining_mines,  #Number of undiscovered mines (all of them at start)
        'Remaining Unknowns' : W * H,
        'Move History' : [],
        'Game State' : 1,        #Game state variable, 1: in progress, 0: game over (win or lose) not sure if needed
        'Grid Rect' : grid_rect,
        'Smiley Loc' : smiley_center
    }

    tile = 0
    while tile < (W * H): #For each square in the game
        tile += 1
        
        #find coords of the square
        X_coord = tile%W                   #if x = 1, X = 1. if x=10, X = 10, if x=11, X = 1
        if X_coord == 0:
            X_coord = W
        Y_coord = int((tile-1)/W)+1              #if x = 1, Y = 1. if x=10, Y = 1, if x=11, Y = 2

        tile_coords = [(grid_rect[0] + (X_coord-1)*minesweeper_grid_pixel_width + int(minesweeper_grid_pixel_width/2)), (grid_rect[1] + (Y_coord-1)*minesweeper_grid_pixel_width + int(minesweeper_grid_pixel_width/2))]
    

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
            'Adjacent Mines' : [],  #contains tile ID of known mines       
            'Edge' : edge,
            'Tile Coords' : tile_coords,
            'Image' : get_tile_image(tile_coords,grid_image,grid_rect)
            }

    

        game_board.append(new_square)
    
    #debug tool
    # refs = import_reference_images('Tiles')
    # image_compare(game_board[1]['Image'],refs,True)


    return game_board


def rand_move(game_board):
    """Make a random, non-edge move  (might need a case for if only things left are edges)"""
    # new_tile = 0
    # last_tile = 
    # adjacent_last_tile = 
    # # W = game_board[0]['W']
    # # H = game_board[0]['H']
    # edge = True
    # value = '0'
    # while (edge == True) or (value != 'U') or new_tile == adjacent_last_tile:
    #     new_tile = randrange(1,game_board[0]['Total Tiles'])
    #     edge = game_board[new_tile]['Edge']
    #     value = game_board[new_tile]['Value']
    #     print(f"looped new random tile: {new_tile}\n {edge=}\n{value=}")
    # print(f"Selected new tile: {new_tile}")
    #return new_tile


    new_tile = 1
    #Find random tile with 8 adjacents
    
    i = 8
    count = 0
    while len(game_board[new_tile]['Adjacent Unknowns']) != i:
        new_tile = randrange(1,game_board[0]['Total Tiles'])
        print(f"{new_tile=} {i=} {count=}")
        count += 1
        if count >= 10:
            i -= 1
            count = 0
    
    return new_tile


def mouse_click(tile_attributes,click_type = 'L'):
    X = tile_attributes['Tile Coords'][0]
    Y = tile_attributes['Tile Coords'][1]
    pyautogui.moveTo(X,Y,0.1)
    if click_type == 'L':
        print("Left Click")
        pyautogui.click(X,Y)
    elif click_type == 'R':
        print("Right Click")
        pyautogui.rightClick(X,Y)
    


def update_board(game_board):
    tile = 0 
    print("Updating Board")  
    #Import Mine Count Reference Images
    T_ref_images = import_reference_images('Tiles')

    #Take snapshot of grid
    grid_image = np.array(ImageGrab.grab(game_board[0]['Grid Rect']))

    while tile < (game_board[0]['Total Tiles']):
        tile += 1
         
        if game_board[tile]['Value'] == 'U': #Only update non-complete spaces

            #Update Value with image compare
            new_tile_img = get_tile_image(game_board[tile]['Tile Coords'], grid_image,game_board[0]['Grid Rect']) #Get updated image of tile
            new_tile_val, error = image_compare(new_tile_img, T_ref_images) #compare new image with refs to get val

            #print(f"{tile=} {new_tile_val}  {error}")

            if new_tile_val == 'U':
                continue
            else:
                game_board[tile]['Value'] = new_tile_val
                game_board[0]['Remaining Unknowns'] -= 1
                if game_board[tile]['Value'] == 'M':
                    game_board[0]['Game State'] = 0


    # for i in range(1, len(game_board)):
    #     Adjacent_Unknowns = list(game_board[i]['Adjacent Unknowns'])
    #     #print(f"{Adjacent_Unknowns=} pre removal")
    #     for adjacent_unknown in Adjacent_Unknowns:  #steps through every adjacent tile to the tile whose count is being updated
    #         #print(f"{adjacent_unknown} step in for loop")
    #         if game_board[adjacent_unknown]['Value'] != 'U':
    #             game_board[i]['Adjacent Unknowns'].remove(adjacent_unknown) #remove that value from the list of unkowns
    #         #print(f"{game_board[i]['Adjacent Unknowns']} post removal")

    for Tile in game_board[1:]:    #Updates the adjacent unknowns counter for every tile that has >0 adjacent unknowns
        Adjacent_Unknowns = list(Tile['Adjacent Unknowns'])
        for adjacent_unknown in Adjacent_Unknowns:  #steps through every adjacent tile to the tile whose count is being updated
            if game_board[adjacent_unknown]['Value'] != 'U':
                Tile['Adjacent Unknowns'].remove(adjacent_unknown) #remove that value from the list of unkowns
        
            





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



def choose_next_tile(game_board):
    #Only look attiles with number value tiles of 1+ *with adjacent unknowns*
    #First look for corners or things with only 1 left (len(adjacent unknowns) = 1)
    #Prioritize tiles with low number of adjacent unknowns

    move_made = 0
    for i in range(1,9):
        for new_tile in range(1,game_board[0]['Total Tiles'] + 1):
            print(f"moving? {new_tile=}")
            #Only continue with NUMBER tiles WITH adjacent unknowns left (others are already done)
            #Prioritize tiles with least unknowns
            if game_board[new_tile]['Value'].isnumeric() and len(game_board[new_tile]['Adjacent Unknowns']) == i:
                #Do these checks and do this stuff, Afterwards/otherwise check tiles with 2 adjacent unknowns, then 3

                print(f"Checking tile {new_tile} with Logic\n Numeric: {game_board[new_tile]['Value'].isnumeric()}\n Length{len(game_board[new_tile]['Adjacent Unknowns'])}\n {i}")

                ####Move Logic #1####
                if len(game_board[new_tile]['Adjacent Unknowns']) + len(game_board[new_tile]['Adjacent Mines']) == int(game_board[new_tile]['Value']):
                    #If #Adjacent Unknowns + #Adjacent Mines = tile value:  then all adjacent unknowns are mines.
                    print(f"Logic 1 {new_tile}")
                    #Flag the found mine(s)
                    for found_mine in game_board[new_tile]['Adjacent Unknowns']:
                        mouse_click(game_board[found_mine],click_type = 'R')
                        game_board[0]['Remaining Mines'] -= 1

                        #Add newfound mine to list of adjacent mines for every tile adjacent to the new mine
                        for adjacent_to_mine in game_board[found_mine]['Adjacent']:
                            game_board[adjacent_to_mine]['Adjacent Mines'].append(found_mine)
                    move_made = 1


                ####Move Logic #2####
                elif len(game_board[new_tile]['Adjacent Mines']) == int(game_board[new_tile]['Value']):
                    #If #Adjacent mines = tile value:   then all adjacent unknowns are not mines
                    print(f"Logic 2 {new_tile}")
                    #left click all tiles in adjacent unknowns
                    for not_mine in game_board[new_tile]['Adjacent Unknowns']:
                        mouse_click(game_board[not_mine],click_type = 'L')
                    move_made = 1

            if move_made == 1:
                break
        if move_made == 1:
            break

        if i > 8:
            print("Something has gone wrong, game is stuck")
            game_board[0]['Game State'] = 0
            break




def game_end_check(game_board):
    if game_board[0]['Remaining Unknowns'] == 0:
        game_board[0]['Game State'] = 0

    if game_board[0]['Remaining Unknowns'] == game_board[0]["Remaining Mines"]:
        #All remaining unknowns are mines, therefore flag them all
        #_____right click all remaining unknowns_______
        game_board[0]['Game State'] = 0

    if game_board[0]["Remaining Mines"] == 0:
        #All remaining unknowns are safe
        #_____left click all remaining unknowns________
        game_board[0]['Game State'] = 0



def debug(game_board):
    #Can add options to ask for input to request info about certain things
    from IPython import embed; embed()

    #Sample Input:
    #   tile = 
    #   image_compare(game_board[tile]['Image'],'Tiles',output = True)
    #   game_board[tile]









def main():
    game_board = [0]

    board_define_tic = time.perf_counter()
    board_define(game_board)    #intial board definition
    board_define_toc = time.perf_counter()
    print(f"Board Definition Time: {board_define_toc - board_define_tic:0.4f}s")


    #Test for timing
    game_update_tic = time.perf_counter()
    update_board(game_board)
    game_update_toc = time.perf_counter()
    print(f"Initial Game Board Update Time: {game_update_toc - game_update_tic:0.4f}s")

    #Starting moves
    while game_board[0]['Remaining Unknowns'] > 5/6 * game_board[0]['Total Tiles'] and game_board[0]['Game State'] == 1:
        #click on random tiles until at least 1/3 of board is revealed  
        new_tile = rand_move(game_board)    
        mouse_click(game_board[new_tile],click_type = 'L')  
        game_board[0]['Move History'].append(new_tile)
        update_board(game_board)

    update_board(game_board)
    while game_board[0]['Game State'] != 0:
        #determine next tile to analyze
        choose_next_tile(game_board)
        update_board(game_board)


        #Check for end state
        game_end_check(game_board)

        

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

    #debug(game_board)

    # image = game_board[1]['Image']
    #image.show()


"""To do"""
"""
-finish game end clicks
-combine ref images into one file

- Update random move to not move to adjacents
    -only move to tile that has 8 adjacent unknowns (takes care of edge case and non adjacency)
        -if none, move to 7 adjacent unknowns, and so on
- Add game logic and move system

- Maybe consider 2x2 array data structure




________Later Features_________
- Add option to start over when game is over
    -find smiley location to click



__________Done_____________
- Something that keeps track of number of adjacent unknowns?
    -How to keep it updated?
-Add done/completed boolean for each tile (when number of adjacent unknowns = 0)
    -Or just len(adjacent unknowns)



___________________Notes__________________
-Old method time for expert (30x16) mine count image compare = 0.12s
-Old method time for expert (30x16) board definition = 16.3s
-Old method time for expert (30x16) board update = 16.2s





"""
    







    # http://timgolden.me.uk/pywin32-docs/win32gui__FindWindow_meth.html

    #from IPython import embed; embed()


"""
    - Need to grab images of each icon from minesweeper as pngs and put them in this dir
    - Need to write a function that converts game grid image to numpy array designating what's in each grid location using MSE or some other image processing
"""



if __name__ == '__main__':
    main()
