import pygame
import pygame_gui
from pygame_gui.windows import UIFileDialog
# import easygui
# from tkinter import filedialog as fd
import os
import button
import csv
import pickle
import json
from collections import defaultdict
from level_data import TilesetConfig, CharacterData, WorldData, GraphData
from level_colors import *
from level_text import *
from level_windows import EventWindow, EventPart
from dataclasses import dataclass


# panel config
@dataclass
class PanelConfig:
    space_w: int = 60
    space_h: int = 40
    margin_w: int = 20
    margin_h: int = 20


class LevelEditorMain:
    # window settings
    SCREEN_WIDTH = 1055
    SCREEN_HEIGHT = 800
    LOWER_MARGIN = 100
    SIDE_MARGIN = 650
    ROWS = 16
    MAX_COLS = 150
    # FPS
    FPS = 30
    # special button indices
    GRAPH_IDX = 0
    PLAYER_IDX = 1
    ENEMY_IDX = 2
    TRIGGER_IDX = 3
    ACTION_IDX = 4
    # File data keys
    DATA_KEY_TILESET_CONFIG = "tileset_config"
    DATA_KEY_WORLD_DATA = "world_data"
    DATA_KEY_GRAPH_DATA = "graph_data"

    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
         
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH + self.SIDE_MARGIN, self.SCREEN_HEIGHT + self.LOWER_MARGIN))
        pygame.display.set_caption('Level Editor')
        pygame.display.set_icon(pygame.image.load('img/level_editor_icon.png'))

        # define editor variables
        self.panel_config = PanelConfig()
        self.tileset_config = TilesetConfig("/home/matt/projects/Escaper/res/tiles/station", self.SCREEN_HEIGHT, self.ROWS)
        self.world_data = WorldData(self.ROWS, self.MAX_COLS, self.tileset_config)
        self.graph_data = GraphData(self.ROWS, self.MAX_COLS, self.tileset_config)
        self.current_tile = None 
        self.run = True

        # scroll attributes
        self.scroll_left = False
        self.scroll_right = False
        self.scroll = 0
        self.scroll_speed = 1

        # tile data
        self.img_list = list()
        self.button_list = list()

        # background data
        self.bg_img_list = list()
        #pine1_img = pygame.image.load('img/Background/pine1.png').convert_alpha()
        #pine2_img = pygame.image.load('img/Background/pine2.png').convert_alpha()
        #mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha()
        #sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()

        # define fonts
        self.font = pygame.font.SysFont('Futura', 30)
        self.font_small = pygame.font.SysFont('Futura', 20)
        self.font_graph = pygame.font.SysFont('Futura', 25, bold=True)

        # gui elements
        self.ui_manager = pygame_gui.UIManager((800, 600), "gui_theme_v2.json")
        self.file_dialog_tileset = None
        self.file_dialog_save = None
        self.file_dialog_load = None
        self.event_window = None 

        # create buttons
        # save and load buttons
        save_img = pygame.image.load('img/save_btn.png').convert_alpha()
        save_img_hovering = pygame.image.load('img/save_btn_hovering.png').convert_alpha()
        save_img_clicked = pygame.image.load('img/save_btn_clicked.png').convert_alpha()
        load_img = pygame.image.load('img/load_btn.png').convert_alpha()
        load_img_hovering = pygame.image.load('img/load_btn_hovering.png').convert_alpha()
        load_img_clicked = pygame.image.load('img/load_btn_clicked.png').convert_alpha()
        load_tileset_img = pygame.image.load('img/load_tileset_btn.png').convert_alpha()
        load_tileset_img_hovering = pygame.image.load('img/load_tileset_btn_hovering.png').convert_alpha()
        load_tileset_img_clicked = pygame.image.load('img/load_tileset_btn_clicked.png').convert_alpha()

        self.save_button = button.Button(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT + self.LOWER_MARGIN - 50, 
                [save_img, save_img_hovering, save_img_clicked], 1)
        self.load_button = button.Button(self.SCREEN_WIDTH // 2 + 100, self.SCREEN_HEIGHT + self.LOWER_MARGIN - 50, 
                [load_img, load_img_hovering, load_img_clicked], 1)
        self.load_tileset_button = button.Button(self.SCREEN_WIDTH // 2 + 250, self.SCREEN_HEIGHT + self.LOWER_MARGIN - 50, 
                [load_tileset_img, load_tileset_img_hovering, load_tileset_img_clicked], 1)

        # special buttons
        self.special_button_list = list()
        self.special_btn_idx = None
        img_show = pygame.image.load("img/show_icon.png")
        img_show = pygame.transform.scale(img_show, (self.tileset_config.tile_size, self.tileset_config.tile_size))
        img_hide = pygame.image.load("img/hide_icon.png")
        img_hide = pygame.transform.scale(img_show, (self.tileset_config.tile_size, self.tileset_config.tile_size))
        self.show_special_btn_list = list()

        x_btn_pos = self.SCREEN_WIDTH 
        y_btn_pos = self.SCREEN_HEIGHT + self.LOWER_MARGIN - 100 

        for img_path in ['img/graph_mode.png', 'img/player_btn.png', 'img/enemy_btn.png', 'img/trigger_btn.png', 'img/action_btn.png']:
            img = pygame.image.load(img_path).convert_alpha()
            img = pygame.transform.scale(img, (self.tileset_config.tile_size, self.tileset_config.tile_size))
            btn = button.Button(x_btn_pos, y_btn_pos, [img], 1)
            self.special_button_list.append(btn)
            self.show_special_btn_list.append(button.Button(x_btn_pos, y_btn_pos + img.get_rect().height, [img_show], 1))
            x_btn_pos += btn.rect.width

        # load special images 
        self.img_node = pygame.image.load('img/node.png').convert_alpha()
        self.img_node = pygame.transform.scale(self.img_node, (int(self.tileset_config.tile_size / 2), int(self.tileset_config.tile_size / 2)))
        self.img_node_selected = pygame.image.load('img/node_selected.png').convert_alpha()
        self.img_node_selected = pygame.transform.scale(self.img_node_selected, (int(self.tileset_config.tile_size / 2), int(self.tileset_config.tile_size / 2)))
        self.img_player_instance = pygame.image.load('img/player_instance.png').convert_alpha()
        self.img_enemy_instance = pygame.image.load('img/enemy_instance.png').convert_alpha()
        self.img_trigger_instance = pygame.image.load('img/trigger_instance.png').convert_alpha()
        self.img_trigger_instance_selected = pygame.image.load('img/trigger_instance_selected.png').convert_alpha()
        self.img_action_instance = pygame.image.load('img/action_instance.png').convert_alpha()
        self.img_action_instance_selected = pygame.image.load('img/action_instance_selected.png').convert_alpha()

        # obstacle marker
        self.img_obstacle = pygame.image.load('img/wall.png').convert_alpha()

    def load_background_images(self, bg_img_path_list):
        # load background images
        self.bg_img_list = list()
        for bg_img_path in bg_img_path_list:
            self.bg_img_list.append(pygame.image.load(bg_img_path).convert_alpha())

        return self.bg_img_list

    # create function for drawing background
    def draw_bg(self):
        self.screen.fill(BLUE)
        #width = sky_img.get_width()
        #for x in range(4):
        #    screen.blit(sky_img, ((x * width) - self.scroll * 0.5, 0))
        #    screen.blit(mountain_img, ((x * width) - self.scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        #    screen.blit(pine1_img, ((x * width) - self.scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        #    screen.blit(pine2_img, ((x * width) - self.scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))

    # draw grid
    def draw_grid(self):
        # vertical lines
        for c in range(self.MAX_COLS + 1):
            pygame.draw.line(self.screen, WHITE, (c * self.tileset_config.tile_size - self.scroll, 0), (c * self.tileset_config.tile_size - self.scroll, self.SCREEN_HEIGHT))
        # horizontal lines
        for c in range(self.ROWS + 1):
            pygame.draw.line(self.screen, WHITE, (0, c * self.tileset_config.tile_size), (self.SCREEN_WIDTH, c * self.tileset_config.tile_size))

    def load_tile_images(self, dir_path):
        # store tiles in a list
        self.img_list = []
        num_tiles = len([f for f in os.listdir(dir_path) if f.endswith('.png') and os.path.isfile(os.path.join(dir_path, f))])
        for x in range(num_tiles):
            img = pygame.image.load(f'{dir_path}/tile_{x}.png').convert_alpha()
            img = pygame.transform.scale(img, (self.tileset_config.tile_size, self.tileset_config.tile_size))
            self.img_list.append(img)

        return self.img_list

    def create_tile_buttons(self):
        # make a button list
        self.button_list = []
        button_col = 0
        button_row = 0
        for i in range(len(self.img_list)):
            tile_button = button.Button(self.SCREEN_WIDTH + self.panel_config.margin_w + (self.tileset_config.tile_size_w + self.panel_config.space_w) * button_col, self.panel_config.margin_h + (self.tileset_config.tile_size_h + self.panel_config.space_h) * button_row, [self.img_list[i]], 1)
            self.button_list.append(tile_button)
            button_col += 1
            if button_col == self.tileset_config.TILE_PANEL_COLS:
                button_row += 1
                button_col = 0

        return self.button_list

    def save_map(self, file_path_name):
        # save level data
        # level_file_names = list()
        # for lyr in range(MAX_LAYERS):
        #    level_file_name = f"lvl_{level}_lyr_{lyr}_data.csv"
        #    with open(level_file_name, 'w', newline='') as csvfile:
        #        writer = csv.writer(csvfile, delimiter = ',')
        #        for row in self.world_data[lyr]:
        #            writer.writerow(row)
        #    level_file_names.append(level_file_name)
        #level_data_dict = {"level_files": level_file_names, "tileset": tileset_dir_path}
        #with open(f'lvl_{level}.json', 'w') as f:
        #    json.dump(level_data_dict, f)

        # alternative pickle method
        pickle_out = open(file_path_name, 'wb')
        pickle.dump({LevelEditorMain.DATA_KEY_WORLD_DATA: self.world_data, 
            LevelEditorMain.DATA_KEY_TILESET_CONFIG: self.tileset_config,
            LevelEditorMain.DATA_KEY_GRAPH_DATA: self.graph_data}, pickle_out)
        pickle_out.close()

    def load_map(self, file_path):
        # load in level data
        if file_path is not None and os.path.exists(file_path):
            # reset self.scroll back to the start of the level
            self.scroll = 0
           # with open(file_path) as f:
           #     level_data_dict = json.load(f)

           # csv_file_paths = level_data_dict["level_files"]
           # for csv_file in csv_file_paths:
           #     with open(csv_file, 'r') as csvfile:
           #         lyr = int(csv_file.split("_")[3])
           #         reader = csv.reader(csvfile, delimiter = ',')
           #         for x, row in enumerate(reader):
           #             for y, tile in enumerate(row):
           #                 self.world_data[lyr][x][y] = int(tile)
           # self.img_list, self.button_list, tileset_dir_path = self.load_tileset(level_data_dict["tileset"])
            # alternative pickle method
            pickle_in = open(file_path, 'rb')
            data_dict = pickle.load(pickle_in)
            self.tileset_config = data_dict[LevelEditorMain.DATA_KEY_TILESET_CONFIG]
            self.world_data = data_dict[LevelEditorMain.DATA_KEY_WORLD_DATA]
            self.graph_data = data_dict[LevelEditorMain.DATA_KEY_GRAPH_DATA]
            self.img_list, self.button_list = self.load_tileset(self.tileset_config.tileset_dir_path)

            return self.world_data, self.graph_data, self.tileset_config, self.img_list, self.button_list

    def load_tileset(self, dir_path):
        self.img_list = self.button_list = list()
        # dir_path = easygui.diropenbox(msg="Choose directory containing tileset images...")
        if dir_path is not None and os.path.exists(dir_path):
            self.img_list = self.load_tile_images(dir_path)
            self.button_list = self.create_tile_buttons()
        else:
            print(f"ERR: could not open tileset! Is the path correct?")

        return self.img_list, self.button_list

    def main_loop(self):
        while self.run:
            time_delta = self.clock.tick(self.FPS) / 1000.0

            self.draw_bg()
            self.draw_grid()
            self.world_data.draw_world(self.screen, self.scroll, self.img_list)
            self.world_data.draw_characters(self.screen, self.img_player_instance, self.img_enemy_instance, self.font_small)
            self.graph_data.draw_graph(self.screen, self.scroll, self.img_node, self.img_node_selected, self.font_graph)

            draw_text(self.screen, f'Current Level: {self.world_data.level}', self.font, WHITE, 10, self.SCREEN_HEIGHT + self.LOWER_MARGIN - 90)
            draw_text(self.screen, '(Press UP or DOWN to change level)', self.font_small, WHITE, 200, self.SCREEN_HEIGHT + self.LOWER_MARGIN - 85)
            draw_text(self.screen, f'Current Layer: {self.world_data.curr_lyr}', self.font, WHITE, 10, self.SCREEN_HEIGHT + self.LOWER_MARGIN - 60)
            draw_text(self.screen, f'(Press 1-{self.world_data.MAX_LAYERS} to change layer)', self.font_small, WHITE, 200, self.SCREEN_HEIGHT + self.LOWER_MARGIN - 55)
            draw_text(self.screen, f'{self.world_data.LYR_DESCR[self.world_data.curr_lyr]}', self.font_small, WHITE, 10, self.SCREEN_HEIGHT + self.LOWER_MARGIN - 40)

            # draw buttons
            self.save_button.draw(self.screen)
            self.load_button.draw(self.screen)
            self.load_tileset_button.draw(self.screen)

            for btn in self.special_button_list:
                btn.draw(self.screen)

            for btn in self.show_special_btn_list:
                btn.draw(self.screen)

            # draw tile panel and tiles
            pygame.draw.rect(self.screen, MAGENTA, (self.SCREEN_WIDTH, 0, self.SIDE_MARGIN, self.SCREEN_HEIGHT))

            # draw tiles
            for btn in self.button_list:
                btn.draw(self.screen)

            # draw obstacle markers
            for obstacle_idx in self.tileset_config.tile_obstacles:
                tile_rect = self.button_list[obstacle_idx].rect
                x_pos = tile_rect.x + tile_rect.width + 2
                y_pos = tile_rect.y + tile_rect.height/2 
                self.screen.blit(self.img_obstacle, (x_pos, y_pos))

            # highlight the selected tile or special button
            if self.current_tile is not None and self.special_btn_idx is None:
                pygame.draw.rect(self.screen, RED, self.button_list[self.current_tile].rect, 3)
            elif self.current_tile is None and self.special_btn_idx is not None:
                pygame.draw.rect(self.screen, YELLOW, self.special_button_list[self.special_btn_idx].rect, 3)

            # self.scroll the map
            if self.scroll_left == True and self.scroll > 0:
                self.scroll -= 5 * self.scroll_speed
            if self.scroll_right == True and self.scroll < (self.MAX_COLS * self.tileset_config.tile_size) - self.SCREEN_WIDTH:
                self.scroll += 5 * self.scroll_speed

            # update buttons
            self.save_button.update()
            self.load_button.update()
            self.load_tileset_button.update()
            for btn in self.button_list:
                btn.update()
            for btn in self.special_button_list:
                btn.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False

                # gui events
                if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
                    if event.ui_element == self.file_dialog_save:
                        print(f"saving data to {event.text}")
                        # file_path_name = easygui.filesavebox("Select save file path...", "Save...", f"lvl_{level}_data.bin", ["*.bin"])
                        self.save_map(event.text)
                        self.file_dialog_save = None
                    if event.ui_element == self.file_dialog_load:
                        print(f"loading data from file {event.text}")
                        self.world_data, self.graph_data, self.tileset_config, self.img_list, self.button_list = self.load_map(event.text)
                        self.file_dialog_load = None
                    if event.ui_element == self.file_dialog_tileset:
                        print(f"loading tileset {event.text}")
                        tileset_dir_path = event.text
                        self.img_list, self.button_list = self.load_tileset(event.text)
                        self.file_dialog_tileset = None
                if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and self.event_window and event.ui_element == self.event_window.drop_menu:
                    self.event_window.drop_menu_item_changed(event.text)
                if event.type == pygame_gui.UI_BUTTON_PRESSED and self.event_window and event.ui_element == self.event_window.btn_add:
                    self.event_window.add_button_pressed()

                # keyboard presses
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        level += 1
                    if event.key == pygame.K_DOWN and level > 0:
                        level -= 1
                    if event.key == pygame.K_LEFT:
                        self.scroll_left = True
                    if event.key == pygame.K_RIGHT:
                        self.scroll_right = True
                    if event.key == pygame.K_RSHIFT:
                        self.scroll_speed = 5
                    if event.key == pygame.K_1:
                        self.world_data.curr_lyr = 1
                    if event.key == pygame.K_2:
                        self.world_data.curr_lyr = 2
                    if event.key == pygame.K_3:
                        self.world_data.curr_lyr = 3
                    if event.key == pygame.K_4:
                        self.world_data.curr_lyr = 4

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.scroll_left = False
                    if event.key == pygame.K_RIGHT:
                        self.scroll_right = False
                    if event.key == pygame.K_RSHIFT:
                        self.scroll_speed = 1

                # mouse events
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # get mouse position
                    pos = pygame.mouse.get_pos()
                    x = (pos[0] + self.scroll) // self.tileset_config.tile_size
                    y = pos[1] // self.tileset_config.tile_size

                    # check that the coordinates are within the map area
                    # only process interactions on the map if no file dialog is open!
                    if all([fd is None for fd in [self.file_dialog_save, self.file_dialog_load, self.file_dialog_tileset]]) and pos[0] < self.SCREEN_WIDTH and pos[1] < self.SCREEN_HEIGHT:
                        # update graph value 
                        if self.special_btn_idx == self.GRAPH_IDX:
                            self.graph_data.update_value(x, y)

                        # update character pos
                        if self.special_btn_idx == self.PLAYER_IDX:
                            self.world_data.add_character_data("player", "player", 100, x, y, self.scroll)
                        elif self.special_btn_idx == self.ENEMY_IDX:
                            self.world_data.add_character_data("enemy", "catcher", 100, x, y, self.scroll)
                        elif self.event_window is None and self.special_btn_idx == self.TRIGGER_IDX:
                            self.event_window = EventWindow(EventPart.TRIGGER, 1, x, y, list(self.world_data.character_dict.keys()), self.ui_manager)
                        elif self.event_window is None and self.special_btn_idx == self.ACTION_IDX:
                            self.event_window = EventWindow(EventPart.ACTION, 1, x, y, list(self.world_data.character_dict.keys()), self.ui_manager)

                    else:
                        if self.save_button.check_button_click():
                            self.file_dialog_save = UIFileDialog(pygame.Rect(160, 50, 440, 500), self.ui_manager, window_title="Save map data...", initial_file_path="./")
                        if self.load_button.check_button_click():
                            # file_path = easygui.fileopenbox(msg="Select file to open...", title="Open...", filetypes=["*.bin"])
                            self.file_dialog_load = UIFileDialog(pygame.Rect(160, 50, 440, 500), self.ui_manager, window_title="Load map data...", initial_file_path="./")
                        if self.load_tileset_button.check_button_click():
                            self.file_dialog_tileset = UIFileDialog(pygame.Rect(160, 50, 440, 500), self.ui_manager, window_title="Choose tileset directory...",  initial_file_path="./", allow_picking_directories=True)

                        for idx, btn in enumerate(self.button_list):
                            button_click = btn.check_button_click()
                            if button_click == button.MouseClick.LEFT:
                                self.current_tile = idx
                                self.special_btn_idx = None
                            elif self.current_tile == idx and button_click == button.MouseClick.RIGHT:
                                self.tileset_config.tile_obstacles.append(idx)

                        for idx, btn in enumerate(self.special_button_list):
                            if btn.check_button_click():
                                self.current_tile = None
                                self.special_btn_idx = idx

                if event.type == pygame.MOUSEBUTTONUP:
                    self.save_button.check_button_up()
                    self.load_button.check_button_up()
                    self.load_tileset_button.check_button_up()
                    for btn in self.button_list:
                        btn.check_button_up()
                    for btn in self.special_button_list:
                        btn.check_button_up()
            
                # this is necessary to process events in the pygame gui manager
                self.ui_manager.process_events(event)

            # update tile value
            mouse_click = pygame.mouse.get_pressed()
            pos = pygame.mouse.get_pos()
            if mouse_click[0] and self.current_tile is not None and pos[0] < self.SCREEN_WIDTH and pos[1] < self.SCREEN_HEIGHT:
                x = (pos[0] + self.scroll) // self.tileset_config.tile_size
                y = pos[1] // self.tileset_config.tile_size
                self.world_data.update_tile_value(x, y, self.current_tile)
                            
            self.ui_manager.update(time_delta)
            self.ui_manager.draw_ui(self.screen)

            pygame.display.update()

        pygame.quit()


if __name__ == "__main__":
    le = LevelEditorMain()
    le.main_loop()

