import arcade


class Weapon:
    def __init__(self, name, damage, attack_duration_frames=3):
        self.name = name
        self.damage = damage
        self.attack_duration_frames = attack_duration_frames
        self.attack_frames_right = []
        self.attack_frames_left = []

    def load_attack_animations(self, base_path, frame_count):
        """Загружает анимацию атаки по шаблону: base_path/attack1.png, attack2.png и т.д."""
        for i in range(1, frame_count + 1):
            path = f"{base_path}/attack_sword{i}.png"
            tex_right = arcade.load_texture(path)
            tex_left = tex_right.flip_left_right()
            self.attack_frames_right.append(tex_right)
            self.attack_frames_left.append(tex_left)

    @classmethod
    def create_sword(cls):
        weapon = cls(name="sword", damage=50, attack_duration_frames=3)
        weapon.load_attack_animations("models/hero/death_knight/animations/attack_sword", 3)
        return weapon
