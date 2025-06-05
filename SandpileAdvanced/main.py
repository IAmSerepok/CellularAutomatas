import pygame as pg
import numpy as np

from copy import deepcopy
from numba import prange
from math import ceil
from colorsys import hsv_to_rgb

import sys
from pathlib import Path

general_path = Path(__file__).parent.parent / "general"
sys.path.append(str(general_path))

from save import save_screen


class App:
    def __init__(self, columns=480, rows=540, tile_size=2, fps=60, speed=1, cmap=None, rule=None):
        pg.init()

        self.tile_size = tile_size
        self.rows, self.columns = rows, columns
        self.screen = pg.display.set_mode([columns * tile_size, rows * tile_size])
        self.clock = pg.time.Clock()

        self.is_grid = False

        self.FPS = fps
        self.speed = speed
        self.time = 0
        self.running = True

        self.cmap = cmap
        self.colors = None
        self.rule = np.array(rule)
        self.max_val = np.sum(self.rule)
        self.radius = (self.rule.shape[0] - 1) // 2

        self.next_field = np.zeros((self.columns + 2, self.rows + 2), dtype=int)
        self.current_field = np.zeros((self.columns + 2, self.rows + 2), dtype=int)

    def generate_grid(self):
        [pg.draw.line(self.screen, (30, 30, 30), (x, 0), (x, self.rows * self.tile_size), 1)
         for x in prange(0, self.columns * self.tile_size, self.tile_size)]
        [pg.draw.line(self.screen, (30, 30, 30), (0, y), (self.columns * self.tile_size, y), 1)
         for y in prange(0, self.rows * self.tile_size, self.tile_size)]

    def generate_colors(self):
        if self.cmap is None:
            start_color, end_color = (0.0, 0.0, 0.0), (0.0, 0.0, 1.0)
        else:
            start_color, end_color = self.cmap
        colors = []
        h0, s0, v0 = start_color
        h1, s1, v1 = end_color
        n = self.max_val - 1
        for _1 in prange(n + 1):
            r, g, b = (hsv_to_rgb(h0 + (h1 - h0) * _1 / n,
                                  s0 + (s1 - s0) * _1 / n,
                                  v0 + (v1 - v0) * _1 / n))
            colors.append((255 * r, 255 * g, 255 * b))
        self.colors = colors

    def get_cords(self, pos):
        x, y = pos
        x = ceil(x / self.tile_size)
        y = ceil(y / self.tile_size)
        return x, y

    def drop(self, x, y):
        self.next_field[x, y] -= self.max_val
        for i in range(x - self.radius, x + self.radius + 1):
            for j in range(y - self.radius, y + self.radius + 1):
                self.next_field[i, j] += self.rule[i - x + self.radius, j - y + self.radius]

    def drop_fast(self, x, y):
        delta = self.current_field[x][y] // self.max_val
        new = self.current_field[x][y] % self.max_val
        self.next_field[x, y] = new
        for i in range(x - self.radius, x + self.radius + 1):
            for j in range(y - self.radius, y + self.radius + 1):
                self.next_field[i, j] += self.rule[i - x + self.radius, j - y + self.radius] * delta

    def run(self, fast):
        self.generate_colors()

        while True:
            self.screen.fill(pg.Color('black'))
            if self.is_grid:
                self.generate_grid()

            self.next_field = deepcopy(self.current_field)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    x, y = self.get_cords(event.pos)
                    if event.button == 1:
                        self.next_field[x, y] += 1
                    elif event.button == 3:
                        self.running = not self.running

            # draw life
            for x in prange(1, self.columns + 1):
                for y in prange(1, self.rows + 1):
                    if self.current_field[x, y] >= self.max_val:
                        color = self.colors[-1]
                        if (self.time % self.speed) == 0 and self.running:
                            if fast:
                                self.drop_fast(x, y)
                            else:
                                self.drop(x, y)
                    else:
                        color = self.colors[self.current_field[x, y]]

                    size = self.tile_size
                    delta = 2 if self.is_grid else 0
                    pg.draw.rect(self.screen, color, ((x - 1) * size + delta, (y - 1) * size + delta,
                                                      size - delta, size - delta))

            self.current_field = deepcopy(self.next_field)
            pg.display.flip()
            self.time += 1
            self.clock.tick(self.FPS)


if __name__ == "__main__":
    app = App(
        speed=1, cmap=[(60/360, 1.0, 0.0), (80/360, 1.0, 0.7)],
        rule=[
            [2, 1, 2],
            [1, 0, 1],
            [2, 1, 2]
        ]
        )
    app.current_field[app.columns // 2][app.rows // 2] = 10 ** 9
    # for delta in range(app.columns // 2): app.current_field[app.columns // 4 + delta, app.rows // 2] = 10 ** 9
    app.run(fast=False)
