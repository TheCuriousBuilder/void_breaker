import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 1200, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Shooter")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

# Colors
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
RED = (220, 60, 60)
GREEN = (60, 220, 60)
BLUE = (60, 140, 255)
YELLOW = (255, 255, 0)
PURPLE = (180, 80, 255)


def reset_game():
    return {
        "player_x": WIDTH // 2,
        "player_y": HEIGHT // 2,
        "health": 100,
        "score": 0,
        "wave": 1,
        "bullets": [],
        "enemies": [],
        "particles": [],
        "powerups": [],
        "spawn_timer": 0,
        "shoot_timer": 0,
        "rapid_timer": 0,
        "dash_timer": 0,
        "game_over": False,
    }


game = reset_game()
high_score = 0


def spawn_enemy():
    side = random.randint(0, 3)

    if side == 0:
        x = random.randint(0, WIDTH)
        y = -40
    elif side == 1:
        x = WIDTH + 40
        y = random.randint(0, HEIGHT)
    elif side == 2:
        x = random.randint(0, WIDTH)
        y = HEIGHT + 40
    else:
        x = -40
        y = random.randint(0, HEIGHT)

    speed = random.uniform(
        1.5 + game["wave"] * 0.2,
        3 + game["wave"] * 0.3
    )

    health = 1 + game["wave"] // 3

    game["enemies"].append(
        [x, y, speed, health]
    )


def create_explosion(x, y):
    for _ in range(15):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1, 5)

        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed

        game["particles"].append(
            [x, y, vx, vy, 30]
        )


running = True

