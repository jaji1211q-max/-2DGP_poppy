from pico2d import (
    SDL_KEYDOWN,
    SDL_QUIT,
    SDLK_ESCAPE,
    clear_canvas,
    close_canvas,
    delay,
    get_events,
    get_time,
    open_canvas,
    update_canvas,
)

from poppy import CANVAS_HEIGHT, CANVAS_WIDTH, Poppy


FRAMES_PER_SECOND = 60
FRAME_DURATION = 1.0 / FRAMES_PER_SECOND


def main():
    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        poppy = Poppy()
        running = True
        previous_frame_time = get_time()

        while running:
            frame_start_time = get_time()

            for event in get_events():
                if event.type == SDL_QUIT:
                    running = False
                    break
                if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
                    running = False
                    break
                poppy.handle_event(event)

            if not running:
                break

            current_time = get_time()
            poppy.update(current_time - previous_frame_time)
            previous_frame_time = current_time

            clear_canvas()
            poppy.draw()
            update_canvas()

            frame_time = get_time() - frame_start_time
            delay(max(0.0, FRAME_DURATION - frame_time))
    finally:
        close_canvas()


if __name__ == "__main__":
    main()
