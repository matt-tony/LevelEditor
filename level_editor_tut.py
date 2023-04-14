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
TILE_SIZE = SCREEN_HEIGHT // ROWS
level = 0
current_tile = None
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1
TILE_SIZE_W = 16
TILE_SIZE_H = 16
tileset_dir_path = None

bg_img_list = list()
img_list = list()
button_list = list()

# define colours
RED = (200, 25, 25)
GREEN = (144, 201, 120)
BLUE = (80, 120, 200)
YELLOW = (200, 200, 20)
MAGENTA = (20, 100, 200)
GRAY = (50, 50, 50)
WHITE = (255, 255, 255)

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

# define fonts
font = pygame.font.SysFont('Futura', 30)
font_small = pygame.font.SysFont('Futura', 20)
font_graph = pygame.font.SysFont('Futura', 25, bold=True)

# create empty tile list
# lyr 0: Background image layer
# lyr 1: Background layer 1 (default tile layer)
# lyr 2: Background layer 2
# lyr 3: Background layer 3
# lyr 4: Foreground layer
# Note that the Background image layer is reserved for a background image
MAX_LAYERS = 4
lyr_descr = {1: "Default background tile layer", 2: "Layer used to set elevators and stuff with alpha channel", 
        3: "Layer that can be used to set decorations (e.g. blood traces, dust, etc.)", 
        4: "Foreground layer that stores stuff that is in front of the player"}
curr_lyr = 1
world_data = defaultdict(list)
for lyr in range(MAX_LAYERS):
    for row in range(ROWS):
        r = [-1] * MAX_COLS
        world_data[lyr].append(r)

    # create ground
    for tile in range(0, MAX_COLS):
        world_data[lyr][ROWS - 1][tile] = 0

# init graph data
graph_data = list()
node_positions = dict()
edges = set()
node_id = 0
node_selected = -1
for row in range(ROWS):
    r = [-1] * MAX_COLS
    graph_data.append(r)

# function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


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
        pygame.draw.line(screen, WHITE, (c * TILE_SIZE - scroll, 0), (c * TILE_SIZE - scroll, SCREEN_HEIGHT))
    # horizontal lines
    for c in range(ROWS + 1):
        pygame.draw.line(screen, WHITE, (0, c * TILE_SIZE), (SCREEN_WIDTH, c * TILE_SIZE))


# function for drawing the world tiles
def draw_world():
    if len(img_list) > 0:
        for lyr in range(MAX_LAYERS):
            for y, row in enumerate(world_data[lyr]):
                for x, tile in enumerate(row):
                    if tile >= 0:
                        screen.blit(img_list[tile], (x * TILE_SIZE - scroll, y * TILE_SIZE))

# function for drawing graph data
def draw_graph():
    # draw edges
    for node1, node2 in edges:
        y1, x1 = node_positions[node1]
        y2, x2 = node_positions[node2]
        x_pos_start = x1 * TILE_SIZE + TILE_SIZE/2 - scroll
        y_pos_start = y1 * TILE_SIZE + TILE_SIZE/2
        x_pos_end = x2 * TILE_SIZE + TILE_SIZE/2 - scroll
        y_pos_end = y2 * TILE_SIZE + TILE_SIZE/2
        pygame.draw.line(screen, GRAY, (x_pos_start, y_pos_start), (x_pos_end, y_pos_end), width=5)

    # draw nodes
    for y, row in enumerate(graph_data):
        for x, node in enumerate(row):
            if node >= 0:
                x_pos = x * TILE_SIZE + TILE_SIZE/4 - scroll
                y_pos = y * TILE_SIZE + TILE_SIZE/4
                img = img_node_selected if node == node_selected else img_node
                screen.blit(img, (x_pos, y_pos))
                font_x_pos = x_pos + TILE_SIZE/(6 + len(str(node)))
                draw_text(f'{node}', font_graph, GRAY, font_x_pos, y_pos + TILE_SIZE/6)

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
img_graph_mode = pygame.transform.scale(img_graph_mode, (TILE_SIZE, TILE_SIZE))
img_node = pygame.image.load('img/node.png').convert_alpha()
img_node = pygame.transform.scale(img_node, (TILE_SIZE / 2, TILE_SIZE / 2))
img_node_selected = pygame.image.load('img/node_selected.png').convert_alpha()
img_node_selected = pygame.transform.scale(img_node_selected, (TILE_SIZE / 2, TILE_SIZE / 2))
graph_mode_btn = button.Button(SCREEN_WIDTH + 20, SCREEN_HEIGHT + LOWER_MARGIN - 80, [img_graph_mode], 1)
special_button_list.append(graph_mode_btn)
special_btn_idx = None


