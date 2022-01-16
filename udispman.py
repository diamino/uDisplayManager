"""
>> Basic display manager for Micropython <<

Currently only menu's with submenu's are supported.

The 'main' function runs a simple testcase on a SSD1306 128x64 OLED display.

Diamino 2022
"""

DM_EVENT_UP = 0
DM_EVENT_DOWN = 1
DM_EVENT_LEFT = 2
DM_EVENT_RIGHT = 3
DM_EVENT_BUTTON_DOWN = 4
DM_EVENT_BUTTON_UP = 5

DM_TRANS_BACK = 1

class Screen():

    def __init__(self):
        self.displaymanager = None
        self.backscreen = None
        self.display = None

    def register_displaymanager(self, dm):
        self.displaymanager = dm
        # Cache reference to display
        self.display = self.displaymanager.display

    def registerback(self, back):
        self.backscreen = back

    def handle_event(self, event):
        pass

    def redraw(self):
        self.display.fill(0)
        self.display.show()

class ScreenMenu(Screen):

    title_height = 16    
    item_height = 12
    top_margin = 2
    left_margin = 5

    def __init__(self, items, title=None, activeitem = 0):
        super().__init__()
        self.title = title
        self.items = items
        self.activeitem = activeitem

    def handle_event(self, event):
        if event == DM_EVENT_UP:
            if self.activeitem > 0:
                self.draw_menuitem(self.activeitem, False)
                self.activeitem -= 1
                self.draw_menuitem(self.activeitem, True)
                self.display.show()
        elif event == DM_EVENT_DOWN:
            if self.activeitem < (len(self.items) - 1):
                self.draw_menuitem(self.activeitem, False)
                self.activeitem += 1
                self.draw_menuitem(self.activeitem, True)
                self.display.show()
        elif event == DM_EVENT_BUTTON_DOWN:
            target = self.items[self.activeitem][1]
            if target == DM_TRANS_BACK:
                self.displaymanager.transition(self.backscreen)
            elif isinstance(target, Screen):
                self.displaymanager.transition(target, True)
        else:
            # Not implemented here. Call super event handler
            super().handle_event(event)

    def draw_titlebar(self):
        self.display.fill_rect(0, 0, self.display.width, self.title_height, 1)
        if self.title:
            self.display.text(self.title, self.left_margin, self.top_margin, 0)

    def draw_menuitem(self, itemnr, active):
        self.display.fill_rect(0, (itemnr*self.item_height)+self.title_height, self.display.width, self.item_height, active)
        self.display.text(self.items[itemnr][0], self.left_margin, (itemnr*self.item_height)+self.title_height+1, not active)

    def redraw(self):
        self.display.fill(0)
        self.draw_titlebar()
        for i, _ in enumerate(self.items):
            self.draw_menuitem(i, i == self.activeitem)
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

    submenu1 = ScreenMenu((('Subitem 1.1', None),
                           ('Subitem 1.2', None),
                           ('Back', DM_TRANS_BACK)),
                           title="Submenu 1")
    submenu2 = ScreenMenu((('Subitem 2.1', None),
                           ('Subitem 2.2', None),
                           ('Subitem 2.3', None),
                           ('Back', DM_TRANS_BACK)),
                           title="Submenu 2")
    menu1 = ScreenMenu((('Submenu 1', submenu1),
                        ('Submenu 2', submenu2)),
                        title="Main Menu")

    dm = DisplayManager(oled, menu1)
    dm.redraw()
    time.sleep(3)
    dm.handle_event(DM_EVENT_DOWN) # Select Submenu 2
    time.sleep(1)
    dm.handle_event(DM_EVENT_BUTTON_DOWN) # Enter Submenu 2
    time.sleep(1)
    dm.handle_event(DM_EVENT_DOWN) # Select Subitem 2.2
    time.sleep(2)
    dm.handle_event(DM_EVENT_UP) # Select Subitem 2.1
    time.sleep(2)
    dm.handle_event(DM_EVENT_UP) # Should be ignored
    time.sleep(1)
    dm.handle_event(DM_EVENT_DOWN) # Select Subitem 2.2
    time.sleep(1)
    dm.handle_event(DM_EVENT_DOWN) # Select Subitem 2.3
    time.sleep(1)
    dm.handle_event(DM_EVENT_DOWN) # Select Back
    time.sleep(1)
    dm.handle_event(DM_EVENT_BUTTON_DOWN) # Go back to 'Main' menu
    time.sleep(1)
    dm.handle_event(DM_EVENT_DOWN) # Should be ignored
    time.sleep(1)
    dm.handle_event(DM_EVENT_UP) # Select Submenu 1
    time.sleep(1)
    dm.handle_event(DM_EVENT_BUTTON_DOWN) # Enter Submenu 1


if __name__ == "__main__":
    main()