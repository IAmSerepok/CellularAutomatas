import pygame as pg
import numpy as np

from random import randrange, random
from copy import deepcopy
from math import ceil
from numba import prange

import sys
from pathlib import Path

general_path = Path(__file__).parent.parent / "general"
sys.path.append(str(general_path))

from neighborhood import neighborhood_funcs


class App:
    def __init__(
            self, columns=200, rows=200, tile_size=4, fps=60,
            random_field=False, probability=0.5
    ):
        pg.init()

        self.rows, self.columns = rows, columns
        self.screen = pg.display.set_mode([columns * tile_size, rows * tile_size])
        self.clock = pg.time.Clock()

        self.rule_b, self.rule_s = None, None

        self.FPS = fps
        self.speed = 2
        self.time = 0
        self.running = True

        self.color = self.get_random_color()
        self.tile_size = tile_size

        self.next_field = np.zeros((self.columns + 2, self.rows + 2), dtype=int)
        self.current_field = np.zeros((self.columns + 2, self.rows + 2), dtype=int)
        if random_field:
            for x in prange(1, self.columns + 1):
                for y in prange(1, self.rows + 1):
                    if random() < probability:
                        self.current_field[x, y] = 1

    @staticmethod
    def get_random_color():
        return randrange(30, 220), randrange(30, 220), randrange(30, 220)

    def check_cell(self, current_field_, x, y):
        count = neighborhood_funcs['M'](current_field_, x, y, 1, 1)

        if current_field_[x, y]:
            if count in self.rule_s:
                return 1
            return 0
        else:
            if count in self.rule_b:
                return 1
            return 0

    def generate_grid(self, grid_visible):
        if grid_visible:
            [pg.draw.line(self.screen, 'gray', (x, 0), (x, self.rows * self.tile_size), 1) for x in
             prange(0, self.columns * self.tile_size, self.tile_size)]
            [pg.draw.line(self.screen, 'gray', (0, y), (self.columns * self.tile_size, y), 1) for y in
             prange(0, self.rows * self.tile_size, self.tile_size)]

    def set_rules(self, birth, survival):
        self.rule_b = birth
        self.rule_s = survival

    def get_cords(self, pos):
        x, y = pos
        x = ceil(x / self.tile_size)
        y = ceil(y / self.tile_size)
        return x, y

    def draw_life(self, grid_visible):
        for x in prange(1, self.columns + 1):
            for y in prange(1, self.rows + 1):
                if self.current_field[x, y]:
                    size = self.tile_size
                    if grid_visible:
                        pg.draw.rect(self.screen, self.color, ((x - 1) * size + 2,
                                                               (y - 1) * size + 2, size - 2, size - 2))
                    else:
                        pg.draw.rect(self.screen, self.color, ((x - 1) * size,
                                                               (y - 1) * size, size, size))
                if ((self.time % self.speed) == 0) and self.running:
                    self.next_field[x, y] = self.check_cell(self.current_field, x, y)

    def run(self, grid_visible):
        while True:
            self.screen.fill(pg.Color('black'))
            self.generate_grid(grid_visible)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    x, y = self.get_cords(event.pos)
                    if event.button == 1:
                        self.next_field[x, y] = not self.current_field[x, y]
                    elif event.button == 3:
                        self.running = not self.running

            self.draw_life(grid_visible)
            self.current_field = deepcopy(self.next_field)
            pg.display.flip()
            self.time += 1
            self.clock.tick(self.FPS)


if __name__ == "__main__":
    app = App(random_field=True, probability=0.5)
    app.set_rules([3], [2, 3])
    app.run(grid_visible=False)
