# uDisplayManager

A basic display manager for MicroPython.

## Description

uDisplayManager is a very basic display manager for use with MicroPython. The display manager expects a `FrameBuffer` subclassed display object like a [SSD1306](https://github.com/micropython/micropython/blob/master/drivers/display/ssd1306.py) instance to work on and can be configured to handle different 'Screens'. Screens are entities like windows but full screen. Based on events handed to the display manager interaction with the screens can be accomplished. For instance scrolling through a menu, accessing a submenu or selecting an item.
Currently only menus with submenus (and subsubmenus, and subsubsubmenus, and ...) are implemented. But it is very easy to extend the display manager with other 'Screens' by subclassing the `Screen` class.

### ToDo
* Scrolling menus
* Value entry screens
* Simple text screens

## Getting Started

### Dependencies

* Built for use with MicroPython (tested on 1.17), but the module should also work on other Python flavors.
* No dependencies on non-standard modules

### Installing

Simply copy the module file `udispmgr.py` to your MicroPython device using a tool like `ampy` or `rshell`.

Remove the `main` function from the module file to save on memory resources.

### Running / Using

See the test code at the end of the module file for an example how to use the module.

Basically instantiate `Screen` objects linked to eachother using targets and feed the start screen to an instance of `DisplayManager`. The event handler on the `DisplayManager` can be called to interact with the screens.

```python
import udispmgr

submenu1 = udispmgr.ScreenMenu((('Subitem 1.1', None),
                        ('Subitem 1.2', None),
                        ('Back', udispmgr.DM_TRANS_BACK)),
                        title="Submenu 1")
submenu2 = udispmgr.ScreenMenu((('Subitem 2.1', None),
                        ('Subitem 2.2', None),
                        ('Subitem 2.3', None),
                        ('Back', udispmgr.DM_TRANS_BACK)),
                        title="Submenu 2")
menu1 = udispmgr.ScreenMenu((('Submenu 1', submenu1),
                    ('Submenu 2', submenu2)),
                    title="Main Menu")

dm = udispmgr.DisplayManager(display, menu1)
```

Through subclassing of the `Screen` class extra screens can be created.

## Authors

[Diamino](https://github.com/diamino)

## Version History

* 0.1
    * Initial Release

## License

This project is licensed under the MIT License - see the LICENSE.md file for details
