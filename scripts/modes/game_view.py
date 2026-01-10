import arcade
from arcade import Camera2D
from scripts.characters import hero_death_knight, hero_wizard

# Глобальные константы — можно вынести в отдельный файл
PLAYER_SIZE = 0.1
PLAYER_SPEED = 5
GRAVITY = 0.5
JUMP_SPEED = 25

class GameView(arcade.View):  # ← НАСЛЕДУЕТСЯ ОТ View, НЕ Window!
    def __init__(self):
        super().__init__()
        self.walls = None
        self.platform = None
        self.player1 = None
        self.player2 = None
        self.camera = None
        self.physics_engine = None

    def setup(self):
        # Загрузка карты
        test_map = arcade.load_tilemap("models/map/test_map/карта.tmx", scaling=1.2)
        self.walls = test_map.sprite_lists["walls"]
        self.platform = test_map.sprite_lists["platforms"]

        all_collision = arcade.SpriteList()
        all_collision.extend(self.walls)
        all_collision.extend(self.platform)

        # Камера
        self.camera = Camera2D()

        # Игрок
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
            start_x, start_y,
            speed=PLAYER_SPEED,
            scale=PLAYER_SIZE,
            number_player=2,
            colision_sprites=all_collision,
            jump_speed=JUMP_SPEED,
            gravity=GRAVITY
        )

        self.physics_engine1 = self.player1.physicks_engine
        self.physics_engine2 = self.player2.physicks_engine

        # Центрируем карту по окну
        all_sprites = arcade.SpriteList()
        all_sprites.extend(self.walls)
        all_sprites.extend(self.platform)

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

        # Используем камеру ДО отрисовки игровых объектов
        self.camera.use()
        self.walls.draw()
        self.platform.draw()
        self.player1.draw()
        self.player2.draw()

    def on_update(self, delta_time):
        self.player1.on_update(delta_time)
        self.player2.on_update(delta_time)
        self.physics_engine1.update()
        self.physics_engine2.update()

        # Двигаем камеру за игроком
        self.camera.position = self.player1.player_sprite.position

    def on_key_press(self, key, modifiers):
        self.player1.on_key_press(key, modifiers)
        self.player2.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        self.player1.on_key_release(key, modifiers)
        self.player2.on_key_release(key, modifiers)
