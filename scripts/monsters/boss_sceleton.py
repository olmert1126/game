import arcade

class Skeleton:
    def __init__(self, x, y, collision_sprites, players, gravity=0.5, damage=30, attack_range=4000, attack_cooldown=2.0):
        self.loading_texture()
        self.skeleton_sprites_list = arcade.SpriteList()
        self.arrow_list = arcade.SpriteList()

        self.speed = 2
        self.facing = "right"
        self.hp = 100
        self.max_hp = self.hp
        self.is_alive = True

        self.gravity = gravity
        self.players = players
        self.damage = damage
        self.attack_range = attack_range
        self.attack_cooldown = attack_cooldown
        self._last_attack_time = 0.0
        self.is_attacking = False

        self.center_x = x
        self.center_y = y

        self.skeleton_sprite = arcade.Sprite()
        self.skeleton_sprite.texture = self.main_form
        self.skeleton_sprite.center_x = self.center_x
        self.skeleton_sprite.center_y = self.center_y
        self.skeleton_sprite.scale = 0.15

        self.skeleton_sprites_list.append(self.skeleton_sprite)

        self.collision_sprites = collision_sprites

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.skeleton_sprite,
            collision_sprites,
            gravity_constant=self.gravity,
        )

        # === АНИМАЦИИ ===
        # Бег
        self.anim_run_right = [
            self.one_shot_run,
            self.two_shot_run,
            self.three_shot_run,
            self.four_shot_run
        ]
        self.anim_run_left = [
            self.one_shot_run_left,
            self.two_shot_run_left,
            self.three_shot_run_left,
            self.four_shot_run_left
        ]

        # Атака
        self.anim_attack_right = [
            self.one_shot_attack,
            self.two_shot_attack,
            self.three_shot_attack,
            self.four_shot_attack
        ]
        self.anim_attack_left = [
            self.one_shot_attack_left,
            self.two_shot_attack_left,
            self.three_shot_attack_left,
            self.four_shot_attack_left
        ]

        # Индексы и таймеры
        self.current_texture_run = 0
        self.texture_change_time_run = 0
        self.texture_change_delay_run = 0.2

    def loading_texture(self):
        # Основная форма
        self.main_form = arcade.load_texture("models/monsters/boss_skeleton/skeleton_boss_right.png")
        self.main_form_left = self.main_form.flip_left_right()

        # Бег
        self.one_shot_run = arcade.load_texture("models/monsters/boss_skeleton/animations/run/run1.png")
        self.two_shot_run = arcade.load_texture("models/monsters/boss_skeleton/animations/run/run2.png")


        self.one_shot_run_left = self.one_shot_run.flip_left_right()
        self.two_shot_run_left = self.two_shot_run.flip_left_right()

        # Атака
        self.one_shot_attack = arcade.load_texture("models/monsters/boss_skeleton/animations/attack/attack1.png")

        self.one_shot_attack_left = self.one_shot_attack.flip_left_right()

        # Стрела
        self.arrow_texture = arcade.load_texture("models/monsters/skeleton/arrow.png")
        self.arrow_texture_left = self.arrow_texture.flip_left_right()

    def _reverse_direction(self):
        self.facing = "left" if self.facing == "right" else "right"
        self.current_texture_run = 0

    def _shoot_arrow(self, target_player):
        arrow = arcade.Sprite()
        arrow.center_x = self.skeleton_sprite.center_x
        arrow.center_y = self.skeleton_sprite.center_y + 10

        dx = target_player.player_sprite.center_x - arrow.center_x
        dy = target_player.player_sprite.center_y - arrow.center_y
        distance = (dx**2 + dy**2) ** 0.5
        if distance == 0:
            return

        norm_dx = dx / distance
        norm_dy = dy / distance

        arrow.change_x = norm_dx * 8
        arrow.change_y = norm_dy * 8

        angle = arcade.math.get_angle_degrees(arrow.center_x, arrow.center_y, target_player.player_sprite.center_x, target_player.player_sprite.center_y)
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
        # Физика и стрелы
        self.physics_engine.update()

        for arrow in self.arrow_list:
            arrow.update()
            if arcade.check_for_collision_with_list(arrow, self.collision_sprites):
                arrow.remove_from_sprite_lists()
            if (abs(arrow.center_x - self.skeleton_sprite.center_x) > 5000 or
                abs(arrow.center_y - self.skeleton_sprite.center_y) > 5000):
                arrow.remove_from_sprite_lists()

            for player in self.players:
                if not player.is_alive:
                    continue
                if arcade.check_for_collision(arrow, player.player_sprite):
                    player.take_damage(self.damage)
                    arrow.remove_from_sprite_lists()
                    break

        # === ПОИСК ИГРОКА ===
        target_player = None
        for player in self.players:
            if not player.is_alive:
                continue
            distance = arcade.get_distance_between_sprites(self.skeleton_sprite, player.player_sprite)
            if distance <= self.attack_range:
                target_player = player
                break

        if target_player is not None:
            self.is_attacking = True
            self._last_attack_time += delta_time
            if self._last_attack_time >= self.attack_cooldown:
                self._shoot_arrow(target_player)
                self._last_attack_time = 0.0

            # Поворот к игроку
            if target_player.player_sprite.center_x > self.skeleton_sprite.center_x:
                self.facing = "right"
            else:
                self.facing = "left"
        else:
            self.is_attacking = False
            direction = 1 if self.facing == "right" else -1
            next_x = self.skeleton_sprite.center_x + self.speed * direction

            test_front = arcade.Sprite(center_x=next_x, center_y=self.skeleton_sprite.center_y)
            test_front.texture = self.main_form
            test_front.scale = self.skeleton_sprite.scale
            front_collisions = arcade.check_for_collision_with_list(test_front, self.collision_sprites)

            if front_collisions:
                self._reverse_direction()
            else:
                self.skeleton_sprite.center_x = next_x

        # Обновляем анимацию (ходьба или атака)
        self.update_animation(delta_time)

    def update_animation(self, delta_time: float = 1 / 60):
        self.texture_change_time_run += delta_time
        if self.texture_change_time_run >= self.texture_change_delay_run:
            self.texture_change_time_run = 0

            if self.is_attacking:
                # Анимация атаки
                self.current_texture_run = (self.current_texture_run + 1) % len(self.anim_attack_right)
                if self.facing == "right":
                    self.skeleton_sprite.texture = self.anim_attack_right[self.current_texture_run]
                else:
                    self.skeleton_sprite.texture = self.anim_attack_left[self.current_texture_run]
            else:
                # Анимация бега
                self.current_texture_run = (self.current_texture_run + 1) % len(self.anim_run_right)
                if self.facing == "right":
                    self.skeleton_sprite.texture = self.anim_run_right[self.current_texture_run]
                else:
                    self.skeleton_sprite.texture = self.anim_run_left[self.current_texture_run]

    def draw(self):
        self.skeleton_sprites_list.draw()
        self.arrow_list.draw()

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
