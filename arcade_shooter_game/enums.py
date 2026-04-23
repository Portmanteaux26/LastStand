from enum import Enum

class Movement_styles(Enum):
    #Head straight for the target
    MOVEMENT_CHASER = 0
    #Try and stay a certain distance away from the target, otherwise stay still
    MOVEMENT_SHY = 1
    #Try and maintain a specific distance / range from the target, (Ex: 10>dis>5)
    MOVEMENT_ELUSIVE = 2
    #Bounce around the screen
    MOVEMENT_BOUNCER = 3
    #Move about in a totally random way
    MOVEMENT_MAGE = 4
    #Stationary
    MOVEMENT_STATIONARY = 5
class Shape(Enum):
    RECTANGLE = 0
    CIRCLE = 1