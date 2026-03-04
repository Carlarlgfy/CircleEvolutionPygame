#food class
#the food class is basically a thing that the player makes
#food satiates the creatures needs which gradually increase over time

#basically food is drawn in the surface of the screen when the
#player clikc on a part of the screen and it shouldnt be drawn outside of the bounds of the screen
#so food should auto snap to the closest play inside the screen and not come outside it
import pygame
class Food:
    def __init__(self, pos):
        self.size = 10
        self.color = (60, 200, 90) # should be green
        self.x, self.y = pos
        self.x = max(self.size, min(self.x, 800 - self.size))
        self.y = max(self.size, min(self.y, 600 - self.size))

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)

    #do we put the update function here?
    #the food needs to disappear after the creature eats the food
