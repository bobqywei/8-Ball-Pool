"""
    File: classes.py
    Authors: Bob Wei
    Date: 6/6/2017
    Project Name: 8 Ball Pool
    Description: A file containing the definitions of various classes that are called upon in main.py
"""
# imports necessary modules
import pygame

# ==================================================================================================================
# CLASSES
# ==================================================================================================================


# class for the balls used in the game
class ball (object):
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
class player (object):
    def __init__(self, number, colour):
        self.number = number
        self.colour = colour
        self.only_eight_ball_left = False

