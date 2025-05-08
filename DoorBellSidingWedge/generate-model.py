#! /home/tfili/Source/tfili/3d-printing/venv/bin/python

from solid import *
from solid.utils import *
import subprocess
import math

# Dimensions
height = 159             # vertical height (Y)
width = 43.5             # width of the side face (Z)
top_thickness = 17.5     # thickness at the top (X)
bottom_thickness = 2     # thickness at the bottom (X)
screw_diameter = 3.75
screw_radius = screw_diameter / 2

# Hole positions (from top and bottom)
hole1_from_top = 24.5
hole2_from_bottom = 22
hole1_y = hole1_from_top                     # 24.5mm from top
hole2_y = height - hole2_from_bottom         # 22mm from bottom

rounded_edge_radius = 15

# Calculate slope angle in degrees
slope_angle = math.degrees(math.atan2(top_thickness - bottom_thickness, height))

# Second wedge parameters
second_wedge_length = 132  # vertical height along original Y
second_top_thickness = 6
second_bottom_thickness = 0

# Calculate thickness at a specific Y position along the slope
def thickness_at(y):
    return top_thickness - (top_thickness - bottom_thickness) * (y / height)

# Create wedge shape
def create_wedge():
    profile = polygon(points=[
        [0, 0],
        [top_thickness, 0],
        [bottom_thickness, height],
        [0, height]
    ])
    return linear_extrude(width)(profile)

# Create a hole through the side at a specific Y position
def create_side_hole(y_pos):
    local_thickness = thickness_at(y_pos)
    return translate([local_thickness / 2, y_pos, width / 2])(
        rotate([0, 90, 0])(
            cylinder(h=width + 2, r=screw_radius, center=True)
        )
    )

# Add a second wedge on the sloped face
def create_second_wedge():
    # This wedge lies directly on top of the sloped face
    # So we offset all X values by the thickness of the first wedge at each Y

    # Find the first wedge thickness at the end of the second wedge
    wedge_thickness = thickness_at(second_wedge_length)

    profile = polygon(points=[
        [top_thickness, 0],
        [top_thickness + 5, 0],
        [wedge_thickness, second_wedge_length],
        [wedge_thickness, second_wedge_length]  # optional, for clarity
    ])
    return linear_extrude(width)(profile)

# Create a hole in the second wedge at 24.5mm from the top
def create_second_wedge_hole(y_pos):
    # Second wedge thickness at y
    local_thickness = 5 * (1 - y_pos / second_wedge_length)
    x_pos = thickness_at(y_pos) + local_thickness / 2
    return translate([x_pos, y_pos, width / 2])(
        rotate([0, 90, 0])(
            cylinder(h=width + 2, r=screw_radius, center=True)
        )
    )

# Generate a rectangle and cut a cylinder out of it and subtract that from the model
def create_rounded_mask(top=True):
    thickness = top_thickness + second_top_thickness
    scaleFactor = width / (2 * rounded_edge_radius);
    rect = translate([0, (0 if top else rounded_edge_radius), 0]) (
             cube([thickness, rounded_edge_radius, width], center = False)
           )
    cyl = scale([1, 1, (width/(rounded_edge_radius*2))+0.1]) (
            translate([0, rounded_edge_radius, rounded_edge_radius]) (
              rotate([0,90,0]) (
                cylinder(r = rounded_edge_radius, h = thickness, center = False)
              )
            )
          )

    return rect - cyl

# Move it to the bottom
def create_bottom_rounded_mask():
    return translate([0, height-rounded_edge_radius*2, 0]) (
      create_rounded_mask(False)
    )

# Build model
wedge = create_wedge()
hole1 = create_side_hole(hole1_y)
hole2 = create_side_hole(hole2_y)
second_wedge = create_second_wedge()
second_hole = create_second_wedge_hole(hole1_y)
top_mask = create_rounded_mask();
bottom_mask = create_bottom_rounded_mask()

# Combine everything
model = (wedge + second_wedge) - (hole1 + hole2 + second_hole) - top_mask - bottom_mask

# Export to SCAD
scad_render_to_file(model, 'wedge.scad')

# Convert to STL
subprocess.run(["openscad", "-o", "wedge.stl", "wedge.scad"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)