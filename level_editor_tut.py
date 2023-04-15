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
from level_data import TilesetConfig, WorldData, GraphData
from level_colors import *
from level_text import *


pygame.init()

clock = pygame.time.Clock()
FPS = 30

# window
SCREEN_WIDTH = 1055
SCREEN_HEIGHT = 800
LOWER_MARGIN = 100
SIDE_MARGIN = 500 

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption('Level Editor')

# define game variables
ROWS = 16
MAX_COLS = 150
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1
img_list = list()
button_list = list()
bg_img_list = list()

tileset_config = TilesetConfig("/home/matt/projects/Escaper/res/tiles/station", SCREEN_HEIGHT, ROWS)
world_data = WorldData(ROWS, MAX_COLS, tileset_config)
graph_data = GraphData(ROWS, MAX_COLS, tileset_config)
current_tile = None 

# define fonts
font = pygame.font.SysFont('Futura', 30)
font_small = pygame.font.SysFont('Futura', 20)

# gui elements
ui_manager = pygame_gui.UIManager((800, 600), "gui_theme_v2.json")
file_dialog_tileset = None
file_dialog_save = None
file_dialog_load = None

def load_background_images(bg_img_path_list):
    # load background images
    bg_img_list = list()
    for bg_img_path in bg_img_path_list:
        bg_img_list.append(pygame.image.load(bg_img_path).convert_alpha())

    return bg_img_list

#pine1_img = pygame.image.load('img/Background/pine1.png').convert_alpha()
#pine2_img = pygame.image.load('img/Background/pine2.png').convert_alpha()
#mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha()
#sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()


# create function for drawing background
def draw_bg():
    screen.fill(BLUE)
    #width = sky_img.get_width()
    #for x in range(4):
    #    screen.blit(sky_img, ((x * width) - scroll * 0.5, 0))
    #    screen.blit(mountain_img, ((x * width) - scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
    #    screen.blit(pine1_img, ((x * width) - scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
    #    screen.blit(pine2_img, ((x * width) - scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))

# draw grid
def draw_grid():
    # vertical lines
    for c in range(MAX_COLS + 1):
        pygame.draw.line(screen, WHITE, (c * tileset_config.tile_size - scroll, 0), (c * tileset_config.tile_size - scroll, SCREEN_HEIGHT))
    # horizontal lines
    for c in range(ROWS + 1):
        pygame.draw.line(screen, WHITE, (0, c * tileset_config.tile_size), (SCREEN_WIDTH, c * tileset_config.tile_size))


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

save_button = button.Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT + LOWER_MARGIN - 50, 
        [save_img, save_img_hovering, save_img_clicked], 1)
load_button = button.Button(SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT + LOWER_MARGIN - 50, 
        [load_img, load_img_hovering, load_img_clicked], 1)
load_tileset_button = button.Button(SCREEN_WIDTH // 2 + 250, SCREEN_HEIGHT + LOWER_MARGIN - 50, 
        [load_tileset_img, load_tileset_img_hovering, load_tileset_img_clicked], 1)

open_save_dialog = False
open_load_dialog = False
open_load_tileset_dialog = False

# obstacle marker
img_obstacle = pygame.image.load('img/wall.png').convert_alpha()
tile_obstacles = list()

# special buttons
GRAPH_IDX = 0
CHARACTER_IDX = 1
TRIGGER_IDX = 2
ACTION_IDX = 3
special_button_list = list()

# init graph related attributes
img_graph_mode = pygame.image.load('img/graph_mode.png').convert_alpha()
img_graph_mode = pygame.transform.scale(img_graph_mode, (tileset_config.tile_size, tileset_config.tile_size))
graph_mode_btn = button.Button(SCREEN_WIDTH + 20, SCREEN_HEIGHT + LOWER_MARGIN - 80, [img_graph_mode], 1)
special_button_list.append(graph_mode_btn)
special_btn_idx = None


def load_tile_images(dir_path):
    # store tiles in a list
    img_list = []
    num_tiles = len([f for f in os.listdir(dir_path) if f.endswith('.png') and os.path.isfile(os.path.join(dir_path, f))])
    for x in range(num_tiles):
        img = pygame.image.load(f'{dir_path}/tile_{x}.png').convert_alpha()
        img = pygame.transform.scale(img, (tileset_config.tile_size, tileset_config.tile_size))
        img_list.append(img)

    return img_list

