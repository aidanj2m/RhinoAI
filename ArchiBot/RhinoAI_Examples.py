"""
RhinoAI_Examples.py

This file contains example implementation functions for common geometric patterns
that might be requested through RhinoAI. These examples demonstrate how to properly
implement various geometric structures in Rhino Python using rhinoscriptsyntax and RhinoCommon.

These examples are meant for reference and educational purposes to understand how RhinoAI
would generate geometry based on natural language instructions.
"""

import rhinoscriptsyntax as rs
import Rhino
import Rhino.Geometry as rg
import scriptcontext as sc
import math
import random
import System

# Basic Shapes
def create_sphere(center=(0,0,0), radius=10):
    """Create a sphere with the specified center and radius."""
    # Create the sphere
    sphere = rs.AddSphere(center, radius)
    return sphere

def create_box(center=(0,0,0), width=10, length=10, height=10):
    """Create a box with the specified center and dimensions."""
    # Calculate corner points
    x, y, z = center
    dx, dy, dz = width/2, length/2, height/2
    
    # Create the box
    box = rs.AddBox([
        [x-dx, y-dy, z-dz], [x+dx, y-dy, z-dz], 
        [x+dx, y+dy, z-dz], [x-dx, y+dy, z-dz],
        [x-dx, y-dy, z+dz], [x+dx, y-dy, z+dz],
        [x+dx, y+dy, z+dz], [x-dx, y+dy, z+dz]
    ])
    return box

# Parametric Patterns
def create_honeycomb(origin=(0,0,0), spacing=30, rows=5, cols=5, height=10):
    """Create a honeycomb lattice structure with hexagons spaced at the specified distance."""
    # Ensure the 'Honeycomb' layer exists
    if not rs.IsLayer("Honeycomb"):
        rs.AddLayer("Honeycomb", rs.CreateColor(255, 200, 0))
    
    # Calculate hexagon parameters
    radius = spacing / 2
    hex_height = radius * math.sqrt(3)
    
    cells = []
    
    for i in range(rows):
        for j in range(cols):
            # Calculate the center of each hexagon with offset for even rows
            offset = radius if i % 2 == 1 else 0
            x = origin[0] + j * spacing * 1.5 + offset
            y = origin[1] + i * hex_height
            z = origin[2]
            
            # Create the hexagon
            hexagon_points = []
            for angle in range(0, 360, 60):
                px = x + radius * math.cos(math.radians(angle))
                py = y + radius * math.sin(math.radians(angle))
                hexagon_points.append([px, py, z])
            
            # Close the hexagon
            hexagon_points.append(hexagon_points[0])
            
            # Create the hexagon curve
            hexagon = rs.AddPolyline(hexagon_points)
            
            # Extrude the hexagon to create a cell
            if height > 0:
                cell = rs.ExtrudeCurveStraight(hexagon, [0, 0, 0], [0, 0, height])
                rs.DeleteObject(hexagon)  # Remove the base curve
                cells.append(cell)
            else:
                cells.append(hexagon)
    
    # Group the cells and set the layer
    if cells:
        group = rs.AddGroup("Honeycomb")
        rs.AddObjectsToGroup(cells, group)
        rs.ObjectLayer(cells, "Honeycomb")
    
    return cells

def create_spiral_staircase(center=(0,0,0), radius=20, steps=20, total_height=50, step_width=3):
    """Create a spiral staircase with the specified parameters."""
    # Ensure the 'Staircase' layer exists
    if not rs.IsLayer("Staircase"):
        rs.AddLayer("Staircase", rs.CreateColor(200, 200, 200))
    
    # Calculate step parameters
    angle_per_step = 360 / steps  # Degrees
    height_per_step = total_height / steps
    
    stairs = []
    
    for i in range(steps):
        # Calculate step position
        angle = math.radians(i * angle_per_step)
        start_angle = angle - math.radians(step_width)
        end_angle = angle + math.radians(step_width)
        
        height = i * height_per_step
        
        # Create step as a curved surface
        step_points = []
        
        # Inner points (at center + small offset)
        inner_radius = radius * 0.3
        step_points.append([
            center[0] + inner_radius * math.cos(start_angle),
            center[1] + inner_radius * math.sin(start_angle),
            center[2] + height
        ])
        step_points.append([
            center[0] + inner_radius * math.cos(end_angle),
            center[1] + inner_radius * math.sin(end_angle),
            center[2] + height
        ])
        
        # Outer points
        step_points.append([
            center[0] + radius * math.cos(end_angle),
            center[1] + radius * math.sin(end_angle),
            center[2] + height
        ])
        step_points.append([
            center[0] + radius * math.cos(start_angle),
            center[1] + radius * math.sin(start_angle),
            center[2] + height
        ])
        
        # Close the polygon
        step_points.append(step_points[0])
        
        # Create the step surface
        step_curve = rs.AddPolyline(step_points)
        step_surface = rs.AddPlanarSrf(step_curve)
        
        # Extrude the step slightly for thickness
        step_solid = rs.ExtrudeSurface(step_surface, rs.AddLine(
            [0, 0, 0],
            [0, 0, -0.5]
        ))
        
        # Clean up intermediate objects
        rs.DeleteObjects([step_curve, step_surface])
        
        stairs.append(step_solid)
    
    # Create a central column
    column = rs.AddCylinder(
        rs.WorldXYPlane(),
        total_height,
        inner_radius * 0.6
    )
    stairs.append(column)
    
    # Group the staircase and set the layer
    if stairs:
        group = rs.AddGroup("SpiralStaircase")
        rs.AddObjectsToGroup(stairs, group)
        rs.ObjectLayer(stairs, "Staircase")
    
    return stairs

