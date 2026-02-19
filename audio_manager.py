import pygame
import os


class AudioManager:
    def __init__(self):
        self.audio_enabled = True
        self.sounds = {}

        try:
            pygame.mixer.init()
        except pygame.error:
            print("Attention : Aucun périphérique audio trouvé.")
            self.audio_enabled = False

    def load_music(self, path, volume=0.2):
        if not self.audio_enabled: return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume)
        except pygame.error:
            print(f"Impossible de charger la musique : {path}")

    def play_music(self):
        if self.audio_enabled:
            pygame.mixer.music.play(-1)

    def load_sound(self, name, path, volume=0.5):
        if not self.audio_enabled: return
        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(volume)
            self.sounds[name] = sound
        except pygame.error:
            print(f"Impossible de charger le son : {path}")

    def play_sound(self, name):
        if self.audio_enabled and name in self.sounds:
            self.sounds[name].play()