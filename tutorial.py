import os       #TD: Operating System Module that lets us connect to the computer
import random   #TD: Random Module for numbers
import math     #TD: Math Module for numbers
import pygame
from os import listdir 
from os.path import isfile, join
pygame.init()       #TD: Starts the Pygame Window

pygame.display.set_caption("Best Platformer")    #TD: caption for out display window


WIDTH, HEIGHT = 1000, 800                                           #TD: Dimensions of our game window
FPS = 60                                                           #TD: Refresh rate of our game window
PLAYER_VEL = 6                                                      #TD: Player Velocty, the higher the faster the character 

PATH = r'C:\Coding Projects\2D-Platformer\assets'                   #TD: The directory that I used to collect objects for the game

window = pygame.display.set_mode((WIDTH, HEIGHT))                   #TD: Using the Width & Height variables


def flip(sprites):  #CG: Sprites originally all face the right so this function will flip the sprites so they will face the left if the player is facing the left
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]   #CG: Built-in function which checks the direction of the character, which way to flip depending on if it is true or false and will do this for every sprite image per player sprite   


def load_sprite_sheets(dir1, dir2, width, height, direction=False):  #CG: This function will load all of the different sprite sheets for each character. Direction determines if the sprite is flipped or not
    path = join(PATH, dir1, dir2) #CG: Built-in function that creates a path to the directory of images 
    images = [f for f in listdir(path) if isfile(join(path, f))] #CG: Will load every file in that directory allowing them to be loaded in and manipulated

    all_sprites = {}  #CG: A dictionary that will have each sprite sheet's individual images added to it 

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha() #Will load a transparent background image from the needed image directory for each image in the directory

        sprites = [] #CG: Creates anempty list to collect each individual image in a given sprite sheet
        for i in range(sprite_sheet.get_width() // width): #CG: This will chop up the sprite sheets containing the entire animation cycles into each individual frame of the animation by dividing the length of the sprite sheet by the width of each individual animation frame.
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32) #CG: Creates surface that an image can be blitted (drawn) on and is the size of an individual animation frame
            rect = pygame.Rect(i * width, 0, width, height) #CG: Determines where in the sprite sheet the image is pulled from in this case the top left corner of each animation frame is the "starting point" of the sprite
            surface.blit(sprite_sheet, (0, 0), rect) #CG Draws specific sprite frame needed which is determined by rect onto the surface which is a given size of the sprite
            sprites.append(pygame.transform.scale2x(surface)) #CG: Adds this sprite to the list of sprites while scaling it up by a factor of 2 

        if direction: #CGAdds a mirror image of each type of sprite sheet ie. falling, jumping to the master dictionary of all_sprites depending on direction
            all_sprites[image.replace(".png", "") + "_right"] = sprites #CG: The next two lines will add to all_sprite sheets depending on the direction and will use the flip function if player is facing left
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites #CG: Otherwise just use base sprites facing right

    return all_sprites #CG: Allows all sprites that have been stripped and chopped up to now be called and applied to whatever object requires a sprite in the game 


def get_block(size):
    path = join(PATH, "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):                         #TD: We are using the built-in pygame Sprite Class to animate and move our character. CG: We use a class to define the player so that a multitude of functions can be called upon while interacting with the player
    COLOR = (255, 0, 0)                                     #CG: Sets a basic colour to the character but will not be seen once the sprite is loaded and covers it up
    GRAVITY = 1                                             #This is the base velocity of gravity downwards
    SPRITES = load_sprite_sheets("MainCharacters", "VirtualGuy", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):                #TD: This is the first function that gets initialized once the game begins CG: self is used for all functions under the class player to refer to functions and variables only accessible by the player class
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)        #TD: This is the player's rectangle hitbox, lots of built-in Pygame functions are being used
        self.x_vel = 0                                      #TD: Speed in the x direction per frame
        self.y_vel = 0                                      #TD: Speed in the y direction per frame
        self.mask = None                                    #TD: 
        self.direction = "left"                             #TD: When the game gets initialized, the character's direction begins by facing the left
        self.animation_count = 0                            #TD: When the game gets initialized, the character's animation count begins at 0
        self.fall_count = 0                                 #TD: When the game begins, the fall count starts at zero CG: is a variable set to track how long the character has been falling
        self.jump_count = 0                                 #TD: When the game begins, the jump count is also zero  
        self.hit = False                                    #TD: When the game starts the character is NOT being hit
        self.hit_count = 0                                  #TD: When the game starts the character hit count is at zero

    def jump(self):                                         
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx                                   #TD: Some calculus, basically adding a change in the X direction
        self.rect.y += dy                                   #TD: Adding Some change in the Y direction

    def make_hit(self):
        self.hit = True

    def move_left(self, vel):
        self.x_vel = -vel                                   #TD: Some Physics, essentially a left movement is a negative velocity movement CG: it is negative because you must subtract from the x and y coordinates of the player to move them left
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel                                    #TD: Movement in the right is positive velocity
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):                                    #CG: Will be called every frame and will check which direction the player is facing and update the animation accordingly as well as move the player
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY) #CG: This will make the player be affected by gravity. It works by making the player fall at the specified unit of gravity which is 1 but will increase the speed at which you fall depending on how long you are falling. This is done by dividing fall_count by fps to track how many seconds character has been falling and the adding additional acceleration downwards
        self.move(self.x_vel, self.y_vel)  #CG: This will move the character left and right if the variables are changed

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1 #CG: This will make you fall permanently unless you are colliding with an object simulating gravity in the game
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):    #CG: Will animate all visual changes
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


