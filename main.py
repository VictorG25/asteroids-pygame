import pygame
import random
import math
import os
from constants import *
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
from particule import Particle
from powerup import PowerUp
from ufo import UFO, Mine, Explosion, Torpedo
from audio_manager import AudioManager
from trail import Trail
from upgrade_manager import UpgradeManager
from score_manager import ScoreManager
from boss import Boss
from decoration import Decoration

def draw_menu(screen, big_font, font):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 20, 40, 230))
    screen.blit(overlay, (0, 0))
    title = big_font.render("Faivre Shooter", True, "cyan")
    screen.blit(title, (SCREEN_WIDTH / 2 - title.get_width() / 2, 100))
    controls = [
        "Z, Q, S, D : Déplacement",
        "ESPACE : Laser",
        "MAJ (Shift) : Torpille",
        "ECHAP : Pause / Reprendre",
        "",
        "--- APPUYEZ SUR ENTREE POUR PLONGER ---"
    ]
    for i, line in enumerate(controls):
        color = "white" if "---" not in line else "yellow"
        text = font.render(line, True, color)
        screen.blit(text, (SCREEN_WIDTH / 2 - text.get_width() / 2, 250 + i * 40))

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    audio = AudioManager()
    audio.load_music("assets/sounds/regular_battle.mp3", 0.2)
    audio.play_music()
    for s in [("laser", "laser1.wav"), ("explosion", "explosion.wav"), ("playerDeath", "player_dead.wav"),
              ("levelup", "levelup.mp3"), ("alarm", "warning.wav"), ("boss_death", "boss_explosion.mp3")]:
        try:
            audio.load_sound(s[0], f"assets/sounds/{s[1]}", 0.4)
        except:
            pass

    score_mgr = ScoreManager()
    upgrade_mgr = UpgradeManager()

    try:
        background_img = pygame.image.load("assets/images/water_texture.png").convert()
        background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        background_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        background_img.fill((0, 50, 100))

    try:
        torp_icon_img = pygame.image.load("assets/images/torpedo.png").convert_alpha()
        torp_icon_img = pygame.transform.scale(torp_icon_img, (30, 15))
    except:
        torp_icon_img = None

    updatable, drawable = pygame.sprite.Group(), pygame.sprite.Group()
    asteroids, shots, ufos = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()
    mines, torpedoes = pygame.sprite.Group(), pygame.sprite.Group()
    powerups, decorations = pygame.sprite.Group(), pygame.sprite.Group()

    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable,)
    Shot.containers = (shots, updatable, drawable)
    PowerUp.containers = (powerups, updatable, drawable)
    UFO.containers = (ufos, updatable, drawable)
    Mine.containers = (mines, updatable, drawable)
    Explosion.containers = (updatable, drawable)
    Torpedo.containers = (torpedoes, updatable, drawable)
    Trail.containers = (updatable, drawable)
    Particle.containers = (updatable, drawable)

    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    asteroid_field = AsteroidField()

    for _ in range(40):
        decorations.add(Decoration(random.randint(0, SCREEN_WIDTH), random.randint(50, SCREEN_HEIGHT - 50),
                                   random.choice(["grass", "corals"])))

    font, big_font = pygame.font.SysFont(None, 36), pygame.font.SysFont(None, 72)
    current_state = "MENU"
    is_paused = False
    is_upgrading = False

    game_state = {"score": 0, "lives": 5}
    options_to_display = []
    invincibility_timer, alert_timer = 0, 0
    ufo_spawn_timer = 5.0
    last_difficulty_milestone = 1
    shake_intensity = 0
    score_saved = False
    dt = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return

            if current_state == "MENU":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    current_state = "PLAYING"

            elif current_state == "PLAYING":
                if is_upgrading:
                    if event.type == pygame.KEYDOWN and event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                        idx = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2}[event.key]
                        if idx < len(options_to_display):
                            upgrade_mgr.apply(player, options_to_display[idx][0], game_state)
                            is_upgrading = False
                else:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        is_paused = not is_paused

            elif current_state == "GAMEOVER":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    main()
                    return

        if current_state == "PLAYING" and not is_paused and not is_upgrading:
            # --- SPAWN UFO ---
            ufo_spawn_timer -= dt
            if ufo_spawn_timer <= 0:
                diff = asteroid_field.difficulty
                if diff >= 2.0 and random.random() < 0.3:
                    UFO(kind="minelayer")
                else:
                    chance_for_fast = min(0.8, (diff - 1.0) * 0.5)
                    UFO(kind="fast" if random.random() < chance_for_fast else "normal")
                ufo_spawn_timer = random.uniform(10, 20) / diff

            # --- MISES À JOUR ---
            boss_exists = any(isinstance(u, Boss) for u in ufos)
            MAX_ASTEROIDS = 20

            for obj in updatable:
                if isinstance(obj, AsteroidField):
                    if len(asteroids) < MAX_ASTEROIDS and not boss_exists:
                        obj.update(dt)
                    continue
                if isinstance(obj, UFO):
                    obj.update(dt, player.position)
                else:
                    obj.update(dt)

            # Gestion Alerte Difficulté
            curr_diff = int(asteroid_field.difficulty)
            if curr_diff > last_difficulty_milestone:
                audio.play_sound("alarm")
                alert_timer, shake_intensity = 4.0, 25
                last_difficulty_milestone = curr_diff

            # --- COLLISIONS DES TORPILLES (CORRIGÉ : FONCTIONNE TOUT LE TEMPS) ---
            for torpedo in torpedoes:
                boss_hit = False
                for u in ufos:
                    if isinstance(u, Boss):
                        if torpedo.position.distance_to(u.position) < (u.radius + 10):
                            boss_hit = True
                            break

                other_hit = pygame.sprite.spritecollide(torpedo, asteroids, False) or \
                            pygame.sprite.spritecollide(torpedo, ufos, False)

                if boss_hit or other_hit:
                    torpedo.explode()
                    shake_intensity = 25
                    explosion_radius = 200
                    for a in list(asteroids):
                        if a.position.distance_to(torpedo.position) < explosion_radius:
                            a.split()
                            game_state["score"] += 10
                    for u in list(ufos):
                        if u.position.distance_to(torpedo.position) < explosion_radius:
                            if isinstance(u, Boss):
                                u.take_damage(5)
                            else:
                                u.kill()
                                game_state["score"] += 200

            # --- COLLISIONS DES TIRS LASER ---
            for shot in shots:
                if shot.owner == "player":
                    for a in asteroids:
                        if a.collides_with(shot):
                            shot.kill(); a.split(); game_state["score"] += 10
                            player.xp += 35; audio.play_sound("explosion"); break
                    for m in mines:
                        if m.collides_with(shot): shot.kill(); m.explode(); game_state["score"] += 50; break
                    for u in ufos:
                        if u.collides_with(shot):
                            shot.kill()
                            if isinstance(u, Boss):
                                u.health -= 1
                                if u.health <= 0: u.kill(); audio.play_sound("boss_death"); game_state["score"] += 2000; player.xp += 500
                            else:
                                if random.random() < 0.2: PowerUp(u.position.x, u.position.y, "torpedo")
                                u.kill(); game_state["score"] += 200; player.xp += 100; audio.play_sound("explosion")
                            break
                elif shot.owner == "ufo" and player.collides_with(shot):
                    shot.kill()
                    if invincibility_timer <= 0: audio.play_sound("playerDeath"); game_state["lives"] -= 1; invincibility_timer = 2.0

            # --- COLLISIONS JOUEUR ---
            if invincibility_timer <= 0:
                for m in mines:
                    if m.collides_with(player): m.explode(); audio.play_sound("playerDeath"); game_state["lives"] -= 1; invincibility_timer = 2.0
                for a in asteroids:
                    if a.collides_with(player): audio.play_sound("playerDeath"); game_state["lives"] -= 1; shake_intensity = 20; invincibility_timer = 2.0
                for u in ufos:
                    if u.collides_with(player): audio.play_sound("playerDeath"); game_state["lives"] -= 1; invincibility_timer = 2.0; u.kill() if not isinstance(u, Boss) else None

            for pu in powerups:
                if pu.collides_with(player):
                    if pu.kind == "shield": invincibility_timer = 5.0
                    elif pu.kind == "torpedo":
                        # Limite de STOCK de torpilles à 5 maximum
                        player.torpedo_stock = min(5, player.torpedo_stock + 3)
                    pu.kill()

            # Level Up
            if player.xp >= player.xp_next_level:
                is_upgrading = True
                audio.play_sound("levelup")
                player.xp -= player.xp_next_level
                player.level += 1
                player.xp_next_level = int(player.xp_next_level * 1.8)
                options_to_display = upgrade_mgr.get_random_choices(3)
                if player.level % 2 == 0: Boss()

            invincibility_timer = max(0, invincibility_timer - dt)
            alert_timer = max(0, alert_timer - dt)
            shake_intensity = max(0, shake_intensity - dt * 20)
            if game_state["lives"] <= 0: current_state = "GAMEOVER"

        # --- DESSIN ---
        screen.blit(background_img, (0, 0))
        render_offset = pygame.Vector2(random.uniform(-shake_intensity, shake_intensity),
                                       random.uniform(-shake_intensity, shake_intensity)) if shake_intensity > 0 else (0, 0)

        for deco in decorations: screen.blit(deco.image, deco.rect.move(render_offset))
        for obj in drawable:
            if isinstance(obj, Player): obj.draw(screen, invincibility_timer > 0)
            elif hasattr(obj, "draw"): obj.draw(screen)

        # HUD
        screen.blit(font.render(f"Score: {game_state['score']}", True, "white"), (10, 10))
        diff_text = font.render(f"Difficulté: {asteroid_field.difficulty:.1f}x", True, "yellow")
        screen.blit(diff_text, (SCREEN_WIDTH - diff_text.get_width() - 10, 10))
        screen.blit(font.render(f"Oxygène: {game_state['lives']}", True, "cyan"), (10, 45))

        # Barre d'XP
        xp_bar_width = 200
        xp_fill = (player.xp / player.xp_next_level) * xp_bar_width
        pygame.draw.rect(screen, (50, 50, 50), (10, 80, xp_bar_width, 15))
        pygame.draw.rect(screen, (0, 255, 100), (10, 80, xp_fill, 15))
        pygame.draw.rect(screen, (255, 255, 255), (10, 80, xp_bar_width, 15), 1)
        screen.blit(font.render(f"Niv. {player.level}", True, "white"), (xp_bar_width + 20, 75))

        if torp_icon_img:
            screen.blit(font.render("TORPILLES:", True, "orange"), (10, 110))
            for i in range(player.torpedo_stock): screen.blit(torp_icon_img, (10 + (i * 35), 140))

        if alert_timer > 0 and int(pygame.time.get_ticks() / 150) % 2 == 0:
            txt = big_font.render("!!! PROFONDEUR DANGEREUSE !!!", True, "red")
            screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100)))

        # Overlays
        if current_state == "MENU": draw_menu(screen, big_font, font)
        elif is_upgrading:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 40, 80, 200))
            screen.blit(overlay, (0, 0))
            title = big_font.render(f"NIVEAU {player.level} ATTEINT !", True, "cyan")
            screen.blit(title, (SCREEN_WIDTH / 2 - title.get_width() / 2, 100))
            for i, opt in enumerate(options_to_display):
                txt = font.render(f"{i + 1}. {opt[0]}", True, "white")
                screen.blit(txt, (SCREEN_WIDTH / 2 - txt.get_width() / 2, 250 + i * 60))
        elif is_paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0)); txt = big_font.render("PAUSE", True, "white")
            screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)))
        elif current_state == "GAMEOVER":
            if not score_saved: score_mgr.save_score(game_state["score"]); score_saved = True
            msg = big_font.render("NAUFRAGE", True, "red")
            screen.blit(msg, (SCREEN_WIDTH / 2 - msg.get_width() / 2, SCREEN_HEIGHT / 4))
            leaderboard = score_mgr.get_leaderboard()
            for i, (name, score) in enumerate(leaderboard[:5]):
                color = "green" if name == os.getlogin() else "white"
                screen.blit(font.render(f"{i + 1}. {name}: {score}", True, color), (SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 + i * 30))
            screen.blit(font.render("Appuie sur [R] pour recommencer", True, "white"), (SCREEN_WIDTH / 2 - 180, SCREEN_HEIGHT - 100))

        pygame.display.flip()
        dt = clock.tick(60) / 1000

if __name__ == "__main__":
    main()