# Organic Structures
def create_wavy_surface(origin=(0,0,0), width=100, length=100, wave_height=10, resolution=20):
    """Create a wavy surface resembling ocean waves."""
    # Ensure the 'Waves' layer exists
    if not rs.IsLayer("Waves"):
        rs.AddLayer("Waves", rs.CreateColor(0, 100, 255))
    
    # Create a grid of points
    points = []
    
    for i in range(resolution + 1):
        row = []
        for j in range(resolution + 1):
            x = origin[0] + (width * i / resolution)
            y = origin[1] + (length * j / resolution)
            
            # Calculate a wave pattern for the z-coordinate
            # Using sine and cosine functions with varying frequencies
            z = origin[2]
            z += wave_height * 0.5 * math.sin(i * math.pi * 3 / resolution)
            z += wave_height * 0.3 * math.cos(j * math.pi * 2 / resolution)
            z += wave_height * 0.2 * math.sin((i + j) * math.pi * 4 / resolution)
            
            row.append([x, y, z])
        points.append(row)
    
    # Create a NURBS surface from the point grid
    surface = rs.AddSrfControlPtGrid(points)
    
    # Set the layer
    if surface:
        rs.ObjectLayer(surface, "Waves")
    
    return surface

def create_tree_structure(origin=(0,0,0), trunk_height=50, trunk_radius=5, levels=3, branch_reduction=0.7, angle=30):
    """Create a tree-like branching structure with the specified number of branching levels."""
    # Ensure the 'Tree' layer exists
    if not rs.IsLayer("Tree"):
        rs.AddLayer("Tree", rs.CreateColor(50, 150, 50))
    
    tree_parts = []
    
    # Create the trunk
    trunk = rs.AddCylinder(
        rs.PlaneFromNormal(origin, [0, 0, 1]),
        trunk_height,
        trunk_radius
    )
    tree_parts.append(trunk)
    
    def create_branches(start_point, direction, length, radius, current_level):
        """Recursive function to create branches at each level."""
        if current_level > levels:
            return []
        
        branches = []
        
        # Create this branch as a cylinder
        end_point = [
            start_point[0] + direction[0] * length,
            start_point[1] + direction[1] * length,
            start_point[2] + direction[2] * length
        ]
        
        branch = rs.AddCylinder(
            rs.PlaneFromNormal(start_point, direction),
            length,
            radius
        )
        branches.append(branch)
        
        # Calculate new length and radius for sub-branches
        new_length = length * branch_reduction
        new_radius = radius * branch_reduction
        
        # Only create sub-branches if we're not at max level
        if current_level < levels:
            # Create 2-3 sub-branches
            num_branches = random.randint(2, 3)
            
            for i in range(num_branches):
                # Create a random direction with upward bias
                rand_angle = random.uniform(-angle, angle)
                
                # Rotate the direction vector
                x_rotation = rs.RotateVector(direction, rand_angle, [1, 0, 0])
                new_direction = rs.RotateVector(x_rotation, random.uniform(0, 360), direction)
                
                # Ensure the direction has some upward component
                if new_direction[2] < 0:
                    new_direction[2] *= -0.5
                
                # Normalize and create sub-branches
                new_direction = rs.VectorUnitize(new_direction)
                branches.extend(create_branches(
                    end_point,
                    new_direction,
                    new_length,
                    new_radius,
                    current_level + 1
                ))
        
        return branches
    
    # Create first level branches
    trunk_top = [origin[0], origin[1], origin[2] + trunk_height]
    
    # Create 3-5 main branches
    num_main_branches = random.randint(3, 5)
    
    for i in range(num_main_branches):
        # Calculate branch direction with upward bias
        angle_h = random.uniform(0, 360)
        angle_v = random.uniform(20, 60)
        
        direction = [
            math.sin(math.radians(angle_h)) * math.sin(math.radians(angle_v)),
            math.cos(math.radians(angle_h)) * math.sin(math.radians(angle_v)),
            math.cos(math.radians(angle_v))
        ]
        
        # Create the branch and its sub-branches
        branches = create_branches(
            trunk_top,
            direction,
            trunk_height * 0.7,
            trunk_radius * 0.7,
            1
        )
        tree_parts.extend(branches)
    
    # Group the tree parts and set the layer
    if tree_parts:
        group = rs.AddGroup("Tree")
        rs.AddObjectsToGroup(tree_parts, group)
        rs.ObjectLayer(tree_parts, "Tree")
    
    return tree_parts

