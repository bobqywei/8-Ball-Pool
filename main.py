"""
    File: main.py
    Author: Bob Wei
    Date: 6/6/2017
    Project Name: 8 Ball Pool
    Description: An 8 Ball Pool game that uses a self-written Pygame game engine to provide accurate game physics and 
                 monitoring of game events and player input
    Variable Table: All global game variable are explained in the "IN-GAME LIST AND VARIABLE DECLARATIONS" section
"""
# ==================================================================================================================
# IMPORT LIBRARIES
# ==================================================================================================================
import sys
import pygame
from pygame.locals import *
import math
import time

# ==================================================================================================================
# INITIALIZING MEDIA AND LIBRARIES
# ==================================================================================================================
# initializes PyGame and fonts library
pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.init()
pygame.font.init()
# used fonts
mainFont = pygame.font.SysFont("impact", 30)
# loads all sound effects
hit_sound = pygame.mixer.Sound('hit.wav')
sunk_sound = pygame.mixer.Sound('sunk.ogg')
strike_sound = pygame.mixer.Sound('strike.wav')
# sets the display size
gameDisplay = pygame.display.set_mode((1400, 800))
pygame.display.set_caption('8 Ball Pool')
# built in frame rate throttling
clock = pygame.time.Clock()

# ==================================================================================================================
# CLASSES
# ==================================================================================================================


# class for the balls used in the game
class Ball (object):
    def __init__(self, colour, x, y, img_name):
        # stripes or solids
        self.colour = colour
        # coordinates of ball
        self.x = x
        self.y = y
        # sprite of ball
        self.sprite = pygame.image.load(img_name)
        # direction of ball in degrees
        self.movement_direction = 0
        # speed of ball
        self.speed = 0
        # frames used in ball movement
        self.frames = 0
        # check for whether ball is potted
        self.potted = False
        self.collision_monitor = []
        # fills the monitor list with False
        for i in range(16):
            self.collision_monitor.append(False)


# class for the two player object types
class Player (object):
    def __init__(self, number, colour):
        self.number = number
        self.colour = colour
        self.only_eight_ball_left = False

# ==================================================================================================================
# IN-GAME LIST AND VARIABLE DECLARATIONS
# ==================================================================================================================
# tuple containing coordinates and dimensions of walls of pool table
walls = (pygame.Rect(150, 100, 1100, 50), pygame.Rect(150, 650, 1100, 50), pygame.Rect(1200, 100, 50, 600), pygame.Rect(150, 100, 50, 600))
# tuple containing coordinates of pockets
holes = ((210, 160), (700, 150), (1190, 160), (210, 640), (700, 650), (1190, 640))
# image of pool cue
pool_cue_original = pygame.image.load('cue.png')
# variable that will be used to store rotated version of pool cue image
pool_cue_rotated = pygame.transform.rotate(pool_cue_original, 0)
# stores the coordinates of the pool cue image
pool_cue_coords = (0, 0)
# stores the coordinates of the mouse cursor when needed
mouse_hold_coords = (0, 0)
# keeps track of the state of the mouse
mouse_held = False
# instantiates an object of ball class for the cue ball
cue_ball = Ball('', 550, 400, 'ball0.png')
# variable that stores the direction of the player cue as a number in degrees
cue_direction = 0
# variable used to store the distance the player pulls the cue back to strike the ball
strike_distance = 0
draw_guide = True
# boolean variable keeping tack of whether or not any balls are in motion
in_play = False
# boolean variable for keeping track of whether or not the colours (stripes or solids) have been assigned
initial_break = True
# creates two instances of the player class for player 1 and player 2
# note that the colour parameter is currently left empty
player_1, player_2 = Player(1, ''), Player(2, '')
# variable that stores the player object that is currently in possession
player_turn = player_1
# boolean variable representing whether or not the player has cue ball in hand
cue_ball_in_hand = False
# boolean variable representing whether or not the player turn changes depending on in game events
turn_change = True
# variable that will store the first ball hit by the cue ball during each player's turn
first_ball_collided_with = None
# variable that will store the winning player
winner = None
# list containing ball objects (all 16 balls)
balls = [cue_ball, Ball('solids', 950, 400, 'ball1.png'), Ball('solids', 986, 420, 'ball2.png'),
         Ball('solids', 1022, 420, 'ball3.png'), Ball('solids', 1022, 360, 'ball4.png'),
         Ball('solids', 968, 390, 'ball5.png'), Ball('solids', 1004, 410, 'ball6.png'),
         Ball('solids', 1004, 370, 'ball7.png'),
         Ball('eight', 986, 400, 'ball8.png'), Ball('stripes', 986, 380, 'ball9.png'),
         Ball('stripes', 1004, 430, 'ball10.png'), Ball('stripes', 1004, 390, 'ball11.png'),
         Ball('stripes', 1022, 440, 'ball12.png'), Ball('stripes', 1022, 380, 'ball13.png'),
         Ball('stripes', 968, 410, 'ball14.png'), Ball('stripes', 1022, 400, 'ball15.png')
         ]
