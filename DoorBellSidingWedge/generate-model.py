#! /home/tfili/Source/tfili/3d-printing/venv/bin/python

from solid import *
from solid.utils import *
import subprocess
import math

# Dimensions
height = 151             # vertical height (Y)
width = 43.5             # width of the side face (Z)
top_thickness = 23       # thickness at the top (X)
bottom_thickness = 2     # thickness at the bottom (X)
screw_diameter = 3.75
screw_radius = screw_diameter / 2

# Hole positions (from top and bottom)
hole1_from_top = 16.5
hole2_from_bottom = 21.5
hole1_y = hole1_from_top                     # 24.5mm from top
hole2_y = height - hole2_from_bottom         # 22mm from bottom

rounded_edge_radius = 18
ellipse_height = 5
ellipse_top_offset = 21
ellipse_bottom_offset = 23

# Calculate slope angle in degrees
slope_angle = math.degrees(math.atan2(top_thickness - bottom_thickness, height))

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

# Generate a rectangle and cut a cylinder out of it and subtract that from the model
def create_rounded_mask(top=True):
    scaleFactor = width / (2 * rounded_edge_radius);
    rect = translate([0, (0 if top else rounded_edge_radius), 0]) (
             cube([top_thickness, rounded_edge_radius, width], center = False)
           )
    cyl = scale([1, 1, width/(rounded_edge_radius*2)]) (
            translate([0, rounded_edge_radius, rounded_edge_radius]) (
              rotate([0,90,0]) (
                cylinder(r = rounded_edge_radius, h = top_thickness, center = False)
              )
            )
          )

    return rect - cyl

# Move it to the bottom
def create_bottom_rounded_mask():
    return translate([0, height-rounded_edge_radius*2, 0]) (
      create_rounded_mask(False)
    )

def semi_ellipse(segments=100):
    rx = (height - ellipse_top_offset - ellipse_bottom_offset)/2
    ry = ellipse_height
    points = []
    for i in range(segments + 1):
        angle = math.pi * (i / segments)  # 0 to pi
        x = rx * math.cos(angle)
        y = ry * math.sin(angle)
        points.append([x, y])
    
    # Close the shape by adding the base edge
    points.append([-rx, 0])
    points.append([rx, 0])
    
    shape_2d = polygon(points)

    triangle_offset = (height - ellipse_top_offset - ellipse_bottom_offset) / 2
    triangle_wedge = polygon(points = [[triangle_offset-2, 0.0000000000],[triangle_offset-2, 1.3500000000],[triangle_offset+2, 0.0000000000]]);
    x_translate = ((height-ellipse_top_offset)/height) * top_thickness - bottom_thickness - ellipse_height - 0.2
    return translate([x_translate, rx+ellipse_top_offset, 0]) (
        rotate([0, 0, -90+slope_angle]) (
            linear_extrude(width)(shape_2d),
            linear_extrude(width)(triangle_wedge)
        )
    )

# Build model
wedge = create_wedge()
hole1 = create_side_hole(hole1_y)
hole2 = create_side_hole(hole2_y)
top_mask = create_rounded_mask();
bottom_mask = create_bottom_rounded_mask()
ellipse = semi_ellipse()

# Combine everything
model = wedge - (hole1 + hole2) - top_mask - bottom_mask

# Export to SCAD
scad_render_to_file(model + ellipse, 'wedge.scad')

# Convert to STL
subprocess.run(["openscad", "-o", "wedge.stl", "wedge.scad"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)