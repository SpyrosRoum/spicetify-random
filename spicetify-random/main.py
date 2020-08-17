#!/bin/python
"""
A simple python script to set a random spotify theme

The options file should have one theme per line in the following format:

theme_name color_scheme=scheme extensions=comma.js,separated.js,list.js

if a theme doesn't have color schemes then you can omit that completely like this:

theme_name extensions=comma.js,separated.js,list.js

same with the extensions:

theme_name color_scheme=scheme
"""
import os
import sys
import random
import subprocess
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Theme:
    """Represents a theme"""
    name: str
    color_scheme: Optional[str]
    extensions: List[str]


class Spicetify:
    """A class wrapping all the spicetify related functions"""
    def __init__(self, options_path=None):
        self.path = os.popen("which spicetify").read().rstrip("\n") or None
        self.options_path = options_path or Path("~/.config/spicetify/options.txt").expanduser()

    @staticmethod
    def parse_extensions(line: str) -> List[str]:
        """Parse a line from the options file and get the extensions"""
        if "extensions" not in line:
            # The theme has no extensions
            extensions = list()
        else:
            # extensions are always last in the line
            extensions = line.split(" ")[-1].split("=")[-1]
            extensions = list(map(lambda ext: ext.rstrip("\n"), extensions.split(",")))

        return extensions

    def get_old_theme(self) -> Theme:
        """Get the theme that was used last time
            returns a tuple with (theme_name, color_scheme, [extension, extension, ...])
        """
        theme = os.popen(f"{self.path} config current_theme").read().rstrip("\n")
        color_scheme = os.popen(f"{self.path} config color_scheme").read().rstrip("\n")

        # The only way to get the extensions of a theme is from the options file
        with open(self.options_path, "r") as file:
            for line in file.readlines():
                if line.startswith(theme):
                    extensions = self.parse_extensions(line)
                    break
            else:
                # uh-uh we didn't find the theme in the list
                print("WARNING: I didn't find the old theme in the options file. "
                      "You may have to manually unload the old theme's extensions")
                extensions = list()

        return Theme(theme, color_scheme, extensions)

    def get_rand_theme(self) -> Theme:
        """Get a random theme from the list"""
        with open(self.options_path, "r") as file:
            options = list(map(lambda s: s.rstrip("\n"), file.readlines()))
            line = random.choice(options)

        line_lst = line.split(" ")
        theme = line_lst[0]

        if "color_scheme" in line:
            # color_scheme is always the second item in the line
            color_scheme = line_lst[1].split("=")[-1]
        else:
            # It can't be an empty string, it needs a space for spicetify
            color_scheme = " "

        extensions = self.parse_extensions(line)

        return Theme(theme, color_scheme, extensions)

    def manage_ext(self, ext: str, load):
        """Load or unload an extension from spicetify"""
        if not load and not ext.endswith("-"):
            ext += "-"

        cmd = [self.path, "config", "extensions", ext]
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL).wait()
        if load:
            print(f"Loaded extension: {ext}")
        else:
            print(f"Unloaded extension: {ext[:-1:]}")

    def change_theme(self, old_theme: Theme, new_theme: Theme):
        """Set the new theme in the config file and save it"""

        # Unload old extensions and load new:
        for ext in old_theme.extensions:
            self.manage_ext(ext, load=False)
        for ext in new_theme.extensions:
            self.manage_ext(ext, load=True)

        scripts = [
            [self.path, "config", "current_theme", new_theme.name],
            [self.path, "config", "color_scheme", new_theme.color_scheme]
        ]
        for script in scripts:
            subprocess.Popen(script, stdout=subprocess.DEVNULL).wait()

    def update(self):
        """Apply and Update spicetify"""
        # --no-restart is so spotify doesn't open when the script runs
        subprocess.Popen([self.path, "apply", "--no-restart"], stdout=subprocess.DEVNULL).wait()
        subprocess.Popen([self.path, "update"], stdout=subprocess.DEVNULL).wait()


if __name__ == "__main__":
    spice = Spicetify()
    if spice.path is None:
        print("You need to install spicetify first.\n"
              "Please follow the instruction here: "
              "https://github.com/khanhas/spicetify-cli/wiki/Installation")
        sys.exit(1)

    old_theme = spice.get_old_theme()
    print(f"Old theme: {old_theme.name}")
    while True:
        # Get a new theme until you get a different one than last time
        new_theme = spice.get_rand_theme()

        if new_theme.name != old_theme.name:
            break

    spice.change_theme(old_theme, new_theme)
    print(f"New theme: {new_theme.name}")
    spice.update()
    print("You should restart spotify for the changes to take effect.")