def get_background(name):                                       #TD: Background Function that is going to return how many tiles we need to draw CG: name is used to change the type of tile that is called to change background if needed
    image = pygame.image.load(join(PATH, "Background", name))   #TD: collects the assets path, within the background subfolder and name variable representing the filename
    _, _, width, height = image.get_rect()                      #TD: get_rect() Collects the X & Y values needed for each tile
    tiles = []  #CG: creates an empty list and following for loops will add the tiles needed to this list and will then display the list

    for i in range(WIDTH // width + 1):         
        for j in range(HEIGHT // height + 1):       #TD: Basically divides the number tiles needed in the X & Y and adds 1 so there is no empty space
            pos = (i * width, j * height)           #TD: Creates a tuple of the x,y and needed for the entire window 
            tiles.append(pos)                       #TD: inserts the number of tiles needed from the position calculation variable

    return tiles, image                             #TD: now we can use the image and tiles outside of the function
                                                    #TD: In summary, the function will take a background image from my computers memory and divides it into tiles. The function will also calculate the position of these tiles in order to be used later on

def draw(window, background, bg_image, player, objects, offset_x): #CG: This function will draw the background onto the game screen in combination with the get_background function and draw the player
    for tile in background:                         #TD: loops through the background and gets a number of tiles per background
        window.blit(bg_image, tile)                 #CG: This line will loop for each tile and draw the background at the position of the tile variable which contains the x and y coordinates of every tile that needs to be drawn

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x) 

    pygame.display.update()  #CG: This updates the screen at every frame and will reload the images each frame so old drawings don't stay on the screen


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects):  #CG: This function will change the coordinates of the player based on the keys pressed
    keys = pygame.key.get_pressed() #CG: built-in function that checks which keys are being pressed

    player.x_vel = 0  #CG: Must set velocity to initial of 0 so that the x velocity isn't permanently set to the direction you move in and will be reset to zero so you stop moving when a key is not being pressed
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:  #CG checks if the left arrow keys are being pressed and that the player is not currently colliding with anything to the left of it
        player.move_left(PLAYER_VEL)  #CG: If true makes the character move to the left at the speed previously chosen by Player_vel
    if keys[pygame.K_RIGHT] and not collide_right: #CG checks if the right arrow keys are being pressed and that the player is not currently colliding with anything to the right of it
        player.move_right(PLAYER_VEL) #CG: If true makes the character move to the right at the speed previously chosen by Player_vel

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()


def main(window):       #TD: Main code for the actual game
    clock = pygame.time.Clock()   #CG: regulates how fast the game will run
    background, bg_image = get_background("Gray.png")   #CG: Will call background based on asset name in this case we use the gray background

    block_size = 96

    player = Player(100, 100, 50, 50)   #CG: Creates a basic block character with given c and y coordinates and width and height
    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]
    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size),
               Block(block_size * 3, HEIGHT - block_size * 4, block_size), fire]

    offset_x = 0
    scroll_area_width = 200

    run = True
    while run:
        clock.tick(FPS) #CG: using line 284 will set the speed of the game to the FPS so it won't run too fast or too slow

        for event in pygame.event.get():   #CG: for event checks for specific events or action taken
            if event.type == pygame.QUIT:   #CG: This checks that in the event of the player exiting the game the program is stopped
                run = False
                break  #CG: Break is used to exit the loop as soon as run=False so that the computer does not keep checking for pygame.Quit

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        player.loop(FPS) #CG: Need to call the loop function as it is what moves the player and it is set to refresh and move the character at the same rate as our declared framerate of 60
        fire.loop()
        handle_move(player, objects) #CG: This will call the movement function and apply it to the character and objects
        draw(window, background, bg_image, player, objects, offset_x) #CG: This line will call the draw function and will display the objects, background and character in the game

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()   #CG: This line and the line below will quit the Python program if the game is stopped
    quit()


if __name__ == "__main__":    #CG: This line makes the main function run only if the game is run but, if something is imported from the game it will not run the entire game
    main(window)
