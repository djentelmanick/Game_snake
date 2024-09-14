import pygame
import random
import json
import pyaudio
import time
from vosk import Model, KaldiRecognizer

# Создание экземпляра модели и инициализация рекогнизера с заданной частотой дискретизации
model = Model("model")
rec = KaldiRecognizer(model, 16000)

# Инициализация аудиопотока для записи аудиосигнала с помощью PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()


def get_words():
    '''Функция для получения слов из распознанной речи'''
    data = stream.read(10, exception_on_overflow=False)
    if (rec.AcceptWaveform(data)) and (len(data) > 0):
        answer = json.loads(rec.Result())
        if len(answer['text']) > 0:
            words = answer['text']
            # print(words)
            return words
    return ''


# инициализация библиотеки Pygame
pygame.init()

# задание игрового поля, размера ячекйи и частоты кадров (нет необходимости при распознавании речи)
width, height = 400, 300
cell_size = 20
fps = 60

# создание экрана игры и заголовка
screen = pygame.display.set_mode((width + 150, height))
pygame.display.set_caption("Змейка")

# создание змейки и задание направления
snake = [((width // cell_size // 2 - 1)*cell_size, (height // cell_size // 2)*cell_size)]
snake_direction = (1, 0)

# создание всего поля, по которому может перемещаться змейка
field = []
for x in range(0, width, cell_size):
    for y in range(0, height, cell_size):
        field.append((x, y))


def random_apple(a, b):
    '''Функция для случайного выбора координаты яблока'''
    apple = random.choice(a)
    while apple in b:
        a.remove(apple)
        apple = random.choice(a)
    return apple


# случайный выбор координаты яблока
apple = random_apple(field.copy(), snake)

# авторизация и регистрация пользователя
font = pygame.font.SysFont("Arial", 24)
text = font.render("Ваше имя: ", True, (255, 255, 255))
screen.blit(text, (10, 10))
pygame.display.update()
player = ''
while player == '':
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
    player = get_words()
    if player != '':
        name = font.render(player, True, (255, 255, 255))
        screen.blit(name, (text.get_width()+10, 10))
        text_approval = font.render("Все верно? Скажите да / нет", True, (255, 255, 255))
        screen.blit(text_approval, (10, 50))
        pygame.display.update()
        approval = ''
        while approval != 'да' and approval != 'нет':
            approval = get_words()
        if approval == 'нет':
            player = ''
            pygame.draw.rect(screen, (0, 0, 0), (text.get_width()+10, 0, width, 50))
            pygame.draw.rect(screen, (0, 0, 0), (10, 50, width, 50))
            pygame.display.update()

# чтение Players.json
with open('Players.json', 'r') as file:
    data = json.load(file)

# приветствие пользователя
if player in data:
    hi = font.render("Приветсвую, " + player + f"!  Ваш лучший счет: {data[player]}", True, (255, 255, 255))
else:
    hi = font.render("Приветсвую, " + player + "!  Вы новенький, удачи!", True, (255, 255, 255))
    data[player] = 0
screen.blit(hi, (10, 90))
pygame.display.update()
pygame.time.wait(6000)


def save_score(score):
    '''Функция для сохранения лучшего числа, набранных очков'''
    if data[player] < score:
        data[player] = score
    with open('Players.json', 'w') as file:
        json.dump(data, file)

# подготовка экрана для игры
screen.fill((0, 0, 0))
pygame.draw.rect(screen, (169, 169, 169), (width, 0, width+150, height))

# отображение очков и имени игрока с его лучшим результатом
score_lb = font.render("Score: ", True, (0, 0, 0))
screen.blit(score_lb, (width + 10, 1))
score = 0
score_dig = font.render(str(score), True, (0, 0, 0))
screen.blit(score_dig, (width + score_lb.get_width() + 10, 1))
screen.blit(font.render(player + ": " + str(data[player]), True, (0, 0, 0)), (width + 10, height-30))

# для работы со временем
clock = pygame.time.Clock()
now_time = time.time()

# запуск игры
while True:
    # 1,5 секунды для распознавания команды
    command = get_words()
    if time.time() - now_time >= 1.5 and command == '':
        command = '0'
    
    # смена событий в игре
    if command != '':

        # обработка крестика
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_score(score)
                pygame.quit()
                quit()

        # обработка команды "выход из игры"
        if command == 'выход из игры':
            save_score(score)
            pygame.quit()
            quit()
        
        # обработка команды "пауза" и "продолжить"
        if command == 'пауза':
            while command != 'продолжить':
                command = get_words()
        
        # изменение направления змейки
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_RIGHT] or 'прав' in command) and snake_direction != (-1, 0):
            snake_direction = (1, 0)
        elif (keys[pygame.K_LEFT] or 'лев' in command) and snake_direction != (1, 0):
            snake_direction = (-1, 0)
        elif (keys[pygame.K_UP] or 'вер' in command) and snake_direction != (0, 1):
            snake_direction = (0, -1)
        elif (keys[pygame.K_DOWN] or 'низ' in command) and snake_direction != (0, -1):
            snake_direction = (0, 1)

        # голова змейка
        snake_head = (snake[0][0] + snake_direction[0] * cell_size, snake[0][1] + snake_direction[1] * cell_size)

        # обработка краев игрового поля
        if snake_head[0] >= width:
            snake_head = (0, snake_head[1])
        elif snake_head[0] < 0:
            snake_head = (width - cell_size, snake_head[1])
        elif snake_head[1] >= height:
            snake_head = (snake_head[0], 0)
        elif snake_head[1] < 0:
            snake_head = (snake_head[0], height - cell_size)

        # добавление головы змейки
        snake.insert(0, snake_head)

        # обработка съедания яблока (яблоко становится головой змейки или удаляется хвост)
        if snake_head == apple:
            try:
                apple = random_apple(field.copy(), snake)
            except IndexError:
                pass
            pygame.draw.rect(screen, (169, 169, 169), (width + score_lb.get_width()+5, 0, 
                                                 width+150, score_lb.get_height()))
            # увеличение очков
            score += 1
            score_dig = font.render(str(score), True, (0, 0, 0))
            screen.blit(score_dig, (width + score_lb.get_width() + 10, 1))
        else:
            snake.pop()
        
        # обработка столкновения змейки
        if snake[0] in snake[1:]:
            font_lose = pygame.font.SysFont("Arial", 60)
            text_score = font_lose.render(f"You score: {score}", True, (255, 255, 255))
            text_again = font_lose.render(f"Try again!", True, (255, 255, 255))
            screen.blit(text_score, (50, 50))
            screen.blit(text_again, (60, 120))
            pygame.display.update()
            pygame.time.wait(10000)
            save_score(score)
            pygame.quit()
            quit()

        # отрисовывание произошедших событий
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, width, height))
        pygame.draw.rect(screen, (255, 0, 0), (*apple, cell_size, cell_size))
        for segment in snake:
            pygame.draw.rect(screen, (0, 255, 0), (*segment, cell_size, cell_size))

        # отображение отрисованного
        pygame.display.update()

        clock.tick(fps)

        # проверка пользователя на выигрыш
        if len(snake) == width * height // cell_size**2:
            font_win = pygame.font.SysFont("Arial", 60)
            text_win = font_win.render("You win!", True, (255, 255, 255))
            screen.blit(text_win, (100, 100))
            pygame.display.update()
            pygame.time.wait(10000)
            save_score(score)
            pygame.quit()
            quit()

        # обновление времени на распознование речи
        now_time = time.time()
