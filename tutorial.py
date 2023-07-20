import os 
import random
import math
import pygame
from os import listdir
from os.path import isfile, join, splitext

pygame.init()

pygame.display.set_caption("Capital Clash")

# Key Variables
WIDTH, HEIGHT = 1056, 800
FPS = 60
PLAYER_VEL = 5
HEALTH_FONT = pygame.font.Font(join("assets", "Menu", "Text", "retro_font.ttf"), 20)
WINNER_FONT = pygame.font.Font(join("assets", "Menu", "Text", "retro_font.ttf"), 80)

MAX_HEALTH = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, scale=1.0, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f)) and splitext(f)[-1].lower() != ".wav"]
    
    all_sprites = {}
    
    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()
        
        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale(surface, (width * scale, height * scale)))
            
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites
            
    return all_sprites

def load_sprite_audio(dir1, dir2):
    path = join("assets", dir1, dir2, "audio.wav")
    audio = pygame.mixer.Sound(path) 
    return audio

def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

def draw_lives(window, name, health, x_coord):
    header = HEALTH_FONT.render(name, 1, (0,0,0))

    window.blit(header, (x_coord, 50))

    angle = 75
    path = join("assets", "Other", "full_card.png")
    full_card = pygame.image.load(path).convert_alpha()
    path = join("assets", "Other", "empty_card.png")
    empty_card = pygame.image.load(path).convert_alpha()

    full_card = pygame.transform.scale(pygame.transform.rotate(full_card, angle), (50, 32))
    empty_card = pygame.transform.scale(pygame.transform.rotate(empty_card, angle), (50, 32))

    for i in range(MAX_HEALTH):
        if i < health:
            window.blit(full_card, (x_coord + (i*55), 100))
        else:
            window.blit(empty_card, (x_coord + (i*55), 100))


def draw_winner(window, winner):
    text = WINNER_FONT.render(winner.upper(), 1, (255,0,0))
    wins = WINNER_FONT.render("WINS!!!", 1, (255,0,0))
    window.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 3*text.get_height()//2))
    window.blit(wins, (WIDTH//2 - wins.get_width()//2, HEIGHT//2 - text.get_height()//2))

    


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    # SPRITES = load_sprite_sheets("MainCharacters", "Taylor", 75, 101, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height, controls, sprites, audio, voice, name):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.controls = controls
        self.SPRITES = sprites
        self.audio = audio
        self.voice = voice
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.is_hit = False
        self.hit_count = 0
        self.health = MAX_HEALTH
        self.name = name
        
    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def play_sound(self):
        if self.voice.get_busy():
            self.voice.stop()
        self.voice.play(self.audio)
    
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        
    def hit(self):
        self.is_hit = True
        self.hit_count = 0

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0
    
    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)
        
        if self.is_hit:
            self.hit_count += 1
        if self.hit_count > fps:
            self.is_hit = False
            self.hit_count = 0
        
        self.fall_count += 1
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
        if self.is_hit:
            sprite_sheet = "hit"
        if self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.jump_count == 1:
                sprite_sheet = "jump"
        elif self.jump_count == 2:
            sprite_sheet = "double_jump"            
        elif self.x_vel != 0:
            sprite_sheet = "run"
            
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        if self.animation_count > 100:
            self.animation_count = 0
        self.update()
        
    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)
    
    def draw(self, win, offset_x):
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
        
# class Fire(Object):
#     ANIMATION_DELAY = 3
#     def __init__(self, x, y, width, height):
#         super().__init__(x, y, width, height, "fire")
#         self.fire = load_sprite_sheets("Traps", "Fire", width, height)
#         self.image = self.fire["off"][0]
#         self.mask = pygame.mask.from_surface(self.image)
#         self.animation_count = 0
#         self.animation_name = "off"
        
#     def on(self):
#         self.animation_name = "on"
        
#     def off(self):
#         self.animation_name = "off"
        
#     def loop(self):
#         sprites = self.fire[self.animation_name]
#         sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
#         self.image = sprites[sprite_index]
#         self.animation_count += 1
#         self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
#         self.mask = pygame.mask.from_surface(self.image)
        
#         if self.animation_count // self.ANIMATION_DELAY > len(sprites):
#             self.animation_count = 0
        
    

# chooses one static background that scales the window
def get_static_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    size = pygame.transform.scale(image, (WIDTH, HEIGHT))
    window.blit(size, (0, 0))
    pygame.display.update()

# chooses background and sets up tile position
def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    # generates tiles for background in sequence
    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)
    
    return tiles, image

