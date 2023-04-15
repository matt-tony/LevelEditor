import pygame
from level_colors import *
from level_text import *
from collections import defaultdict


class TilesetConfig:
    def __init__(self, tileset_path_dir, screen_height, rows, tile_size_w=16, tile_size_h=16, tileset_scale_factor=2):
        self.tileset_path_dir = tileset_path_dir
        self.tile_size_w = tile_size_w
        self.tile_size_h = tile_size_h
        self.tile_scale_factor = tileset_scale_factor
        self.tile_size = screen_height // rows # self.tile_size_w * self.tile_scale_factor
        self.current_tile = None
        self.TILE_PANEL_COLS = 8


# create empty tile list
# lyr 0: Background image layer
# lyr 1: Background layer 1 (default tile layer)
# lyr 2: Background layer 2
# lyr 3: Background layer 3
# lyr 4: Foreground layer
# Note that the Background image layer is reserved for a background image
class WorldData:
    MAX_LAYERS = 4
    LYR_DESCR = {1: "Default background tile layer", 2: "Layer used to set elevators and stuff with alpha channel"    , 
        3: "Layer that can be used to set decorations (e.g. blood traces, dust, etc.)", 
        4: "Foreground layer that stores stuff that is in front of the player"}
    def __init__(self, max_rows, max_cols, tileset_config: TilesetConfig):
        self.curr_lyr: int = 1
        self.data = defaultdict(list)
        self.max_rows = max_rows
        self.max_cols = max_cols
        self.level:int = 0
        self.tileset_config = tileset_config

        for lyr in range(self.MAX_LAYERS):
            for row in range(self.max_rows):
                r = [-1] * self.max_cols
                self.data[lyr].append(r)

            # create ground
            for tile in range(0, self.max_cols):
                self.data[lyr][self.max_rows - 1][tile] = 0

    def draw_world(self, screen, scroll, img_list):
        if len(img_list) > 0:
            for lyr in range(self.MAX_LAYERS):
                for y, row in enumerate(self.data[lyr]):
                    for x, tile in enumerate(row):
                        if tile >= 0:
                            screen.blit(img_list[tile], (x * self.tileset_config.tile_size - scroll, 
                                y * self.tileset_config.tile_size))

    def update_tile_value(self, x, y, current_tile):
        # update tile value
        if pygame.mouse.get_pressed()[0] == 1:
            if self.data[self.curr_lyr][y][x] != current_tile:
                self.data[self.curr_lyr][y][x] = current_tile
        if pygame.mouse.get_pressed()[2] == 1:
            self.data[self.curr_lyr][y][x] = -1



class GraphData:
    def __init__(self, max_rows, max_cols, tileset_config: TilesetConfig):
        self.data = list()
        self.node_positions = dict()
        self.edges = set()
        self.node_id: int = 0
        self.node_selected: int = -1
        self.max_rows = max_rows
        self.max_cols = max_cols
        self.tileset_config = tileset_config
        self.font = pygame.font.SysFont('Futura', 25, bold=True)
        self.img_node = pygame.image.load('img/node.png').convert_alpha()
        self.img_node = pygame.transform.scale(self.img_node, (int(self.tileset_config.tile_size / 2), int(self.tileset_config.tile_size / 2)))
        self.img_node_selected = pygame.image.load('img/node_selected.png').convert_alpha()
        self.img_node_selected = pygame.transform.scale(self.img_node_selected, (int(self.tileset_config.tile_size / 2), int(self.tileset_config.tile_size / 2)))

        # init graph data
        for row in range(self.max_rows):
            r = [-1] * self.max_cols
            self.data.append(r)

    # function for drawing graph data
    def draw_graph(self, screen, scroll):
        # draw edges
        for node1, node2 in self.edges:
            y1, x1 = self.node_positions[node1]
            y2, x2 = self.node_positions[node2]
            x_pos_start = x1 * self.tileset_config.tile_size + self.tileset_config.tile_size/2 - scroll
            y_pos_start = y1 * self.tileset_config.tile_size + self.tileset_config.tile_size/2
            x_pos_end = x2 * self.tileset_config.tile_size + self.tileset_config.tile_size/2 - scroll
            y_pos_end = y2 * self.tileset_config.tile_size + self.tileset_config.tile_size/2
            pygame.draw.line(screen, GRAY, (x_pos_start, y_pos_start), (x_pos_end, y_pos_end), width=5)

        # draw nodes
        for y, row in enumerate(self.data):
            for x, node in enumerate(row):
                if node >= 0:
                    x_pos = x * self.tileset_config.tile_size + self.tileset_config.tile_size/4 - scroll
                    y_pos = y * self.tileset_config.tile_size + self.tileset_config.tile_size/4
                    img = self.img_node_selected if node == self.node_selected else self.img_node

                    screen.blit(img, (x_pos, y_pos))
                    font_x_pos = x_pos + self.tileset_config.tile_size/(6 + len(str(node)))
                    draw_text(screen, f'{node}', self.font, GRAY, font_x_pos, y_pos + self.tileset_config.tile_size/6)

    def update_value(self, x, y):
         if pygame.mouse.get_pressed()[0] == 1:
             if self.data[y][x] == -1:
                 self.data[y][x] = self.node_id
                 self.node_positions[self.node_id] = (y, x)
                 self.node_id += 1
                 self.node_selected = -1
             elif self.node_selected == -1:
                 self.node_selected = self.data[y][x]
             else:
                 self.edges.add((self.node_selected, self.data[y][x]))
                 self.node_selected = self.data[y][x]
         if pygame.mouse.get_pressed()[2] == 1:
             self.data[y][x] = -1

