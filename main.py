import pygame
import random
import math
from constants import *
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
from particule import Particle
from powerup import PowerUp
from ufo import UFO
from audio_manager import AudioManager
from trail import Trail
from upgrade_manager import UpgradeManager
from score_manager import ScoreManager
from boss import Boss


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # --- INITIALISATION MODULES ---
    audio = AudioManager()
    audio.load_music("assets/sounds/regular_battle.mp3", 0.2)
    audio.play_music()
    audio.load_sound("laser", "assets/sounds/laser1.wav", 0.3)
    audio.load_sound("explosion", "assets/sounds/explosion.wav", 0.2)
    audio.load_sound("playerDeath", "assets/sounds/player_dead.wav", 0.6)
    audio.load_sound("levelup", "assets/sounds/levelup.mp3", 0.7)
    audio.load_sound("alarm", "assets/sounds/warning.wav", 0.6)
    audio.load_sound("boss_death", "assets/sounds/boss_explosion.mp3", 0.8)

    score_mgr = ScoreManager()
    upgrade_mgr = UpgradeManager()

    # --- GROUPES & CONTAINERS ---
    updatable, drawable = pygame.sprite.Group(), pygame.sprite.Group()
    asteroids, shots, ufos = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()
    powerups, particles, trails = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()

    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable,)
    Shot.containers = (shots, updatable, drawable)
    Particle.containers = (updatable, drawable, particles)
    PowerUp.containers = (powerups, updatable, drawable)
    UFO.containers = (ufos, drawable)
    Trail.containers = (updatable, drawable, trails)

    # --- SETUP JEU ---
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    asteroid_field = AsteroidField()
    stars = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) for _ in range(100)]
    font, big_font = pygame.font.SysFont(None, 36), pygame.font.SysFont(None, 72)

    game_state = {"score": 0, "lives": 3, "active": True, "paused": False}
    options_to_display = []
    invincibility_timer = 0
    ufo_spawn_timer = 15.0
    alert_timer = 0
    last_difficulty_milestone = 100
    shake_intensity = 0
    dt = 0

    while True:
        # 1. GESTION ÉVÉNEMENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return

            if game_state["paused"] and event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    idx = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2}[event.key]
                    if idx < len(options_to_display):
                        upgrade_mgr.apply(player, options_to_display[idx][0], game_state)
                        game_state["paused"] = False

            elif not game_state["active"] and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: main(); return

        # 2. LOGIQUE
        if game_state["active"] and not game_state["paused"]:
            # On vérifie s'il y a un Boss dans le groupe des UFOs
            boss_exists = any(isinstance(u, Boss) for u in ufos)
            shots_before = len(shots)
            # On ne met à jour le champ d'astéroïdes QUE s'il n'y a pas de boss
            for obj in updatable:
                if isinstance(obj, AsteroidField) and boss_exists:
                    continue
                obj.update(dt)


            if len(shots) > shots_before:
                # On vérifie que c'est bien un tir du joueur pour ne pas jouer
                # le son quand l'UFO tire
                new_shots = [s for s in shots if s.owner == "player"]
                audio.play_sound("laser")

            invincibility_timer = max(0, invincibility_timer - dt)
            alert_timer = max(0, alert_timer - dt)
            shake_intensity = max(0, shake_intensity - dt * 20)

            # --- LOGIQUE DIFFICULTÉ & ALARME ---
            current_diff = int(asteroid_field.difficulty * 100)
            if current_diff >= last_difficulty_milestone + 50:
                last_difficulty_milestone += 50
                alert_timer = 2.0
                audio.play_sound("alarm")

            ufo_spawn_timer -= dt
            if ufo_spawn_timer <= 0:
                UFO()
                ufo_spawn_timer = random.uniform(15, 25) / asteroid_field.difficulty

            # Update UFOs avec la position du joueur pour le tracking
            for ufo in ufos:
                ufo.update(dt, player.position)

            # --- GESTION DES COLLISIONS ---

            # 1. Projectiles (Shots)
            for shot in shots:
                collision_occurred = False

                # Collision Shot vs Astéroïde
                for asteroid in asteroids:
                    if shot.owner == "player" and asteroid.collides_with(shot):
                        shot.kill()
                        asteroid.split()
                        game_state["score"] += 10
                        player.xp += 35
                        audio.play_sound("explosion")
                        shake_intensity = 5
                        collision_occurred = True
                        break

                if collision_occurred: continue

                # Collision Shot vs UFO / Boss
                for ufo in ufos:
                    if shot.owner == "player" and ufo.collides_with(shot):
                        shot.kill()
                        if isinstance(ufo, Boss):
                            ufo.health -= 1
                            shake_intensity = 8
                            # Feedback visuel pour le boss
                            for _ in range(3): Particle(shot.position.x, shot.position.y)
                            if ufo.health <= 0:
                                ufo.kill()
                                # 1. Son de mort massif
                                audio.play_sound("boss_death")

                                # 2. Gros bonus et secousse
                                game_state["score"] += 2000
                                player.xp += 500
                                shake_intensity = 40

                                # 3. EXPLOSION FINALE (100 particules)
                                for _ in range(100):
                                    p = Particle(ufo.position.x, ufo.position.y)
                                    # Explosion circulaire
                                    angle = random.uniform(0, 2 * math.pi)
                                    speed = random.uniform(150, 500)
                                    p.velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
                        else:
                            ufo.kill()
                            game_state["score"] += 200
                            player.xp += 100
                            audio.play_sound("explosion")
                            shake_intensity = 10
                            for _ in range(15): Particle(ufo.position.x, ufo.position.y)

                        collision_occurred = True
                        break

                    # Projectile ennemi touche le joueur
                    elif shot.owner == "ufo" and player.collides_with(shot):
                        shot.kill()
                        if invincibility_timer <= 0:
                            audio.play_sound("playerDeath")
                            game_state["lives"] -= 1
                            shake_intensity = 15
                            invincibility_timer = 2.0
                            if game_state["lives"] <= 0:
                                game_state["active"] = False
                                score_mgr.save_highscore(game_state["score"])
                        collision_occurred = True
                        break

            # 2. Corps à Corps (Player vs Enemies)
            for asteroid in asteroids:
                if asteroid.collides_with(player) and invincibility_timer <= 0:
                    audio.play_sound("playerDeath")
                    game_state["lives"] -= 1
                    shake_intensity = 15
                    invincibility_timer = 2.0
                    if game_state["lives"] <= 0:
                        game_state["active"] = False
                        score_mgr.save_highscore(game_state["score"])

            for ufo in ufos:
                if ufo.collides_with(player) and invincibility_timer <= 0:
                    if not isinstance(ufo, Boss): ufo.kill()
                    audio.play_sound("playerDeath")
                    game_state["lives"] -= 1
                    shake_intensity = 20
                    invincibility_timer = 2.0
                    if game_state["lives"] <= 0:
                        game_state["active"] = False
                        score_mgr.save_highscore(game_state["score"])

            # LEVEL UP logic
            if player.xp >= player.xp_next_level:
                game_state["paused"] = True
                audio.play_sound("levelup")
                player.xp -= player.xp_next_level
                player.level += 1
                player.xp_next_level = int(player.xp_next_level * 1.8)
                options_to_display = upgrade_mgr.get_random_choices(3)

                if player.level % 1 == 0:
                    # 1. On détruit tous les astéroïdes actuels
                    for asteroid in asteroids:
                        asteroid.kill()

                    # 2. On spawn le Boss
                    Boss()

            for pu in powerups:
                if pu.collides_with(player):
                    if pu.kind == "shield":
                        invincibility_timer = 5.0
                    elif pu.kind == "triple_shot":
                        player.has_triple_shot = 5.0
                    pu.kill()

        # 3. DESSIN
        screen.fill("black")

        render_offset = pygame.Vector2(0, 0)
        if shake_intensity > 0:
            render_offset.x = random.uniform(-shake_intensity, shake_intensity)
            render_offset.y = random.uniform(-shake_intensity, shake_intensity)

        for star in stars:
            pygame.draw.circle(screen, "white", pygame.Vector2(star) + render_offset, 1)

        for obj in drawable:
            if isinstance(obj, Player):
                obj.draw(screen, invincibility_timer > 0)
            else:
                obj.draw(screen)

        # HUD
        screen.blit(font.render(f"Score: {game_state['score']}", True, "white"), (10, 10))
        screen.blit(font.render(f"Record: {score_mgr.highscore}", True, "gold"), (10, 80))
        screen.blit(font.render(f"Vies: {game_state['lives']}", True, "red"), (10, 45))

        # DIFFICULTÉ
        diff_text = f"Difficulté: {int(asteroid_field.difficulty * 100)}%"
        diff_color = "red" if alert_timer > 0 and int(alert_timer * 5) % 2 == 0 else "white"
        screen.blit(font.render(diff_text, True, diff_color), (SCREEN_WIDTH - 220, 10))

        if alert_timer > 0:
            danger_text = big_font.render("VITESSE AUGMENTÉE !", True, "red")
            screen.blit(danger_text, (SCREEN_WIDTH / 2 - danger_text.get_width() / 2, 150))

        # Barre XP
        pygame.draw.rect(screen, (50, 50, 50), (SCREEN_WIDTH / 2 - 100, 20, 200, 10))
        xp_ratio = min(max(player.xp / player.xp_next_level, 0), 1.0)
        pygame.draw.rect(screen, (0, 255, 100), (SCREEN_WIDTH / 2 - 100, 20, 200 * xp_ratio, 10))

        if game_state["paused"]:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            title = big_font.render(f"LEVEL UP! (Niv. {player.level})", True, "yellow")
            screen.blit(title, (SCREEN_WIDTH / 2 - title.get_width() / 2, 100))
            for i, opt in enumerate(options_to_display):
                color = {1: "white", 2: "cyan", 3: "orange"}.get(opt[2], "white")
                txt = font.render(f"{i + 1}. {opt[0]} : {opt[1]}", True, color)
                screen.blit(txt, (SCREEN_WIDTH / 2 - txt.get_width() / 2, 250 + i * 60))

        if not game_state["active"]:
            msg = big_font.render("GAME OVER", True, "red")
            screen.blit(msg, (SCREEN_WIDTH / 2 - msg.get_width() / 2, SCREEN_HEIGHT / 2))
            restart_msg = font.render("Pressez 'R' pour recommencer", True, "white")
            screen.blit(restart_msg, (SCREEN_WIDTH / 2 - restart_msg.get_width() / 2, SCREEN_HEIGHT / 2 + 80))

        pygame.display.flip()
        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()