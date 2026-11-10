from pico2d import load_image

import game_framework

# 월드 스케일 : 배경 눈금자(ruler.png) 100 px = 3 m  →  10 px = 30 cm
PIXEL_PER_METER = (10.0 / 0.3)

# 시트 격자가 균일하지 않아(가로 182 px 간격, 세로 줄 간격 제각각)
# 투명하지 않은 픽셀의 연결 영역 14개를 찾아 프레임마다 정확한 사각형을 측정했다.
# 날갯짓해도 모양이 변하지 않는 눈동자 중심을 기준점으로 함께 측정했다.
# (left, bottom, width, height, eye_x, eye_y)
#   left/bottom : pico2d 좌표계 (이미지 왼쪽 아래가 원점)
#   eye_x/eye_y : 잘라낸 사각형의 왼쪽 아래 기준 눈동자 중심
FRAMES = (
    ( 34, 362, 146, 143,  89.2, 50.7),  # 0
    (216, 363, 146, 141,  89.2, 50.5),  # 1
    (398, 364, 146, 130,  89.6, 51.4),  # 2
    (555, 367, 171, 122, 114.6, 51.4),  # 3
    (728, 370, 182,  88, 123.6, 51.4),  # 4
    ( 34, 171, 146, 118,  89.2, 80.7),  # 5
    (216, 166, 146, 124,  89.6, 87.4),  # 6
    (398, 170, 146, 120,  89.2, 82.5),  # 7
    (580, 180, 146, 109,  89.6, 72.4),  # 8
    (762, 177, 146, 110,  89.6, 73.4),  # 9
    ( 34,   6, 146, 108,  89.6, 71.4),  # 10
    (216,   6, 146, 106,  89.2, 68.5),  # 11
    (376,  23, 168,  88, 111.2, 50.5),  # 12
    (546,  22, 180, 114, 123.2, 50.7),  # 13
)
FRAMES_PER_FLAP = len(FRAMES)

# 스프라이트 몸통(꼬리 끝 ~ 부리 끝) 길이와 눈 위치 (px)
SPRITE_BODY_LENGTH_PX = 146
SPRITE_EYE_TO_BODY_CENTER_PX = 89.4 - SPRITE_BODY_LENGTH_PX / 2  # 눈은 몸통 중심보다 16.4 px 앞

# 새 몸길이 1.0 m → 화면에서 약 33 px
BIRD_BODY_LENGTH_M = 1.0
BIRD_BODY_LENGTH_PX = BIRD_BODY_LENGTH_M * PIXEL_PER_METER
BIRD_SCALE = BIRD_BODY_LENGTH_PX / SPRITE_BODY_LENGTH_PX

# 날갯짓 초당 3 회, 1 회 = 14 프레임 → 초당 42 프레임 진행
FLAPS_PER_SECOND = 3.0
FRAMES_PER_SECOND = FLAPS_PER_SECOND * FRAMES_PER_FLAP


class Bird:
    image = None

    def __init__(self):
        if Bird.image is None:
            Bird.image = load_image('bird_animation.png')
        self.x, self.y = 800, 400
        self.frame = 0

    def update(self):
        self.frame = (self.frame + FRAMES_PER_SECOND * game_framework.frame_time) % FRAMES_PER_FLAP

    def draw(self):
        left, bottom, w, h, eye_x, eye_y = FRAMES[int(self.frame)]
        draw_w, draw_h = w * BIRD_SCALE, h * BIRD_SCALE

        # (self.x, self.y) 는 몸통 중심. 눈을 기준으로 잘라낸 사각형의 중심 위치를 보정한다.
        offset_x = (w / 2 - eye_x + SPRITE_EYE_TO_BODY_CENTER_PX) * BIRD_SCALE
        offset_y = (h / 2 - eye_y) * BIRD_SCALE

        Bird.image.clip_draw(left, bottom, w, h,
                             self.x + offset_x, self.y + offset_y, draw_w, draw_h)
