import pygame as pg
import numpy as np

from random import random
from copy import deepcopy
from math import ceil
from numba import prange

import sys
from pathlib import Path

general_path = Path(__file__).parent.parent / "general"
sys.path.append(str(general_path))

from neighborhood import neighborhood_funcs
from save import save_screen


class App:
    def __init__(
            self, columns=200, rows=200, tile_size=5, fps=60,
            random_field=False, probability=0.5
    ):
        pg.init()

        self.rows, self.columns = rows, columns
        self.screen = pg.display.set_mode([columns * tile_size, rows * tile_size])
        self.clock = pg.time.Clock()

        self.rule_b, self.rule_s, self.rule_f, self.rule_k, self.rule_l = None, None, None, None, None

        self.FPS = fps
        self.speed = 1
        self.time = 0
        self.running = True
        self.colors = None

        self.tile_size = tile_size

        self.next_field = np.zeros((self.columns + 2, self.rows + 2), dtype=int)
        self.current_field = np.zeros((self.columns + 2, self.rows + 2), dtype=int)
        if random_field:
            for x in prange(1, self.columns + 1):
                for y in prange(1, self.rows + 1):
                    if random() < probability:
                        self.current_field[x, y] = 1

    def check_cell(self, current_field_, x, y):
        count_live = neighborhood_funcs['M'](current_field_, x, y, 1, 1)
        count_killers = neighborhood_funcs['M'](current_field_, x, y, 2, 1)

        if current_field_[x, y] == 1:
            if count_killers in self.rule_k:
                return 0
            if not (count_live in self.rule_s):
                return 2
            return 1
        elif current_field_[x, y] == 0:
            if (count_live in self.rule_b) and (count_killers in self.rule_f):
                return 1
            return 0
        else:
            if count_live in self.rule_l:
                return 0
            return 2

    def generate_grid(self, grid_visible):
        if grid_visible:
            [pg.draw.line(self.screen, 'gray', (x, 0), (x, self.rows * self.tile_size), 1) for x in
             prange(0, self.columns * self.tile_size, self.tile_size)]
            [pg.draw.line(self.screen, 'gray', (0, y), (self.columns * self.tile_size, y), 1) for y in
             prange(0, self.rows * self.tile_size, self.tile_size)]

    def set_rules(self, birth, survival, fate, killer, life):
        self.rule_b = birth
        self.rule_s = survival
        self.rule_f = fate
        self.rule_k = killer
        self.rule_l = life

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
                        pg.draw.rect(self.screen, self.colors[self.current_field[x, y]],
                                     ((x - 1) * size + 2, (y - 1) * size + 2, size - 2, size - 2))
                    else:
                        pg.draw.rect(self.screen, self.colors[self.current_field[x, y]],
                                     ((x - 1) * size, (y - 1) * size, size, size))
                if ((self.time % self.speed) == 0) and self.running:
                    self.next_field[x, y] = self.check_cell(self.current_field, x, y)

    def set_colors(self, death, live, killer):
        self.colors = [death, live, killer]

    def run(self, grid_visible):
        while True:
            self.screen.fill(pg.Color(self.colors[0]))
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
    app = App(random_field=True, probability=0.1)
    app.set_colors((0, 0, 0), (255, 36, 36), (215, 36, 255))
    app.set_rules([2, 6, 7], [3, 4, 5], [0, 2, 7, 8], [6, 7, 7], [0, 1, 2, 8])
    app.run(grid_visible=False)
