import arcade
from arcade import Camera2D
from scripts.characters import hero_death_knight, hero_wizard
from scripts.monsters import slime
from arcade import LBWH, XYWH

# Глобальные константы
PLAYER_SIZE = 0.1
PLAYER_SPEED = 5
GRAVITY = 0.5
JUMP_SPEED = 25
SLIME_DAMAGE = 45
DAMAGE_COOLDOWN = 1.0


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.walls = None
        self.platform = None
        self.invis = None
        self.player1 = None
        self.player2 = None
        self.camera = None
        self.ui_camera = None  # ← НОВАЯ UI-камера
        self.slime = None
        self.HP_bar = None
        self.HP_bar_sprite_list = arcade.SpriteList()

        self.loading_texture()

        # Таймеры урона
        self._last_damage_time_p1 = 0.0
        self._last_damage_time_p2 = 0.0

    def setup(self):
        # Загрузка карты
        test_map = arcade.load_tilemap("models/map/test_map/карта.tmx", scaling=1.2)
        self.walls = test_map.sprite_lists["walls"]
        self.platform = test_map.sprite_lists["platforms"]
        self.invis = test_map.sprite_lists.get("invis", arcade.SpriteList())

        # Коллизии
        all_collision = arcade.SpriteList()
        all_collision.extend(self.walls)
        all_collision.extend(self.platform)

        collision_slime = arcade.SpriteList()
        collision_slime.extend(self.walls)
        collision_slime.extend(self.platform)
        collision_slime.extend(self.invis)

        # Камеры
        self.camera = Camera2D()
        self.ui_camera = Camera2D()  # ← UI-камера: всегда "смотрит" на (0, 0)

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
            players=[self.player1, self.player2],
            gravity=GRAVITY,
            damage=SLIME_DAMAGE,
            damage_cooldown=DAMAGE_COOLDOWN
        )

        hp_sprite_p1 = arcade.Sprite()
        hp_sprite_p1.texture = self.HP_bar
        hp_sprite_p2 = arcade.Sprite()
        hp_sprite_p2.texture = self.HP_bar_p2

        hp_sprite_p2.scale = 0.5
        hp_sprite_p1.scale = 0.5

        # Добавляем в SpriteList
        self.HP_bar_sprite_list.append(hp_sprite_p1)
        self.HP_bar_sprite_list.append(hp_sprite_p2)

        # Центрируем карту
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

        # Игровой мир
        self.camera.use()
        self.walls.draw()
        self.platform.draw()
        if self.player1.is_alive:
            self.player1.draw()
        if self.player2.is_alive:
            self.player2.draw()
        self.slime.draw()

        # UI
        self.ui_camera.use()

        if len(self.HP_bar_sprite_list) >= 2:
            p1 = self.HP_bar_sprite_list[0]
            p2 = self.HP_bar_sprite_list[1]

            # Левый верхний угол
            p1.center_x = p1.width / 2
            p1.center_y = self.window.height - p1.height / 2

            # Правый верхний угол
            p2.center_x = self.window.width - p2.width / 2
            p2.center_y = self.window.height - p2.height / 2

        # Рисуем все HP-бары
        self.HP_bar_sprite_list.draw()
        self.draw_hp_fill()

    def on_update(self, delta_time):
        # Обновление игроков
        if self.player1.is_alive:
            self.player1.on_update(delta_time)
        if self.player2.is_alive:
            self.player2.on_update(delta_time)

        # Физика
        if self.player1.is_alive:
            self.player1.physics_engine.update()
        if self.player2.is_alive:
            self.player2.physics_engine.update()

        # Слизень
        self.slime.on_update(delta_time)

        # Коллизия между игроками
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
        distance = max(0.1, (dx ** 2 + dy ** 2) ** 0.5)

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


    def draw_hp_fill(self):
        """Рисует заполнение строго внутри полосы, не заходя на шарики."""
        if not self.player1.is_alive and not self.player2.is_alive:
            return

        # Размеры бара с учётом масштаба
        bar_width = self.HP_bar.width * 0.5
        bar_height = self.HP_bar.height * 0.5

        # Подобранные отступы (увеличь, если линия заходит на шарики)
        padding_left = 155  # ← увеличено! было 30 → теперь 35
        padding_right = 155  # ← увеличено!
        inner_height = 50

        inner_width = bar_width - padding_left - padding_right

        # === Игрок 1 (левый) ===
        if self.player1.is_alive:
            ratio = max(0.0, min(1.0, self.player1.hp / self.player1.max_hp))
            fill_width = inner_width * ratio

            if fill_width > 0:
                arcade.draw_rect_filled(
                    LBWH(
                        left=padding_left,  # начинаем после левого шарика
                        bottom=self.window.height - bar_height + (bar_height - inner_height) // 2,
                        # по центру по высоте
                        width=fill_width,
                        height=inner_height
                    ),
                    color=arcade.color.GREEN
                )

        # === Игрок 2 (правый) ===
        if self.player2.is_alive:
            ratio = max(0.0, min(1.0, self.player2.hp / self.player2.max_hp))
            fill_width = inner_width * ratio

            if fill_width > 0:
                arcade.draw_rect_filled(
                    LBWH(
                        left=self.window.width - bar_width + padding_left,  # начинаем после правого шарика
                        bottom=self.window.height - bar_height + (bar_height - inner_height) // 2,
                        width=fill_width,
                        height=inner_height
                    ),
                    color=arcade.color.BLUE
                )

    def on_key_release(self, key, modifiers):
        if self.player1.is_alive:
            self.player1.on_key_release(key, modifiers)
        if self.player2.is_alive:
            self.player2.on_key_release(key, modifiers)

    def loading_texture(self):
        self.HP_bar = arcade.load_texture("models/UI/HP_bar.png")
        self.HP_bar_p2 = self.HP_bar.flip_left_right()
