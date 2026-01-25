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
        self.projectiles = arcade.SpriteList()
        self.summoned_skeletons = []
        self.spawned_slimes = []  # ← НОВОЕ: список спавненных слаймов
        self.loading_texture()
        self._last_damage_time_p1 = 0.0
        self._last_damage_time_p2 = 0.0

    def setup(self):
        test_map = arcade.load_tilemap("models/map/test_map/map.tmx", scaling=1.2)
        self.walls = test_map.sprite_lists["walls"]
        self.platform = test_map.sprite_lists["platforms"]
        self.invis = test_map.sprite_lists.get("invis", arcade.SpriteList())
        self.spawn_slimes = test_map.sprite_lists["spawn_slimes"]
        self.spawn_sceletons = test_map.sprite_lists["spawn_sceletons"]
        self.spawn_players = test_map.sprite_lists["spawn_players"]
        self.spawn_boss = test_map.sprite_lists["spawn_boss"]

        all_collision = arcade.SpriteList()
        all_collision.extend(self.walls)
        all_collision.extend(self.platform)

        self.collision_slime = arcade.SpriteList()
        self.collision_slime.extend(self.walls)
        self.collision_slime.extend(self.platform)
        self.collision_slime.extend(self.invis)

        slime_spawn = self.spawn_slimes[0]
        skeleton_spawn = self.spawn_sceletons[0]
        boss_spawn = self.spawn_boss[0]

        self.camera_player1 = Camera2D()
        self.camera_player1.viewport = LBWH(0, 0, self.window.width // 2, self.window.height)
        self.camera_player2 = Camera2D()
        self.camera_player2.viewport = LBWH(self.window.width // 2, 0, self.window.width // 2, self.window.height)
        self.camera_player1.zoom = 1.2
        self.camera_player2.zoom = 1.2
        self.ui_camera = Camera2D()

        self.player1_spawn = self.spawn_players[0]
        self.player2_spawn = self.spawn_players[1]

        self.sword_weapon = SwordWeapon.create_sword()
        self.sword_weapon.load_attack_animations("models/hero/death_knight/animations/attack_sword", frame_count=3)
        self.staff_weapon = StaffWeapon.create_staff()
        self.staff_weapon.load_attack_animations("models/hero/wizard/animations/staff_attack", frame_count=3)

        hp_sprite_p1 = arcade.Sprite(self.HP_bar, scale=0.5)
        hp_sprite_p2 = arcade.Sprite(self.HP_bar_p2, scale=0.5)
        self.HP_bar_sprite_list.extend([hp_sprite_p1, hp_sprite_p2])

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
            for lst in [self.spawn_slimes, self.spawn_sceletons, self.spawn_players, self.spawn_boss]:
                for spawn in lst:
                    spawn.center_x += dx
                    spawn.center_y += dy

        staff_x = self.player2_spawn.center_x
        staff_y = self.player1_spawn.center_y
        self.staff_list = arcade.SpriteList()
        staff_sprite = arcade.Sprite("models/items/staff.png", scale=0.15)
        staff_sprite.center_x, staff_sprite.center_y = staff_x, staff_y
        self.staff_list.append(staff_sprite)
        self.staff_collected = False

        sword_x = self.player1_spawn.center_x
        sword_y = self.player1_spawn.center_y
        self.sword_list = arcade.SpriteList()
        self.sword_sprite = arcade.Sprite("models/items/sword.png", scale=0.15)
        self.sword_sprite.center_x, self.sword_sprite.center_y = sword_x, sword_y
        self.sword_list.append(self.sword_sprite)
        self.sword_collected = False

        self.player1 = hero_death_knight.DeathKnight(
            self.player1_spawn.center_x, self.player1_spawn.center_y,
            speed=PLAYER_SPEED, scale=PLAYER_SIZE, number_player=1,
            colision_sprites=all_collision, jump_speed=JUMP_SPEED, gravity=GRAVITY
        )
        self.player2 = hero_wizard.Wizard(
            self.player2_spawn.center_x, self.player2_spawn.center_y,
            speed=PLAYER_SPEED, scale=PLAYER_SIZE, number_player=2,
            colision_sprites=all_collision, jump_speed=JUMP_SPEED, gravity=GRAVITY
        )

        self.slime = slime.Slime(x=slime_spawn.center_x, y=slime_spawn.center_y,
                                 collision_sprites=self.collision_slime, players=[self.player1, self.player2],
                                 gravity=GRAVITY, damage=SLIME_DAMAGE, damage_cooldown=DAMAGE_COOLDOWN)
        self.skeleton = skeleton.Skeleton(x=skeleton_spawn.center_x, y=skeleton_spawn.center_y,
                                 collision_sprites=self.collision_slime, players=[self.player1, self.player2],
                                 gravity=GRAVITY, damage=SKELETON_DAMAGE,
                                 attack_range=SKELETON_ATTACK_RANGE, attack_cooldown=SKELETON_ATTACK_COOLDOWN)
        self.boss_skeleton = boss_skeleton.Boss_skeleton(x=boss_spawn.center_x, y=boss_spawn.center_y,
                                           collision_sprites=self.collision_slime, players=[self.player1, self.player2],
                                           gravity=GRAVITY, damage=SKELETON_DAMAGE,
                                           attack_range=SKELETON_ATTACK_RANGE, attack_cooldown=SKELETON_ATTACK_COOLDOWN)

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)

        self.camera_player1.use()
        self._draw_game_world()
        self.camera_player2.use()
        self._draw_game_world()
        self.ui_camera.use()
        self._draw_ui()

        arcade.draw_text(f"FPS: {arcade.get_fps():.0f}", 10, 30, arcade.color.WHITE, 16)

    def on_update(self, delta_time):
        # Обновление игроков
        if self.player1.is_alive:
            self.player1.on_update(delta_time)
            self.player1.physics_engine.update()
        if self.player2.is_alive:
            self.player2.on_update(delta_time)
            self.player2.physics_engine.update()

        # Монстры
        self.slime.on_update(delta_time)
        self.skeleton.on_update(delta_time)
        self.boss_skeleton.on_update(delta_time)

        # Призыв скелетов
        if self.boss_skeleton.is_alive and self.boss_skeleton.should_summon:
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

        # Обновление призванных скелетов
        for skel in self.summoned_skeletons[:]:
            if skel.is_alive:
                skel.on_update(delta_time)
        self.summoned_skeletons = [skel for skel in self.summoned_skeletons if skel.is_alive]

        # Обработка взрыва слайм-шаров → спавн слаймов
        for proj in self.boss_skeleton.projectiles[:]:
            if not hasattr(proj, 'is_slime_projectile'):
                continue

            hit_wall = arcade.check_for_collision_with_list(proj, self.collision_slime)
            hit_player = False
            for player in [self.player1, self.player2]:
                if player.is_alive and arcade.check_for_collision(proj, player.player_sprite):
                    player.take_damage(getattr(proj, 'damage', 40))
                    hit_player = True

            if hit_wall or hit_player:
                new_slime = slime.Slime(
                    x=proj.center_x,
                    y=proj.center_y,
                    collision_sprites=self.collision_slime,
                    players=[self.player1, self.player2],
                    gravity=GRAVITY,
                    damage=SLIME_DAMAGE,
                    damage_cooldown=DAMAGE_COOLDOWN
                )
                self.spawned_slimes.append(new_slime)
                proj.remove_from_sprite_lists()

        # Обновление спавненных слаймов
        for s in self.spawned_slimes[:]:
            if s.is_alive:
                s.on_update(delta_time)
        self.spawned_slimes = [s for s in self.spawned_slimes if s.is_alive]

        # Коллизия между игроками
        if self.player1.is_alive and self.player2.is_alive:
            self.resolve_collision(self.player1.player_sprite, self.player2.player_sprite)

        # Подбор предметов
        if not self.sword_collected and self.player1.is_alive and arcade.check_for_collision(self.sword_sprite, self.player1.player_sprite):
            self.player1.equip_weapon(self.sword_weapon)
            self.sword_collected = True
            self.sword_list.clear()
            print("Меч подобран!")

        if not self.staff_collected and self.staff_list and self.player2.is_alive:
            staff = self.staff_list[0]
            if arcade.check_for_collision(staff, self.player2.player_sprite):
                self.player2.equip_weapon(self.staff_weapon)
                self.staff_collected = True
                self.staff_list.clear()
                print("Посох подобран!")

        # Урон от ближнего боя
        if self.slime.is_alive:
            self._check_attack_hit(self.player1, self.slime.slime_sprite, self.slime)
        if self.skeleton.is_alive:
            self._check_attack_hit(self.player1, self.skeleton.skeleton_sprite, self.skeleton)
        if self.boss_skeleton.is_alive:
            self._check_attack_hit(self.player1, self.boss_skeleton.skeleton_boss_sprite, self.boss_skeleton)
        for skel in self.summoned_skeletons:
            if skel.is_alive:
                self._check_attack_hit(self.player1, skel.skeleton_sprite, skel)
        for s in self.spawned_slimes:  # ← НОВОЕ
            if s.is_alive:
                self._check_attack_hit(self.player1, s.slime_sprite, s)

        # Урон от снарядов игрока
        for proj in self.projectiles:
            if self.slime.is_alive and arcade.check_for_collision(proj, self.slime.slime_sprite):
                self.slime.take_damage(proj.damage)
                proj.remove_from_sprite_lists()
            if self.skeleton.is_alive and arcade.check_for_collision(proj, self.skeleton.skeleton_sprite):
                self.skeleton.take_damage(proj.damage)
                proj.remove_from_sprite_lists()
            if self.boss_skeleton.is_alive and arcade.check_for_collision(proj, self.boss_skeleton.skeleton_boss_sprite):
                self.boss_skeleton.take_damage(proj.damage)
                proj.remove_from_sprite_lists()
            for skel in self.summoned_skeletons:
                if skel.is_alive and arcade.check_for_collision(proj, skel.skeleton_sprite):
                    skel.take_damage(proj.damage)
                    proj.remove_from_sprite_lists()
                    break
            for s in self.spawned_slimes:  # ← НОВОЕ
                if s.is_alive and arcade.check_for_collision(proj, s.slime_sprite):
                    s.take_damage(proj.damage)
                    proj.remove_from_sprite_lists()
                    break

        self.projectiles.update(delta_time)
        for proj in self.projectiles:
            if proj.center_x < -200 or proj.center_x > self.window.width + 200:
                proj.remove_from_sprite_lists()

        # Камеры
        for i, (player, cam, shake_timer, shake_mag) in enumerate([
            (self.player1, self.camera_player1, self.shake_timer_p1, self.shake_magnitude_p1),
            (self.player2, self.camera_player2, self.shake_timer_p2, self.shake_magnitude_p2)
        ], start=1):
            if player.is_alive:
                base_x, base_y = player.player_sprite.position
                if getattr(self, f'shake_timer_p{i}') > 0:
                    offset_x = random.uniform(-shake_mag, shake_mag)
                    offset_y = random.uniform(-shake_mag, shake_mag)
                    cam.position = (base_x + offset_x, base_y + offset_y)
                    setattr(self, f'shake_timer_p{i}', getattr(self, f'shake_timer_p{i}') - delta_time)
                else:
                    cam.position = (base_x, base_y)

        # Тряска при уроне
        for i, player in enumerate([self.player1, self.player2], start=1):
            if player.is_alive:
                prev_hp = getattr(self, f'_prev_hp_p{i}')
                if prev_hp is not None and player.hp < prev_hp:
                    self.start_camera_shake(i, duration=0.25, magnitude=8)
                setattr(self, f'_prev_hp_p{i}', player.hp)

    def _draw_ui(self):
        if len(self.HP_bar_sprite_list) >= 2:
            p1, p2 = self.HP_bar_sprite_list[0], self.HP_bar_sprite_list[1]
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
        if self.slime.is_alive: self.slime.draw()
        if self.skeleton.is_alive: self.skeleton.draw()
        if self.boss_skeleton.is_alive: self.boss_skeleton.draw()
        self.projectiles.draw()
        for skel in self.summoned_skeletons:
            if skel.is_alive:
                skel.draw()
        for s in self.spawned_slimes:  # ← НОВОЕ
            if s.is_alive:
                s.draw()

    def on_key_release(self, key, modifiers):
        if self.player1.is_alive: self.player1.on_key_release(key, modifiers)
        if self.player2.is_alive: self.player2.on_key_release(key, modifiers)

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