import arcade
from scripts.modes.start_view import StartView

def main():
    # Создаём ОДНО окно
    window = arcade.Window(
        width=arcade.get_display_size()[0] - 60,
        height=arcade.get_display_size()[1] - 60,
        title="Игра",
        fullscreen=False
    )

    # Показываем стартовое меню
    start_view = StartView()
    window.show_view(start_view)

    arcade.run()

if __name__ == "__main__":
    main()