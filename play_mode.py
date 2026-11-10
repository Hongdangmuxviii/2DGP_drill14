from pico2d import *
import game_world
import game_framework
from grass import Grass
from bird import Bird


def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()


def init():
    grass = Grass()
    game_world.add_object(grass, 0)

    bird = Bird()
    game_world.add_object(bird, 1)


def pause():
    pass


def resume():
    pass


def finish():
    game_world.clear()


def update():
    game_world.update()


def render():
    clear_canvas()
    game_world.render()
    update_canvas()
