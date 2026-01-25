import arcade

class Boss_skeleton:
    def __init__(self, x, y, collision_sprites, players, gravity=0.5, damage=30, attack_range=4000, attack_cooldown=2.0):
        self.loading_texture()
        self.skeleton_boss_sprites_list = arcade.SpriteList()
        self.projectiles = arcade.SpriteList()

        self.speed = 2
        self.facing = "right"
        self.hp = 1000
        self.max_hp = self.hp
        self.is_alive = True

        # Таймеры
        self.summon_cooldown = 20.0
        self._last_summon_time = 0.0
        self.should_summon = False

        self.slime_attack_cooldown = 2.0
        self._last_slime_attack_time = 0.0

        # Параметры боя
        self.gravity = gravity
        self.players = players
        self.damage = damage
        self.attack_range = attack_range
        self.attack_cooldown = attack_cooldown
        self._last_arrow_attack_time = 0.0
        self.is_attacking = False

        self.center_x = x
        self.center_y = y

        self.skeleton_boss_sprite = arcade.Sprite(self.main_form, scale=0.15)
        self.skeleton_boss_sprite.center_x = self.center_x
        self.skeleton_boss_sprite.center_y = self.center_y

        # Защита от нулевых размеров
        if self.skeleton_boss_sprite.width == 0 or self.skeleton_boss_sprite.height == 0:
            self.skeleton_boss_sprite.width = 100
            self.skeleton_boss_sprite.height = 100

        self.skeleton_boss_sprites_list.append(self.skeleton_boss_sprite)
        self.collision_sprites = collision_sprites

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.skeleton_boss_sprite,
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
        self.slime_ball_texture = arcade.load_texture("models/monsters/slime/slime_main_form.png")

    def _reverse_direction(self):
        self.facing = "left" if self.facing == "right" else "right"
        self.current_texture_run = 0

    def _shoot_arrow(self, target_player):
        arrow = arcade.Sprite(self.arrow_texture, scale=0.1)
        arrow.center_x = self.skeleton_boss_sprite.center_x
        arrow.center_y = self.skeleton_boss_sprite.center_y + 10

        dx = target_player.player_sprite.center_x - arrow.center_x
        dy = target_player.player_sprite.center_y - arrow.center_y
        distance = (dx ** 2 + dy ** 2) ** 0.5
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
        arrow.damage = self.damage
        self.projectiles.append(arrow)

    def _shoot_slime_ball(self, target_player):
        slime_ball = arcade.Sprite(self.slime_ball_texture, scale=0.1)
        slime_ball.center_x = self.skeleton_boss_sprite.center_x
        slime_ball.center_y = self.skeleton_boss_sprite.center_y + 10

        dx = target_player.player_sprite.center_x - slime_ball.center_x
        dy = target_player.player_sprite.center_y - slime_ball.center_y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance == 0:
            return

        norm_dx = dx / distance
        norm_dy = dy / distance
        slime_ball.change_x = norm_dx * 6
        slime_ball.change_y = norm_dy * 6

        angle = arcade.math.get_angle_degrees(
            slime_ball.center_x, slime_ball.center_y,
            target_player.player_sprite.center_x,
            target_player.player_sprite.center_y
        )
        slime_ball.angle = angle
        slime_ball.damage = 40
        slime_ball.is_slime_projectile = True  # ← флаг для GameView
        self.projectiles.append(slime_ball)

    def on_update(self, delta_time):
        if not self.is_alive:
            return

        self.physics_engine.update()

        for proj in self.projectiles[:]:
            proj.update()
            # Удаляем, если улетел слишком далеко
            if (abs(proj.center_x - self.skeleton_boss_sprite.center_x) > 5000 or
                abs(proj.center_y - self.skeleton_boss_sprite.center_y) > 5000):
                proj.remove_from_sprite_lists()

        # Выбор цели
        target_player = None
        for player in self.players:
            if not player.is_alive:
                continue
            distance = arcade.get_distance_between_sprites(self.skeleton_boss_sprite, player.player_sprite)
            if distance <= self.attack_range:
                target_player = player
                break

        current_hp_ratio = self.hp / self.max_hp

        if target_player is not None:
            self.is_attacking = True
            self.facing = "right" if target_player.player_sprite.center_x > self.skeleton_boss_sprite.center_x else "left"

            if current_hp_ratio > 0.5:
                # Фаза 1: стрельба стрелами
                self._last_arrow_attack_time += delta_time
                if self._last_arrow_attack_time >= self.attack_cooldown:
                    self._shoot_arrow(target_player)
                    self._last_arrow_attack_time = 0.0
            else:
                # Фаза 2: стрельба слаймами
                self._last_slime_attack_time += delta_time
                if self._last_slime_attack_time >= self.slime_attack_cooldown:
                    self._shoot_slime_ball(target_player)
                    self._last_slime_attack_time = 0.0
        else:
            self.is_attacking = False
            # Движение вперёд/назад
            direction = 1 if self.facing == "right" else -1
            next_x = self.skeleton_boss_sprite.center_x + self.speed * direction

            half_width = self.skeleton_boss_sprite.width / 2
            half_height = self.skeleton_boss_sprite.height / 2
            future_left = next_x - half_width
            future_right = next_x + half_width
            future_bottom = self.skeleton_boss_sprite.center_y - half_height
            future_top = self.skeleton_boss_sprite.center_y + half_height

            blocked = False
            for wall in self.collision_sprites:
                if (future_left < wall.right and future_right > wall.left and
                    future_bottom < wall.top and future_top > wall.bottom):
                    blocked = True
                    break

            if blocked:
                self._reverse_direction()
            else:
                self.skeleton_boss_sprite.center_x = next_x

        # Призыв скелетов — только в фазе 1
        if current_hp_ratio > 0.5:
            self._last_summon_time += delta_time
            if self._last_summon_time >= self.summon_cooldown:
                self.should_summon = True
                self._last_summon_time = 0.0
        else:
            self.should_summon = False

        self.update_animation(delta_time)

    def update_animation(self, delta_time: float = 1 / 60):
        self.texture_change_time_run += delta_time
        if self.texture_change_time_run >= self.texture_change_delay_run:
            self.texture_change_time_run = 0
            if self.is_attacking:
                self.current_texture_run = (self.current_texture_run + 1) % len(self.anim_attack_right)
                tex_list = self.anim_attack_right if self.facing == "right" else self.anim_attack_left
            else:
                self.current_texture_run = (self.current_texture_run + 1) % len(self.anim_run_right)
                tex_list = self.anim_run_right if self.facing == "right" else self.anim_run_left
            self.skeleton_boss_sprite.texture = tex_list[self.current_texture_run]

    def draw(self):
        self.skeleton_boss_sprites_list.draw()
        self.projectiles.draw()

    def take_damage(self, damage):
        if not self.is_alive:
            return
        self.hp -= damage
        print(f"boss получил {damage} урона. Осталось HP: {self.hp}")
        if self.hp <= 0:
            self.death()

    def death(self):
        self.is_alive = False
        print("boss умер!")