def create_tile_buttons(img_list):
    # make a button list
    button_list = []
    button_col = 0
    button_row = 0
    space_w = 40
    space_h = 40
    margin_w = 20
    margin_h = 20
    for i in range(len(img_list)):
        tile_button = button.Button(SCREEN_WIDTH + margin_w + (tileset_config.tile_size_w + space_w) * button_col, 
                margin_h + (tileset_config.tile_size_h + space_h) * button_row, [img_list[i]], 1)
        button_list.append(tile_button)
        button_col += 1
        if button_col == tileset_config.TILE_PANEL_COLS:
            button_row += 1
            button_col = 0

    return button_list

def save_map(file_path_name):
    # save level data
    # level_file_names = list()
    # for lyr in range(MAX_LAYERS):
    #    level_file_name = f"lvl_{level}_lyr_{lyr}_data.csv"
    #    with open(level_file_name, 'w', newline='') as csvfile:
    #        writer = csv.writer(csvfile, delimiter = ',')
    #        for row in world_data[lyr]:
    #            writer.writerow(row)
    #    level_file_names.append(level_file_name)
    #level_data_dict = {"level_files": level_file_names, "tileset": tileset_dir_path}
    #with open(f'lvl_{level}.json', 'w') as f:
    #    json.dump(level_data_dict, f)

    # alternative pickle method
    pickle_out = open(file_path_name, 'wb')
    pickle.dump({"world_data": world_data, 
                 "tileset_config": tileset_config,
                 "graph_data": graph_data}, pickle_out)
    pickle_out.close()

def load_map(file_path):
    # load in level data
    if file_path is not None and os.path.exists(file_path):
        # reset scroll back to the start of the level
        scroll = 0
       # with open(file_path) as f:
       #     level_data_dict = json.load(f)

       # csv_file_paths = level_data_dict["level_files"]
       # for csv_file in csv_file_paths:
       #     with open(csv_file, 'r') as csvfile:
       #         lyr = int(csv_file.split("_")[3])
       #         reader = csv.reader(csvfile, delimiter = ',')
       #         for x, row in enumerate(reader):
       #             for y, tile in enumerate(row):
       #                 world_data[lyr][x][y] = int(tile)
       # img_list, button_list, tileset_dir_path = load_tileset(level_data_dict["tileset"])
        # alternative pickle method
        pickle_in = open(file_path, 'rb')
        data_dict = pickle.load(pickle_in)
        tileset_config = data_dict["tileset_config"]
        world_data = data_dict["world_data"]
        graph_data = data_dict["graph_data"]
        img_list, button_list = load_tileset(tileset_config.tileset_dir_path)

        return world_data, graph_data, tileset_config, img_list, button_list

def load_tileset(dir_path):
    img_list = button_list = list()
    # dir_path = easygui.diropenbox(msg="Choose directory containing tileset images...")
    if dir_path is not None and os.path.exists(dir_path):
        img_list = load_tile_images(dir_path)
        button_list = create_tile_buttons(img_list)
    else:
        print(f"ERR: could not open tileset! Is the path correct?")

    return img_list, button_list


