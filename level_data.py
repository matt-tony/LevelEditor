import pygame
from level_colors import *
from level_text import *
from collections import defaultdict
from dataclasses import dataclass


class TilesetConfig:
    def __init__(self, tileset_dir_path, screen_height, rows, tile_size_w=16, tile_size_h=16, tileset_scale_factor=2):
        self.tileset_dir_path = tileset_dir_path
        self.tile_size_w = tile_size_w
        self.tile_size_h = tile_size_h
        self.tile_scale_factor = tileset_scale_factor
        self.tile_size = screen_height // rows # self.tile_size_w * self.tile_scale_factor
        self.tile_obstacles = list()
        self.current_tile = None
        self.TILE_PANEL_COLS = 8


@dataclass
class CharacterData:
    name: str 
    x_pos: int
    y_pos: int
    obj_id: str
    obj_type: str
    health: int


@dataclass
class TriggerData:
    trigger_id: str
    conditions: list


@dataclass
class ActionData:
    action_id: str
    data: dict


class EventData:
    def __init__(self):
        self.trigger_action_dict = dict()

        
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
        self.character_dict = dict()
        self.obj_id_player = 0
        self.obj_id_enemy = 0

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

    def draw_characters(self, screen, img_player, img_enemy, font):
        for k, char_data in self.character_dict.items():
            img = img_player if k == "player" else img_enemy
            screen.blit(img, (char_data.x_pos, char_data.y_pos))
            draw_text(screen, f'{char_data.obj_id}', font, GRAY, char_data.x_pos + img.get_rect().width / 3, char_data.y_pos + img.get_rect().height/3)

    def add_character_data(self, name, obj_type, health, x, y, scroll):
        x_pos = x * self.tileset_config.tile_size - scroll # + self.tileset_config.tile_size / 2
        y_pos = y * self.tileset_config.tile_size # + self.tileset_config.tile_size / 2

        if obj_type == "player":
            key = obj_type
            obj_id = self.obj_id_player 
        else: 
            obj_id = self.obj_id_enemy
            key = f"{obj_type}_{obj_id}"
            self.obj_id_enemy += 1

        cd = CharacterData(name, x_pos, y_pos, obj_id, obj_type, health)
        self.character_dict[key] = cd

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

        # init graph data
        for row in range(self.max_rows):
            r = [-1] * self.max_cols
            self.data.append(r)

    # function for drawing graph data
    def draw_graph(self, screen, scroll, img_node, img_node_selected, font):
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
                    img = img_node_selected if node == self.node_selected else img_node

                    screen.blit(img, (x_pos, y_pos))
                    font_x_pos = x_pos + self.tileset_config.tile_size/(6 + len(str(node)))
                    draw_text(screen, f'{node}', font, GRAY, font_x_pos, y_pos + self.tileset_config.tile_size/6)

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

