import random

from pico2d import load_image, get_canvas_width

import game_framework


# ---------------------------------------------------------------------------
# 월드 스케일 : 배경의 거리 눈금자(ruler.png)를 기준으로 한다.
#   ruler.png 눈금 100 px = 3 m  →  10 px = 30 cm
# ---------------------------------------------------------------------------
PIXEL_PER_METER = (10.0 / 0.3)

# ---------------------------------------------------------------------------
# 스프라이트 시트 분석 결과 (bird_animation.png, 918 x 506)
#
#   시트는 5 x 3 칸처럼 보이지만 줄 간격이 균일하지 않다.
#   (가로 간격은 182 px 로 일정, 세로 줄 높이는 제각각)
#   918/5, 506/3 으로 나눠 자르면 날개가 잘리거나 옆 프레임이 섞여 들어오고,
#   프레임마다 몸통 위치가 달라져 새가 위아래로 떨린다.
#
#   그래서 투명하지 않은 픽셀의 연결 영역 14개를 찾아 프레임마다
#   정확한 사각형(left, bottom, width, height)을 구하고,
#   몸통에서 가장 흔들림 없는 '눈동자 중심'을 기준점으로 측정했다.
#
#   (left, bottom, width, height, eye_x, eye_y)
#     left/bottom : pico2d 좌표계 (이미지 왼쪽 아래가 원점)
#     eye_x/eye_y : 잘라낸 사각형의 왼쪽 아래 기준 눈동자 중심 좌표
#
#   순서 : 0~4 날개를 위로 든 뒤 뒤로 젖힘 → 5~11 날개를 아래로 내려침
#          → 12~13 날개를 다시 들어 올림 → 0 으로 이어지는 한 번의 날갯짓
# ---------------------------------------------------------------------------
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
FRAMES_PER_FLAP = len(FRAMES)  # 날갯짓 1회 = 14 프레임

# 날개를 접은 몸통(꼬리 끝 ~ 부리 끝) 길이와 그 중심 (스프라이트 픽셀)
SPRITE_BODY_LENGTH_PX = 146
SPRITE_EYE_TO_BODY_CENTER_PX = 89.4 - SPRITE_BODY_LENGTH_PX / 2  # 눈은 몸통 중심보다 16.4 px 앞

# ---------------------------------------------------------------------------
# 새 크기
#   실제 홍관조(약 22 cm)로 그리면 7 px 밖에 안 돼 형태를 알아볼 수 없다.
#   1600 x 600 화면에서 날갯짓 모양까지 구분되도록
#   몸길이 1.0 m (= 33 px, 눈금자 3 m 칸의 1/3) 의 큰 새로 설정했다.
#   날개를 편 프레임은 최대 약 42 px, 한 마리가 화면 폭의 약 2% 라
#   10 마리가 날아도 화면을 가리지 않는다. (왜가리·독수리 급 실제 크기)
# ---------------------------------------------------------------------------
BIRD_BODY_LENGTH_M = 1.0
BIRD_BODY_LENGTH_PX = BIRD_BODY_LENGTH_M * PIXEL_PER_METER
BIRD_SCALE = BIRD_BODY_LENGTH_PX / SPRITE_BODY_LENGTH_PX

# ---------------------------------------------------------------------------
# 비행 속도 : 평균 25 km/h (새마다 20 ~ 30 km/h)
#   25 km/h = 6.94 m/s = 231 px/s → 1600 px 화면을 약 7 초에 가로지른다.
#   실제 큰 새(30 ~ 50 km/h)보다 느리게 잡아, 화면 안에서 날갯짓을 충분히 볼 수 있게 했다.
#   (50 km/h 면 3.5 초 만에 지나가고 60 FPS 에서 한 프레임에 7.7 px 씩 건너뛴다)
#   날갯짓 1 회(초당 약 3 회)에 약 2.3 m, 몸길이의 2.3 배를 나아간다.
#   새마다 ±20% 차이를 둬 떼가 줄 맞춰 움직이지 않게 한다.
# ---------------------------------------------------------------------------
FLY_SPEED_KMPH_MIN = 20.0
FLY_SPEED_KMPH_MAX = 30.0


def kmph_to_pps(kmph):
    mpm = kmph * 1000.0 / 60.0
    mps = mpm / 60.0
    return mps * PIXEL_PER_METER


# ---------------------------------------------------------------------------
# 날갯짓 속도 : 몸집이 클수록 날갯짓이 느리다. 몸길이 1 m 급 새는 초당 약 2 ~ 4 회
#   1 회 = 14 프레임 → 초당 42 프레임을 진행시켜야 한다.
#   새마다 2.7 ~ 3.3 회로 조금씩 달리 해서 떼 전체가 똑같이 퍼덕이지 않게 한다.
# ---------------------------------------------------------------------------
FLAPS_PER_SECOND_MIN = 2.7
FLAPS_PER_SECOND_MAX = 3.3

# 비행 고도 (지면 기준, m) : 잔디 위 ~ 화면 위쪽
GROUND_Y = 40
FLY_ALTITUDE_M_MIN = 3.0
FLY_ALTITUDE_M_MAX = 15.5


class Bird:
    image = None

    def __init__(self):
        if Bird.image is None:
            Bird.image = load_image('bird_animation.png')

        half = BIRD_BODY_LENGTH_PX / 2
        self.x = random.uniform(half, get_canvas_width() - half)
        self.y = GROUND_Y + random.uniform(FLY_ALTITUDE_M_MIN, FLY_ALTITUDE_M_MAX) * PIXEL_PER_METER
        self.dir = random.choice((-1, 1))

        self.speed_pps = kmph_to_pps(random.uniform(FLY_SPEED_KMPH_MIN, FLY_SPEED_KMPH_MAX))
        self.frames_per_second = random.uniform(FLAPS_PER_SECOND_MIN, FLAPS_PER_SECOND_MAX) * FRAMES_PER_FLAP
        self.frame = random.uniform(0, FRAMES_PER_FLAP)

    def update(self):
        dt = game_framework.frame_time

        self.frame = (self.frame + self.frames_per_second * dt) % FRAMES_PER_FLAP

        self.x += self.dir * self.speed_pps * dt
        half = BIRD_BODY_LENGTH_PX / 2
        if self.x > get_canvas_width() - half:
            self.x = get_canvas_width() - half
            self.dir = -1
        elif self.x < half:
            self.x = half
            self.dir = 1

    def draw(self):
        left, bottom, w, h, eye_x, eye_y = FRAMES[int(self.frame)]
        draw_w, draw_h = w * BIRD_SCALE, h * BIRD_SCALE

        # (self.x, self.y) 는 몸통 중심. 눈은 진행 방향으로 16.4 px 앞에 있다.
        # 눈을 기준으로 잘라낸 사각형의 중심이 어디에 와야 하는지 계산한다.
        offset_x = (w / 2 - eye_x + SPRITE_EYE_TO_BODY_CENTER_PX) * BIRD_SCALE
        offset_y = (h / 2 - eye_y) * BIRD_SCALE

        if self.dir == 1:
            Bird.image.clip_draw(left, bottom, w, h,
                                 self.x + offset_x, self.y + offset_y, draw_w, draw_h)
        else:
            Bird.image.clip_composite_draw(left, bottom, w, h, 0, 'h',
                                           self.x - offset_x, self.y + offset_y, draw_w, draw_h)
