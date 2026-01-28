import arcade
from arcade import Camera2D
from scripts.characters import hero_death_knight, hero_wizard
from scripts.monsters import slime, skeleton, boss_skeleton
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
        self.camera_player1 = None
        self.camera_player2 = None
        self.ui_camera = None
        self.slime = None
        self.skeleton = None
        self.boss_skeleton = None
        self.boss_spawned = False
        self.boss_spawn_point = None

        self.sword_sprite = None
        self.sword_collected = False
        self.staff_list = None
        self.staff_collected = False
        self.HP_bar = None
        self.bgm = arcade.load_sound("models/sounds/bgm_dungeon.ogg", streaming=True)
        self.bgm_player = None
        self.sword_weapon = None
        self.staff_weapon = None
        self.HP_bar_sprite_list = arcade.SpriteList()
        self.shake_timer_p1 = 0.0
        self.shake_magnitude_p1 = 0
        self.shake_timer_p2 = 0.0
        self.shake_magnitude_p2 = 0
        self.projectiles = arcade.SpriteList()
        self.summoned_skeletons = []
        self.spawned_slimes = []
        self.loading_texture()

        # Тексты для UI (чтобы избежать draw_text)
        self.fps_text = arcade.Text("", 10, 30, arcade.color.WHITE, 16)
        self.death_text_p1 = arcade.Text("УМЕР", 0, 0, arcade.color.WHITE, 48, anchor_x="center", anchor_y="center")
        self.death_text_p2 = arcade.Text("УМЕР", 0, 0, arcade.color.WHITE, 48, anchor_x="center", anchor_y="center")
        self.game_over_text = arcade.Text("ПОРАЖЕНИЕ", 0, 0, arcade.color.RED, 72, anchor_x="center")
        self.game_over_subtext = arcade.Text("Возврат в меню...", 0, 0, arcade.color.WHITE, 32, anchor_x="center")

        self.current_level = 1
        self.total_levels = 2
        self.all_monsters_defeated = False

        self.fps_history = []
        self.fps_display = 0
        self.game_over = False
        self.game_over_callback = None

    def setup(self, level=1):
        self.current_level = level
        self.all_monsters_defeated = False
        self.game_over = False

        # Очистка
        self.summoned_skeletons.clear()
        self.spawned_slimes.clear()
        self.projectiles.clear()
        self.sword_collected = False
        self.staff_collected = False

        map_name = f"models/map/test_map/map{level}.tmx"
        test_map = arcade.load_tilemap(map_name, scaling=1.2)

        # Слои карты
        self.walls = test_map.sprite_lists.get("walls", arcade.SpriteList())
        self.platform = test_map.sprite_lists.get("platforms", arcade.SpriteList())
        self.invis = test_map.sprite_lists.get("invis", arcade.SpriteList())

        # Слои спавна (безопасно!)
        self.spawn_slimes = test_map.sprite_lists.get("spawn_slimes", arcade.SpriteList())
        self.spawn_sceletons = test_map.sprite_lists.get("spawn_sceletons", arcade.SpriteList())
        self.spawn_players = test_map.sprite_lists.get("spawn_players", arcade.SpriteList())
        self.spawn_boss = test_map.sprite_lists.get("spawn_boss", arcade.SpriteList())

        # Коллизии
        all_collision = arcade.SpriteList()
        all_collision.extend(self.walls)
        all_collision.extend(self.platform)

        self.collision_slime = arcade.SpriteList()
        self.collision_slime.extend(self.walls)
        self.collision_slime.extend(self.platform)
        self.collision_slime.extend(self.invis)

        # Камеры
        self.camera_player1 = Camera2D()
        self.camera_player1.viewport = LBWH(0, 0, self.window.width // 2, self.window.height)
        self.camera_player2 = Camera2D()
        self.camera_player2.viewport = LBWH(self.window.width // 2, 0, self.window.width // 2, self.window.height)
        self.camera_player1.zoom = 1.2
        self.camera_player2.zoom = 1.2
        self.ui_camera = Camera2D()

        # Центрирование карты
        all_sprites = arcade.SpriteList()
        for lst in [self.walls, self.platform, self.invis,
                    self.spawn_slimes, self.spawn_sceletons,
                    self.spawn_players, self.spawn_boss]:
            all_sprites.extend(lst)

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

        # Игроки
        if len(self.spawn_players) >= 2:
            p1_spawn = self.spawn_players[0]
            p2_spawn = self.spawn_players[1]
        else:
            # Резервные координаты
            p1_spawn = type('Spawn', (), {'center_x': 100 + dx, 'center_y': 100 + dy})()
            p2_spawn = type('Spawn', (), {'center_x': 150 + dx, 'center_y': 100 + dy})()

        self.player1 = hero_death_knight.DeathKnight(
            p1_spawn.center_x, p1_spawn.center_y,
            speed=PLAYER_SPEED, scale=PLAYER_SIZE, number_player=1,
            colision_sprites=all_collision, jump_speed=JUMP_SPEED, gravity=GRAVITY
        )
        self.player2 = hero_wizard.Wizard(
            p2_spawn.center_x, p2_spawn.center_y,
            speed=PLAYER_SPEED, scale=PLAYER_SIZE, number_player=2,
            colision_sprites=all_collision, jump_speed=JUMP_SPEED, gravity=GRAVITY
        )

        # Оружие
        self.sword_weapon = SwordWeapon.create_sword()
        self.sword_weapon.load_attack_animations("models/hero/death_knight/animations/attack_sword", frame_count=3)
        self.staff_weapon = StaffWeapon.create_staff()
        self.staff_weapon.load_attack_animations("models/hero/wizard/animations/staff_attack", frame_count=3)

        # Предметы
        self.sword_list = arcade.SpriteList()
        self.sword_sprite = arcade.Sprite("models/items/sword.png", scale=0.15)
        self.sword_sprite.center_x, self.sword_sprite.center_y = p1_spawn.center_x, p1_spawn.center_y
        self.sword_list.append(self.sword_sprite)

        self.staff_list = arcade.SpriteList()
        staff_sprite = arcade.Sprite("models/items/staff.png", scale=0.15)
        staff_sprite.center_x, staff_sprite.center_y = p2_spawn.center_x, p2_spawn.center_y
        self.staff_list.append(staff_sprite)

        # Монстры
        slime_spawn = self.spawn_slimes[0] if self.spawn_slimes else None
        skeleton_spawn = self.spawn_sceletons[0] if self.spawn_sceletons else None

        if slime_spawn:
            self.slime = slime.Slime(
                x=slime_spawn.center_x, y=slime_spawn.center_y,
                collision_sprites=self.collision_slime,
                players=[self.player1, self.player2],
                gravity=GRAVITY, damage=SLIME_DAMAGE, damage_cooldown=DAMAGE_COOLDOWN
            )
        else:
            self.slime = None

        if skeleton_spawn:
            self.skeleton = skeleton.Skeleton(
                x=skeleton_spawn.center_x, y=skeleton_spawn.center_y,
                collision_sprites=self.collision_slime,
                players=[self.player1, self.player2],
                gravity=GRAVITY, damage=SKELETON_DAMAGE,
                attack_range=SKELETON_ATTACK_RANGE, attack_cooldown=SKELETON_ATTACK_COOLDOWN
            )
        else:
            self.skeleton = None

        # Босс
        if self.spawn_boss:
            boss_spawn = self.spawn_boss[0]
            self.boss_spawn_point = (boss_spawn.center_x, boss_spawn.center_y)
        else:
            self.boss_spawn_point = None
            self.boss_skeleton = None
            self.boss_spawned = False

        # HP-бары
        hp_sprite_p1 = arcade.Sprite(self.HP_bar, scale=0.5)
        hp_sprite_p2 = arcade.Sprite(self.HP_bar_p2, scale=0.5)
        self.HP_bar_sprite_list = arcade.SpriteList()
        self.HP_bar_sprite_list.extend([hp_sprite_p1, hp_sprite_p2])

        # Музыка
        if self.bgm_player is None:
            self.bgm_player = arcade.play_sound(self.bgm, volume=0.3)

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)

        # Левый экран
        self.camera_player1.use()
        self._draw_game_world()
        self.projectiles.draw()

        # Правый экран
        self.camera_player2.use()
        self._draw_game_world()
        self.projectiles.draw()

        # UI
        self.ui_camera.use()
        self._draw_ui()
        self.fps_text.draw()

        # Экраны смерти
        if not self.player1.is_alive and not self.game_over:
            arcade.draw_rect_filled(
                LBWH(0, 0, self.window.width // 2, self.window.height),
                color=(0, 0, 0, 200)
            )
            self.death_text_p1.position = (self.window.width // 4, self.window.height // 2)
            self.death_text_p1.draw()

        if not self.player2.is_alive and not self.game_over:
            arcade.draw_rect_filled(
                LBWH(self.window.width // 2, 0, self.window.width // 2, self.window.height),
                color=(0, 0, 0, 200)
            )
            self.death_text_p2.position = (self.window.width * 3 // 4, self.window.height // 2)
            self.death_text_p2.draw()

        # Полное поражение
        if self.game_over:
            arcade.draw_rect_filled(
                LBWH(0, 0, self.window.width, self.window.height),
                color=(0, 0, 0, 230)
            )
            self.game_over_text.position = (self.window.width // 2, self.window.height // 2 + 50)
            self.game_over_subtext.position = (self.window.width // 2, self.window.height // 2 - 30)
            self.game_over_text.draw()
            self.game_over_subtext.draw()

        # HP босса
        if self.boss_skeleton and self.boss_skeleton.is_alive and not self.game_over:
            self.ui_camera.use()
            boss_max_width = 400
            boss_height = 20
            ratio = max(0.0, min(1.0, self.boss_skeleton.hp / self.boss_skeleton.max_hp))
            fill_width = boss_max_width * ratio
            center_x = self.window.width // 2
            top_y = self.window.height - 30
            arcade.draw_rect_filled(
                LBWH(center_x - boss_max_width // 2, top_y, boss_max_width, boss_height),
                color=arcade.color.DARK_GRAY
            )
            if fill_width > 0:
                arcade.draw_rect_filled(
                    LBWH(center_x - boss_max_width // 2, top_y, fill_width, boss_height),
                    color=arcade.color.RED
                )

    def on_update(self, delta_time):
        # FPS
        if delta_time > 0:
            instant_fps = 1.0 / delta_time
            self.fps_history.append(instant_fps)
            if len(self.fps_history) > 10:
                self.fps_history.pop(0)
            self.fps_display = sum(self.fps_history) / len(self.fps_history)
            self.fps_text.text = f"FPS: {int(self.fps_display)}"

        # Обновление игроков
        if self.player1.is_alive:
            self.player1.on_update(delta_time)
            self.player1.physics_engine.update()
        if self.player2.is_alive:
            self.player2.on_update(delta_time)
            self.player2.physics_engine.update()

        # Монстры
        if self.slime:
            self.slime.on_update(delta_time)
        if self.skeleton:
            self.skeleton.on_update(delta_time)

        # Активация босса
        if not self.boss_spawned and self.boss_spawn_point:
            bx, by = self.boss_spawn_point
            p1_ok = (self.player1.is_alive and abs(self.player1.player_sprite.center_x - bx) <= 100)
            p2_ok = (self.player2.is_alive and abs(self.player2.player_sprite.center_x - bx) <= 100)
            if p1_ok or p2_ok:
                self.boss_skeleton = boss_skeleton.Boss_skeleton(
                    x=bx, y=by,
                    collision_sprites=self.collision_slime,
                    players=[self.player1, self.player2],
                    gravity=GRAVITY,
                    damage=SKELETON_DAMAGE,
                    attack_range=SKELETON_ATTACK_RANGE,
                    attack_cooldown=SKELETON_ATTACK_COOLDOWN
                )
                self.boss_spawned = True
                print("✅ Босс активирован!")

        # Обновление босса
        if self.boss_skeleton:
            self.boss_skeleton.on_update(delta_time)

        # Призыв скелетов
        if self.boss_skeleton and self.boss_skeleton.is_alive and self.boss_skeleton.should_summon:
            self.boss_skeleton.should_summon = False
            offset_x = 50 if self.boss_skeleton.facing == "right" else -50
            new_skeleton = skeleton.Skeleton(
                x=self.boss_skeleton.skeleton_boss_sprite.center_x + offset_x,
                y=self.boss_skeleton.skeleton_boss_sprite.center_y,
                collision_sprites=self.collision_slime,
                players=[self.player1, self.player2],
                gravity=GRAVITY,
                damage=25,
                attack_range=1000,
                attack_cooldown=2.0
            )
            self.summoned_skeletons.append(new_skeleton)

        # Обновление призванных
        for skel in self.summoned_skeletons[:]:
            if skel.is_alive:
                skel.on_update(delta_time)
        self.summoned_skeletons = [s for s in self.summoned_skeletons if s.is_alive]

        for s in self.spawned_slimes[:]:
            if s.is_alive:
                s.on_update(delta_time)
        self.spawned_slimes = [s for s in self.spawned_slimes if s.is_alive]

        # Снаряды босса → слизни
        if self.boss_skeleton:
            for proj in self.boss_skeleton.projectiles[:]:
                hit = False
                for player in [self.player1, self.player2]:
                    if player.is_alive and arcade.check_for_collision(proj, player.player_sprite):
                        player.take_damage(getattr(proj, 'damage', 30))
                        proj.remove_from_sprite_lists()
                        hit = True
                        break
                if not hit and arcade.check_for_collision_with_list(proj, self.collision_slime):
                    if hasattr(proj, 'is_slime_projectile'):
                        spawn_x, spawn_y = proj.center_x, proj.center_y
                        walls = arcade.check_for_collision_with_list(proj, self.collision_slime)
                        if walls:
                            wall = walls[0]
                            spawn_y = wall.top + 10
                            spawn_x = max(wall.left + 10, min(spawn_x, wall.right - 10))
                        new_slime = slime.Slime(
                            x=spawn_x, y=spawn_y,
                            collision_sprites=self.collision_slime,
                            players=[self.player1, self.player2],
                            gravity=GRAVITY, damage=SLIME_DAMAGE, damage_cooldown=DAMAGE_COOLDOWN
                        )
                        self.spawned_slimes.append(new_slime)
                    proj.remove_from_sprite_lists()

        # Коллизии игроков
        if self.player1.is_alive and self.player2.is_alive:
            self.resolve_collision(self.player1.player_sprite, self.player2.player_sprite)

        # Подбор предметов
        if not self.sword_collected and self.player1.is_alive and arcade.check_for_collision(self.sword_sprite, self.player1.player_sprite):
            self.player1.equip_weapon(self.sword_weapon)
            self.sword_collected = True
            self.sword_list.clear()

        if not self.staff_collected and self.staff_list and self.player2.is_alive:
            staff = self.staff_list[0]
            if arcade.check_for_collision(staff, self.player2.player_sprite):
                self.player2.equip_weapon(self.staff_weapon)
                self.staff_collected = True
                self.staff_list.clear()

        # Урон от монстров
        targets = [
            self.slime,
            self.skeleton,
            self.boss_skeleton,
            *self.summoned_skeletons,
            *self.spawned_slimes
        ]
        for target in targets:
            if target and target.is_alive:
                sprite_attr = 'slime_sprite' if isinstance(target, slime.Slime) else 'skeleton_sprite'
                if hasattr(target, 'skeleton_boss_sprite'):
                    sprite_attr = 'skeleton_boss_sprite'
                sprite = getattr(target, sprite_attr)
                self._check_attack_hit(self.player1, sprite, target)

        # Снаряды игроков
        for proj in self.projectiles:
            proj.update(delta_time)
            hit = False
            all_targets = [self.slime, self.skeleton, self.boss_skeleton] + self.summoned_skeletons + self.spawned_slimes
            for target in all_targets:
                if target and target.is_alive:
                    attr = 'slime_sprite' if isinstance(target, slime.Slime) else 'skeleton_sprite'
                    if hasattr(target, 'skeleton_boss_sprite'):
                        attr = 'skeleton_boss_sprite'
                    if arcade.check_for_collision(proj, getattr(target, attr)):
                        target.take_damage(proj.damage)
                        proj.remove_from_sprite_lists()
                        hit = True
                        break
            if not hit and (abs(proj.center_x) > 10000 or abs(proj.center_y) > 10000):
                proj.remove_from_sprite_lists()

        # Камеры
        if self.player1.is_alive:
            self.camera_player1.position = self.player1.player_sprite.position
        if self.player2.is_alive:
            self.camera_player2.position = self.player2.player_sprite.position

        # Тряска
        for i in [1, 2]:
            player = getattr(self, f'player{i}')
            cam = getattr(self, f'camera_player{i}')
            timer = getattr(self, f'shake_timer_p{i}')
            mag = getattr(self, f'shake_magnitude_p{i}')
            if player.is_alive and timer > 0:
                offset_x = random.uniform(-mag, mag)
                offset_y = random.uniform(-mag, mag)
                cam.position = (player.player_sprite.center_x + offset_x, player.player_sprite.center_y + offset_y)
                setattr(self, f'shake_timer_p{i}', timer - delta_time)

        # Проверка победы
        if not self.all_monsters_defeated and not self.game_over:
            monsters_alive = []
            for target in [self.slime, self.skeleton, self.boss_skeleton] + self.summoned_skeletons + self.spawned_slimes:
                if target and target.is_alive:
                    monsters_alive.append(True)
            if not monsters_alive:
                self.all_monsters_defeated = True
                if self.current_level < self.total_levels:
                    print(f"✅ Уровень {self.current_level} завершён! Загрузка уровня {self.current_level + 1}...")
                    self.setup(level=self.current_level + 1)
                else:
                    print("🎉 Все уровни пройдены!")

        # Поражение
        if not self.game_over and not self.player1.is_alive and not self.player2.is_alive:
            self.game_over = True
            from scripts.modes.start_view import StartView
            def return_to_menu(dt):
                self.window.show_view(StartView())
            self.game_over_callback = return_to_menu
            arcade.schedule(self.game_over_callback, 2.0)

    def _draw_ui(self):
        if len(self.HP_bar_sprite_list) >= 2:
            p1, p2 = self.HP_bar_sprite_list[0], self.HP_bar_sprite_list[1]
            p1.center_x = p1.width / 2
            p1.center_y = self.window.height - p1.height / 2
            p2.center_x = self.window.width - p2.width / 2
            p2.center_y = self.window.height - p2.height / 2
        self.HP_bar_sprite_list.draw()
        self.draw_hp_fill()

    def draw_hp_fill(self):
        if not self.player1.is_alive and not self.player2.is_alive:
            return

        bar_width = self.HP_bar.width * 0.5
        bar_height = self.HP_bar.height * 0.5
        padding = 30
        inner_height = 50
        inner_width = bar_width - 2 * padding

        for i, player in enumerate([self.player1, self.player2], start=1):
            if player.is_alive:
                ratio = max(0.0, min(1.0, player.hp / player.max_hp))
                fill_width = inner_width * ratio
                if fill_width > 0:
                    x = padding if i == 1 else self.window.width - bar_width + padding
                    y = self.window.height - bar_height + (bar_height - inner_height) // 2
                    color = arcade.color.GREEN if i == 1 else arcade.color.BLUE
                    arcade.draw_rect_filled(LBWH(x, y, fill_width, inner_height), color=color)

    def _draw_game_world(self):
        self.walls.draw()
        self.platform.draw()
        if self.player1.is_alive: self.player1.draw()
        if self.player2.is_alive: self.player2.draw()
        if not self.sword_collected: self.sword_list.draw()
        if not self.staff_collected: self.staff_list.draw()
        if self.slime and self.slime.is_alive: self.slime.draw()
        if self.skeleton and self.skeleton.is_alive: self.skeleton.draw()
        if self.boss_skeleton and self.boss_skeleton.is_alive: self.boss_skeleton.draw()
        for skel in self.summoned_skeletons:
            if skel.is_alive: skel.draw()
        for s in self.spawned_slimes:
            if s.is_alive: s.draw()

    def resolve_collision(self, sprite1, sprite2):
        if not arcade.check_for_collision(sprite1, sprite2):
            return
        dx = sprite1.center_x - sprite2.center_x
        dy = sprite1.center_y - sprite2.center_y
        distance = max(0.1, (dx*dx + dy*dy) ** 0.5)
        min_dist = (sprite1.width + sprite2.width) * 0.4
        if distance < min_dist:
            overlap = (min_dist - distance) * 0.5
            norm_x, norm_y = dx / distance, dy / distance
            sprite1.center_x += norm_x * overlap
            sprite1.center_y += norm_y * overlap
            sprite2.center_x -= norm_x * overlap
            sprite2.center_y -= norm_y * overlap

    def on_key_press(self, key, modifiers):
        if self.player1.is_alive:
            self.player1.on_key_press(key, modifiers)
        if self.player2.is_alive:
            proj = self.player2.on_key_press(key, modifiers)
            if proj:
                self.projectiles.append(proj)

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

        attack_range = player.weapon.attack_range
        attack_width = player.weapon.attack_width
        attack_height = player.weapon.attack_height

        if player.facing == "right":
            hit_left = player.player_sprite.center_x
            hit_right = player.player_sprite.center_x + attack_range
        else:
            hit_left = player.player_sprite.center_x - attack_range
            hit_right = player.player_sprite.center_x

        hit_bottom = player.player_sprite.center_y - attack_height / 2
        hit_top = player.player_sprite.center_y + attack_height / 2

        if (hit_left < target_sprite.right and
            hit_right > target_sprite.left and
            hit_bottom < target_sprite.top and
            hit_top > target_sprite.bottom):
            target_object.take_damage(player.weapon.damage)
            player.has_dealt_damage_this_attack = True
            return True
        return False

    def on_hide_view(self):
        if self.bgm_player:
            arcade.stop_sound(self.bgm_player)
        self.bgm_player = None
        if self.game_over_callback:
            arcade.unschedule(self.game_over_callback)
            self.game_over_callback = None