import pygame
import random
import math
from circleshape import CircleShape
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_SHOOT_SPEED
from shot import Shot
from particule import Particle


# ==========================================
# 1. CLASSE EXPLOSION
# ==========================================
class Explosion(pygame.sprite.Sprite):
    containers = ()
    frames = []

    def __init__(self, x, y, sound_type="mine"):
        super().__init__(self.containers)
        self.position = pygame.Vector2(x, y)

        if not Explosion.frames:
            self.load_frames()

        self.current_frame = 0
        self.image = Explosion.frames[self.current_frame]
        self.rect = self.image.get_rect(center=self.position)

        self.animation_speed = 0.05
        self.timer = 0

        sound_files = {
            "mine": "assets/sounds/boss_explosion.mp3",
            "torpedo": "assets/sounds/torpedo_sound.mp3"
        }

        try:
            sound_path = sound_files.get(sound_type, sound_files["mine"])
            sound = pygame.mixer.Sound(sound_path)
            sound.set_volume(0.6 if sound_type == "torpedo" else 0.4)
            sound.play()
        except Exception as e:
            print(f"Erreur son explosion: {e}")

    def load_frames(self):
        try:
            sheet = pygame.image.load("assets/images/explosion.png").convert_alpha()
            frame_width, frame_height = 32, 32
            total_frames = 6
            for i in range(total_frames):
                rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                frame = sheet.subsurface(rect)
                frame = pygame.transform.scale(frame, (120, 120))
                Explosion.frames.append(frame)
        except:
            surf = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 100, 0), (40, 40), 40)
            Explosion.frames.append(surf)

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.animation_speed:
            self.timer = 0
            self.current_frame += 1
            if self.current_frame < len(Explosion.frames):
                self.image = Explosion.frames[self.current_frame]
                self.rect = self.image.get_rect(center=self.position)
            else:
                self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.rect)


# ==========================================
# 2. CLASSE MINE
# ==========================================
class Mine(CircleShape):
    containers = ()

    def __init__(self, x, y):
        super().__init__(x, y, 20)
        self.velocity = pygame.Vector2(0, 80)
        try:
            self.image = pygame.image.load("assets/images/mine.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (45, 45))
        except:
            self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(self.image, "orange", (20, 20), 15)
        self.rect = self.image.get_rect(center=self.position)

    def update(self, dt):
        self.position += self.velocity * dt
        self.rect.center = self.position
        if self.position.y > SCREEN_HEIGHT + 50: self.kill()

    def explode(self):
        Explosion(self.position.x, self.position.y, sound_type="mine")
        self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.rect)