# list for storing the balls that have been potted after each turn
recent_potted_balls = []
# list for storing all of the potted balls over the course of the game
potted_balls = []
# colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FELT = (49, 185, 77)
OAK = (79, 36, 18)
RED = (255, 0, 0)

# ==================================================================================================================
# FUNCTIONS
# ==================================================================================================================


# draws the background and pool table
def draw_background():
    # white background
    gameDisplay.fill(WHITE)
    # green felt for pool table
    pygame.draw.rect(gameDisplay, FELT, (200, 150, 1000, 500))
    # draws all of the table walls
    for wall in walls: pygame.draw.rect(gameDisplay, OAK, wall)
    # draws each of the six pockets
    for hole in holes: pygame.draw.circle(gameDisplay, BLACK, hole, 22)
    p1_colour = player_1.colour
    p2_colour = player_2.colour
    # draws the player and turn information at the top of the game display
    gameDisplay.blit(mainFont.render('PLAYER 1', 1, BLACK), (20, 10))
    gameDisplay.blit(mainFont.render(p1_colour.upper(), 1, BLACK), (20, 50))
    gameDisplay.blit(mainFont.render('PLAYER 2', 1, BLACK), (1260, 10))
    gameDisplay.blit(mainFont.render(p2_colour.upper(), 1, BLACK), (1260, 50))
    gameDisplay.blit(mainFont.render('PLAYER ' + str(player_turn.number) + '\'S TURN', 1, RED), (600, 10))


# function that switches the active player during each turn switch
def player_turn_switch(turn):
    if turn.number == 1:
        return player_2
    else:
        return player_1


# draws all of the potted balls on the lower left portion of the screen
def draw_potted_balls():
    for index in range(len(potted_balls)):
        gameDisplay.blit(potted_balls[index].sprite, (250 + (index * 25), 750))


