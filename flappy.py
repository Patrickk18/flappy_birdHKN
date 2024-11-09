import pygame
from pygame.locals import *
import pickle
import os
import random

# TODO: replace sprites

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 864
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

# Leaderboard storage file
leaderboard_file = "leaderboard.pkl"

#define fonts
font = pygame.font.SysFont('Bauhaus 93', 60)
small_font = pygame.font.SysFont('Arial Bold', 28)

#define colours
white = (255, 255, 255)

#define game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500  #milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False
player_code = ""
attempt_input = ""
leaderboard = {}

#load images
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')
button_img = pygame.image.load('img/restart.png')

# Load leaderboard
if os.path.exists(leaderboard_file):
    with open(leaderboard_file, 'rb') as f:
        leaderboard = pickle.load(f)


#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_leaderboard():
    draw_text("Leaderboard", small_font, white, screen_width - 150, 10)
    y_offset = 45
    sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
    for i, (code, score) in enumerate(sorted_leaderboard[:5]):
        text = f"{code}: {score}"
        draw_text(text, small_font, white, screen_width - 150, y_offset + i * 29)


def draw_player_data():
    draw_text(player_code, small_font, white, screen_width - 700, 20)
    draw_text(f"Intento: {total_attempts - attempts_left + 1}/{total_attempts}", small_font, white, 20, 20)


def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    return score


class Bird(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f"img/bird{num}.png")
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):

        if flying == True:
            #apply gravity
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if game_over == False:
            #jump
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            #handle the animation
            flap_cooldown = 5
            self.counter += 1

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
                self.image = self.images[self.index]

            #rotate the bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            #point the bird at the ground
            self.image = pygame.transform.rotate(self.images[self.index], -90)


class Pipe(pygame.sprite.Sprite):

    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/pipe.png")
        self.rect = self.image.get_rect()
        #position variable determines if the pipe is coming from the bottom or top
        #position 1 is from the top, -1 is from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        elif position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()

        #check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        # draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action


pipe_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))

bird_group.add(flappy)

#create restart button instance
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)


def save_leaderboard():
    with open(leaderboard_file, 'wb') as f:
        pickle.dump(leaderboard, f)


run = True
input_mode = True

total_attempts = 0
attempts_left = 0

while run:

    if input_mode:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and player_code and attempt_input.isdigit():
                    player_code = player_code.split("0")[0]
                    total_attempts = int(attempt_input)
                    attempts_left = total_attempts
                    input_mode = False  # goes to play screen
                elif event.key == pygame.K_BACKSPACE:
                    if len(attempt_input) > 0:
                        attempt_input = attempt_input[:-1]
                    elif len(player_code) > 0:
                        player_code = player_code[:-1]
                else:
                    if not player_code.endswith("0"):
                        player_code += event.unicode
                    else:
                        attempt_input += event.unicode

        screen.fill((0, 0, 0))
        draw_text("Enter Player Code:", small_font, white, 20, 20)
        draw_text(player_code, small_font, white, 20, 60)
        draw_text("Attempts:", small_font, white, 20, 100)
        draw_text(attempt_input, small_font, white, 20, 140)
        pygame.display.update()

        continue

    clock.tick(fps)

    #draw background
    screen.blit(bg, (0, 0))

    pipe_group.draw(screen)
    bird_group.draw(screen)
    bird_group.update()

    #draw and scroll the ground
    screen.blit(ground_img, (ground_scroll, 768))

    #check the score
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
                and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
                and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False
    draw_text(str(score), font, white, int(screen_width / 2), 20)

    #look for collision
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True
    #once the bird has hit the ground it's game over and no longer flying
    if flappy.rect.bottom >= 768:
        game_over = True
        flying = False

    if flying == True and game_over == False:
        #generate new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        pipe_group.update()

        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

    # Check and update score for leaderboard
    if game_over and player_code:
        if player_code not in leaderboard or score > leaderboard[player_code]:
            leaderboard[player_code] = score
            save_leaderboard()

    # Draw leaderboard on the right side
    draw_leaderboard()

    # Draw player metatada
    draw_player_data()

    # check for game over and reset
    if game_over and button.draw():
        attempts_left -= 1
        game_over = False
        flying = False
        score = reset_game()
        # back to input mode
        if attempts_left ==0:
            player_code = ""
            attempt_input = ""
            input_mode = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not flying and not game_over:
            flying = True

    pygame.display.update()

pygame.quit()