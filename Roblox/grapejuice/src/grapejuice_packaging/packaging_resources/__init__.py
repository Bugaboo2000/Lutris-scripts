import os

HERE = os.path.dirname(os.path.abspath(__file__))


def bin_grapejuice_path():
    return os.path.join(HERE, "bin", "grapejuice")


def bin_grapejuice_gui_path():
    return os.path.join(HERE, "bin", "grapejuice-gui")


def local_bin_grapejuice_path():
    return os.path.join(HERE, "local_bin", "grapejuice")


def local_bin_grapejuice_gui_path():
    return os.path.join(HERE, "local_bin", "grapejuice-gui")
