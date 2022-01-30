"""
>> Basic display manager for Micropython <<

Currently only menus with submenus are supported.

The 'main' function runs a simple testcase on an SSD1306 128x64 OLED display.

Diamino 2022
"""

DM_EVENT_UP = 0
DM_EVENT_DOWN = 1
DM_EVENT_LEFT = 2
DM_EVENT_RIGHT = 3
DM_EVENT_BUTTON_DOWN = 4
DM_EVENT_BUTTON_UP = 5
DM_EVENT_REDRAW = 6

class Screen():

    def __init__(self):
        self.displaymanager = None
        self.backscreen = None
        self.display = None

    def register_displaymanager(self, dm):
        self.displaymanager = dm
        # Cache reference to display
        self.display = self.displaymanager.display
        self.cache_display_properties()

    # Overload this method to cache properties or calculate properties based on
    #  the display properties
    def cache_display_properties(self):
        pass

    def registerback(self, back):
        self.backscreen = back

    def handle_event(self, event):
        if event == DM_EVENT_REDRAW:
            self.redraw()

    def redraw(self):
        self.display.fill(0)
        self.display.show()

class MenuItem():

    def __init__(self, name, callback = None):
        self.name = name
        self.callback = callback

class MenuItemSubmenu(MenuItem):

    def __init__(self, name, submenu, **kwargs):
        super().__init__(name, **kwargs)
        self.submenu = submenu

class MenuItemOption(MenuItem):

    def __init__(self, name, enabled=False, **kwargs):
        super().__init__(name, **kwargs)
        self.enabled = enabled
    
    def toggle(self):
        self.enabled = not self.enabled

class MenuItemBack(MenuItem):
    pass

class ScreenTitle(Screen):

    title_height = 16    
    top_margin = 3
    left_margin = 5

    def __init__(self, title=None):
        super().__init__()
        self.title = title

    def draw_titlebar(self):
        self.display.fill_rect(0, 0, self.display.width, self.title_height, 1)
        if self.title:
            self.display.text(self.title, self.left_margin, self.top_margin, 0)


class ScreenMenu(ScreenTitle):

    item_height = 12

    def __init__(self, items, activeitem = 0, **kwargs):
        super().__init__(**kwargs)
        self.items = items
        self.activeitem = activeitem
        self.top_item = 0

    def cache_display_properties(self):
        super().cache_display_properties()
        self.items_on_screen = int((self.display.height - self.title_height) / self.item_height)

    def handle_event(self, event):
        if event == DM_EVENT_UP:
            if self.activeitem > 0: # not on top of menu
                previtem = self.activeitem
                self.activeitem -= 1
                activeline = previtem - self.top_item
                if activeline == 0: # Scroll
                    self.top_item -= 1
                    self.redraw()
                else: # only update changed items
                    self.draw_menuitem(activeline)
                    self.draw_menuitem(activeline - 1)
                    self.display.show()
        elif event == DM_EVENT_DOWN:
            if self.activeitem < (len(self.items) - 1): # not at end of menu
                previtem = self.activeitem
                self.activeitem += 1
                activeline = previtem - self.top_item
                if activeline == (self.items_on_screen - 1): # Scroll
                    self.top_item += 1
                    self.redraw()
                else: # only update changed items
                    self.draw_menuitem(activeline)
                    self.draw_menuitem(activeline + 1)
                    self.display.show()
        elif event == DM_EVENT_BUTTON_DOWN:
            activeitem = self.items[self.activeitem]
            if isinstance(activeitem, MenuItemBack):
                self.displaymanager.transition(self.backscreen)
            elif isinstance(activeitem, MenuItemSubmenu):
                self.displaymanager.transition(activeitem.submenu, True)
            elif isinstance(activeitem, MenuItemOption):
                activeitem.toggle()
                self.draw_menuitem(self.activeitem - self.top_item) # Redraw menu item
                self.display.show()
            if activeitem.callback:
                activeitem.callback(self)
        else:
            # Not implemented here. Call super event handler
            super().handle_event(event)

    def draw_menuitem(self, linenr):
        itemnr = self.top_item + linenr
        if itemnr >= len(self.items):
            return
        active = (itemnr == self.activeitem)
        item = self.items[itemnr]
        self.display.fill_rect(0, (linenr*self.item_height)+self.title_height, self.display.width, self.item_height, active)
        self.display.text(item.name, self.left_margin, (linenr*self.item_height)+self.title_height+1, not active)
        if isinstance(item, MenuItemSubmenu):
            self.display.text('>', self.display.width - 10, (linenr*self.item_height)+self.title_height+1, not active)
        elif isinstance(item, MenuItemBack):
            self.display.text('<', self.display.width - 10, (linenr*self.item_height)+self.title_height+1, not active)
        elif isinstance(item, MenuItemOption):
            if item.enabled:
                self.display.fill_rect(self.display.width - 10, (linenr*self.item_height)+self.title_height+2, self.item_height - 4, self.item_height - 4, not active)
            else:
                self.display.rect(self.display.width - 10, (linenr*self.item_height)+self.title_height+2, self.item_height - 4, self.item_height - 4, not active)

    def redraw(self):
        self.display.fill(0)
        self.draw_titlebar()
        for line in range(self.items_on_screen):
            self.draw_menuitem(line)
        self.display.show()

