import pygame
import pygame_gui
import json
from enum import Enum
from collections import defaultdict


class EventPart(Enum):
    TRIGGER="Trigger"
    ACTION="Action"


class EventWindow(pygame_gui.elements.UIWindow):
    EVENT_WINDOW_WIDTH=400
    EVENT_WINDOW_HEIGHT=500
    
    def __init__(self, event_part: EventPart, obj_id, x_pos, y_pos, world_obj_ids, ui_manager, window_position=(100, 100)):
        super().__init__(rect=pygame.Rect(window_position, (self.EVENT_WINDOW_WIDTH, self.EVENT_WINDOW_HEIGHT)), manager=ui_manager, window_display_title=event_part.value)
        x = 2
        y = 20
        self.content_info = defaultdict(list)
        self.world_obj_ids = world_obj_ids

        # obj id label
        self.obj_id = obj_id
        obj_id_label_rect = pygame.Rect((x, y), (100, 30))
        self.obj_id_label = pygame_gui.elements.UILabel(relative_rect=obj_id_label_rect, text=f"{event_part.value} ID", manager=ui_manager, container=self)
        obj_id_val_label_rect = pygame.Rect((x + 120, y), (100, 30))
        self.obj_id_value_label = pygame_gui.elements.UILabel(relative_rect=obj_id_val_label_rect, text=f"{self.obj_id}", manager=ui_manager, container=self)
        y += 40

        # create position field
        self.pos_label, self.pos_label_value = self.__create_position_field__(x, y, x_pos, y_pos)
        y += 40

        # type label
        label_rect = pygame.Rect((x, y), (100, 30))
        self.type_label = pygame_gui.elements.UILabel(relative_rect=label_rect, text=f"{event_part.value} Type", manager=ui_manager, container=self)
        self.type_label.normal_text = (255, 255, 255)

        # drop menu trigger type
        self.type_data = self.__load_event_part_types__(event_part)
        drop_menu_rect = pygame.Rect((x + 120, y), (200, 30))
        #items = [('Item 1', 'item1'), ('Item 2', 'item2'), ('Item 3', 'item3')]
        first_item = list(self.type_data.keys())[0]
        self.drop_menu = pygame_gui.elements.ui_drop_down_menu.UIDropDownMenu(options_list=list(self.type_data.keys()),
                                                                             starting_option=first_item,
                                                                             relative_rect=drop_menu_rect,
                                                                             manager=self.ui_manager,
                                                                             container=self)
        y += 40
        self.type_dependent_x_start = x
        self.type_dependent_y_start = y
        self.type_field_labels = list()
        self.type_fields = list()
        self.btn_add = None
        self.textfield = None
        self.btn_cancel = None
        self.btn_ok = None
        x, y = self.__create_type_dependent_fields__(x, y, first_item)
        x, y = self.__add_event_part_info__(x, y)
        self.__add_cancel_ok_buttons__(x, y)

    def __load_event_part_types__(self, event_part):
        event_part_file_template = "event_triggers_list" if event_part == EventPart.TRIGGER else "event_actions_list"
        with open(event_part_file_template, 'r') as f:
            data = json.loads(f.read())

        return data

    def __create_label__(self, x, y, text):
        # label
        label_rect = pygame.Rect((x, y), (100, 30))
        label = pygame_gui.elements.UILabel(relative_rect=label_rect, text=text, manager=self.ui_manager, container=self)

        return label

    def __create_position_field__(self, x, y, x_pos, y_pos):
        label = self.__create_label__(x, y, "Position")

        # position field
        pos_rect = pygame.Rect((x + 120, y), (100, 30))
        pos_label = pygame_gui.elements.UILabel(relative_rect=pos_rect, text=f"({x_pos}, {y_pos})", manager=self.ui_manager, container=self)

        return label, pos_label

    def __create_type_dependent_fields__(self, x, y, item):
        for l in self.type_field_labels:
            l.kill()
        for f in self.type_fields:
            f.kill()

        # create type dependent fields
        self.type_field_labels = list()
        self.type_fields = list()

        for k, _ in self.type_data[item].items():
            if k == "pos":
                continue
            if k == "obj_id":
                label, field = self.__create_drop_menu_field__(x, y, k, self.world_obj_ids)
            else:
                label, field = self.__create_text_entry_field__(x, y, k)
            self.type_field_labels.append(label)
            self.type_fields.append(field)
            y += 40

        return x, y
    
    def __create_drop_menu_field__(self, x, y, name, item_list):
        label = self.__create_label__(x, y, name)
        drop_menu_rect = pygame.Rect((x + 120, y), (200, 30))
        drop_menu = pygame_gui.elements.ui_drop_down_menu.UIDropDownMenu(options_list=item_list, 
                                        starting_option=item_list[0], relative_rect=drop_menu_rect,
                                        manager=self.ui_manager, container=self)
        return label, drop_menu

    def __create_text_entry_field__(self, x, y, label_name):
        label = self.__create_label__(x, y, label_name)

        # text entry field
        te_rect = pygame.Rect((x + 120, y), (100, 30))
        te = pygame_gui.elements.UITextEntryLine(relative_rect=te_rect, manager=self.ui_manager, container=self)

        return label, te

    def __add_event_part_info__(self, x, y):
        if self.btn_add:
            self.btn_add.kill()
        if self.textfield:
            self.textfield.kill()

        # add button
        add_btn_rect = pygame.Rect((x + 250, y), (100, 25))
        self.btn_add = pygame_gui.elements.UIButton(relative_rect=add_btn_rect, text="Add", manager=self.ui_manager, container=self)
        y += 40

        # event part info
        print(self.content_info)
        content = json.dumps(self.content_info)
        print(content)
        textbox_rect = pygame.Rect((x, y), (350, 150))
        self.textfield = pygame_gui.elements.UITextBox(relative_rect=textbox_rect, html_text=content, manager=self.ui_manager, container=self)
        self.textfield.enable()
        y += 150

        return x, y

    def __add_cancel_ok_buttons__(self, x, y):
        if self.btn_ok:
            self.btn_ok.kill()
        if self.btn_cancel:
            self.btn_cancel.kill()

        # ok/cancel buttons
        btn_ok_rect = pygame.Rect((x + 250, y), (100, 25))
        self.btn_ok = pygame_gui.elements.UIButton(relative_rect=btn_ok_rect, text="Ok", manager=self.ui_manager, container=self)
        btn_cancel_rect = pygame.Rect((x + 150, y), (100, 25))
        self.btn_cancel = pygame_gui.elements.UIButton(relative_rect=btn_cancel_rect, text="Cancel", manager=self.ui_manager, container=self)
        
    def drop_menu_item_changed(self, selected_item):
        x = self.type_dependent_x_start
        y = self.type_dependent_y_start
        if selected_item in self.type_data:
            x, y = self.__create_type_dependent_fields__(self.type_dependent_x_start, self.type_dependent_y_start, selected_item)
        x, y = self.__add_event_part_info__(x, y)
        self.__add_cancel_ok_buttons__(x, y)

    def add_button_pressed(self):
        new_content_info = dict()
        for k, v in zip(self.type_field_labels, self.type_fields):
            print(type(v))
            if type(v) == pygame_gui.elements.UIDropDownMenu:
                value = v.selected_option
            else:
                value = v.get_text()
            new_content_info[k.text] = value
        self.content_info[self.drop_menu.selected_option].append(new_content_info)
        content = json.dumps(self.content_info)
        self.textfield.set_text(content)

