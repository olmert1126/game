import random
import arcade
from scripts.monsters.skeleton import Skeleton

class BossSkeleton:
    def __init__(self, x, y, collision_sprites, players, gravity=0.5, damage=30, attack_range=1500, attack_cooldown=2.0):
        self.loading_texture()
        self.boss_sprites_list = arcade.SpriteList()
        self.arrow_list = arcade.SpriteList()

        self.speed = 1
        self.facing = "right"
        self.hp = 500
        self.max_hp = self.hp
        self.is_alive = True

        self.gravity = gravity
        self.players = players
        self.damage = damage
        self.attack_range = attack_range
        self.attack_cooldown = attack_cooldown
        self._last_attack_time = 0.0
        self.is_attacking = False

        self.skeleton_spawn_cooldown = 10.0  # раз в 10 секунд
        self._last_skeleton_spawn_time = 0.0
        self.minions = []  # храним живых миньонов

        self.center_x = x
        self.center_y = y

        self.boss_sprite = arcade.Sprite()
        self.boss_sprite.texture = self.main_form
        self.boss_sprite.center_x = self.center_x
        self.boss_sprite.center_y = self.center_y
        self.boss_sprite.scale = 0.25

        self.boss_sprites_list.append(self.boss_sprite)
        self.collision_sprites = collision_sprites

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.boss_sprite,
            collision_sprites,
            gravity_constant=self.gravity,
        )

        # Анимации
        self.anim_run_right = [self.one_shot_run, self.two_shot_run]
        self.anim_run_left = [self.one_shot_run_left, self.two_shot_run_left]
        self.anim_attack_right = [self.one_shot_attack]
        self.anim_attack_left = [self.one_shot_attack_left]

        self.current_texture_run = 0
        self.texture_change_time_run = 0
        self.texture_change_delay_run = 0.2

    def loading_texture(self):
        self.main_form = arcade.load_texture("models/monsters/boss_skeleton/skeleton_boss_right.png")
        self.main_form_left = self.main_form.flip_left_right()
        self.one_shot_run = arcade.load_texture("models/monsters/boss_skeleton/animations/run/run1.png")
        self.two_shot_run = arcade.load_texture("models/monsters/boss_skeleton/animations/run/run2.png")
        self.one_shot_run_left = self.one_shot_run.flip_left_right()
        self.two_shot_run_left = self.two_shot_run.flip_left_right()
        self.one_shot_attack = arcade.load_texture("models/monsters/boss_skeleton/animations/attack/attack1.png")
        self.one_shot_attack_left = self.one_shot_attack.flip_left_right()
        self.arrow_texture = arcade.load_texture("models/monsters/boss_skeleton/arrow.png")
        self.arrow_texture_left = self.arrow_texture.flip_left_right()

    def _reverse_direction(self):
        self.facing = "left" if self.facing == "right" else "right"
        self.current_texture_run = 0

    def _shoot_arrow(self, target_player):
        arrow = arcade.Sprite()
        arrow.center_x = self.boss_sprite.center_x
        arrow.center_y = self.boss_sprite.center_y + 10

        dx = target_player.player_sprite.center_x - arrow.center_x
        dy = target_player.player_sprite.center_y - arrow.center_y
        distance = (dx**2 + dy**2) ** 0.5
        if distance == 0:
            return

        norm_dx = dx / distance
        norm_dy = dy / distance
        arrow.change_x = norm_dx * 8
        arrow.change_y = norm_dy * 8

        angle = arcade.math.get_angle_degrees(
            arrow.center_x, arrow.center_y,
            target_player.player_sprite.center_x,
            target_player.player_sprite.center_y
        )
        arrow.angle = angle

        if dx >= 0:
            arrow.texture = self.arrow_texture
        else:
            arrow.texture = self.arrow_texture_left

        arrow.scale = 0.25
        self.arrow_list.append(arrow)

    def on_update(self, delta_time):
        if not self.is_alive:
            return

        self.physics_engine.update()

        # === СПАВН СКЕЛЕТОВ (только если HP > 50%) ===
        if self.hp > self.max_hp * 0.5:
            self._last_skeleton_spawn_time += delta_time
            if self._last_skeleton_spawn_time >= self.skeleton_spawn_cooldown:
                offset_x = random.choice([-100, 100])
                spawn_x = self.boss_sprite.center_x + offset_x
                spawn_y = self.boss_sprite.center_y

                new_skeleton = Skeleton(
                    x=spawn_x,
                    y=spawn_y,
                    collision_sprites=self.collision_sprites,
                    players=self.players,
                    gravity=self.gravity,
                    damage=self.damage,
                    attack_range=self.attack_range,
                    attack_cooldown=self.attack_cooldown
                )
                self.minions.append(new_skeleton)
                self._last_skeleton_spawn_time = 0.0

        # === ОБНОВЛЕНИЕ МИНЬОНОВ ===
        for minion in self.minions[:]:  # копия списка для безопасного удаления
            minion.on_update(delta_time)
            if not minion.is_alive:
                self.minions.remove(minion)

        # === СТРЕЛЫ ===
        for arrow in self.arrow_list:
            arrow.update()
            if arcade.check_for_collision_with_list(arrow, self.collision_sprites):
                arrow.remove_from_sprite_lists()
                continue
            if abs(arrow.center_x - self.boss_sprite.center_x) > 2000:
                arrow.remove_from_sprite_lists()
                continue
            for player in self.players:
                if not player.is_alive:
                    continue
                if arcade.check_for_collision(arrow, player.player_sprite):
                    player.take_damage(self.damage)
                    arrow.remove_from_sprite_lists()
                    break

        # === ПОИСК ЦЕЛИ И ДВИЖЕНИЕ ===
        target_player = None
        min_dist = float('inf')
        for player in self.players:
            if not player.is_alive:
                continue
            dist = arcade.get_distance_between_sprites(self.boss_sprite, player.player_sprite)
            if dist <= self.attack_range and dist < min_dist:
                min_dist = dist
                target_player = player

        if target_player is not None:
            self.is_attacking = True
            self._last_attack_time += delta_time
            if self._last_attack_time >= self.attack_cooldown:
                self._shoot_arrow(target_player)
                self._last_attack_time = 0.0

            if target_player.player_sprite.center_x > self.boss_sprite.center_x:
                self.facing = "right"
            else:
                self.facing = "left"
        else:
            self.is_attacking = False
            direction = 1 if self.facing == "right" else -1
            next_x = self.boss_sprite.center_x + self.speed * direction

            test_front = arcade.Sprite(center_x=next_x, center_y=self.boss_sprite.center_y)
            test_front.texture = self.main_form
            test_front.scale = self.boss_sprite.scale
            front_collisions = arcade.check_for_collision_with_list(test_front, self.collision_sprites)

            if front_collisions:
                self._reverse_direction()
            else:
                self.boss_sprite.center_x = next_x

        self.update_animation(delta_time)

    def update_animation(self, delta_time: float):
        self.texture_change_time_run += delta_time
        if self.texture_change_time_run >= self.texture_change_delay_run:
            self.texture_change_time_run = 0
            if self.is_attacking:
                self.current_texture_run = (self.current_texture_run + 1) % len(self.anim_attack_right)
                tex_list = self.anim_attack_right if self.facing == "right" else self.anim_attack_left
            else:
                self.current_texture_run = (self.current_texture_run + 1) % len(self.anim_run_right)
                tex_list = self.anim_run_right if self.facing == "right" else self.anim_run_left
            self.boss_sprite.texture = tex_list[self.current_texture_run]

    def draw(self):
        self.boss_sprites_list.draw()
        self.arrow_list.draw()
        # Рисуем миньонов
        for minion in self.minions:
            minion.draw()

    def take_damage(self, damage):
        if not self.is_alive:
            return
        self.hp -= damage
        print(f"Босс получил {damage} урона. Осталось HP: {self.hp}")
        if self.hp <= 0:
            self.death()

    def death(self):
        self.is_alive = False
        print("Босс умер!")