def load_tile_images(dir_path):
    # store tiles in a list
    img_list = []
    num_tiles = len([f for f in os.listdir(dir_path) if f.endswith('.png') and os.path.isfile(os.path.join(dir_path, f))])
    for x in range(num_tiles):
        img = pygame.image.load(f'{dir_path}/tile_{x}.png').convert_alpha()
        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
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
        tile_button = button.Button(SCREEN_WIDTH + margin_w + (TILE_SIZE_W + space_w) * button_col, 
                margin_h + (TILE_SIZE_H + space_h) * button_row, [img_list[i]], 1)
        button_list.append(tile_button)
        button_col += 1
        if button_col == 8:
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
    pickle.dump({"map_data": world_data, 
                 "tileset": tileset_dir_path, 
                 "tile_size": (TILE_SIZE_W, TILE_SIZE_H),
                 "graph_nodes": graph_data, 
                 "graph_node_positions": node_positions,
                 "graph_edges": edges}, pickle_out)
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
        world_data = None
        pickle_in = open(file_path, 'rb')
        data_dict = pickle.load(pickle_in)
        tileset_dir_path = data_dict["tileset"]
        world_data = data_dict["map_data"]
        graph_data = data_dict["graph_data"]
        node_positions = data_dict["graph_node_positions"]
        edges = data_dict["graph_edges"]
        img_list, button_list = load_tileset(tileset_dir_path)

        return world_data, graph_data, node_positions, edges, tileset_dir_path, img_list, button_list

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
    draw_world()
    draw_graph()

    draw_text(f'Current Level: {level}', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 90)
    draw_text('(Press UP or DOWN to change level)', font_small, WHITE, 200, SCREEN_HEIGHT + LOWER_MARGIN - 85)
    draw_text(f'Current Layer: {curr_lyr}', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 60)
    draw_text(f'(Press 1-{MAX_LAYERS} to change layer)', font_small, WHITE, 200, SCREEN_HEIGHT + LOWER_MARGIN - 55)
    draw_text(f'{lyr_descr[curr_lyr]}', font_small, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 40)

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

    # highlight the selected tile or special button
    if current_tile is not None and special_btn_idx is None:
        pygame.draw.rect(screen, RED, button_list[current_tile].rect, 3)
    elif current_tile is None and special_btn_idx is not None:
        pygame.draw.rect(screen, YELLOW, special_button_list[special_btn_idx].rect, 3)

    # scroll the map
    if scroll_left == True and scroll > 0:
        scroll -= 5 * scroll_speed
    if scroll_right == True and scroll < (MAX_COLS * TILE_SIZE) - SCREEN_WIDTH:
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
                world_data, graph_data, node_positions, edges, tileset_dir_path, img_list, button_list = load_map(event.text)
            if event.ui_element == file_dialog_tileset:
                print(f"loading tileset {event.text}")
                tileset_dir_path = event.text
                img_list, button_list = load_tileset(event.text)

        # mouse events
        if event.type == pygame.MOUSEBUTTONDOWN:
            # get mouse position
            pos = pygame.mouse.get_pos()
            x = (pos[0] + scroll) // TILE_SIZE
            y = pos[1] // TILE_SIZE

            # check that the coordinates are within the map area
            if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
                # update tile value
                if current_tile is not None:
                    if pygame.mouse.get_pressed()[0] == 1:
                        if world_data[curr_lyr][y][x] != current_tile:
                            world_data[curr_lyr][y][x] = current_tile
                    if pygame.mouse.get_pressed()[2] == 1:
                        world_data[curr_lyr][y][x] = -1
                # check graph mode 
                if special_btn_idx == GRAPH_IDX:
                    if pygame.mouse.get_pressed()[0] == 1:
                        if graph_data[y][x] == -1:
                            graph_data[y][x] = node_id
                            node_positions[node_id] = (y, x)
                            node_id += 1
                            node_selected = -1
                        elif node_selected == -1:
                            node_selected = graph_data[y][x]
                        else:
                            edges.add((node_selected, graph_data[y][x]))
                            node_selected = graph_data[y][x]
                    if pygame.mouse.get_pressed()[2] == 1:
                        graph_data[y][x] = -1
            else:
                if save_button.check_button_click():
                    open_save_dialog = True
                if load_button.check_button_click():
                    open_load_dialog = True
                if load_tileset_button.check_button_click():
                    open_load_tileset_dialog = True

                for idx, btn in enumerate(button_list):
                    if btn.check_button_click():
                        current_tile = idx
                        special_btn_idx = None

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
                curr_lyr = 1
            if event.key == pygame.K_2:
                curr_lyr = 2
            if event.key == pygame.K_3:
                curr_lyr = 3
            if event.key == pygame.K_4:
                curr_lyr = 4

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