run = True
while run:
    time_delta = clock.tick(FPS) / 1000.0

    draw_bg()
    draw_grid()
    world_data.draw_world(screen, scroll, img_list)
    graph_data.draw_graph(screen, scroll)

    draw_text(screen, f'Current Level: {world_data.level}', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 90)
    draw_text(screen, '(Press UP or DOWN to change level)', font_small, WHITE, 200, SCREEN_HEIGHT + LOWER_MARGIN - 85)
    draw_text(screen, f'Current Layer: {world_data.curr_lyr}', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 60)
    draw_text(screen, f'(Press 1-{world_data.MAX_LAYERS} to change layer)', font_small, WHITE, 200, SCREEN_HEIGHT + LOWER_MARGIN - 55)
    draw_text(screen, f'{world_data.LYR_DESCR[world_data.curr_lyr]}', font_small, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 40)

    # draw buttons
    save_button.draw(screen)
    load_button.draw(screen)
    load_tileset_button.draw(screen)

    for btn in special_button_list:
        btn.draw(screen)

    # draw tile panel and tiles
    pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT))

    # draw tiles
    for btn in button_list:
        btn.draw(screen)

    # draw obstacle markers
    for obstacle_idx in tile_obstacles:
        x_pos = SCREEN_WIDTH + (int(obstacle_idx % tileset_config.TILE_PANEL_COLS) * tileset_config.tile_size_w + tileset_config.tile_size_w) * tileset_config.tile_scale_factor
        y_pos = (int(obstacle_idx / tileset_config.TILE_PANEL_COLS) * tileset_config.tile_size_w + tileset_config.size_h / 2) * tileset_config.tile_scale_factor
        screen.blit(img_obstacle, (x_pos, y_pos))

    # highlight the selected tile or special button
    if current_tile is not None and special_btn_idx is None:
        pygame.draw.rect(screen, RED, button_list[current_tile].rect, 3)
    elif current_tile is None and special_btn_idx is not None:
        pygame.draw.rect(screen, YELLOW, special_button_list[special_btn_idx].rect, 3)

    # scroll the map
    if scroll_left == True and scroll > 0:
        scroll -= 5 * scroll_speed
    if scroll_right == True and scroll < (MAX_COLS * tileset_config.tile_size) - SCREEN_WIDTH:
        scroll += 5 * scroll_speed

    # update buttons
    save_button.update()
    load_button.update()
    load_tileset_button.update()
    for btn in button_list:
        btn.update()
    for btn in special_button_list:
        btn.update()

    if open_save_dialog:
        file_dialog_save = UIFileDialog(pygame.Rect(160, 50, 440, 500), ui_manager, window_title="Save map data...", initial_file_path="./")
    elif open_load_dialog:
        # file_path = easygui.fileopenbox(msg="Select file to open...", title="Open...", filetypes=["*.bin"])
        file_dialog_load = UIFileDialog(pygame.Rect(160, 50, 440, 500), ui_manager, window_title="Load map data...", initial_file_path="./")
    elif open_load_tileset_dialog:
        file_dialog_tileset = UIFileDialog(pygame.Rect(160, 50, 440, 500), ui_manager, window_title="Choose tileset directory...",  initial_file_path="./", allow_picking_directories=True)

    open_save_dialog = False
    open_load_dialog = False
    open_load_tileset_dialog = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        # gui events
        if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
            if event.ui_element == file_dialog_save:
                print(f"saving data to {event.text}")
                # file_path_name = easygui.filesavebox("Select save file path...", "Save...", f"lvl_{level}_data.bin", ["*.bin"])
                save_map(event.text)
            if event.ui_element == file_dialog_load:
                print(f"loading data from file {event.text}")
                world_data, graph_data, tileset_config, img_list, button_list = load_map(event.text)
            if event.ui_element == file_dialog_tileset:
                print(f"loading tileset {event.text}")
                tileset_dir_path = event.text
                img_list, button_list = load_tileset(event.text)

        # mouse events
        if event.type == pygame.MOUSEBUTTONDOWN:
            # get mouse position
            pos = pygame.mouse.get_pos()
            x = (pos[0] + scroll) // tileset_config.tile_size
            y = pos[1] // tileset_config.tile_size

            # check that the coordinates are within the map area
            if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
                # update tile value
                if current_tile is not None:
                    world_data.update_tile_value(x, y, current_tile)
                
                # update graph value 
                if special_btn_idx == GRAPH_IDX:
                    graph_data.update_value(x, y)
            else:
                if save_button.check_button_click():
                    open_save_dialog = True
                if load_button.check_button_click():
                    open_load_dialog = True
                if load_tileset_button.check_button_click():
                    open_load_tileset_dialog = True

                for idx, btn in enumerate(button_list):
                    button_click = btn.check_button_click()
                    if button_click == button.MouseClick.LEFT:
                        current_tile = idx
                        special_btn_idx = None
                    elif current_tile == idx and button_click == button.MouseClick.RIGHT:
                        tile_obstacles.append(idx)

                for idx, btn in enumerate(special_button_list):
                    if btn.check_button_click():
                        current_tile = None
                        special_btn_idx = idx

        if event.type == pygame.MOUSEBUTTONUP:
            save_button.check_button_up()
            load_button.check_button_up()
            load_tileset_button.check_button_up()
            for btn in button_list:
                btn.check_button_up()
            for btn in special_button_list:
                btn.check_button_up()

        # keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                level += 1
            if event.key == pygame.K_DOWN and level > 0:
                level -= 1
            if event.key == pygame.K_LEFT:
                scroll_left = True
            if event.key == pygame.K_RIGHT:
                scroll_right = True
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 5
            if event.key == pygame.K_1:
                world_data.curr_lyr = 1
            if event.key == pygame.K_2:
                world_data.curr_lyr = 2
            if event.key == pygame.K_3:
                world_data.curr_lyr = 3
            if event.key == pygame.K_4:
                world_data.curr_lyr = 4

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                scroll_left = False
            if event.key == pygame.K_RIGHT:
                scroll_right = False
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 1
        
        ui_manager.process_events(event)

    ui_manager.update(time_delta)
    ui_manager.draw_ui(screen)

    pygame.display.update()

pygame.quit()

