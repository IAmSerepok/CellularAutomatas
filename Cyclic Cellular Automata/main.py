import pygame as pg
import numpy as np

from random import randint
from copy import deepcopy
from colorsys import hsv_to_rgb
from numba import prange

import sys
from pathlib import Path

general_path = Path(__file__).parent.parent / "general"
sys.path.append(str(general_path))

from neighborhood import neighborhood_funcs
from save import save_screen


class App:

    def __init__(self, columns=200, rows=200, tile_size=4, fps=60, random_field=False, cmap=None):
        pg.init()

        self.tile_size = tile_size
        self.rows, self.columns = rows, columns
        self.screen = pg.display.set_mode([columns * tile_size, rows * tile_size])
        self.clock = pg.time.Clock()

        self.FPS = fps
        self.speed = 1
        self.time = 0
        self.running = True

        self.radius, self.threshold, self.states, self.neighborhood = None, None, None, None
        self.colors = None
        self.cmap = cmap

        self.random_field = random_field
        self.next_field, self.current_field = None, None

    def generate_grid(self):
        self.next_field = np.zeros((self.columns + 2 * self.radius, self.rows + 2 * self.radius), dtype=int)
        self.current_field = np.zeros((self.columns + 2 * self.radius, self.rows + 2 * self.radius), dtype=int)

        if self.random_field:
            for x in prange(self.radius, self.columns + self.radius):
                for y in prange(self.radius, self.rows + self.radius):
                    self.current_field[x, y] = randint(0, self.states - 1)

    def set_rule(self, radius, threshold, states, neighborhood):
        self.radius = radius
        self.threshold = threshold
        self.states = states
        self.neighborhood = neighborhood_funcs[neighborhood]

        self.generate_grid()

    def check_cell(self, color, x, y):
        prev_col = color
        col = (color + 1) % self.states
        count = self.neighborhood(self.current_field, x, y, col, self.radius)
        if count >= self.threshold:
            return col
        else:
            return prev_col

    def draw_life(self):
        for x in prange(self.radius, self.columns + self.radius):
            for y in prange(self.radius, self.rows + self.radius):
                color = self.colors[self.current_field[x, y]]
                size = self.tile_size

                pg.draw.rect(self.screen, color, ((x - self.radius) * size, (y - self.radius) * size, size, size))

                if ((self.time % self.speed) == 0) and self.running:
                    self.next_field[x, y] = self.check_cell(self.current_field[x, y], x, y)

    def generate_colors(self):
        if self.cmap is None:
            start_color, end_color = (0.0, 0.0, 1.0), (0.0, 0.0, 0.0)
        elif len(self.cmap) == self.states:
            self.colors = self.cmap
            return
        else:
            start_color, end_color = self.cmap

        colors = []

        h0, s0, v0 = start_color
        h1, s1, v1 = end_color
        n = self.states - 1
        for _1 in prange(n + 1):
            r, g, b = (hsv_to_rgb(h0 + (h1 - h0) * _1 / n,
                                  s0 + (s1 - s0) * _1 / n,
                                  v0 + (v1 - v0) * _1 / n))
            colors.append((255 * r, 255 * g, 255 * b))
        self.colors = colors

    def run(self):
        self.generate_colors()

        while True:
            self.screen.fill(pg.Color('black'))

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.running = not self.running

            self.draw_life()
            self.current_field = deepcopy(self.next_field)
            pg.display.flip()
            self.time += 1
            self.clock.tick(self.FPS)


if __name__ == '__main__':
    app = App(random_field=True, 
              cmap=[(8, 32, 50), (44, 57, 75), (51, 71, 86), (255, 76, 41), (235, 91, 0)])
    app.set_rule(3, 3, 5, 'L')
    app.run()
