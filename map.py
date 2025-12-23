import arcade
from arcade.examples.camera_platform import GRAVITY

import hero_death_knight

SCREEN_WIDTH = arcade.get_display_size()[0]
SCREEN_HEIGHT = arcade.get_display_size()[1]
PLAYER_SIZE = 0.1
PLAYER_SPEED = 200
GRAVITY = 7
JUMP_SPEED = 25
COYOTE_TIME = 0.08 # плавность камеры

class Map(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, fullscreen=False)

        self.walls = arcade.SpriteList()
        self.platform = arcade.SpriteList()


    def setup(self):
        test_map = arcade.load_tilemap("models/map/test_map/карта.tmx", scaling=1.2)
        self.all_colosion_sprites = arcade.SpriteList()
        self.walls = test_map.sprite_lists["walls"]
        self.platform = test_map.sprite_lists["platforms"]
        self.all_colosion_sprites.extend(self.walls)
        self.all_colosion_sprites.extend(self.platform)

        all_sprites = arcade.SpriteList()
        all_sprites.extend(self.walls)
        all_sprites.extend(self.platform)

        self.player1 = hero_death_knight.DeathKnight(SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT / 2, PLAYER_SPEED,
                                                     PLAYER_SIZE, 1, self.all_colosion_sprites, JUMP_SPEED, GRAVITY, COYOTE_TIME)

        if len(all_sprites) > 0:
            left = min(sprite.left for sprite in all_sprites)
            right = max(sprite.right for sprite in all_sprites)
            bottom = min(sprite.bottom for sprite in all_sprites)
            top = max(sprite.top for sprite in all_sprites)

            map_center_x = (left + right) / 2
            map_center_y = (bottom + top) / 2

            dx = SCREEN_WIDTH / 2 - map_center_x #контроль нахождения карты
            dy = SCREEN_HEIGHT / 2 - map_center_y

            for sprite in all_sprites:
                sprite.center_x += dx
                sprite.center_y += dy

        self.physics_engine_player1 = self.player1.physicks_engine


    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)
        self.player1.draw()
        self.walls.draw()
        self.platform.draw()

    def on_update(self, delta_time):
        self.player1.on_update(delta_time)
        self.player1.change_y -= GRAVITY
        self.physics_engine_player1.update()

    def on_key_press(self, key, modifiers):
        self.player1.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        self.player1.on_key_release(key, modifiers)

def setup_game(width=800, height=600, title="Тест карта"):
    game = Map(width, height, title)
    game.setup()
    return game


def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT)
    arcade.run()


if __name__ == "__main__":
    main()
