import arcade
from arcade import Camera2D
from scripts.characters import hero_death_knight, hero_wizard
from scripts.monsters import slime, skeleton
from arcade import LBWH, XYWH

# Глобальные константы
PLAYER_SIZE = 0.1
PLAYER_SPEED = 5
GRAVITY = 0.5
JUMP_SPEED = 25
SLIME_DAMAGE = 45
DAMAGE_COOLDOWN = 1.0
SKELETON_DAMAGE = 30
SKELETON_ATTACK_RANGE = 1500
SKELETON_ATTACK_COOLDOWN = 2.0


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
        self.skeleton = None
        self.sword_sprite = None
        self.sword_collected = False
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
        self.camera_player1 = Camera2D()
        self.camera_player1.viewport = arcade.LBWH(0, 0, self.window.width // 2, self.window.height)

        self.camera_player2 = Camera2D()
        self.camera_player2.viewport = arcade.LBWH(self.window.width // 2, 0, self.window.width // 2,
                                                   self.window.height)
        self.camera_player1.zoom = 1.2
        self.camera_player2.zoom = 1.2
        self.ui_camera = Camera2D()  # по умолчанию весь экран

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

        self.skeleton = skeleton.Skeleton(
            x=self.window.width / 2 - 400,
            y=self.window.height / 2,
            collision_sprites=collision_slime,
            players=[self.player1, self.player2],
            gravity=GRAVITY,
            damage=SKELETON_DAMAGE,
            attack_range=SKELETON_ATTACK_RANGE,
            attack_cooldown=SKELETON_ATTACK_COOLDOWN
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

        # Меч (предмет на земле)
        sword_x = self.window.width / 2 - 100   # ← можно взять из TMX-слоя позже
        sword_y = self.window.height / 2 - 50

        self.sword_list = arcade.SpriteList()
        self.sword_sprite = arcade.Sprite("models/items/sword.png")
        self.sword_list.append(self.sword_sprite)
        self.sword_sprite.center_x = sword_x
        self.sword_sprite.center_y = sword_y
        self.sword_sprite.scale = 0.15
        self.sword_collected = False

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

            # Центрируем меч вместе с картой
            self.sword_sprite.center_x += dx
            self.sword_sprite.center_y += dy

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)

        # Рисуем левую часть
        self.camera_player1.use()
        self._draw_game_world()

        # Рисуем правую часть
        self.camera_player2.use()
        self._draw_game_world()

        # UI — рисуем поверх всего, используя отдельную UI-камеру без viewport'а
        self.ui_camera.use()
        self._draw_ui()

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

        # Скелет
        self.skeleton.on_update(delta_time)

        # Коллизия между игроками
        if self.player1.is_alive and self.player2.is_alive:
            self.resolve_collision(self.player1.player_sprite, self.player2.player_sprite)

        # Проверка подбора меча
        if not self.sword_collected:
            collected_by_p1 = (self.player1.is_alive and
                               arcade.check_for_collision(self.sword_sprite, self.player1.player_sprite))


            if collected_by_p1:
                self.sword_collected = True
                # Можно добавить звук, эффект или усилить игрока
                print("Меч подобран!")

        # Камера следует за первым живым игроком
        if self.player1.is_alive:
            self.camera_player1.position = self.player1.player_sprite.position
        if self.player2.is_alive:
            self.camera_player2.position = self.player2.player_sprite.position

    def _draw_ui(self):
        if len(self.HP_bar_sprite_list) >= 2:
            p1 = self.HP_bar_sprite_list[0]
            p2 = self.HP_bar_sprite_list[1]

            # Левый верхний угол — для игрока 1
            p1.center_x = p1.width / 2
            p1.center_y = self.window.height - p1.height / 2

            # Правый верхний угол — для игрока 2
            p2.center_x = self.window.width - p2.width / 2
            p2.center_y = self.window.height - p2.height / 2

        self.HP_bar_sprite_list.draw()
        self.draw_hp_fill()

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

        bar_width = self.HP_bar.width * 0.5
        bar_height = self.HP_bar.height * 0.5

        padding_left = 30
        padding_right = 30
        inner_height = 50
        inner_width = bar_width - padding_left - padding_right

        # === Игрок 1 (левый) ===
        if self.player1.is_alive:
            ratio = max(0.0, min(1.0, self.player1.hp / self.player1.max_hp))
            fill_width = inner_width * ratio
            if fill_width > 0:
                arcade.draw_rect_filled(
                    LBWH(
                        padding_left,
                        self.window.height - bar_height + (bar_height - inner_height) // 2,
                        fill_width,
                        inner_height
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
                        self.window.width - bar_width + padding_left,
                        self.window.height - bar_height + (bar_height - inner_height) // 2,
                        fill_width,
                        inner_height
                    ),
                    color=arcade.color.BLUE
                )

    def _draw_game_world(self):
        self.walls.draw()
        self.platform.draw()
        if self.player1.is_alive:
            self.player1.draw()
        if self.player2.is_alive:
            self.player2.draw()
        self.slime.draw()
        self.skeleton.draw()

    def on_key_release(self, key, modifiers):
        if self.player1.is_alive:
            self.player1.on_key_release(key, modifiers)
        if self.player2.is_alive:
            self.player2.on_key_release(key, modifiers)

    def loading_texture(self):
        self.HP_bar = arcade.load_texture("models/UI/HP_bar.png")
        self.HP_bar_p2 = self.HP_bar.flip_left_right()
