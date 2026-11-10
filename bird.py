from pico2d import load_image

# 월드 스케일 : 배경 눈금자(ruler.png) 100 px = 3 m  →  10 px = 30 cm
PIXEL_PER_METER = (10.0 / 0.3)

# 스프라이트 몸통(꼬리 끝 ~ 부리 끝) 길이 (px)
SPRITE_BODY_LENGTH_PX = 146

# 새 몸길이 1.0 m → 화면에서 약 33 px
BIRD_BODY_LENGTH_M = 1.0
BIRD_BODY_LENGTH_PX = BIRD_BODY_LENGTH_M * PIXEL_PER_METER
BIRD_SCALE = BIRD_BODY_LENGTH_PX / SPRITE_BODY_LENGTH_PX

# 시트 격자가 균일하지 않아(가로 182 px 간격, 세로 줄 간격 제각각)
# 투명하지 않은 픽셀의 연결 영역 14개를 찾아 프레임마다 정확한 사각형을 측정했다.
# (left, bottom, width, height) - pico2d 좌표계 (이미지 왼쪽 아래가 원점)
FRAMES = (
    ( 34, 362, 146, 143),  # 0
    (216, 363, 146, 141),  # 1
    (398, 364, 146, 130),  # 2
    (555, 367, 171, 122),  # 3
    (728, 370, 182,  88),  # 4
    ( 34, 171, 146, 118),  # 5
    (216, 166, 146, 124),  # 6
    (398, 170, 146, 120),  # 7
    (580, 180, 146, 109),  # 8
    (762, 177, 146, 110),  # 9
    ( 34,   6, 146, 108),  # 10
    (216,   6, 146, 106),  # 11
    (376,  23, 168,  88),  # 12
    (546,  22, 180, 114),  # 13
)
FRAMES_PER_FLAP = len(FRAMES)


class Bird:
    image = None

    def __init__(self):
        if Bird.image is None:
            Bird.image = load_image('bird_animation.png')
        self.x, self.y = 800, 400
        self.frame = 0

    def update(self):
        self.frame = (self.frame + 1) % FRAMES_PER_FLAP

    def draw(self):
        left, bottom, w, h = FRAMES[self.frame]
        Bird.image.clip_draw(left, bottom, w, h,
                             self.x, self.y, w * BIRD_SCALE, h * BIRD_SCALE)