# Architectural Elements
def create_domed_roof(center=(0,0,0), radius=50, height=30):
    """Create a domed roof with the specified parameters."""
    # Ensure the 'Roof' layer exists
    if not rs.IsLayer("Roof"):
        rs.AddLayer("Roof", rs.CreateColor(200, 0, 0))
    
    # Calculate the ellipse parameters
    # To create a dome that's not a full hemisphere, we use an ellipsoid
    dome = None
    
    if height >= radius:
        # If height >= radius, create a hemisphere
        sphere = rs.AddSphere(center, radius)
        cutting_plane = rs.PlaneFromNormal(center, [0, 0, -1])
        dome = rs.SplitBrep(sphere, cutting_plane)[0]
    else:
        # Otherwise create an ellipsoid and cut it
        # Create an ellipsoid by scaling a sphere
        sphere = rs.AddSphere([center[0], center[1], center[2] - (radius - height)], radius)
        scale_factor = height / radius
        rs.ScaleObject(sphere, center, [1, 1, scale_factor])
        
        # Cut the bottom to create the dome
        cutting_plane = rs.PlaneFromNormal(center, [0, 0, -1])
        dome_parts = rs.SplitBrep(sphere, cutting_plane)
        
        # Find the upper part (dome)
        for part in dome_parts:
            bbox = rs.BoundingBox(part)
            center_z = sum(p[2] for p in bbox) / len(bbox)
            if center_z > center[2]:
                dome = part
                break
    
    # Set the layer
    if dome:
        rs.ObjectLayer(dome, "Roof")
    
    return dome

def create_columns_along_path(path_points, column_spacing=20, column_height=20, column_radius=2):
    """Create a series of columns spaced along a path."""
    # Ensure the path is a curve
    if not isinstance(path_points, System.Guid):
        path = rs.AddCurve(path_points)
    else:
        path = path_points
    
    # Ensure the 'Columns' layer exists
    if not rs.IsLayer("Columns"):
        rs.AddLayer("Columns", rs.CreateColor(150, 150, 150))
    
    # Calculate the total length of the path
    path_length = rs.CurveLength(path)
    
    # Calculate the number of columns
    num_columns = int(path_length / column_spacing) + 1
    
    columns = []
    
    for i in range(num_columns):
        # Calculate the parameter along the curve
        t = i / (num_columns - 1) if num_columns > 1 else 0
        
        # Get the point on the curve
        point = rs.EvaluateCurve(path, t)
        
        # Get the tangent to determine orientation
        tangent = rs.CurveTangent(path, t)
        
        # Create a cylinder (column) at this point
        column = rs.AddCylinder(
            rs.PlaneFromNormal(point, [0, 0, 1]),
            column_height,
            column_radius
        )
        
        columns.append(column)
    
    # Group the columns and set the layer
    if columns:
        group = rs.AddGroup("Columns")
        rs.AddObjectsToGroup(columns, group)
        rs.ObjectLayer(columns, "Columns")
    
    return columns

