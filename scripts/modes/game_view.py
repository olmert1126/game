import arcade
from arcade import Camera2D
from scripts.characters import hero_death_knight, hero_wizard
from scripts.monsters import slime

# Глобальные константы
PLAYER_SIZE = 0.1
PLAYER_SPEED = 5
GRAVITY = 0.5
JUMP_SPEED = 25
SLIME_DAMAGE = 45
DAMAGE_COOLDOWN = 1.0  # секунды


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.walls = None
        self.platform = None
        self.invis = None
        self.player1 = None
        self.player2 = None
        self.camera = None
        self.slime = None

        # Таймеры урона
        self._last_damage_time_p1 = 0.0
        self._last_damage_time_p2 = 0.0

    def setup(self):
        # Загрузка карты
        test_map = arcade.load_tilemap("models/map/test_map/карта.tmx", scaling=1.2)
        self.walls = test_map.sprite_lists["walls"]
        self.platform = test_map.sprite_lists["platforms"]
        self.invis = test_map.sprite_lists.get("invis", arcade.SpriteList())

        # Коллизии для игроков
        all_collision = arcade.SpriteList()
        all_collision.extend(self.walls)
        all_collision.extend(self.platform)

        # Коллизии для слизня (включая невидимые триггеры, если нужно)
        collision_slime = arcade.SpriteList()
        collision_slime.extend(self.walls)
        collision_slime.extend(self.platform)
        collision_slime.extend(self.invis)

        # Камера
        self.camera = Camera2D()

        start_x = self.window.width / 2 - 200
        start_y = self.window.height / 2

        self.player1 = hero_death_knight.DeathKnight(
            start_x, start_y,
            speed=PLAYER_SPEED,
            scale=PLAYER_SIZE,
            number_player=1,
            colision_sprites=all_collision,
            jump_speed=JUMP_SPEED,
            gravity=GRAVITY
        )

        self.player2 = hero_wizard.Wizard(
            start_x + 50, start_y,
            speed=PLAYER_SPEED,
            scale=PLAYER_SIZE,
            number_player=2,
            colision_sprites=all_collision,
            jump_speed=JUMP_SPEED,
            gravity=GRAVITY
        )

        self.slime = slime.Slime(
            x=self.window.width / 2 - 400,
            y=self.window.height / 2,
            collision_sprites=collision_slime,
            gravity=GRAVITY
        )

        # Центрируем карту по окну
        all_sprites = arcade.SpriteList()
        all_sprites.extend(self.walls)
        all_sprites.extend(self.platform)
        all_sprites.extend(self.invis)

        if len(all_sprites) > 0:
            left = min(s.left for s in all_sprites)
            right = max(s.right for s in all_sprites)
            bottom = min(s.bottom for s in all_sprites)
            top = max(s.top for s in all_sprites)

            map_center_x = (left + right) / 2
            map_center_y = (bottom + top) / 2

            dx = self.window.width / 2 - map_center_x
            dy = self.window.height / 2 - map_center_y

            for sprite in all_sprites:
                sprite.center_x += dx
                sprite.center_y += dy

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)

        self.camera.use()

        self.walls.draw()
        self.platform.draw()

        if self.player1.is_alive:
            self.player1.draw()
        if self.player2.is_alive:
            self.player2.draw()

        self.slime.draw()

    def on_update(self, delta_time):
        # Обновление игроков
        if self.player1.is_alive:
            self.player1.on_update(delta_time)
        if self.player2.is_alive:
            self.player2.on_update(delta_time)

        # Обновление физики
        if self.player1.is_alive:
            self.player1.physics_engine.update()
        if self.player2.is_alive:
            self.player2.physics_engine.update()

        # Обновление слизня
        self.slime.on_update(delta_time)

        # Урон от слизня
        if self.player1.is_alive and arcade.check_for_collision(
            self.player1.player_sprite, self.slime.slime_sprite
        ):
            self._last_damage_time_p1 += delta_time
            if self._last_damage_time_p1 >= DAMAGE_COOLDOWN:
                self.player1.take_damage(SLIME_DAMAGE)
                self._last_damage_time_p1 = 0.0

        if self.player2.is_alive and arcade.check_for_collision(
            self.player2.player_sprite, self.slime.slime_sprite
        ):
            self._last_damage_time_p2 += delta_time
            if self._last_damage_time_p2 >= DAMAGE_COOLDOWN:
                self.player2.take_damage(SLIME_DAMAGE)
                self._last_damage_time_p2 = 0.0

        # Коллизия между игроками (если оба живы)
        if self.player1.is_alive and self.player2.is_alive:
            self.resolve_collision(self.player1.player_sprite, self.player2.player_sprite)

        # Камера следует за первым живым игроком
        if self.player1.is_alive:
            self.camera.position = self.player1.player_sprite.position
        elif self.player2.is_alive:
            self.camera.position = self.player2.player_sprite.position


    def resolve_collision(self, sprite1, sprite2):
        """Раздвигает два спрайта при пересечении."""
        if not arcade.check_for_collision(sprite1, sprite2):
            return

        dx = sprite1.center_x - sprite2.center_x
        dy = sprite1.center_y - sprite2.center_y
        distance = max(0.1, (dx**2 + dy**2) ** 0.5)

        min_dist = (sprite1.width + sprite2.width) / 2 * 0.8
        if distance < min_dist:
            dx /= distance
            dy /= distance
            overlap = (min_dist - distance) / 2
            sprite1.center_x += dx * overlap
            sprite1.center_y += dy * overlap
            sprite2.center_x -= dx * overlap
            sprite2.center_y -= dy * overlap

    def on_key_press(self, key, modifiers):
        if self.player1.is_alive:
            self.player1.on_key_press(key, modifiers)
        if self.player2.is_alive:
            self.player2.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        if self.player1.is_alive:
            self.player1.on_key_release(key, modifiers)
        if self.player2.is_alive:
            self.player2.on_key_release(key, modifiers)