import pygame, random, blocks

TILESIZE = 30
WIDTH = 16*TILESIZE
HEIGHT = 16*TILESIZE
HATENABLED = False

if HATENABLED:
    import unicornhathd

class Block(object):
    def __init__(self, details):
        self.x = 8
        self.y = 0
        self.shape = details[0]
        self.colour = details[1]
        self.rotation = 0

def create_grid(locked_positions = {}):
    grid = [[(0,0,0) for i in range(16)] for i in range(16)]
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                colour = locked_positions[(j, i)]
                grid[i][j] = colour
    return grid

def renderGrid(surface, grid):
    surface.fill((0,0,0))
    for i in range(len(grid)):
        for j in range(len(grid)):
            pygame.draw.rect(surface, grid[i][j], (j*TILESIZE, i*TILESIZE, TILESIZE, TILESIZE), 0)
            if HATENABLED:
                unicornhathd.set_pixel(i, j, grid[i][j][0], grid[i][j][1], grid[i][j][2])

    for i in range (len(grid)):
        pygame.draw.line(surface, (255,255,255), (0, i*TILESIZE), (WIDTH, i*TILESIZE))#Draws horizontal lines
        for j in range(len(grid)):
            pygame.draw.line(surface,(255,255,255), (j*TILESIZE, 0), (j*TILESIZE, HEIGHT))##Draws vertical lines

    pygame.display.update()

def validSpace(shape, grid): #Probably put this inside shape class
    accepted_pos = [[(j, i) for j in range(16) if grid[i][j] == (0,0,0)] for i in range(16)] # Creates 2D empty grid containing only black squares(IE Empty)
    accepted_pos = [j for sub in accepted_pos for j in sub] ##Flattens 2D list to 1d
    formatted_shape = convertShape(shape)

    for position in formatted_shape:
        if position not in accepted_pos and (position[1] > - 1): #Prevents the function from thinking out of bounds shapes are invalid
            return False
    return True

def checkGameOver(positions):
    for position in positions:
        x, y = position ##Splits coords into x and y
        if y < 1:
            return True ##If any of the positions are outside of the screen, return true (player has lost)
    return False #If they havent lost return false

def convertShape(shape): # Probably put this inside shape class
    positions = []
    shape_format = shape.shape[shape.rotation % len(shape.shape)] ##Gets the correct grid depending on rotation of shape

    for i, line in enumerate(shape_format): ##Row
        row = list(line)
        for j, column in enumerate(row):
             if column == "0": ##If the current coord is a 0 append to list
                positions.append((shape.x + j, shape.y + i)) ##Cycles through position list gathering coords of block

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4) ##Fixes the issue with all coords being offset by the amount of "."s - Prevents out of bounds errors

    return positions

def clearRows(grid, locked_positions):
    increment = 0
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if (0,0,0) not in row:
            increment += 1 ##Increase the amount of total cleared rows
            ind = i
            for j in range(len(row)):
                try:
                    del locked_positions[(j,i)]
                except:
                    continue
    if increment > 0: #If a row has been cleared
        for key in sorted(list(locked_positions), key=lambda x: x[1])[::-1]: #Sorts locked positions by reverse Y value
            x, y = key
            if y < ind:
                new_key = x, (y+increment)
                locked_positions[new_key] = locked_positions.pop(key)#Replaces Key


def main(surface):
    locked_positions = {}
    grid = create_grid(locked_positions)
    clock = pygame.time.Clock()


    change_piece = False
    fall_time = 0 #Initilises the fall time variable to track how long to wait before moving block down
    fall_speed = 0.27#The speed of falling blocks
    level_time = 0
    current_block = getBlock()
    next_block = getBlock()
    game_over = False

    while not game_over:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime() #Gets the real time since the last clock.tick()
        clock.tick()
        #PROBABLY MOVE THIS INTO A DIFFERENT FUNCTION
        if fall_time/2000 > fall_speed: #After a certain time cause the block to move down
            fall_time = 0 # Reset time  till next fall
            current_block.y += 1 #Increment y
            if not (validSpace(current_block, grid)) and current_block.y > 0: # If the block has moved into an invalid square move it back
                current_block.y -= 1
                change_piece = True #Cause the piece to be locked and a new one to spawn


        for event in pygame.event.get():
            pressedKeys = pygame.key.get_pressed()
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                altKey = pressedKeys[pygame.K_LALT] or pressedKeys[pygame.K_RALT]
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_F4 and altKey:
                    game_over = True
                if event.key == pygame.K_LEFT:
                    current_block.x -= 1
                    if not(validSpace(current_block, grid)):
                        current_block.x += 1
                if event.key == pygame.K_RIGHT:
                    current_block.x += 1
                    if not(validSpace(current_block, grid)):
                        current_block.x -= 1
                if event.key == pygame.K_DOWN:
                    current_block.y += 1
                    if not(validSpace(current_block, grid)):
                        current_block.y -= 1
                if event.key == pygame.K_UP:
                    current_block.rotation += 1
                    if not(validSpace(current_block, grid)):
                        current_block.rotation -= 1

        shape_position = convertShape(current_block)
        #Also move this into new function

        for i in range(len(shape_position)):
            x, y = shape_position[i] #Converts coords into x and y variables
            if y > -1:
                grid[y][x] = current_block.colour

        if change_piece: #If the piece must be changed then change (MOVE THIS INTO NEW FUNCTION)
            for position in shape_position:
                p = (position[0], position[1])
                locked_positions[p] = current_block.colour #Adds the static block into the locked positons grid.
            current_block = next_block
            next_block = getBlock()
            change_piece = False
            clearRows(grid, locked_positions)

        #Check if lost (move into new function)
        if checkGameOver(locked_positions):
            game_over = True
            pygame.display.quit()

        renderGrid(surface, grid)
        pygame.display.update()

def getBlock():
    return Block(random.choice(blocks.blocks))

surface = pygame.display.set_mode((WIDTH, HEIGHT))
main(surface)