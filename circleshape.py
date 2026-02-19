import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
#base class for game objects

class CircleShape(pygame.sprite.Sprite):
   def __init__(self,x,y,radius):
      #we will be usinge this later
      if hasattr(self,"containers"):
         super().__init__(self.containers)
      else:
         super().__init__()
      self.position = pygame.Vector2(x,y)
      self.velocity = pygame.Vector2(0,0)
      self.radius = radius

   def collides_with(self,other):
      distance = self.position.distance_to(other.position)
      return distance <= (self.radius + other.radius)

   def wrap_position(self):

      if self.position.x > SCREEN_WIDTH + self.radius:
         self.position.x = -self.radius

      elif self.position.x < -self.radius:
         self.position.x = SCREEN_WIDTH + self.radius

      if self.position.y > SCREEN_HEIGHT + self.radius:
         self.position.y = -self.radius

      elif self.position.y < -self.radius:
         self.position.y = SCREEN_HEIGHT + self.radius

   def draw(self,screen):
      pass
   
   def update(self,dt):
      pass
