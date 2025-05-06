#! /home/tfili/Source/tfili/3d-printing/venv/bin/python

from solid import *
from solid.utils import *
import os
import subprocess

# Parameters
width = 91.85
height = 44.20
thickness = 2.28
corner_radius = 15

# Notch dimensions
notch_width = 3
notch_height = 4
notch_depth = 1.2

# Define main shape with rounded top corners
def main_shape():
    return union()(
        # Main rectangle body
        translate([corner_radius, 0, 0])(cube([width - 2 * corner_radius, height, thickness])),
        cube([corner_radius, height - corner_radius, thickness]),
        translate([width - corner_radius, 0, 0])(cube([corner_radius, height - corner_radius, thickness])),
        # Rounded top corners
        translate([corner_radius, height - corner_radius, 0])(cylinder(h=thickness, r=corner_radius, segments=50)),
        translate([width - corner_radius, height - corner_radius, 0])(cylinder(h=thickness, r=corner_radius, segments=50))
    )

# Notch to subtract from bottom center
def notch():
    return translate([
        (width - notch_width) / 2,
        0,
        0
    ])(cube([notch_width, notch_height, notch_depth]))

# Final model with notch cut out
model = difference()(
    main_shape(),
    notch()
)

# Export to SCAD
scad_render_to_file(model, "separator.scad", file_header='$fn=100;')

# Convert to STL
subprocess.run(["openscad", "-o", "separator.stl", "separator.scad"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)