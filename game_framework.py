import time
running = False
stack = []
frame_time = 0.0


def change_mode(mode):
    if stack:
        stack.pop().finish()
    stack.append(mode)
    mode.init()


def push_mode(mode):
    if stack:
        stack[-1].pause()
    stack.append(mode)
    mode.init()


def pop_mode():
    if stack:
        stack.pop().finish()
    if stack:
        stack[-1].resume()
    else:
        quit()


def quit():
    global running
    running = False


def run(start_mode):
    global running, stack, frame_time
    running = True
    stack = [start_mode]
    try:
        start_mode.init()

        frame_time = 0.0
        current_time = time.time()
        while running:
            stack[-1].handle_events()
            stack[-1].update()
            stack[-1].render()

            frame_time = time.time() - current_time
            frame_rate = 1.0 / frame_time if frame_time > 0 else 0.0
            current_time += frame_time
            print(f'Frame Time: {frame_time:.6f} sec, Frame Rate: {frame_rate:.6f} fps')
    finally:
        while stack:
            stack.pop().finish()
        running = False
