# Sudoku solver and generator with GUI
# Jiri Kruchina, I.rocnik
# zimni semestr 2022/23

import random
import time

def square_gen(A,B):
    # takes rows and columns and outputs list of square names in them
    return [a+b for a in A for b in B]

cols = '123456789'
rows = 'ABCDEFGHI'

digits = '123456789'
# list of all square names (each is a string with a letter and a digit)
squares = square_gen(rows, cols)

# list of all units (rows, cols, 3x3 squares)
unitlist = ([square_gen(rows, c) for c in cols] +        # rows
            [square_gen(r, cols) for r in rows] +        # columns
            [square_gen(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')])        # squares

# dictionary where each square maps to the list of units that contain the square
units = dict((s, [u for u in unitlist if s in u]) for s in squares)

# dictionary where each square s maps to the set of squares formed by the union of the squares in the units of s, but not s itself
# squares that could affect certain square (set of squares in rows, cols and square) -> 20 peers for each square
# sum combines the lists
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in squares)

# grid =  the initial state of a puzzle in text format
# values = dict with all the remaining possible values for each square

# already found any solution?
solutions = False

# store found solution of sudoku
solution = ""

# perses an input grid (assigns all input digits)
def grid_parser(grid):
    # each square can be initially all digits
    values = dict((s, digits) for s in squares)
    
    # counts number of input digits (non empty squares)
    input_d_count = 0
    # tracks unused digits in input
    unused_digs = "123456789"

    # go through dict of input gird, s = each square, d = input digit
    for s, d in grid_values(grid).items():
        if d in digits:
            unused_digs = unused_digs.replace(d, "")
            input_d_count += 1
            if not assign(values, s, d):
                # we can't assign d to square s -> bad sudoku input puzzle (for example two same digits in one unit -> unsolvable)
                return False
    
    # the minimum number of cells that need to be populated to generate a solvable Sudoku is 17
    # also there need to be at least 8 different digits (so at maximum one unused) to have an unique solution
    if input_d_count < 17 or len(unused_digs) > 1:
        return 2

    return values

def grid_values(grid):
    # go through input grid and save all numbers or blank spaces (0, .), ignore all other characters
    chars = [c for c in grid if c in digits or c in "0."]
    # zip -> create tuples, takes i-th element from each list ==> assigns each square a digit from input
    return dict(zip(squares, chars))


def assign(values, s, d):
    # set square s to input digit d
    
    # all possible values except input digit d for square s
    other_values = values[s].replace(d, "")
    # call eliminate function on all other values which are now not gonna be possible -> propagate to units
    if all(eliminate(values, s, d2) for d2 in other_values):
        return values
    else:
        # contradiction detected (at least one elimination failed)
        return False


def eliminate(values, s, d):
    # d is eliminated from possible values of square s, propagate when values or places <= 2

    # digit d already eliminated, we're done
    if d not in values[s]:
        return values

    # remove digit d from possible values of square s
    values[s] = values[s].replace(d, "")

    if len(values[s]) == 0:
        # contradiction -> last possible value was removed -> there is no digit suitable for this square
        return False
    elif len(values[s]) == 1:
        # square s is reduced to one value d2 -> eliminate d2 from peers
        d2 = values[s]
        if not all(eliminate(values, s2, d2) for s2 in peers[s]):
            return False

    for u in units[s]:
        # list of all places (squares) where digit d is a possible value that are in units containing square s (possible affected squares)
        dplaces = [s for s in u if d in values[s]]
        if len(dplaces) == 0:
            # contradiction -> no place for this value
            return False
        elif len(dplaces) == 1:
            # digit d is a possible value for only one square -> place it there
            if not assign(values, dplaces[0], d):
                return False

    return values

# function to solve sudoku -> first it parses the input grid and then it searches for a solution
def solve(grid):
    # set these variables -> no solution has been found, so solution is empty and multiple solutions are false
    global solutions, solution
    solutions = False
    solution = ""

    # start solving
    answer = search(grid_parser(grid))

    # no solution found
    if answer == False and solutions == False:
        return False
    # found one solution
    elif answer == False and solutions == True:
        return solution
    # multiple or none solutions (ivalid sudoku)
    else:        # answer == 2
        return 2
        
def search(values):
    # depth-first search

    if values is False:
        # parsing already failed, bad sudoku
        return False

    elif values == 2:
        # parsing already checked there are multiple or none solutions
        return 2

    if all(len(values[s]) == 1 for s in squares):
        # solved sudoku, each square has only one possible value

        # check if another solutions has already been found
        global solutions, solution
        if solutions == False:
            # first solution -> mark that some solutions exist by setting it to True and return False to search if there is another
            solutions = True
            solution = values
            return False

        else:
            # second solution found -> return 2 as an error
            return 2

    # find square s with the fewest possible values (n is the number of possible values) above 1 (empty square)
    n, s = min((len(values[s]), s) for s in squares if len(values[s]) > 1)

    # count frequencies of all possible digits in the sudoku and order them (lowest freq first)
    # put digits in values[s] in this order of lowest frequency first -> better search
    s_ord_val = order_values(values, s)

    # create a new copy of values (so it doesnt affect the old one -> no need to track changes)
    # try to assign possible values to square s
    # and also immediately call search if assign doesnt return False -> DFS
    # get_true = if any search returns 2 (found second solution / invalid sudoku) we return it (ends the solving)
    return get_true(search(assign(values.copy(), s, d)) for d in s_ord_val)

def get_true(seq):
    # go through a list and if you find a value that is True (in this case equal to 2), return it
    for e in seq:
        if e: return e
    return False

def order_values(values, s):
    # takes all values and returns list of digits, sorted by their frequency in values

    # put all possible values into string
    val_str = "".join(values.values())
    # create dict with digits as keys and their frequency as value
    res = {i: val_str.count(i) for i in set(val_str)}
    # sort this dictionary by values and return a string with ordered digits that are in values[s]
    res = sorted(res.items(), key=lambda item: item[1])
    res = map(lambda x: x[0], res)
    res = "".join(x for x in res if x in values[s])
    return res

def get_pencilmarks(grid):
    # similar to parse, but don't fill in obvious spaces that have only one option
    values = dict((s, digits) for s in squares)

    # put in all the input digits
    for s, d in grid_values(grid).items():
        if d in digits:
            values[s] = d

    # save copy of input values for next loop
    orig_values = values.copy()

    # for each square that is empty look at surrounding non empty digits (peers with only one possible value at input) and remove these from pencilmarks
    for s in squares:
        # check if square is not an input value
        if len(values[s]) > 1:
            for peer in peers[s]:
                # find peers that have input digits
                if len(orig_values[peer]) == 1:
                    # remove this digit from possible values
                    values[s] = values[s].replace(orig_values[peer], "")

    for s in squares:
        if len(orig_values[s]) == 1:
            # remove input digits from pencilmarks -> to not show duplicates (digit is already on screen)
            values[s] = ""

    return values

def check_user_solution(user_grid, solution_vals):
    # compares filled squares by user with solution and returns a list of squares with wrong digits
    if solution_vals == 2 or solution_vals == False:
        # no solution provided
        return []

    solut_str = "".join(solution_vals.values())

    wrong_squares = []
    for i in range(len(user_grid)):
        # check if square is not empty (don't compare empty spaces)
        if user_grid[i] in digits:
            if user_grid[i] != solut_str[i]:
                # incorrect digit found
                wrong_squares.append(squares[i])

    return wrong_squares

def complete_generator():
    # generate random complete valid sudoku
    values = dict((s, digits) for s in squares)
    grid = "."*81

    while True:
        while True:
            # pick random square
            pos = random.randint(0,80)
            rand_square = squares[pos]
            # check if that square hasnt already been picked
            if len(values[rand_square]) > 1:
                # pick random digit from valid digits for that square
                rand_digit = random.choice(values[rand_square])
                # try to add this value to the grid
                answ = assign(values.copy(), rand_square, rand_digit)
                
                if answ == False:
                    # cant add this digit -> try different digit
                    pass
                else:
                    # digit can be added -> update values and grid
                    values = answ
                    grid = grid[:pos] + str(rand_digit) + grid[pos+1:]
                    # break out of generating more digits and try to solve the sudoku
                    break
        sol = solve(grid)
        if sol != 2 and sol != False:
            # solution found == valid complete sudoku found -> we can break and return
            break
        elif sol == False:
            # unsolvable, try again
            return complete_generator()

        """ if sol == 2 -> try generating another digit 
        case: multiple solutions -> reduces the number of solutions by adding another digit
        case: not enough digits -> adds enough digits to get one of the options above
        """

    # return grid string with solved sudoku
    return "".join(sol[s] for s in squares)

def puzzle_generator(complete):
    # remove values from complete sudoku -> leaves less digits in the sudoku than the base sudoku generated by complete_generator()

    # get random list of numbers from 0 to 80 to represent idexes of squares in grid string
    rand_squares = list(range(81))
    random.shuffle(rand_squares)

    # for each square try removing it's digit and check if sudoku is still valid
    for s in rand_squares:
        rem_val = complete[s]
        complete = complete[:s] + "." + complete[s+1:]
        answ = solve(complete)
        if answ == 2 or answ == False:
            # sudoku is not valid -> return digit back and go to another square
            complete = complete[:s] + rem_val + complete[s+1:]

    return complete

def generator():
    # generates random sudoku
    # first it generates complete solved valid sudoku and then it removes some digits while keeping the sudoku valid
    return puzzle_generator(complete_generator())

def grid_to_pygame(my_grid, string=True):
    # converts grid to pygame list format
    py_grid = []
    temp_list = []

    if string == True:
        # converts string grid to pygame list format
        
        # replace dots with zeros if used
        my_grid = my_grid.replace(".", "0")
        for i in range(len(my_grid)):
            temp_list.append(int(my_grid[i]))
            if (i+1) % 9 == 0:
                # new line
                py_grid.append(temp_list)
                temp_list = []
    else:
        # converts values dict to pygame list format

        for i in range(len(squares)):
            temp_list.append(my_grid[squares[i]])
            if (i+1) % 9 == 0:
                # new line
                py_grid.append(temp_list)
                temp_list = []

    return py_grid

def grid_from_pygame(py_grid, dots=True):
    # converts pygame list grid to string grid
    my_grid = ""

    for line in py_grid:
        for val in line:
            my_grid += str(val)

    # dots or zeros for empty spaces
    if dots == True:
        my_grid = my_grid.replace("0", ".")

    return my_grid

########################### PyGame ###########################

import os
# disables pygame support prompt on import
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
import tkinter.filedialog

# initialise pygame font
pygame.font.init()

# entire window, set it's size and initialize it
screen = pygame.display.set_mode((780, 580))
x = 0
y = 0
# size of a square
dif = 500 / 9

# title of window
pygame.display.set_caption("Sudoku")

# load fonts
font1 = pygame.font.SysFont("Verdana", 40)
font2 = pygame.font.SysFont("Verdana", 23)
font3 = pygame.font.SysFont("Verdana", 10)
font4 = pygame.font.SysFont("Verdana", 20)

def get_cord(pos):
    # changes coordinates of highlighted square to clicked space
    global x, y
    # check if we clicked inbounds
    if pos[0] <= 500 and pos[1] <= 500 and pos[0] >= 0 and pos[1] >= 0:
        # calculate the square from coordinates
        x = int(pos[0]//dif)
        y = int(pos[1]//dif)

# highlight selected cell by drawing red square around
def draw_box():
    for i in range(2):
        # straight line drawing functions -> draws sides of red square
        pygame.draw.line(screen, (255, 0, 0), (x * dif-3, (y + i)*dif), (x * dif + dif + 3, (y + i)*dif), 7)
        pygame.draw.line(screen, (255, 0, 0), ( (x + i)* dif, y * dif ), ((x + i) * dif, y * dif + dif), 7)

# draw sudoku board
def draw(error_squares, pencilmarks, marks):
    # draw numbers and fill background
    for i in range (9):
        for j in range (9):
            # squares with digit
            if grid[j][i]!= 0:

                # color square with a digit blue -> rectangle drawing function (Rect(left, top, width, height))
                if frozen_grid[j][i]!= 0:
                    # different color for initial puzzle digits
                    pygame.draw.rect(screen, init_square_color, (i * dif, j * dif, dif + 1, dif + 1))
                else:
                    pygame.draw.rect(screen, square_color, (i * dif, j * dif, dif + 1, dif + 1))

                # Fill grid with default numbers specified
                text1 = font1.render(str(grid[j][i]), 1, (0, 0, 0))
                # puts text object on screen surface (on exact position)
                screen.blit(text1, (i * dif + 15, j * dif + 2))

            if pencilmarks:
                # display pencilmarks above empty spaces (for non empty get_pencilmarks returns empty string)
                str_square = str(chr(j + 65)) + str(i+1)
                penmarks = marks[str_square]

                # draw pencilmarks in two lines if there are too many values
                text1 = font3.render(penmarks[:7], 1, (0, 0, 0))
                screen.blit(text1, (i * dif + 5, j * dif + 2))
                text1 = font3.render(penmarks[7:], 1, (0, 0, 0))
                screen.blit(text1, (i * dif + 5, j * dif + 15))

    # mark every incorrect digit red
    for square in error_squares:
        mark_error(square)

    # Draw lines horizontally and vertically to form a grid 
    for i in range(10):
        # every third line is thicker
        if i % 3 == 0 :
            thick = 7
        else:
            thick = 1
        pygame.draw.line(screen, (0, 0, 0), (0, i * dif), (502, i * dif), thick)
        pygame.draw.line(screen, (0, 0, 0), (i * dif, 0), (i * dif, 502), thick)

def mark_error(square):
    # mark wrong digits in red

    # converts square name to coordinates
    y = ord(square[0]) - 65
    x = int(square[1]) - 1

    # draws red square and the digit on top of it
    pygame.draw.rect(screen, (200,0,0), (x * dif, y * dif, dif + 1, dif + 1))
    text1 = font1.render(str(grid[y][x]), 1, (0, 0, 0))
    screen.blit(text1, (x * dif + 15, y * dif))

def display_text():
    # display text below sudoku puzzle
    text1 = font2.render(bottom_text, 1, (0, 0, 0))
    screen.blit(text1, (20, 520))

def prompt_file():
    # ask user to select file with sudoku to load

    # Create a Tk file dialog and cleanup when finished
    top = tkinter.Tk()
    top.withdraw()  # hide window
    file_name = tkinter.filedialog.askopenfilename(parent=top)
    top.destroy()
    return file_name

def instructions():
    # display instructions / keybinds next to sudoku
    for i in range(len(instr_lines)):
        text1 = font4.render(instr_lines[i], 1, (0, 0, 0))
        screen.blit(text1, (515, 20+25*i))

# variable initialization
run = True                                  # is game running?
insert_val = 0                              # value to insert to square
error_squares = []                          # squares with wrong digit
bottom_text = "Start solving sudoku!"       # text under sudoku
pencilmarks = False                         # user choice of toggling pencilmarks
change = 0                                  # did a change occur on the board?
marks = {}                                  # dict to store pencilmarks
won = False                                 # did user solve the sudoku?
square_color = (245, 227, 207)              # square with digit bg color
init_square_color = (212, 219, 252)         # input square with digit bg color
# instruction text on the right
instr_lines = ["N = generate new puzzle", "C = clear the board", "L = load from file", 
             "R = reset to initial", "G = solve puzzle", "H = solve current board", 
             "J = show error squares", "P = toggle pencilmarks"]

# start with empty grid
# frozen grid is never changed by user, only by program (initial puzzle)
frozen_grid = [
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0]
                ]
# grid is displayed to user and can be edited
grid = [x[:] for x in frozen_grid]

# loop of the sudoku game in pygame
while run:
    # White color background
    screen.fill((255, 255, 255))
    # Loop through the events stored in event.get() -> checking for user inputs
    for event in pygame.event.get():
        # user closed the window -> quit
        if event.type == pygame.QUIT:
            run = False   
        # Get the mouse position at mouse click to move highlighted square there
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            get_cord(pos)
        
        if event.type == pygame.KEYDOWN:
            # change coordinates of cursor on arrow key press (and loop if edge reached)
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                if x > 0:
                    x -= 1
                else:
                    x = 8
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                if x < 8:
                    x += 1
                else:
                    x = 0
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                if y > 0:
                    y-= 1
                else:
                    y = 8
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                if y < 8:
                    y += 1  
                else:
                    y = 0
            # Get the digit to be inserted if key pressed
            if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                insert_val = 1
            if event.key == pygame.K_2 or event.key == pygame.K_KP2:
                insert_val = 2   
            if event.key == pygame.K_3 or event.key == pygame.K_KP3:
                insert_val = 3
            if event.key == pygame.K_4 or event.key == pygame.K_KP4:
                insert_val = 4
            if event.key == pygame.K_5 or event.key == pygame.K_KP5:
                insert_val = 5
            if event.key == pygame.K_6 or event.key == pygame.K_KP6:
                insert_val = 6
            if event.key == pygame.K_7 or event.key == pygame.K_KP7:
                insert_val = 7
            if event.key == pygame.K_8 or event.key == pygame.K_KP8:
                insert_val = 8
            if event.key == pygame.K_9 or event.key == pygame.K_KP9:
                insert_val = 9 

            # empty the selected square
            if event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE or event.key == pygame.K_0 or event.key == pygame.K_KP0:
                # check if this square is empty in initial puzzle (don't remove digits from it)
                if frozen_grid[y][x] == 0:
                    grid[y][x] = 0

                    # if this square was flagged with error -> remove this error (change by user)
                    # convert coordinates to string name of square
                    rem_square = str(chr(y + 65)) + str(x+1)
                    if rem_square in error_squares:
                        error_squares.remove(rem_square)

                    bottom_text=""
                    change = 1

            # C pressed -> clear sudoku board
            if event.key == pygame.K_c:
                frozen_grid = [
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0]
                ]
                grid = [x[:] for x in frozen_grid]
                error_squares = []
                bottom_text="Cleared the board!"
                change = 1

            # R pressed -> load back frozen_grid (initial puzzle)
            if event.key == pygame.K_r:
                grid = [x[:] for x in frozen_grid]
                error_squares = []
                bottom_text="Reset back to initial puzzle!"
                change = 1

            # N pressed -> generate new sudoku (and put it in frozen grid)
            if event.key == pygame.K_n:
                frozen_grid = grid_to_pygame(generator())
                grid = [x[:] for x in frozen_grid]
                error_squares = []
                bottom_text="Generated new sudoku!"
                change = 1

            # G pressed -> solve initial puzzle (frozen_grid)
            if event.key == pygame.K_g:
                # get output from solving initial puzzle
                sol_answ = solve(grid_from_pygame(frozen_grid))

                # one solution found -> display it
                if sol_answ != 2 and sol_answ != False:
                    frozen_grid = grid_to_pygame(sol_answ, string=False)
                    grid = [x[:] for x in frozen_grid]
                    error_squares = []
                    bottom_text="Correct solution to the initial puzzle."
                    change = 1

                # none or multiple solutions of input puzzle (triggers when called on cleared board)
                else:
                    bottom_text="Initial puzzle is not a valid sudoku!"

            # H pressed -> solve user entered grid
            if event.key == pygame.K_h:
                # get output from solve function on user input grid
                sol_answ = solve(grid_from_pygame(grid))

                # one solution was found -> display it
                if sol_answ != 2 and sol_answ != False:
                    frozen_grid = grid_to_pygame(sol_answ, string=False)
                    grid = [x[:] for x in frozen_grid]
                    error_squares = []
                    bottom_text="Correct solution to the current state of puzzle."
                    change = 1

                # none or multiple solutions
                else:
                    bottom_text = "This sudoku is not valid! (unsolvable or multiple solutions)"

            # J / Enter pressed -> show errors in user input
            if event.key == pygame.K_j or event.key == pygame.K_RETURN:
                error_squares = []
                # list of error squares in string -> for displaying to the user
                str_sqr = ""

                # go through list of squares with wrong digit -> add them to the list (and string)
                for square in check_user_solution(grid_from_pygame(grid), solve(grid_from_pygame(frozen_grid))):
                    error_squares.append(square)
                    str_sqr += square + " "

                # check if any errors were found and update bottom text accordingly
                if str_sqr == "":
                    bottom_text = "No incorrect squares!"
                else:
                    bottom_text = "Incorrect squares are: " + str_sqr

            # P pressed -> enable / disable pencilmarks
            if event.key == pygame.K_p:
                pencilmarks = not pencilmarks
                if pencilmarks:
                    bottom_text="Enabled pencilmarks!"
                    change = 1
                else:
                    bottom_text="Disabled pencilmarks!"

            # L pressed -> pop up a window to load file with sudoku puzzle and load it
            if event.key == pygame.K_l:
                sudoku_file = prompt_file()
                # check if file is a text file
                if sudoku_file[-3:] == "txt":
                    new_grid = ""
                    with open(sudoku_file, "r") as f:
                        # read by character until the end of file
                        while True:
                            char = f.read(1)         
                            if not char:
                                break

                            # character is a digit or empty space -> add it to sudoku
                            if char in digits or char in "0.":
                                new_grid += char

                    # check if sudoku is of correct length and load it
                    if len(new_grid) == 81:
                        frozen_grid = grid_to_pygame(new_grid)
                        grid = [x[:] for x in frozen_grid]
                        error_squares = []
                        change = 1
                        bottom_text="Loaded sudoku from a file!"
                    else:
                        bottom_text="Load failed! (bad input sudoku)"
                else:
                    bottom_text="Load failed! (incorrect file type)"

    # checks if user inputed a new digit and puts it in selected square
    if insert_val != 0:
        # insert only to empty squares in initial puzzle
        if frozen_grid[y][x] == 0:
            # change the value only when it's different from the one before
            if grid[y][x] != insert_val:
                grid[y][x] = insert_val

                # remove this square from error marked squares -> user changed it
                rem_square = str(chr(y + 65)) + str(x+1)
                if rem_square in error_squares:
                    error_squares.remove(rem_square)

            bottom_text=""
            change = 1

            # second part checks if user has solved the sudoku by entering this value

            # go through all squares and check if none of them is zero
            if all(grid[i//9][i%9] != 0 for i in range(81)):
                init_sol = solve(grid_from_pygame(frozen_grid))
                if init_sol != 2 and init_sol != False:
                    # the initial puzzle had a solution
                    if len(check_user_solution(grid_from_pygame(grid), init_sol)) == 0:
                        # there is no difference between user solution and correct solution
                        bottom_text="Correct solution!"
                        square_color = (217, 234, 211)
                        init_square_color = (217, 234, 211)
                        won = True
                    else:
                        won = False
                else:
                    won = False
            else:
                won = False
        
        # reset insert value back to zero
        insert_val = 0
    
    # user changed the board
    if change == 1:
        # keep normal colors if user hasn't won
        if won == False:
            square_color = (245, 227, 207)
            init_square_color = (212, 219, 252)
 
        if pencilmarks:
            # get pencilmarks if showing them is enabled and a change to the board occured
            marks = get_pencilmarks(grid_from_pygame(grid))
        change = 0

    # draw sudoku and bottom text
    draw(error_squares, pencilmarks, marks)
    display_text()
    instructions()

    # draw highlight around selected square
    draw_box()
    
    # Update screen
    pygame.display.update()

    # limit framerate
    time.sleep(0.015)

# Quit pygame window
pygame.quit()