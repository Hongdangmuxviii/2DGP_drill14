from pico2d import load_image

# 월드 스케일 : 배경 눈금자(ruler.png) 100 px = 3 m  →  10 px = 30 cm
PIXEL_PER_METER = (10.0 / 0.3)

# 스프라이트 몸통(꼬리 끝 ~ 부리 끝) 길이 (px)
SPRITE_BODY_LENGTH_PX = 146

# 새 몸길이 1.0 m → 화면에서 약 33 px
BIRD_BODY_LENGTH_M = 1.0
BIRD_BODY_LENGTH_PX = BIRD_BODY_LENGTH_M * PIXEL_PER_METER
BIRD_SCALE = BIRD_BODY_LENGTH_PX / SPRITE_BODY_LENGTH_PX


class Bird:
    image = None

    def __init__(self):
        if Bird.image is None:
            Bird.image = load_image('bird_animation.png')
        self.x, self.y = 800, 400
        self.frame = 0

    def update(self):
        pass

    def draw(self):
        pass
