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


FRAMES_PER_SECOND = 60
FRAME_DURATION = 1.0 / FRAMES_PER_SECOND


def run(game_world):
    open_canvas(*game_world.canvas_size)
    try:
        game_world.initialize()
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
                game_world.handle_event(event)

            if not running:
                break

            current_time = get_time()
            game_world.update(current_time - previous_frame_time)
            previous_frame_time = current_time

            clear_canvas()
            game_world.draw()
            update_canvas()

            frame_time = get_time() - frame_start_time
            delay(max(0.0, FRAME_DURATION - frame_time))
    finally:
        try:
            game_world.finalize()
        finally:
            close_canvas()
