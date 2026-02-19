import pygame
import random
from circleshape import CircleShape
from constants import LINE_WIDTH,ASTEROID_MIN_RADIUS
from logger import log_event

class Asteroid(CircleShape):
   def __init__(self,x,y,radius):
      super().__init__(x,y,radius)
   
   def draw(self, screen):
      pygame.draw.circle(screen, "white", self.position, self.radius, LINE_WIDTH)

   def update(self,dt):
      self.position += (self.velocity * dt)
   
   def split(self):
      # 1. On détruit l'astéroïde actuel quoi qu'il arrive
      self.kill()

      # 2. Si c'est un petit, on s'arrête là
      if self.radius <= ASTEROID_MIN_RADIUS:
         return

      # 3. Sinon, on prépare la division
      log_event("asteroid_split")
      
      # Angle aléatoire entre 20 et 50 degrés
      random_angle = random.uniform(20, 50)

      # Création des deux nouveaux vecteurs de direction
      velocity1 = self.velocity.rotate(random_angle)
      velocity2 = self.velocity.rotate(-random_angle)

      # Calcul du nouveau rayon
      new_radius = self.radius - ASTEROID_MIN_RADIUS

      # Création des deux nouveaux astéroïdes
      # Ils apparaissent à la position actuelle (self.position.x, self.position.y)
      asteroid1 = Asteroid(self.position.x, self.position.y, new_radius)
      asteroid2 = Asteroid(self.position.x, self.position.y, new_radius)

      # On leur donne une vitesse plus élevée (x 1.2)
      asteroid1.velocity = velocity1 * 1.2
      asteroid2.velocity = velocity2 * 1.2
      