# function finds the distance between two points given the x and y coordinates
def distance_between_points(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


# function finds the difference in degrees between two angles
def difference_between_angles(a1, a2):
    # finds the absolute differences between the two angles (two different orders)
    distance1, distance2 = abs(a1 - a2), abs(a2 - a1)

    # if the first distance is less than or equal to 180 degrees, the second must be greater than 180
    # and so the first angle is returned
    if distance1 <= 180:
        return distance1
    # similarly the second angle is returned if it is less than or equal to 180 degrees
    elif distance2 <= 180:
        return distance2
    # if else, then another angle value is returned that takes into account the cyclic nature of degrees
    # (0-360 cycle, where 1 degrees is the same as 361 degrees)
    else:
        if a1 > a2:
            return 360 - a1 + a2
        else:
            return 360 - a2 + a1


# function finds the angle formed by the line connecting any two coordinates
def coordinates_to_angle(x1, y1, x2, y2):
    # finds the x and y differences between the two separate coordinates
    x_diff, y_diff = x2 - x1, -(y2 - y1)
    # checks if the x difference (denominator) is 0
    if x_diff == 0:
        # depending on the value of the y difference, the angle is determined
        if y_diff > 0:
            return 90
        elif y_diff < 0:
            return 270
        else:
            return 0
    # if the x difference is not 0, then inverse tangent is used to find the temporary angle beta
    else:
        beta = math.degrees(math.atan(y_diff/x_diff))

    if x_diff > 0:
        if y_diff < 0:
            beta += 360
    elif x_diff < 0:
        beta += 180
    # returns the angle in degrees
    return beta


# function finds the second coordinate of a line given the angle, first coordinate, and length of the line
def angle_to_coordinates(startx, starty, angle, length):
    if angle is not None:
        return startx + length * math.cos(math.radians(angle)), starty - length * math.sin(math.radians(angle))
    else:
        return startx, starty


# function returns a rotated surface given the original image and the angle (in degrees) to be rotated
def rot_center(image, angle):
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image


# function returns the angle of a moving ball if it collides with a wall (given the ball's coordinates)
def collision_with_wall(x, y, angle):
    # returns the modified angle depending on which wall the ball collides with
    # if the ball collides with upper or lower wall
    if y - 10 <= 150 or y + 10 >= 650:
        return 360 - angle
    # if the ball collides with right wall
    elif x + 10 >= 1200:
        if angle < 90:
            return 180 - angle
        elif angle > 270:
            return 540 - angle
    # if the ball collides with left wall
    elif x - 10 <= 200:
        if 180 > angle > 90:
            return 180 - angle
        elif 270 > angle >= 180:
            return 540 - angle


# resets all of the booleans in the collision monitor list for each of the 16 balls
# sllows for balls to collide once again
def collision_monitor_reset():
    for b in balls:
        if not b.potted:
            for b2 in range(16):
                b.collision_monitor[b2] = False


# checks whether a given ball is colliding with any of the other balls
def check_collision_with_other_ball(x, y, ball1):
    # loops through the balls list
    for b in balls:
        # checks the collision monitoring list to make sure that the specific collision is not redundant
        if not ball1.collision_monitor[balls.index(b)] and not b.potted:
            # makes sure that the two balls being compared are not the same ball
            if b.x != x and b.y != y:
                # finally checks if the two balls collide
                if distance_between_points(x, y, b.x, b.y) <= 20:
                    # returns the ball object if there is a successful collision
                    return b


# function returns the updated directions and speeds of balls after a collision based on physics
def ball_collision_physics(x1, y1, x2, y2, initial_angle, initial_speed):
    # the angle of the second ball will be the angle determined by the origins of the two colliding balls
    angle2 = coordinates_to_angle(x1, y1, x2, y2)
    # two variables used to determine which direction initial ball came from (left or right of second ball)
    clockwise, counter_clockwise = angle2 - 90, angle2 + 90
    # the angle of the first ball is determined based on which value the initial angle is closer to
    if difference_between_angles(clockwise, initial_angle) < difference_between_angles(counter_clockwise, initial_angle):
        angle1 = clockwise
    else:
        angle1 = counter_clockwise
    # speeds of each ball is determined through vector projection calculations
    speed1 = initial_speed * math.cos(math.radians(difference_between_angles(angle1, initial_angle)))
    speed2 = initial_speed * math.cos(math.radians(difference_between_angles(angle2, initial_angle)))
    # makes sure the speed is not a decimal value that is less than 1
    if speed1 < 1:
        speed1 = 1
    if speed2 < 1:
        speed2 = 1
    # returns the updated values
    return angle1, angle2, speed1, speed2


# function checks for whether any balls are still moving
def balls_stopped():
    for ball in balls:
        if ball.speed > 0 and not ball.potted:
            return False
    # returns true if none are moving
    return True


# function for checking if a given ball is potted given its x and y coordinates
def ball_potted(x, y):
    for hole in holes:
        # compares the x and y coordinates of the ball with that of each hole
        # in order to determine if the ball is potted
        if distance_between_points(x, y, hole[0], hole[1]) < 17:
            return True
    return False


# function call for when the ball is in hand (able to be moved by the player)
def ball_in_hand():
    # variables for ball and mouse state
    ball_dropped = False
    button_down = False
    while not ball_dropped:
        # draws everything
        draw_background()
        draw_potted_balls()
        for ball in balls:
            if not ball.potted: gameDisplay.blit(ball.sprite, (ball.x - 10, ball.y - 10))
        pygame.display.update()
        # acquires each game event
        for e in pygame.event.get():
            # quits game if user exits
            if e.type == QUIT:
                pygame.quit()
                sys.exit()
            # if the mouse is moved, the coordinates are obtained and the cue ball is moved only if the mouse is
            # not colliding with any of the other active balls
            if e.type == MOUSEMOTION:
                mouseX, mouseY = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
                if 210 < mouseX < 1190 and 160 < mouseY < 640:
                    if check_collision_with_other_ball(mouseX, mouseY, cue_ball) is None:
                        cue_ball.x, cue_ball.y = mouseX, mouseY
            # once the player clicks, the ball is dropped and the ball is no longer in hand
            if e.type == MOUSEBUTTONDOWN:
                button_down = True
            if e.type == MOUSEBUTTONUP and button_down:
                ball_dropped = True


# function for checking the number of balls potted that are of the given colour 'c' (i.e. stripes or solids)
def number_of_balls_potted(c):
    total = 0
    for b in potted_balls:
        if b.colour == c:
            total += 1
    return total


# function call for when the game ends and a winner is determined
def game_over():
    while True:
        # acquires each game event
        for e in pygame.event.get():
            # quits game if user exits
            if e.type == QUIT:
                pygame.quit()
                sys.exit()
        # draws everything
        draw_background()
        draw_potted_balls()
        for b in balls:
            if not b.potted:
                gameDisplay.blit(b.sprite, (b.x - 10, b.y - 10))
        # draws text saying who won the match
        gameDisplay.blit(mainFont.render('PLAYER ' + str(winner.number) + ' WINS!', 1, RED), (615, 390))
        # updates screen
        pygame.display.update()

# =====================================================================================================================
# MAIN CODE
# =====================================================================================================================
while winner is None:
    # draws the background setting of the game
    draw_background()
    # draws the balls that have been potted on the lower part of the game screen
    draw_potted_balls()

    for ball in balls:
        if not ball.potted:
            # draws each of the balls present
            gameDisplay.blit(ball.sprite, (ball.x - 10, ball.y - 10))
            # if balls are in play
            if in_play:
                # executes if the specific ball is moving
                if ball.speed > 0:
                    # moves the ball incrementally based on its speed
                    for i in range(int(ball.speed)):
                        # checks if the ball collides with a wall
                        if ball.y - 10 <= 150 or ball.y + 10 >= 650 or ball.x + 10 >= 1200 or ball.x - 10 <= 200:
                            # plays wall hit sound
                            hit_sound.play()
                            # ball loses speed
                            if ball.speed > 1:
                                ball.speed -= 1
                            # calculates new angle of ball following collision
                            ball.movement_direction = collision_with_wall(ball.x, ball.y, ball.movement_direction)
                            # resets monitoring lists so that all ball collisions can occur again
                            collision_monitor_reset()
                        # the coordinates of the ball are translated 1 in the correct direction
                        ball.x, ball.y = angle_to_coordinates(ball.x, ball.y, ball.movement_direction, 1)
                    # checks if the ball was potted
                    # lists and variables are adjusted if it is
                    if ball_potted(ball.x, ball.y):
                        # plays the sunk sound
                        sunk_sound.play()
                        recent_potted_balls.append(ball)
                        potted_balls.append(ball)
                        ball.potted = True
                    # stores the ball object returned from the collision checking function
                    # if None, then the code is not executed
                    ball_collided_with = check_collision_with_other_ball(ball.x, ball.y, ball)
                    if ball_collided_with is not None:
                        # plays the hit sound
                        hit_sound.play()
                        # updates the first ball collided variable if it is None
                        if first_ball_collided_with is None:
                            first_ball_collided_with = ball_collided_with
                        # calls the ball collision physics function
                        # which returns the updated direction and speed of each ball involved
                        ball.movement_direction, ball_collided_with.movement_direction, ball.speed, ball_collided_with.speed = ball_collision_physics(ball.x, ball.y, ball_collided_with.x, ball_collided_with.y, ball.movement_direction, ball.speed)
                        # resets monitoring lists so that all ball collisions can occur again
                        collision_monitor_reset()
                        # sets the following booleans to True in the collision monitoring list
                        # preventing this collision from being calculated again
                        ball.collision_monitor[balls.index(ball_collided_with)] = True
                        ball_collided_with.collision_monitor[balls.index(ball)] = True
                    # ============
                    # FRICTION
                    # ============
                    # decreases the speed of the ball at time increments according to the logarithm below
                    if ball.frames >= (-30) * math.log10(0.05 * (ball.speed + 1)):
                        ball.speed -= 1
                        ball.frames = 0
                    ball.frames += 1
                    # updates the coordinates of the pool cue with those of the moving cue ball
                    if ball is cue_ball:
                        pool_cue_coords = (cue_ball.x - 457, cue_ball.y - 454)
                # if all balls have stopped moving...
                if balls_stopped():
                    # everything is redrawn and screen is updated
                    draw_background()
                    draw_potted_balls()
                    for ball in balls:
                        if not ball.potted:
                            gameDisplay.blit(ball.sprite, (ball.x - 10, ball.y - 10))
                    pygame.display.update()
                    # delay for quarter of a second
                    time.sleep(0.25)

                    # ===================================
                    # CHECKS POTTED BALLS AFTER EACH TURN
                    # ===================================
                    # stores the number of stripes and solids potted respectively
                    stripes, solids = 0, 0
                    # loops through each ball that was potted in the previous turn
                    for ball in recent_potted_balls:
                        # adds one to the stripes total if the ball potted is stripes
                        if ball.colour == 'stripes':
                            stripes += 1
                            # if the players have not been assigned stripes or solids yet,
                            # then the assignments are made based on which player potted the stripes ball
                            if initial_break:
                                initial_break = False
                                turn_change = False
                                if player_turn.number == 1:
                                    player_1.colour = 'stripes'
                                    player_2.colour = 'solids'
                                elif player_turn.number == 2:
                                    player_2.colour = 'stripes'
                                    player_1.colour = 'solids'
                        # adds one to the solids total if the ball potted is solids
                        elif ball.colour == 'solids':
                            solids += 1
                            # if the players have not been assigned stripes or solids yet,
                            # then the assignments are made based on which player potted the solids ball
                            if initial_break:
                                initial_break = False
                                turn_change = False
                                if player_turn.number == 1:
                                    player_1.colour = 'solids'
                                    player_2.colour = 'stripes'
                                elif player_turn.number == 2:
                                    player_2.colour = 'solids'
                                    player_1.colour = 'stripes'
                        # if the ball potted is the eight ball, the game is over and the winner is determined
                        elif ball.colour == 'eight':
                            # if the active player is on his final ball...
                            if player_turn.only_eight_ball_left:
                                # ... and does not pot the cue ball or indirectly strikes the eight ball
                                # then the active player wins
                                if cue_ball.potted or not first_ball_collided_with.colour == 'eight':
                                    if player_turn.number == 1:
                                        winner = player_2
                                    else:
                                        winner = player_1
                                # if else, the other player wins
                                else:
                                    winner = player_turn
                            # if the active player was not on his last ball, then the other player wins
                            else:
                                if player_turn.number == 1:
                                    winner = player_2
                                else:
                                    winner = player_1
                            # calls the game over function
                            game_over()
                    # clears the list for recently potted balls
                    # prepares the list for the following turn
                    recent_potted_balls[:] = []

                    # =============================================================
                    # DETERMINES WHETHER PLAYER TURN CHANGES AND IF BALL IS IN HAND
                    # =============================================================
                    # if only the eight ball is left for the player, then the following is executed
                    if player_turn.only_eight_ball_left:
                        # turn change is true since the player did not successfully pot the eight ball
                        turn_change = True
                        cue_ball_in_hand = False
                        # depending on whether the player hit the eight ball successfully, ball in hand is determined
                        if first_ball_collided_with is not None:
                            if not first_ball_collided_with.colour == 'eight':
                                cue_ball_in_hand = True
                        else:
                            cue_ball_in_hand = True
                    # the following code is executed for all other situations
                    else:
                        # whether or not the turn changes is dependent on the player's assigned colour
                        # and if the player potted any corresponding balls during his/her turn
                        if player_turn.colour == 'stripes':
                            if stripes > 0:
                                turn_change = False
                            else:
                                turn_change = True
                        elif player_turn.colour == 'solids':
                            if solids > 0:
                                turn_change = False
                            else:
                                turn_change = True
                        # if a ball was hit by the cue ball...
                        if first_ball_collided_with is not None:
                            # ...ball in hand is determined based on the colour of the ball hit
                            if player_turn.colour == 'stripes' and not first_ball_collided_with.colour == 'stripes':
                                    turn_change = True
                                    cue_ball_in_hand = True
                            elif player_turn.colour == 'solids' and not first_ball_collided_with.colour == 'solids':
                                    turn_change = True
                                    cue_ball_in_hand = True
                        # if no ball is hit by the cue ball, then the ball is in hand
                        else:
                            turn_change = True
                            cue_ball_in_hand = True
                        # checks the number of balls potted for the player's colour
                        # and determines if the player only has the eight ball left
                        if number_of_balls_potted(player_turn.colour) == 7:
                            player_turn.only_eight_ball_left = True
                    # resets the first ball collided with variable for the next round
                    first_ball_collided_with = None
                    # if cue ball is potted, then the turn changes and the ball is in hand
                    if cue_ball.potted:
                        potted_balls.remove(cue_ball)
                        turn_change = True
                        cue_ball.potted = False
                        cue_ball_in_hand = True

                    # if the turn is supposed to change, then the turn change function is called
                    if turn_change:
                        player_turn = player_turn_switch(player_turn)
                    # if cue ball is supposed to be in hand, then the ball in hand function is called
                    # and the coordinates of the cue ball are adjusted
                    if cue_ball_in_hand:
                        ball_in_hand()
                        pool_cue_coords = (cue_ball.x - 457, cue_ball.y - 454)
                        cue_ball_in_hand = False

                    # balls are no longer in play
                    in_play = False

    # =====================================================================================================================
    # CODE FOR PLAYER TURN (AIMING AND STRIKING THE CUE BALL)
    # =====================================================================================================================
    # makes sure that no balls are in play
    if not in_play:
        if draw_guide:
            # draws the guiding line to help the player aim
            pygame.draw.line(gameDisplay, WHITE, (cue_ball.x, cue_ball.y), mouse_hold_coords, 2)
            # draws the image of the pool cue
            gameDisplay.blit(pool_cue_rotated, pool_cue_coords)
            # draws a circle to help the player aim
            pygame.draw.circle(gameDisplay, WHITE, mouse_hold_coords, 10, 1)

        # ============
        # DRAWING CUE
        # ============
        # executes when the mouse button is held down
        if mouse_held:
            # captures mouse x and y coordinates
            mouseX, mouseY = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
            # adjusts angle value if it is greater than 360
            temporary_angle = cue_direction + 180
            if temporary_angle > 360:
                temporary_angle -= 360
            # the distance the player pulls away from the initial mouse position is calculated
            # 210 is capped as the upper limit for the strike distance
            strike_distance = distance_between_points(mouse_hold_coords[0], mouse_hold_coords[1], mouseX, mouseY)
            if strike_distance > 210:
                strike_distance = 210
            # the image of the pool cue is updated based on how much the player pulls back
            # image follows the mouse as it moves
            pool_cue_coords = angle_to_coordinates(cue_ball.x - 457, cue_ball.y - 454, temporary_angle, strike_distance)

    # =====================================================================================================================
    # GAME EVENT HANDLER
    # =====================================================================================================================
    # acquires each game event
    for event in pygame.event.get():
        # quits game if user exits
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        # does not execute if a ball is still in play (is moving)
        if not in_play:
            # when player holds down on mouse, the coordinates of the mouse are tracked
            if event.type == MOUSEBUTTONDOWN:
                mouse_hold_coords = pygame.mouse.get_pos()
                mouse_held = True
            # executes once mouse button is released up
            elif event.type == MOUSEBUTTONUP:
                mouse_held = False
                # if the player has pulled back on the cue a sufficient amount, a shot will be registered
                if strike_distance > 10:
                    # cue ball is given speed value proportional to the distance the player pulls back
                    cue_ball.speed = round((strike_distance - 10)/10)
                    in_play = True
                    draw_guide = False
                    # plays the strike sound
                    strike_sound.play()
                # cue ball direction is updated as the direction the cue was aimed in
                cue_ball.movement_direction = cue_direction
                # resets monitoring lists so that all ball collisions can occur again
                collision_monitor_reset()
            # detects for mouse motion
            elif event.type == MOUSEMOTION and mouse_held is False:
                draw_guide = True
                # captures mouse x and y coordinates
                mouseX, mouseY = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
                mouse_hold_coords = mouseX, mouseY
                # uses the function to calculate the angle of the line connecting cursor position and cue ball position
                cue_direction = coordinates_to_angle(cue_ball.x, cue_ball.y, mouseX, mouseY)
                # uses the function to obtain a rotated image of the pool cue
                pool_cue_rotated = rot_center(pool_cue_original, cue_direction)
                pool_cue_coords = (cue_ball.x - 457, cue_ball.y - 454)

    # =====================================================================================================================
    # UPDATE GRAPHICS
    # =====================================================================================================================
    # updates the display graphics
    pygame.display.update()
    # caps frame rate at 60fps
    clock.tick(60)