# ==========================================
# 3. CLASSE UFO
# ==========================================
class UFO(CircleShape):
    assets = {}
    containers = ()

    def __init__(self, x=None, y=None, kind="normal"):
        self.kind = kind

        # --- POSITIONNEMENT ---
        if self.kind == "boss":
            x_init = x if x is not None else SCREEN_WIDTH / 2
            y_init = y if y is not None else -200
            self.direction = 0
        elif self.kind == "minelayer":
            x_init = random.randint(100, SCREEN_WIDTH - 100)
            y_init = -40
            self.direction = random.choice([-1, 1])
            self.target_y = random.randint(40, 100)
        else:
            side = random.choice(["left", "right"])
            x_init = -50 if side == "left" else SCREEN_WIDTH + 50
            self.direction = 1 if side == "left" else -1
            y_init = random.randint(100, SCREEN_HEIGHT - 100)
            self.target_y = y_init

        super().__init__(x_init, y_init, 30)

        # Propriétés selon le type
        if self.kind == "fast":
            self.speed, self.shoot_cooldown = 300, 0.8
            self.image_path = "assets/images/ufo_speed.png"
        elif self.kind == "minelayer":
            self.speed, self.shoot_cooldown = 130, 2.5
            self.image_path = "assets/images/ufo_mine.png"
        elif self.kind == "boss":
            self.speed, self.shoot_cooldown = 0, 2.0
            self.image_path = None
        else:
            self.speed, self.shoot_cooldown = 150, 2.0
            self.image_path = "assets/images/ufo_light.png"

        self.velocity = pygame.Vector2(self.direction * self.speed, 40 if self.kind == "minelayer" else 0)
        self.shoot_timer = self.shoot_cooldown

        # Chargement image/son
        if self.kind != "boss" and self.kind not in UFO.assets:
            self.load_ufo_assets()

        # Attribution de l'image pour le dessin
        if self.kind != "boss" and self.kind in UFO.assets:
            self.image = UFO.assets[self.kind]["image"]
            self.rect = self.image.get_rect(center=self.position)
        else:
            # Pour le boss, on crée un rect par défaut qui sera mis à jour dans boss.py
            self.image = None
            self.rect = pygame.Rect(0, 0, 1, 1)

    def load_ufo_assets(self):
        UFO.assets[self.kind] = {"image": None, "sound": None}
        try:
            img = pygame.image.load(self.image_path).convert_alpha()
            ratio = img.get_width() / img.get_height()
            UFO.assets[self.kind]["image"] = pygame.transform.scale(img, (int(65 * ratio), 65))
            snd = pygame.mixer.Sound("assets/sounds/ufo_laser.mp3")
            snd.set_volume(0.15)
            UFO.assets[self.kind]["sound"] = snd
        except:
            pass

    def update(self, dt, player_position=None):
        # On n'applique la logique de mouvement de base QUE si ce n'est pas le boss
        if self.kind != "boss":
            if self.kind == "minelayer" and self.position.y >= self.target_y:
                self.velocity.y = 0

            self.position.y += math.sin(pygame.time.get_ticks() * 0.005) * 1.5
            self.position += self.velocity * dt
            self.rect.center = self.position

            self.shoot_timer -= dt
            if player_position and self.shoot_timer <= 0:
                self.shoot(player_position)
                self.shoot_timer = self.shoot_cooldown

            if self.position.x < -250 or self.position.x > SCREEN_WIDTH + 250:
                self.kill()

    def shoot(self, target_pos):
        if self.kind == "minelayer":
            Mine(self.position.x, self.position.y)
        else:
            try:
                UFO.assets[self.kind]["sound"].play()
            except:
                pass
            direction = (target_pos - self.position).normalize()
            shot = Shot(self.position.x, self.position.y)
            shot.owner = "ufo"
            shot.velocity = direction * (PLAYER_SHOOT_SPEED * 0.7)

    def draw(self, screen):
        # Méthode draw pour les UFO normaux
        if self.image:
            display_img = self.image
            if self.direction == -1:
                display_img = pygame.transform.flip(self.image, True, False)
            screen.blit(display_img, self.rect)


# ==========================================
# 4. CLASSE TORPEDO
# ==========================================
class Torpedo(CircleShape):
    containers = ()

    def __init__(self, x, y, velocity):
        super().__init__(x, y, 15)
        self.velocity = velocity
        try:
            raw_image = pygame.image.load("assets/images/torpedo.png").convert_alpha()
            ratio = raw_image.get_width() / raw_image.get_height()
            small_image = pygame.transform.scale(raw_image, (40, int(40 / ratio)))
            angle = pygame.Vector2(-1, 0).angle_to(self.velocity)
            self.image = pygame.transform.rotate(small_image, angle)
        except:
            self.image = pygame.Surface((30, 10), pygame.SRCALPHA)
            self.image.fill("cyan")
        self.rect = self.image.get_rect(center=self.position)

    def update(self, dt):
        self.position += self.velocity * dt
        self.rect.center = self.position
        if not (0 <= self.position.x <= SCREEN_WIDTH and 0 <= self.position.y <= SCREEN_HEIGHT):
            self.kill()

    def explode(self):
        Explosion(self.position.x, self.position.y, sound_type="torpedo")
        self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.rect)