while running:
    dt = clock.tick(60)

    # EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if (
            event.type == pygame.KEYDOWN
            and game["game_over"]
        ):
            if event.key == pygame.K_r:
                game = reset_game()

    if not game["game_over"]:

        px = game["player_x"]
        py = game["player_y"]

        # Timers
        if game["shoot_timer"] > 0:
            game["shoot_timer"] -= 1

        if game["rapid_timer"] > 0:
            game["rapid_timer"] -= 1

        if game["dash_timer"] > 0:
            game["dash_timer"] -= 1

        # Movement
        keys = pygame.key.get_pressed()

        speed = 5

        dx = 0
        dy = 0

        if keys[pygame.K_w]:
            dy -= speed
        if keys[pygame.K_s]:
            dy += speed
        if keys[pygame.K_a]:
            dx -= speed
        if keys[pygame.K_d]:
            dx += speed

        # Dash
        if (
            keys[pygame.K_SPACE]
            and game["dash_timer"] <= 0
        ):
            dx *= 4
            dy *= 4
            game["dash_timer"] = 60

        game["player_x"] += dx
        game["player_y"] += dy

        game["player_x"] = max(
            20,
            min(WIDTH - 20, game["player_x"])
        )

        game["player_y"] = max(
            20,
            min(HEIGHT - 20, game["player_y"])
        )

        px = game["player_x"]
        py = game["player_y"]

        # Hold-click shooting
        buttons = pygame.mouse.get_pressed()

        fire_rate = (
            3 if game["rapid_timer"] > 0 else 8
        )

        if (
            buttons[0]
            and game["shoot_timer"] <= 0
        ):
            mx, my = pygame.mouse.get_pos()

            angle = math.atan2(
                my - py,
                mx - px
            )

            speed = 12

            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed

            game["bullets"].append(
                [px, py, vx, vy]
            )

            game["shoot_timer"] = fire_rate

        # Enemy spawning
        game["spawn_timer"] += 1

        spawn_delay = max(
            20,
            60 - game["wave"] * 2
        )

        if game["spawn_timer"] >= spawn_delay:
            game["spawn_timer"] = 0
            spawn_enemy()

        # New wave every 20 points
        game["wave"] = game["score"] // 20 + 1

        # Bullets
        for bullet in game["bullets"][:]:
            bullet[0] += bullet[2]
            bullet[1] += bullet[3]

            if (
                bullet[0] < 0
                or bullet[0] > WIDTH
                or bullet[1] < 0
                or bullet[1] > HEIGHT
            ):
                game["bullets"].remove(
                    bullet
                )

        # Enemies
        for enemy in game["enemies"][:]:
            ex, ey, speed, hp = enemy

            dx = px - ex
            dy = py - ey
            dist = math.hypot(dx, dy)

            if dist > 0:
                enemy[0] += (
                    dx / dist * speed
                )
                enemy[1] += (
                    dy / dist * speed
                )

            if dist < 35:
                game["health"] -= 1

            # Bullet collisions
            for bullet in game["bullets"][:]:
                d = math.hypot(
                    bullet[0] - enemy[0],
                    bullet[1] - enemy[1]
                )

                if d < 25:
                    enemy[3] -= 1

                    if bullet in game["bullets"]:
                        game["bullets"].remove(
                            bullet
                        )

                    if enemy[3] <= 0:
                        create_explosion(
                            enemy[0],
                            enemy[1]
                        )

                        if enemy in game["enemies"]:
                            game["enemies"].remove(
                                enemy
                            )

                        game["score"] += 1
                        high_score = max(
                            high_score,
                            game["score"]
                        )

                        # Random powerup
                        if random.random() < 0.08:
                            t = random.choice(
                                ["health", "rapid"]
                            )

                            game["powerups"].append(
                                [
                                    enemy[0],
                                    enemy[1],
                                    t,
                                ]
                            )

                    break

        # Particles
        for p in game["particles"][:]:
            p[0] += p[2]
            p[1] += p[3]
            p[4] -= 1

            if p[4] <= 0:
                game["particles"].remove(
                    p
                )

        # Powerups
        for p in game["powerups"][:]:
            d = math.hypot(
                px - p[0],
                py - p[1]
            )

            if d < 30:
                if p[2] == "health":
                    game["health"] = min(
                        100,
                        game["health"] + 25
                    )

                if p[2] == "rapid":
                    game["rapid_timer"] = 600

                game["powerups"].remove(p)

        if game["health"] <= 0:
            game["game_over"] = True

    # DRAW
    screen.fill(BLACK)

    # Particles
    for p in game["particles"]:
        pygame.draw.circle(
            screen,
            YELLOW,
            (int(p[0]), int(p[1])),
            3,
        )

    # Player
    px = game["player_x"]
    py = game["player_y"]

    pygame.draw.circle(
        screen,
        BLUE,
        (int(px), int(py)),
        20,
    )

    # Gun
    mx, my = pygame.mouse.get_pos()

    angle = math.atan2(
        my - py,
        mx - px
    )

    gx = px + math.cos(angle) * 35
    gy = py + math.sin(angle) * 35

    pygame.draw.line(
        screen,
        WHITE,
        (px, py),
        (gx, gy),
        6,
    )

    # Bullets
    for bullet in game["bullets"]:
        pygame.draw.circle(
            screen,
            YELLOW,
            (int(bullet[0]),
             int(bullet[1])),
            5,
        )

    # Enemies
    for enemy in game["enemies"]:
        pygame.draw.circle(
            screen,
            RED,
            (int(enemy[0]),
             int(enemy[1])),
            20,
        )

    # Powerups
    for p in game["powerups"]:
        color = (
            GREEN
            if p[2] == "health"
            else PURPLE
        )

        pygame.draw.circle(
            screen,
            color,
            (int(p[0]),
             int(p[1])),
            12,
        )

    # Health bar
    pygame.draw.rect(
        screen,
        RED,
        (20, 20, 300, 30),
    )

    pygame.draw.rect(
        screen,
        GREEN,
        (
            20,
            20,
            game["health"] * 3,
            30,
        ),
    )

    score_text = font.render(
        f"Score: {game['score']}",
        True,
        WHITE,
    )

    wave_text = font.render(
        f"Wave: {game['wave']}",
        True,
        WHITE,
    )

    high_text = font.render(
        f"High Score: {high_score}",
        True,
        WHITE,
    )

    screen.blit(score_text, (20, 65))
    screen.blit(wave_text, (20, 100))
    screen.blit(high_text, (20, 135))

    if game["rapid_timer"] > 0:
        t = font.render(
            "RAPID FIRE!",
            True,
            PURPLE,
        )
        screen.blit(
            t,
            (WIDTH - 230, 30)
        )

    if game["game_over"]:
        text1 = big_font.render(
            "GAME OVER",
            True,
            WHITE,
        )

        text2 = font.render(
            "Press R to Restart",
            True,
            WHITE,
        )

        screen.blit(
            text1,
            (
                WIDTH // 2 - 170,
                HEIGHT // 2 - 50,
            ),
        )

        screen.blit(
            text2,
            (
                WIDTH // 2 - 120,
                HEIGHT // 2 + 30,
            ),
        )

    pygame.display.flip()

pygame.quit()
