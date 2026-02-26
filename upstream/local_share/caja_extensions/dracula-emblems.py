#!/usr/bin/env python3
"""
Caja Python Extension: Dracula Themed Emblems
Adds context menu items to tag files with Dracula-themed emblems

Installation: Copy to ~/.local/share/caja-python/extensions/
Requires: python-caja package
"""

from gi.repository import Caja, GObject
import subprocess


class DraculaEmblemsExtension(GObject.GObject, Caja.MenuProvider):
    """Add Dracula-themed emblem menu items to Caja context menu"""

    def __init__(self):
        pass

    def _apply_emblem(self, menu, files, emblem_name):
        """Apply an emblem to selected files using gio metadata"""
        for file_info in files:
            uri = file_info.get_uri()
            try:
                # Use gio to set emblem metadata
                subprocess.run(
                    [
                        "gio",
                        "set",
                        uri,
                        "metadata::emblems",
                        "--type=stringv",
                        emblem_name,
                    ],
                    check=True,
                    capture_output=True,
                )
            except subprocess.CalledProcessError as e:
                print(f"Error applying emblem to {uri}: {e}")

    def _clear_emblems(self, menu, files):
        """Clear all emblems from selected files"""
        for file_info in files:
            uri = file_info.get_uri()
            try:
                # Unset emblem metadata
                subprocess.run(
                    ["gio", "set", uri, "metadata::emblems", "--type=stringv"],
                    check=True,
                    capture_output=True,
                )
            except subprocess.CalledProcessError as e:
                print(f"Error clearing emblems from {uri}: {e}")

    def get_file_items(self, window, files):
        """Return menu items for selected files"""
        if not files:
            return []

        # Create submenu for Dracula emblems
        items = []

        # Purple emblem (Dracula accent color)
        purple_item = Caja.MenuItem(
            name="DraculaEmblems::Purple",
            label="Mark as Important (Purple)",
            tip="Apply Dracula purple emblem",
            icon="emblem-important",
        )
        purple_item.connect("activate", self._apply_emblem, files, "emblem-important")
        items.append(purple_item)

        # Green emblem (success/done)
        green_item = Caja.MenuItem(
            name="DraculaEmblems::Green",
            label="Mark as Done (Green)",
            tip="Apply green checkmark emblem",
            icon="emblem-default",
        )
        green_item.connect("activate", self._apply_emblem, files, "emblem-default")
        items.append(green_item)

        # Red emblem (urgent)
        red_item = Caja.MenuItem(
            name="DraculaEmblems::Red",
            label="Mark as Urgent (Red)",
            tip="Apply red urgent emblem",
            icon="emblem-urgent",
        )
        red_item.connect("activate", self._apply_emblem, files, "emblem-urgent")
        items.append(red_item)

        # Cyan emblem (new)
        cyan_item = Caja.MenuItem(
            name="DraculaEmblems::Cyan",
            label="Mark as New (Cyan)",
            tip="Apply new/recent emblem",
            icon="emblem-new",
        )
        cyan_item.connect("activate", self._apply_emblem, files, "emblem-new")
        items.append(cyan_item)

        # Favorite emblem
        fav_item = Caja.MenuItem(
            name="DraculaEmblems::Favorite",
            label="Mark as Favorite",
            tip="Apply favorite emblem",
            icon="emblem-favorite",
        )
        fav_item.connect("activate", self._apply_emblem, files, "emblem-favorite")
        items.append(fav_item)

        # Separator
        sep_item = Caja.MenuItem(name="DraculaEmblems::Sep", label="—", tip="")
        items.append(sep_item)

        # Clear emblems
        clear_item = Caja.MenuItem(
            name="DraculaEmblems::Clear",
            label="Clear All Emblems",
            tip="Remove all emblems from selection",
            icon="edit-clear",
        )
        clear_item.connect("activate", self._clear_emblems, files)
        items.append(clear_item)

        return items


# EOF