# drawing tiles and updating display
def draw(window, background, bg_image, player1, player2, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)
        
    for obj in objects:
        obj.draw(window, offset_x)
    
    player1.draw(window, offset_x)
    player2.draw(window, offset_x)

    draw_lives(window, player1.name, player1.health, 30)
    draw_lives(window, player2.name, player2.health, WIDTH - 300)

    if player1.health == 0:
        draw_winner(window, player2.name)
    elif player2.health == 0:
        draw_winner(window, player1.name)


    pygame.display.update()
    
def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if player.rect.colliderect(obj):
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

    if player.rect.left <= PLAYER_VEL or player.rect.right >= WIDTH - PLAYER_VEL:
        collided_object = Block(0,0,0)
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break
        
    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects, floor):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)
    
    if keys[player.controls['left']] and not collide_left:
        player.move_left(PLAYER_VEL)

    if keys[player.controls['right']] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, floor + objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check:
        if obj and obj.name == "fire":
            player.hit()
            break

def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")
    
    block_size = 96

    player1 = Player(50, HEIGHT - 200, 50, 50, {"left": pygame.K_a, "right": pygame.K_d}, load_sprite_sheets("MainCharacters", "Taylor", 75, 101, 0.75, True), load_sprite_audio("MainCharacters", "Taylor"), pygame.mixer.Channel(1), "Taylor Swift")
    player2 = Player(WIDTH - 96, HEIGHT - 200, 50, 50, {"left": pygame.K_LEFT, "right": pygame.K_RIGHT},load_sprite_sheets("MainCharacters", "SamJackson", 32, 32, 2, True), load_sprite_audio("MainCharacters", "SamJackson"), pygame.mixer.Channel(2), "Samuel L. Jackson")
    floor = [Block(i * block_size, HEIGHT - block_size, block_size) 
             for i in range(-WIDTH // block_size, WIDTH * 2 // block_size)]
    
    objects = [Block(0, HEIGHT - block_size * 2, block_size), 
               Block(block_size * 3, HEIGHT - block_size * 4, block_size),
               Block(WIDTH - block_size, HEIGHT - block_size * 2, block_size),
               Block(WIDTH - block_size * 4, HEIGHT - block_size * 4, block_size),
               Block(block_size * 5, HEIGHT - block_size * 5, block_size),
               Block(0, HEIGHT - block_size * 6, block_size),
               Block(WIDTH - block_size, HEIGHT - block_size * 6, block_size)]
    
    # left_walls = [Block(-block_size, i * block_size, block_size) for i in range(HEIGHT // block_size)]
    # right_walls = [Block(WIDTH, i * block_size, block_size) for i in range(HEIGHT // block_size)]
    # walls = left_walls + right_walls

    path = join("assets", "Other", "music.mp3")
    pygame.mixer.music.load(path)
    pygame.mixer.music.set_volume(0.75)
    pygame.mixer.music.play(-1)
    
    offset_x = 0
    scroll_area_width = 200
    
    jumped_count = 0
    run = True
    # ensures the game runs at 60 fps
    while run: 
        clock.tick(FPS)

        # checks for events in the game (quit)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and player1.jump_count < 2:
                    player1.jump()
                if event.key == pygame.K_UP and player2.jump_count < 2:
                    player2.jump()
        
        player1.loop(FPS)
        player2.loop(FPS)
        if player1.rect.colliderect(player2.rect):
            if player1.rect.bottom <= player2.rect.top + 20:
                jumped_count += 1
                if jumped_count == 1 and player1.health > 0 and player2.health > 0:
                    player2.health -= 1
                    player1.play_sound()
                    player2.hit()
            elif player2.rect.bottom <= player1.rect.top + 20:
                jumped_count += 1
                if jumped_count == 1 and player1.health > 0 and player2.health > 0:
                    player2.play_sound()
                    player1.health -= 1
                    player1.hit()
            else:
                if player1.rect.x < player2.rect.x:
                    if player1.rect.left <= PLAYER_VEL:
                        player2.rect.left = player1.rect.right
                    else:
                        player1.rect.right = player2.rect.left
                else:
                    if player1.rect.right >= WIDTH - PLAYER_VEL:
                        player2.rect.right = player1.rect.left
                    else:
                        player1.rect.left = player2.rect.right
        else:
            jumped_count = 0
        
        handle_move(player1, objects, floor)
        handle_move(player2, objects, floor)
        draw(window, background, bg_image, player1, player2, floor + objects, offset_x)
        
        # if (player1.rect.right - offset_x >= WIDTH - scroll_area_width and player1.x_vel > 0) or (
        #     player1.rect.left - offset_x <= scroll_area_width and player1.x_vel < 0):
        #     offset_x += player1.x_vel

        pygame.event.pump()

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)
