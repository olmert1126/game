import arcade
from start_view import StartView

def main():
    # Создаём ОДНО окно
    window = arcade.Window(
        width=arcade.get_display_size()[0],
        height=arcade.get_display_size()[1],
        title="Игра",
        fullscreen=True
    )

    # Показываем стартовое меню
    start_view = StartView()
    window.show_view(start_view)

    arcade.run()

if __name__ == "__main__":
    main()