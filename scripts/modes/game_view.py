import arcade
from arcade import Camera2D
from scripts.characters import hero_death_knight, hero_wizard
from scripts.monsters import slime, skeleton
from arcade import LBWH
from scripts.weapon.sword import Weapon as SwordWeapon
from scripts.weapon.staff import StaffWeapon
import random

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
LOW_HP_THRESHOLD = 0.2


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.walls = None
        self.platform = None
        self.invis = None
        self.player1 = None
        self.player2 = None
        self.camera = None
        self.ui_camera = None
        self.slime = None
        self.skeleton = None
        self.sword_sprite = None
        self.sword_collected = False
        self.staff_list = None
        self.staff_collected = False
        self.HP_bar = None
        self.sword_weapon = None
        self.staff_weapon = None
        self._prev_hp_p1 = None
        self._prev_hp_p2 = None
        self.HP_bar_sprite_list = arcade.SpriteList()

        self.shake_timer_p1 = 0.0
        self.shake_magnitude_p1 = 0
        self.shake_timer_p2 = 0.0
        self.shake_magnitude_p2 = 0

        # --- НОВОЕ: список снарядов ---
        self.projectiles = arcade.SpriteList()

        self.loading_texture()

        # Таймеры урона
        self._last_damage_time_p1 = 0.0
        self._last_damage_time_p2 = 0.0

    def setup(self):
        # Загрузка карты
        test_map = arcade.load_tilemap("models/map/test_map/map.tmx", scaling=1.2)
        self.walls = test_map.sprite_lists["walls"]
        self.platform = test_map.sprite_lists["platforms"]
        self.invis = test_map.sprite_lists.get("invis", arcade.SpriteList())
        self.spawn_slimes = test_map.sprite_lists["spawn_slimes"]
        self.spawn_sceletons = test_map.sprite_lists["spawn_sceletons"]

        # Коллизии
        all_collision = arcade.SpriteList()
        all_collision.extend(self.walls)
        all_collision.extend(self.platform)

        collision_slime = arcade.SpriteList()
        collision_slime.extend(self.walls)
        collision_slime.extend(self.platform)
        collision_slime.extend(self.invis)

        slime_spawn = self.spawn_slimes[0]
        skeleton_spawn = self.spawn_sceletons[0]

        # Камеры
        self.camera_player1 = Camera2D()
        self.camera_player1.viewport = arcade.LBWH(0, 0, self.window.width // 2, self.window.height)

        self.camera_player2 = Camera2D()
        self.camera_player2.viewport = arcade.LBWH(self.window.width // 2, 0, self.window.width // 2,
                                                   self.window.height)
        self.camera_player1.zoom = 1.2
        self.camera_player2.zoom = 1.2
        self.ui_camera = Camera2D()

        start_x = self.window.width / 2 - 200
        start_y = self.window.height / 2

        # Оружие
        self.sword_weapon = SwordWeapon.create_sword()
        self.sword_weapon.load_attack_animations("models/hero/death_knight/animations/attack_sword", frame_count=3)

        # Посох
        self.staff_weapon = StaffWeapon.create_staff()
        self.staff_weapon.load_attack_animations("models/hero/wizard/animations/staff_attack", frame_count=3)

        # HP бары
        hp_sprite_p1 = arcade.Sprite()
        hp_sprite_p1.texture = self.HP_bar
        hp_sprite_p2 = arcade.Sprite()
        hp_sprite_p2.texture = self.HP_bar_p2
        hp_sprite_p1.scale = 0.5
        hp_sprite_p2.scale = 0.5
        self.HP_bar_sprite_list.append(hp_sprite_p1)
        self.HP_bar_sprite_list.append(hp_sprite_p2)

        # Центрируем карту
        all_sprites = arcade.SpriteList()
        all_sprites.extend(self.walls)
        all_sprites.extend(self.platform)
        all_sprites.extend(self.invis)

        # Посох
        staff_x = self.window.width / 2 + 100
        staff_y = self.window.height / 2 - 50
        self.staff_list = arcade.SpriteList()
        staff_sprite = arcade.Sprite("models/items/staff.png")
        staff_sprite.center_x = staff_x
        staff_sprite.center_y = staff_y
        staff_sprite.scale = 0.15
        self.staff_list.append(staff_sprite)
        self.staff_collected = False

        # Меч
        sword_x = self.window.width / 2 - 100
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

            for spawn in self.spawn_slimes:
                spawn.center_x += dx
                spawn.center_y += dy

            for spawn in self.spawn_sceletons:
                spawn.center_x += dx
                spawn.center_y += dy

        # Игроки
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

        # Монстры
        self.slime = slime.Slime(
            x=slime_spawn.center_x,
            y=slime_spawn.center_y,
            collision_sprites=collision_slime,
            players=[self.player1, self.player2],
            gravity=GRAVITY,
            damage=SLIME_DAMAGE,
            damage_cooldown=DAMAGE_COOLDOWN
        )

        self.skeleton = skeleton.Skeleton(
            x=skeleton_spawn.center_x,
            y=skeleton_spawn.center_y,
            collision_sprites=collision_slime,
            players=[self.player1, self.player2],
            gravity=GRAVITY,
            damage=SKELETON_DAMAGE,
            attack_range=SKELETON_ATTACK_RANGE,
            attack_cooldown=SKELETON_ATTACK_COOLDOWN
        )

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)

        self.camera_player1.use()
        self._draw_game_world()

        self.camera_player2.use()
        self._draw_game_world()

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

        # Монстры
        self.slime.on_update(delta_time)
        self.skeleton.on_update(delta_time)

        # Коллизия между игроками
        if self.player1.is_alive and self.player2.is_alive:
            self.resolve_collision(self.player1.player_sprite, self.player2.player_sprite)

        # Подбор меча
        if not self.sword_collected and self.player1.is_alive:
            if arcade.check_for_collision(self.sword_sprite, self.player1.player_sprite):
                self.player1.equip_weapon(self.sword_weapon)
                self.sword_collected = True
                self.sword_list.clear()
                print("Меч подобран!")

        # Подбор посоха
        if not self.staff_collected and self.staff_list and self.player2.is_alive:
            staff = self.staff_list[0]
            if arcade.check_for_collision(staff, self.player2.player_sprite):
                self.player2.equip_weapon(self.staff_weapon)
                self.staff_collected = True
                self.staff_list.clear()
                print("Посох подобран!")

        # Урон от DeathKnight (ближний бой)
        if self.slime.is_alive:
            self._check_attack_hit(self.player1, self.slime.slime_sprite, self.slime)
        if self.skeleton.is_alive:
            self._check_attack_hit(self.player1, self.skeleton.skeleton_sprite, self.skeleton)

        # Урон от снарядов (дальний бой)
        for proj in self.projectiles:
            if self.slime.is_alive and arcade.check_for_collision(proj, self.slime.slime_sprite):
                self.slime.take_damage(proj.damage)
                proj.remove_from_sprite_lists()
            if self.skeleton.is_alive and arcade.check_for_collision(proj, self.skeleton.skeleton_sprite):
                self.skeleton.take_damage(proj.damage)
                proj.remove_from_sprite_lists()

        # Обновление снарядов
        self.projectiles.update(delta_time)

        # Удаление снарядов за пределами экрана
        for proj in self.projectiles:
            if proj.center_x < -200 or proj.center_x > self.window.width + 200:
                proj.remove_from_sprite_lists()

        # Камеры
        if self.player1.is_alive:
            base_x, base_y = self.player1.player_sprite.position
            if self.shake_timer_p1 > 0:
                offset_x = random.uniform(-self.shake_magnitude_p1, self.shake_magnitude_p1)
                offset_y = random.uniform(-self.shake_magnitude_p1, self.shake_magnitude_p1)
                self.camera_player1.position = (base_x + offset_x, base_y + offset_y)
                self.shake_timer_p1 -= delta_time
            else:
                self.camera_player1.position = (base_x, base_y)

        if self.player2.is_alive:
            base_x, base_y = self.player2.player_sprite.position
            if self.shake_timer_p2 > 0:
                offset_x = random.uniform(-self.shake_magnitude_p2, self.shake_magnitude_p2)
                offset_y = random.uniform(-self.shake_magnitude_p2, self.shake_magnitude_p2)
                self.camera_player2.position = (base_x + offset_x, base_y + offset_y)
                self.shake_timer_p2 -= delta_time
            else:
                self.camera_player2.position = (base_x, base_y)

        # Камера тряска при получении урона
        if self.player1.is_alive:
            if self._prev_hp_p1 is not None and self.player1.hp < self._prev_hp_p1:
                self.start_camera_shake(1, duration=0.25, magnitude=8)
            self._prev_hp_p1 = self.player1.hp

        if self.player2.is_alive:
            if self._prev_hp_p2 is not None and self.player2.hp < self._prev_hp_p2:
                self.start_camera_shake(2, duration=0.25, magnitude=8)
            self._prev_hp_p2 = self.player2.hp

    def _draw_ui(self):
        if len(self.HP_bar_sprite_list) >= 2:
            p1 = self.HP_bar_sprite_list[0]
            p2 = self.HP_bar_sprite_list[1]
            p1.center_x = p1.width / 2
            p1.center_y = self.window.height - p1.height / 2
            p2.center_x = self.window.width - p2.width / 2
            p2.center_y = self.window.height - p2.height / 2

        self.HP_bar_sprite_list.draw()
        self.draw_hp_fill()

    def start_camera_shake(self, player_num: int, duration: float = 0.3, magnitude: float = 5.0):
        if player_num == 1:
            self.shake_timer_p1 = duration
            self.shake_magnitude_p1 = magnitude
        elif player_num == 2:
            self.shake_timer_p2 = duration
            self.shake_magnitude_p2 = magnitude

    def resolve_collision(self, sprite1, sprite2):
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
            proj = self.player2.on_key_press(key, modifiers)  # ← ВАЖНО: player2, не wizard
            if proj:
                self.projectiles.append(proj)

    def draw_hp_fill(self):
        if not self.player1.is_alive and not self.player2.is_alive:
            return

        bar_width = self.HP_bar.width * 0.5
        bar_height = self.HP_bar.height * 0.5
        padding_left = 30
        padding_right = 30
        inner_height = 50
        inner_width = bar_width - padding_left - padding_right

        # Игрок 1
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

        # Игрок 2
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
        if not self.sword_collected:
            self.sword_list.draw()
        if not self.staff_collected:
            self.staff_list.draw()
        if self.slime.is_alive:
            self.slime.draw()
        if self.skeleton.is_alive:
            self.skeleton.draw()
        self.projectiles.draw()  # ← рисуем снаряды

    def on_key_release(self, key, modifiers):
        if self.player1.is_alive:
            self.player1.on_key_release(key, modifiers)
        if self.player2.is_alive:
            self.player2.on_key_release(key, modifiers)

    def loading_texture(self):
        self.HP_bar = arcade.load_texture("models/UI/HP_bar.png")
        self.HP_bar_p2 = self.HP_bar.flip_left_right()

    def _check_attack_hit(self, player, target_sprite, target_object):
        if not player.is_alive or not player.is_attacking or not player.weapon:
            return False
        if getattr(player, 'has_dealt_damage_this_attack', False):
            return False

        offset_x = player.weapon.attack_range if player.facing == "right" else -player.weapon.attack_range
        hitbox = arcade.Sprite()
        hitbox.center_x = player.player_sprite.center_x + offset_x
        hitbox.center_y = player.player_sprite.center_y
        hitbox.width = player.weapon.attack_width
        hitbox.height = player.weapon.attack_height

        if arcade.check_for_collision(hitbox, target_sprite):
            target_object.take_damage(player.weapon.damage)
            player.has_dealt_damage_this_attack = True
            return True
        return False
