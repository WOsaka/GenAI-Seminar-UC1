import ezdxf
from math import sqrt


def calculate_distance(point1, point2):
    """Calculate Euclidean distance between two points."""
    return sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def path_length(entity):
    """Calculate the length of a path based on its type."""
    try:
        if entity.dxftype() == "LINE":
            # Length of a line
            start = entity.dxf.start
            end = entity.dxf.end
            return calculate_distance(start, end)
        elif entity.dxftype() in {"LWPOLYLINE", "POLYLINE"}:
            # Total length of a polyline
            points = get_points(entity)  # Use the helper function
            return sum(
                calculate_distance(points[i], points[i + 1]) for i in range(len(points) - 1)
            )
        elif entity.dxftype() == "ARC":
            # Approximate length of an arc
            radius = entity.dxf.radius
            start_angle = entity.dxf.start_angle
            end_angle = entity.dxf.end_angle
            angle_diff = abs(end_angle - start_angle)
            return (angle_diff / 360) * (2 * 3.141592 * radius)
        elif entity.dxftype() == "CIRCLE":
            # Circumference of the circle (can treat small circles as noise)
            radius = entity.dxf.radius
            return 2 * 3.141592 * radius
    except Exception as e:
        print(f"Error processing entity {entity.dxftype()}: {e}")
        return 0  # Default for unsupported or problematic entities

def get_points(entity):
    try:
        if entity.dxftype() == "LWPOLYLINE":
            # Safely access points
            return list(entity.get_points())
        elif entity.dxftype() == "POLYLINE":
            # Safely access vertices
            return [v.dxf.location for v in entity.vertices]
        else:
            return []
    except AttributeError as e:
        print(f"Entity {entity.dxftype()} does not support points or vertices: {e}")
        return []


def remove_noise(input_file, output_file, min_length=1.0, max_distance=10.0):
    """
    Remove small or isolated paths from a DXF file.
    :param input_file: Path to the input DXF file.
    :param output_file: Path to the output (cleaned) DXF file.
    :param min_length: Minimum length threshold for paths.
    :param max_distance: Maximum distance for a path to be considered close to others.
    """
    # Load the DXF file
    doc = ezdxf.readfile(input_file)
    msp = doc.modelspace()

    # Collect all entities and their lengths
    entities = []
    for entity in msp:
        if entity.dxftype() in {"LINE", "LWPOLYLINE", "POLYLINE", "ARC", "CIRCLE"}:
            length = path_length(entity)
            if length >= min_length:
                entities.append((entity, length))

    # Identify isolated paths
    remaining_entities = []
    for i, (entity, length) in enumerate(entities):
        start = entity.dxf.start if hasattr(entity.dxf, "start") else None
        center = entity.dxf.center if hasattr(entity.dxf, "center") else None
        position = start or center or (0, 0)

        # Check if the entity is "close" to others
        is_isolated = True
        for j, (other_entity, _) in enumerate(entities):
            if i == j:
                continue
            other_start = other_entity.dxf.start if hasattr(other_entity.dxf, "start") else None
            other_center = other_entity.dxf.center if hasattr(other_entity.dxf, "center") else None
            other_position = other_start or other_center or (0, 0)

            if calculate_distance(position, other_position) <= max_distance:
                is_isolated = False
                break

        if not is_isolated:
            remaining_entities.append(entity)

    # Remove all existing entities in the modelspace
    for entity in list(msp):  # Use list() to avoid modifying during iteration
        msp.delete_entity(entity)

    # Add back the remaining entities
    for entity in remaining_entities:
        if entity.dxftype() == "LINE":
            msp.add_line(entity.dxf.start, entity.dxf.end)
        elif entity.dxftype() == "LWPOLYLINE":
            msp.add_lwpolyline(entity.get_points())
        elif entity.dxftype() == "POLYLINE":
            polyline = msp.add_polyline3d(entity.get_points())
            for vertex in entity.vertices:
                polyline.append_vertex(vertex.dxf.location)
        elif entity.dxftype() == "ARC":
            msp.add_arc(
                entity.dxf.center, entity.dxf.radius, entity.dxf.start_angle, entity.dxf.end_angle
            )
        elif entity.dxftype() == "CIRCLE":
            msp.add_circle(entity.dxf.center, entity.dxf.radius)

    # Save the cleaned DXF file
    doc.saveas(output_file)
    print(f"Cleaned DXF saved to: {output_file}")

# Example usage
input_file = r"GenAI-Seminar-UC1\uploads\output.dxf"
output_file = r"GenAI-Seminar-UC1\uploads\output_cleaned.dxf"

remove_noise(input_file, output_file, min_length=200, max_distance=0.001)
#converter_cv.dxf_to_png(r'uploads\output_cleaned.dxf', r'uploads\output_cleaned.png')
