import pyxel
import math
from random import choice
import logging

SCREEN_WIDTH = 256
SCREEN_HEIGHT = 256
BALL_SIZE = 4
BALL_SPEED = 5
HANDLE_HEIGHT = 40
HANDLE_WIDTH = 5
HANDLE_SPEED = 4
COLOR = pyxel.COLOR_WHITE

logging.basicConfig(
    format='[%(asctime)s %(levelname)s] %(message)s',
    level=logging.DEBUG,
)


class Pong:

    def __init__(self, bot: bool = True):
        self.bot = bot
        self.score = [0, 0]
        self.game_paused = False
        self.p1 = {}
        self.p2 = {}
        self.ball = {}
        self.sound = {}
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, caption='Pyxel Pong')  # , fullscreen=True)
        self.screen_middle = {'x': pyxel.width // 2, 'y': pyxel.height // 2}
        self.setup_sounds()
        self.restart()
        pyxel.run(self.update, self.draw)

    def restart(self):
        self.game_paused = False
        self.p1 = {'x': 7, 'y': self.screen_middle['y'], 'vy': 0}
        self.p2 = {'x': 243, 'y': self.screen_middle['y'], 'vy': 0}
        self.ball = {'x': 113, 'y': 113,
                     'vx': choice((1, -1)) * BALL_SPEED // 2,
                     'vy': choice((1, -1)) * BALL_SPEED // 2}

    def setup_sounds(self):
        pyxel.sound(0).set("f0ra4r", "p", "7", "s", 7)
        self.sound['paused'] = 0
        pyxel.sound(1).set("G2B-2D3R", "p", "7", "s", 3)
        self.sound['p1'] = 1
        pyxel.sound(2).set("G2B-2D2R", "p", "7", "s", 3)
        self.sound['p2'] = 2
        pyxel.sound(3).set("a3a2c2c2", "n", "7742", "s", 10)
        self.sound['point'] = 3
        pyxel.sound(4).set("a3a2c2c2", "n", "7742", "s", 10)
        self.sound['quit'] = 4
        pyxel.sound(4).set("G2B-2D0R", "n", "7742", "s", 3)
        self.sound['wall'] = 4

    def handle_key_input(self):
        if pyxel.btn(pyxel.KEY_Q):
            pyxel.play(0, self.sound['quit'])
            pyxel.quit()
            return
        if pyxel.btn(pyxel.KEY_R):
            self.restart()
        if pyxel.btnp(pyxel.KEY_P):
            self.game_paused = not self.game_paused
            pyxel.play(0, self.sound['paused'])
        if pyxel.btn(pyxel.KEY_UP):
            self.p1['vy'] = -HANDLE_SPEED
        if pyxel.btn(pyxel.KEY_DOWN):
            self.p1['vy'] = HANDLE_SPEED
        if not self.bot:
            if pyxel.btn(pyxel.KEY_W):
                self.p2['vy'] = -HANDLE_SPEED
            if pyxel.btn(pyxel.KEY_S):
                self.p2['vy'] = HANDLE_SPEED

    def bot_move(self):
        if not self.bot or self.ball['x'] < self.screen_middle['x']:
            return

        if self.p2['y'] + HANDLE_HEIGHT / 2 > self.ball['y'] + BALL_SIZE*3:
            self.p2['vy'] = -HANDLE_SPEED
        elif self.p2['y'] + HANDLE_HEIGHT / 2 < self.ball['y'] - BALL_SIZE*3:
            self.p2['vy'] = HANDLE_SPEED

    def handle_ball_interactions(self):
        # point - ball has passed player
        if (self.ball['x'] - BALL_SIZE) <= 0:
            self.game_paused = True
            self.score[1] += 1
            pyxel.play(0, self.sound['point'])
        elif self.ball['x'] + BALL_SIZE >= SCREEN_WIDTH:
            self.game_paused = True
            self.score[0] += 1
            pyxel.play(0, self.sound['point'])

        # ball at floor or ceiling
        if (self.ball['y'] - BALL_SIZE) <= 0:
            self.ball['vy'] = abs(self.ball['vy'])
            pyxel.play(0, self.sound['wall'])
        if (self.ball['y'] + BALL_SIZE) >= pyxel.height:
            self.ball['vy'] = -1 * abs(self.ball['vy'])
            pyxel.play(0, self.sound['wall'])

        if (self.p1['y'] < self.ball['y'] < self.p1['y'] + HANDLE_HEIGHT) \
                and (self.p1['x'] < (self.ball['x'] - BALL_SIZE) < self.p1['x'] + HANDLE_WIDTH):
            self.ball['vx'] = self.ball_speed_player_effect(self.p1)
            pyxel.play(0, self.sound['p1'])
        if (self.p2['y'] < self.ball['y'] < self.p2['y'] + HANDLE_HEIGHT) \
                and (self.p2['x'] < (self.ball['x'] + BALL_SIZE) < self.p2['x'] + HANDLE_WIDTH):
            self.ball['vx'] = -1 * self.ball_speed_player_effect(self.p2)
            pyxel.play(0, self.sound['p2'])

    def ball_speed_player_effect(self, player: dict) -> int:
        speed = BALL_SPEED
        handle_mid = HANDLE_HEIGHT // 2
        speed_percent = abs(
            self.ball['y'] - (player['y'] + handle_mid)
        ) / handle_mid
        logging.debug(
            f'ball: {self.ball["y"]}, player: {player["y"]}, '
            f'handle_mid: {handle_mid}, speed_percent: {speed_percent:.2}, '
            f'res: {math.ceil(speed * speed_percent)} (max: {speed})'
        )
        return math.ceil(speed * speed_percent)

    def update(self):
        self.handle_key_input()
        if self.game_paused:
            return

        self.bot_move()
        self.handle_ball_interactions()

        for player in [self.p1, self.p2]:
            if 0 < player['vy'] + player['y'] < (pyxel.width - HANDLE_HEIGHT):
                player['y'] += player['vy']

        self.ball['x'] += self.ball['vx']
        self.ball['y'] += self.ball['vy']

    def draw_score(self):
        quarter_screen = pyxel.width // 4
        pyxel.text(quarter_screen, 5, str(self.score[0]), COLOR)
        pyxel.text(quarter_screen * 3, 5, str(self.score[1]), COLOR)
        # pyxel.text(SCREEN_WIDTH // 2 - 10, 5, f'{self.score[0]} : {self.score[1]}', COLOR)

    @staticmethod
    def draw_divider():
        screen_middle = pyxel.width // 2
        for y in range(0, pyxel.height - 2, 4):
            pyxel.line(screen_middle, y, screen_middle, y + 2, COLOR)
            # logging.debug(f'>> draw_divider << {screen_middle}, {y}-{y + 5}')

    def draw(self):
        pyxel.cls(0)
        self.draw_divider()
        self.draw_score()
        # pyxel.circ(self.ball['x'], self.ball['y'], BALL_SIZE, 3)
        pyxel.rect(
            self.ball['x'] + BALL_SIZE // 2, self.ball['y'] + BALL_SIZE // 2,
            BALL_SIZE, BALL_SIZE, COLOR
        )
        for player in [self.p1, self.p2]:
            pyxel.rect(player['x'], player['y'], HANDLE_WIDTH, HANDLE_HEIGHT, COLOR)

        if self.game_paused:
            self.draw_paused()

    def draw_paused(self):
        pyxel.text(
            self.screen_middle['x'] - 4*pyxel.FONT_WIDTH,
            self.screen_middle['x'],
            'Pong Paused',
            pyxel.COLOR_YELLOW
        )


def main():
    Pong()


if __name__ == '__main__':
    main()
