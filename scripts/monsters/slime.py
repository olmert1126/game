import arcade

class Slime:
    def __init__(self, x, y, collision_sprites, players, gravity=0.5, damage=45, damage_cooldown=1.0):
        self.loading_texture()
        self.slime_sprites_list = arcade.SpriteList()

        self.speed = 3
        self.facing = "right"
        self.hp = 100
        self.max_hp = self.hp
        self.is_alive = True

        self.gravity = gravity
        self.players = players  # список игроков
        self.damage = damage
        self.damage_cooldown = damage_cooldown
        self._last_damage_times = [0.0] * len(players)

        self.center_x = x
        self.center_y = y
        self.change_x = self.speed
        self.change_y = 0
        self.on_ground = False

        self.anim_run_right = []
        self.anim_run_left = []
        self.current_texture_run = 0
        self.texture_change_time_run = 0
        self.texture_change_delay_run = 0.2
        self.run = True

        self.anim_attack_right = [self.one_shot_attack, self.two_shot_attack]
        self.anim_attack_left = [self.one_shot_attack_left, self.two_shot_attack_left]

        self.is_attacking = False
        self.attack_duration = 0.4  # общая длительность анимации атаки
        self.attack_timer = 0.0
        self.current_texture_attack = 0
        self.texture_change_time_attack = 0
        self.texture_change_delay_attack = self.attack_duration / len(self.anim_attack_right)

        self.slime_sprite = arcade.Sprite()
        self.slime_sprite.texture = self.main_form
        self.slime_sprite.center_x = self.center_x
        self.slime_sprite.center_y = self.center_y
        self.slime_sprite.scale = 0.12

        self.slime_sprites_list.append(self.slime_sprite)

        self.collision_sprites = collision_sprites

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.slime_sprite,
            collision_sprites,
            gravity_constant=self.gravity,
        )

        # Анимации
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

    def loading_texture(self):
        self.main_form = arcade.load_texture("models/monsters/slime/slime_main_form.png")
        self.main_form_left = self.main_form.flip_left_right()

        self.one_shot_run = arcade.load_texture("models/monsters/slime/animations/run/run1.png")
        self.two_shot_run = arcade.load_texture("models/monsters/slime/animations/run/run2.png")
        self.three_shot_run = arcade.load_texture("models/monsters/slime/animations/run/run3.png")
        self.four_shot_run = arcade.load_texture("models/monsters/slime/animations/run/run4.png")
        self.one_shot_run_left = self.one_shot_run.flip_left_right()
        self.two_shot_run_left = self.two_shot_run.flip_left_right()
        self.three_shot_run_left = self.three_shot_run.flip_left_right()
        self.four_shot_run_left = self.four_shot_run.flip_left_right()

        self.one_shot_attack = arcade.load_texture("models/monsters/slime/animations/take_damage/anim_attack1.png")
        self.two_shot_attack = arcade.load_texture("models/monsters/slime/animations/take_damage/anim_attack2.png")
        self.one_shot_attack_left = self.one_shot_attack.flip_left_right()
        self.two_shot_attack_left = self.two_shot_attack.flip_left_right()

    def on_update(self, delta_time):
        if not self.is_alive:
            return
        # Обновляем физику
        self.physics_engine.update()
        direction = 1 if self.facing == "right" else -1
        next_x = self.slime_sprite.center_x + self.speed * direction

        test_front = arcade.Sprite(center_x=next_x, center_y=self.slime_sprite.center_y)
        test_front.texture = self.main_form
        test_front.scale = self.slime_sprite.scale
        front_collisions = arcade.check_for_collision_with_list(test_front, self.collision_sprites)

        if front_collisions:
            self._reverse_direction()
        else:
            self.slime_sprite.center_x = next_x

        self.update_animation(delta_time)

        # === НАНЕСЕНИЕ УРОНА ИГРОКАМ ===
        for i, player in enumerate(self.players):
            if not player.is_alive:
                continue

            if arcade.check_for_collision(self.slime_sprite, player.player_sprite):
                if not self.is_attacking:
                    self.is_attacking = True
                    self.attack_timer = 0.0
                    self.current_texture_attack = 0

                self._last_damage_times[i] += delta_time
                if self._last_damage_times[i] >= self.damage_cooldown:
                    player.take_damage(self.damage)
                    self._last_damage_times[i] = 0.0

    def _reverse_direction(self):
        self.facing = "left" if self.facing == "right" else "right"
        self.current_texture_run = 0

    def update_animation(self, delta_time: float):
        if self.is_attacking:
            self.attack_timer += delta_time
            self.texture_change_time_attack += delta_time

            if self.texture_change_time_attack >= self.texture_change_delay_attack:
                self.texture_change_time_attack = 0
                self.current_texture_attack = (self.current_texture_attack + 1) % len(self.anim_attack_right)

                if self.facing == "right":
                    self.slime_sprite.texture = self.anim_attack_right[self.current_texture_attack]
                else:
                    self.slime_sprite.texture = self.anim_attack_left[self.current_texture_attack]

            # Завершаем анимацию по времени
            if self.attack_timer >= self.attack_duration:
                self.is_attacking = False
                self.current_texture_run = 0  # сброс индекса бега

        else:
            # Обычная анимация бега
            self.texture_change_time_run += delta_time
            if self.texture_change_time_run >= self.texture_change_delay_run:
                self.texture_change_time_run = 0
                self.current_texture_run = (self.current_texture_run + 1) % len(self.anim_run_right)

                if self.facing == "right":
                    self.slime_sprite.texture = self.anim_run_right[self.current_texture_run]
                else:
                    self.slime_sprite.texture = self.anim_run_left[self.current_texture_run]

    def draw(self):
        self.slime_sprites_list.draw()

    def take_damage(self, damage):
        if not self.is_alive:
            return
        self.hp -= damage
        print(f"Slime получил {damage} урона. Осталось HP: {self.hp}")
        if self.hp <= 0:
            self.death()

    def death(self):
        self.is_alive = False
        print("Slime умер!")