# Mathematical Surfaces
def create_mobius_strip(center=(0,0,0), major_radius=30, width=10, segments=100):
    """Create a Möbius strip with the specified parameters."""
    # Ensure the 'Mobius' layer exists
    if not rs.IsLayer("Mobius"):
        rs.AddLayer("Mobius", rs.CreateColor(255, 0, 255))
    
    # Generate points for the mobius strip
    points = []
    
    for i in range(segments + 1):
        t = i * 2 * math.pi / segments
        
        # Create a row of points across the width of the strip
        row = []
        for j in range(2):  # Just need 2 points for the edges in each row
            s = -width/2 + j * width
            
            # Möbius strip parametric equations
            x = center[0] + (major_radius + s * math.cos(t/2)) * math.cos(t)
            y = center[1] + (major_radius + s * math.cos(t/2)) * math.sin(t)
            z = center[2] + s * math.sin(t/2)
            
            row.append([x, y, z])
        
        points.append(row)
    
    # Create the surface
    mobius = rs.AddSrfControlPtGrid(points)
    
    # Set the layer
    if mobius:
        rs.ObjectLayer(mobius, "Mobius")
    
    return mobius

def create_klein_bottle(center=(0,0,0), scale=20, u_segments=30, v_segments=30):
    """Create an approximation of a Klein bottle."""
    # Ensure the 'Klein' layer exists
    if not rs.IsLayer("Klein"):
        rs.AddLayer("Klein", rs.CreateColor(50, 200, 200))
    
    # Generate points for the Klein bottle
    points = []
    
    for i in range(u_segments + 1):
        u = i * 2 * math.pi / u_segments
        row = []
        
        for j in range(v_segments + 1):
            v = j * 2 * math.pi / v_segments
            
            # Klein bottle parametric equations
            # This is one of several possible parametrizations
            if u < math.pi:
                x = (6 * math.cos(u) * (1 + math.sin(u))) + 4 * math.sin(u) * math.cos(v) * (1 + math.sin(u))
                y = 16 * math.sin(u) + 4 * math.sin(u) * math.sin(v) * (1 + math.sin(u))
                z = 4 * math.sin(u) * math.sin(v)
            else:
                x = 6 * math.cos(u) * (1 + math.sin(u)) + 4 * math.sin(v + math.pi)
                y = 16 * math.sin(u)
                z = 0
            
            # Scale and center
            row.append([
                center[0] + x * scale / 20,
                center[1] + y * scale / 20,
                center[2] + z * scale / 20
            ])
        
        points.append(row)
    
    # Create the NURBS surface
    klein_bottle = rs.AddSrfControlPtGrid(points)
    
    # Set the layer
    if klein_bottle:
        rs.ObjectLayer(klein_bottle, "Klein")
    
    return klein_bottle

# Engineering Structures
def create_truss_bridge(start_point=(0,0,0), span=200, segments=10, height=30, width=20):
    """Create a truss bridge spanning the specified distance."""
    # Ensure the 'TrussBridge' layer exists
    if not rs.IsLayer("TrussBridge"):
        rs.AddLayer("TrussBridge", rs.CreateColor(100, 100, 100))
    
    # Calculate segment length
    segment_length = span / segments
    
    bridge_parts = []
    
    # Create bottom chord
    bottom_points_left = []
    bottom_points_right = []
    
    for i in range(segments + 1):
        x = start_point[0] + i * segment_length
        
        # Left bottom chord
        bottom_points_left.append([x, start_point[1] - width/2, start_point[2]])
        
        # Right bottom chord
        bottom_points_right.append([x, start_point[1] + width/2, start_point[2]])
    
    # Create top chord with a slight arch
    top_points_left = []
    top_points_right = []
    
    for i in range(segments + 1):
        x = start_point[0] + i * segment_length
        
        # Parabolic arch for the top chord
        arch_height = height * 4 * (i / segments) * (1 - i / segments)
        z = start_point[2] + height - arch_height
        
        # Left top chord
        top_points_left.append([x, start_point[1] - width/2, z])
        
        # Right top chord
        top_points_right.append([x, start_point[1] + width/2, z])
    
    # Create the chords
    bottom_left = rs.AddPolyline(bottom_points_left)
    bottom_right = rs.AddPolyline(bottom_points_right)
    top_left = rs.AddPolyline(top_points_left)
    top_right = rs.AddPolyline(top_points_right)
    
    bridge_parts.extend([bottom_left, bottom_right, top_left, top_right])
    
    # Create vertical members
    for i in range(segments + 1):
        vert_left = rs.AddLine(bottom_points_left[i], top_points_left[i])
        vert_right = rs.AddLine(bottom_points_right[i], top_points_right[i])
        bridge_parts.extend([vert_left, vert_right])
        
        # Add cross bracing between verticals
        if i < segments:
            # X-bracing in the vertical planes
            diag1_left = rs.AddLine(bottom_points_left[i], top_points_left[i+1])
            diag2_left = rs.AddLine(top_points_left[i], bottom_points_left[i+1])
            diag1_right = rs.AddLine(bottom_points_right[i], top_points_right[i+1])
            diag2_right = rs.AddLine(top_points_right[i], bottom_points_right[i+1])
            bridge_parts.extend([diag1_left, diag2_left, diag1_right, diag2_right])
            
            # Add horizontal bracing between the trusses
            cross_bottom = rs.AddLine(bottom_points_left[i], bottom_points_right[i])
            cross_top = rs.AddLine(top_points_left[i], top_points_right[i])
            bridge_parts.extend([cross_bottom, cross_top])
            
            # Add diagonal cross bracing in the top and bottom planes
            if i % 2 == 0:  # Alternate pattern
                cross_diag1 = rs.AddLine(bottom_points_left[i], bottom_points_right[i+1])
                cross_diag2 = rs.AddLine(bottom_points_right[i], bottom_points_left[i+1])
                bridge_parts.extend([cross_diag1, cross_diag2])
    
    # Convert curves to pipe with a small radius
    pipe_radius = width / 40
    pipe_parts = []
    
    for part in bridge_parts:
        pipe = rs.AddPipe(part, 0, pipe_radius)
        pipe_parts.append(pipe)
        rs.DeleteObject(part)  # Remove the original curve
    
    # Group the bridge and set the layer
    if pipe_parts:
        group = rs.AddGroup("TrussBridge")
        rs.AddObjectsToGroup(pipe_parts, group)
        rs.ObjectLayer(pipe_parts, "TrussBridge")
    
    return pipe_parts

