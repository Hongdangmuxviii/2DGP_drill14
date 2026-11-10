from pico2d import load_image

# 월드 스케일 : 배경 눈금자(ruler.png) 100 px = 3 m  →  10 px = 30 cm
PIXEL_PER_METER = (10.0 / 0.3)

# 스프라이트 몸통(꼬리 끝 ~ 부리 끝) 길이 (px)
SPRITE_BODY_LENGTH_PX = 146

# 새 몸길이 1.0 m → 화면에서 약 33 px
BIRD_BODY_LENGTH_M = 1.0
BIRD_BODY_LENGTH_PX = BIRD_BODY_LENGTH_M * PIXEL_PER_METER
BIRD_SCALE = BIRD_BODY_LENGTH_PX / SPRITE_BODY_LENGTH_PX

# 시트를 5 x 3 균일 격자로 보고 자른다 (마지막 줄은 4칸 → 총 14 프레임)
SHEET_W, SHEET_H = 918, 506
CELL_W, CELL_H = SHEET_W / 5, SHEET_H / 3
FRAMES_PER_FLAP = 14


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
        col, row = self.frame % 5, self.frame // 5
        left = int(col * CELL_W)
        bottom = int(SHEET_H - (row + 1) * CELL_H)
        Bird.image.clip_draw(left, bottom, int(CELL_W), int(CELL_H),
                             self.x, self.y, CELL_W * BIRD_SCALE, CELL_H * BIRD_SCALE)
