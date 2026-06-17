import pygame
import streamlit as st
import numpy as np

# 스트림릿 페이지 설정
st.set_page_config(page_title="스틱맨 칼싸움", layout="centered")
st.title("🥷 2인용 스틱맨 칼싸움 게임")
st.text("주의: 웹 환경 특성상 키 입력 반응이 조금 느릴 수 있습니다.")

# Pygame을 화면 없이(가상으로) 초기화
import os
os.environ["SDL_VIDEODRIVER"] = "dummy" 

# 게임 초기화
pygame.init()

WIDTH, HEIGHT = 800, 500 # 웹 화면에 맞게 약간 축소
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 30 # 웹 환경 안정성을 위해 30fps로 조정

# [기존 Player 클래스 동일하게 유지]
class Player:
    def __init__(self, x, y, color, controls):
        self.x = x
        self.y = y
        self.color = color
        self.controls = controls
        self.width, self.height = 40, 80
        self.vel_x, self.vel_y = 7, 0
        self.is_jumping = False
        self.jump_power, self.gravity = -14, 0.8
        self.is_attacking = False
        self.attack_timer, self.attack_duration = 0, 8
        self.direction = 1
        self.hp = 100

    def handle_input(self, keys):
        if keys[self.controls['left']]: self.x -= self.vel_x; self.direction = -1
        if keys[self.controls['right']]: self.x += self.vel_x; self.direction = 1
        if keys[self.controls['jump']] and not self.is_jumping:
            self.vel_y = self.jump_power
            self.is_jumping = True
        if keys[self.controls['attack']] and not self.is_attacking and self.attack_timer == 0:
            self.is_attacking = True
            self.attack_timer = 15

    def update(self, ground_y):
        self.vel_y += self.gravity
        self.y += self.vel_y
        if self.y + self.height >= ground_y:
            self.y = ground_y - self.height
            self.vel_y = 0
            self.is_jumping = False
        if self.x < 0: self.x = 0
        if self.x + self.width > WIDTH: self.x = WIDTH - self.width
        if self.is_attacking:
            self.attack_duration -= 1
            if self.attack_duration <= 0:
                self.is_attacking = False
                self.attack_duration = 8
        if self.attack_timer > 0: self.attack_timer -= 1

    def draw(self, surface):
        head_radius = 15
        head_x, head_y = self.x + self.width // 2, self.y + head_radius
        pygame.draw.circle(surface, self.color, (head_x, head_y), head_radius, 3)
        pygame.draw.line(surface, self.color, (head_x, head_y + head_radius), (head_x, self.y + 50), 3)
        pygame.draw.line(surface, self.color, (head_x, self.y + 50), (self.x, self.y + self.height), 3)
        pygame.draw.line(surface, self.color, (head_x, self.y + 50), (self.x + self.width, self.y + self.height), 3)
        
        sword_length = 40
        hand_x, hand_y = head_x + (10 * self.direction), self.y + 35
        if self.is_attacking:
            pygame.draw.line(surface, (255, 0, 0), (hand_x, hand_y), (hand_x + (sword_length * self.direction), hand_y), 5)
        else:
            pygame.draw.line(surface, (150, 150, 150), (hand_x, hand_y), (hand_x + (30 * self.direction), hand_y - 30), 3)

    def get_attack_rect(self):
        return pygame.Rect(self.x + self.width if self.direction == 1 else self.x - 40, self.y + 20, 40, 30)
    def get_body_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# 게임 세팅 및 실행 프레임 비우기
GROUND_Y = HEIGHT - 50
p1 = Player(150, GROUND_Y - 80, (100, 100, 255), {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w, 'attack': pygame.K_f})
p2 = Player(600, GROUND_Y - 80, (255, 100, 100), {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP, 'attack': pygame.K_0})

# 스트림릿에서 이미지를 계속 갱신할 공간 생성
image_placeholder = st.empty()

# 임시 게임 루프 (스트림릿용)
for _ in range(600): # 테스트용으로 600프레임 동안 작동 (원하면 무한루프로 변경 가능)
    pygame.event.pump()
    keys = pygame.key.get_pressed()
    
    p1.handle_input(keys)
    p2.handle_input(keys)
    p1.update(GROUND_Y)
    p2.update(GROUND_Y)

    # 충돌 판정
    if p1.is_attacking and p1.attack_duration == 8:
        if p1.get_attack_rect().colliderect(p2.get_body_rect()): p2.hp -= 10; p2.x += 20
    if p2.is_attacking and p2.attack_duration == 8:
        if p2.get_attack_rect().colliderect(p1.get_body_rect()): p1.hp -= 10; p1.x -= 20

    # 그리기
    screen.fill((255, 255, 255))
    pygame.draw.line(screen, (0, 0, 0), (0, GROUND_Y), (WIDTH, GROUND_Y), 5)
    p1.draw(screen)
    p2.draw(screen)

    # 체력 표시
    pygame.draw.rect(screen, (0, 0, 255), (50, 20, max(0, p1.hp), 15))
    pygame.draw.rect(screen, (255, 0, 0), (WIDTH - 150, 20, max(0, p2.hp), 15))

    # Pygame 화면을 이미지 배열로 변환하여 스트림릿에 전달
    img_array = pygame.surfarray.array3d(screen)
    img_array = np.transpose(img_array, (1, 0, 2)) # 가로세로 축 맞추기
    image_placeholder.image(img_array, channels="RGB")

    clock.tick(FPS)