def create_gear(center=(0,0,0), diameter=50, teeth=24, thickness=5):
    """Create a gear with the specified number of teeth and diameter."""
    # Ensure the 'Gear' layer exists
    if not rs.IsLayer("Gear"):
        rs.AddLayer("Gear", rs.CreateColor(200, 200, 0))
    
    # Calculate parameters
    outer_radius = diameter / 2
    inner_radius = outer_radius * 0.8
    tooth_height = outer_radius * 0.15
    
    # Calculate points along the gear perimeter
    points = []
    
    # Angle increments
    tooth_angle = 360 / (teeth * 2)  # Each tooth has a peak and valley
    
    for i in range(teeth * 2):
        angle = math.radians(i * tooth_angle)
        
        # Alternate between tooth peak and valley
        radius = outer_radius + tooth_height if i % 2 == 0 else inner_radius
        
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        z = center[2]
        
        points.append([x, y, z])
    
    # Close the curve
    points.append(points[0])
    
    # Create the gear profile
    gear_curve = rs.AddPolyline(points)
    
    # Create a circle for the central hole
    hole_radius = outer_radius * 0.2
    central_hole = rs.AddCircle(rs.PlaneFromNormal([center[0], center[1], center[2]], [0, 0, 1]), hole_radius)
    
    # Create the gear face with the hole
    gear_face = rs.AddPlanarSrf([gear_curve, central_hole])
    
    # Extrude the gear to create thickness
    gear = rs.ExtrudeSurface(gear_face, rs.AddLine([0, 0, 0], [0, 0, thickness]))
    
    # Clean up intermediate objects
    rs.DeleteObjects([gear_curve, central_hole, gear_face])
    
    # Set the layer
    if gear:
        rs.ObjectLayer(gear, "Gear")
    
    return gear

# Run a simple demo if this file is executed directly
if __name__ == "__main__":
    print("RhinoAI Examples - Running demo")
    
    # Uncomment any of these to see examples
    
    # Basic shapes
    #create_sphere()
    #create_box((10, 0, 0), 20, 30, 10)
    
    # Parametric patterns
    #create_honeycomb((0, 0, 0), 30, 5, 5, 10)
    #create_spiral_staircase((100, 0, 0), 20, 20, 50, 3)
    
    # Organic structures
    #create_wavy_surface((0, 100, 0), 100, 100, 15, 20)
    #create_tree_structure((100, 100, 0), 50, 5, 3, 0.7, 30)
    
    # Architectural elements
    #create_domed_roof((0, 0, 50), 50, 30)
    #path_points = [[0, 0, 0], [20, 20, 0], [40, 0, 0], [60, -20, 0], [80, 0, 0]]
    #path = rs.AddCurve(path_points)
    #create_columns_along_path(path, 10, 20, 2)
    
    # Mathematical surfaces
    #create_mobius_strip((0, 0, 100), 30, 10, 100)
    #create_klein_bottle((100, 0, 100), 20, 30, 30)
    
    # Engineering structures
    #create_truss_bridge((-100, 0, 0), 200, 10, 30, 20)
    #create_gear((0, 0, 0), 50, 24, 5)
    
    print("Demo complete") 