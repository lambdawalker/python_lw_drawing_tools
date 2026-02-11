import mathutils


def compute_3d_bbox_positions(center, rotation, plane_size, bbox, flip=False):
    center_vec = mathutils.Vector(center)
    plane_width, plane_height = plane_size
    x0, y0, x1, y1 = bbox

    factor = -1 if flip else 1

    # Compute the bounding box corners in 2D relative to the plane's local origin
    def sxpx(xp, w): return (xp - .5) * factor * w  # screen x to plane in origin x

    def sypy(yp, h): return (.5 - yp) * h  # screen y to plane in origin y

    px0 = sxpx(x0, plane_width)
    py0 = sypy(y0, plane_height)

    px1 = sxpx(x1, plane_width)
    py1 = sypy(y1, plane_height)

    local_corners_2d = [
        mathutils.Vector((px1, py1)),
        mathutils.Vector((px0, py1)),
        mathutils.Vector((px0, py0)),
        mathutils.Vector((px1, py0)),
    ]

    # Create a rotation matrix from the Euler angles
    rotation_matrix = rotation.to_matrix().to_4x4()

    # Calculate the 3D positions of the bounding box corners
    bbox_3d_positions = []

    for corner in local_corners_2d:
        point = mathutils.Vector((corner.x, corner.y, 0))
        point = center_vec + (rotation_matrix @ point)
        bbox_3d_positions.append(point)

    return tuple([tuple(p) for p in bbox_3d_positions])