class ScreenValue(ScreenTitle):

    def __init__(self, value=0, **kwargs):
        super().__init__(**kwargs)
        self.value = value

    def handle_event(self, event):
        if event == DM_EVENT_BUTTON_DOWN:
            self.displaymanager.transition(self.backscreen)
        else:
            # Not implemented here. Call super event handler
            super().handle_event(event)

    def draw_value(self):
        valuestr = f"{self.value}"
        self.display.text(valuestr, int((self.display.width - len(valuestr)) / 2), int(self.display.height / 2), 1)

    def redraw(self):
        self.display.fill(0)
        self.draw_titlebar()
        self.draw_value()
        self.display.show()

class DisplayManager():

    def __init__(self, display, startscreen):
        self.display = display
        self.activescreen = startscreen
        self.activescreen.register_displaymanager(self)

    def redraw(self):
        self.activescreen.redraw()

    def transition(self, newscreen, registerback=False):
        if registerback:
            newscreen.registerback(self.activescreen)
        newscreen.register_displaymanager(self)
        self.activescreen = newscreen
        self.redraw()

    def handle_event(self, event):
        self.activescreen.handle_event(event)

# Simple testcase using SSD1306 OLED display
def main():
    from machine import Pin, I2C
    from ssd1306 import SSD1306_I2C
    import time

    I2C_ID = 0
    I2C_SCL_PIN = 13
    I2C_SDA_PIN = 12
    I2C_FREQ = 200000

    OLED_WIDTH = 128
    OLED_HEIGHT = 64
    
    i2c = I2C(I2C_ID, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=I2C_FREQ)

    oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)

    def subitem2_2_handler(screen):
        print("Subitem 2.2 handler called...")

    valuescreen = ScreenValue(value = 42, title = "Test")

    submenu2 = ScreenMenu((MenuItemOption('Subitem 2.1'),
                           MenuItem('Subitem 2.2', callback = subitem2_2_handler),
                           MenuItemOption('Subitem 2.3', enabled=True),
                           MenuItemBack('Back')),
                           title="Submenu 2")
    submenu3 = ScreenMenu((MenuItem('Subitem 3.1'),
                           MenuItem('Subitem 3.2'),
                           MenuItemSubmenu('Subitem 3.3', valuescreen),
                           MenuItem('Subitem 3.4'),
                           MenuItem('Subitem 3.5'),
                           MenuItem('Subitem 3.6'),
                           MenuItemBack('Back')),
                           title="Submenu 3")
    submenu1 = ScreenMenu((MenuItem('Subitem 1.1'),
                           MenuItemSubmenu('Subitem 1.2', submenu3),
                           MenuItemBack('Back')),
                           title="Submenu 1")
    menu1 = ScreenMenu((MenuItemSubmenu('Submenu 1', submenu1),
                        MenuItemSubmenu('Submenu 2', submenu2),
                        MenuItemSubmenu('Submenu 3', submenu3)),
                        title="Main Menu")

    dm = DisplayManager(oled, menu1)

    ## Basic testcase
    testevents = [DM_EVENT_REDRAW,      # Draw menu on screen
                  DM_EVENT_DOWN,        # Select Submenu 2
                  DM_EVENT_BUTTON_DOWN, # Enter Submenu 2
                  DM_EVENT_BUTTON_DOWN, # Toggle Subitem 2.1 (option item)
                  DM_EVENT_DOWN,        # Select Subitem 2.2
                  DM_EVENT_UP,          # Select Subitem 2.1
                  DM_EVENT_UP,          # Should be ignored (already on first item)
                  DM_EVENT_DOWN,        # Select Subitem 2.2
                  DM_EVENT_BUTTON_DOWN, # Activate Subitem 2.2 (callback called)
                  DM_EVENT_DOWN,        # Select Subitem 2.3
                  DM_EVENT_BUTTON_DOWN, # Toggle Subitem 2.3 (option item)
                  DM_EVENT_BUTTON_DOWN, # Toggle Subitem 2.3 (option item)
                  DM_EVENT_DOWN,        # Select Back
                  DM_EVENT_BUTTON_DOWN, # Go back to 'Main' menu
                  DM_EVENT_UP,          # Select Submenu 1
                  DM_EVENT_BUTTON_DOWN, # Enter Submenu 1
                  DM_EVENT_DOWN,        # Select Subitem 1.2
                  DM_EVENT_BUTTON_DOWN, # Enter Subitem 1.2 (=submenu 3)
                  DM_EVENT_DOWN, # 3.2
                  DM_EVENT_DOWN, # 3.3
                  DM_EVENT_DOWN, # 3.4
                  DM_EVENT_DOWN, # 3.5
                  DM_EVENT_DOWN, # 3.6
                  DM_EVENT_UP,   # 3.5
                  DM_EVENT_UP,   # 3.4
                  DM_EVENT_UP,   # 3.3
                  DM_EVENT_BUTTON_DOWN, # Enter 3.3 (Value screen)
                  DM_EVENT_BUTTON_DOWN, # Return from Value screen
                  DM_EVENT_UP,   # 3.2
                  DM_EVENT_UP,   # 3.1
                  DM_EVENT_UP,   # should be ignored (already on first item)
                  DM_EVENT_DOWN, # 3.2
                  DM_EVENT_DOWN, # 3.3
                  DM_EVENT_DOWN, # 3.4
                  DM_EVENT_DOWN, # 3.5
                  DM_EVENT_DOWN, # 3.6
                  DM_EVENT_DOWN, # Back
                  DM_EVENT_DOWN, # Should be ignored (already on last item)
                  DM_EVENT_BUTTON_DOWN, # Back to submenu 1
                  DM_EVENT_DOWN, # Select back
                  DM_EVENT_BUTTON_DOWN, # Back to main menu
                  DM_EVENT_REDRAW,]

    for event in testevents:
        dm.handle_event(event)
        time.sleep(1)

if __name__ == "__main__":
    main()