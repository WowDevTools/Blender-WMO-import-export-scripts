from mathutils import Vector


def proj_overlap(poly1_min, poly1_max, poly2_min, poly2_max):
    """ Return true if projections of 2 polygons are overlapping """
    return False if poly1_max < poly2_min or poly2_max < poly1_min else True


# return min coordinate and max coordinate of a vertex list in a tuple
def get_min_max(vertList):
    min = Vector(vertList[0])
    max = Vector(vertList[0])
    for v in vertList:
        if v.x < min.x:
            min.x = v.x
        elif v.x > max.x:
            max.x = v.x
        if v.y < min.y:
            min.y = v.y
        elif v.y > max.y:
            max.y = v.y
        if v.z < min.z:
            min.z = v.z
        elif v.z > max.z:
            max.z = v.z
    return min, max


def project_point(pt, v):
    """ Return projection of point with given direction vector """
    proj = Vector()
    # project on X
    if v.y == 0:
        l = 0
    else:
        l = - pt.y / v.y
    proj.z = pt.x + l * v.x
    # project on Y
    if v.z == 0:
        l = 0
    else:
        l = - pt.z / v.z
    proj.y = pt.x + l * v.x
    # project on Z
    proj.x = pt.y + l * v.y
    return proj


def plane_box_overlap(normal, vert, box):
    v_min = Vector()
    v_max = Vector()
    for q in range(0, 3):
        v = vert[q]
        if normal[q] > 0.0:
            v_min[q] = box[0][q] - v
            v_max[q] = box[1][q] - v
        else:
            v_min[q] = box[1][q] - v
            v_max[q] = box[0][q] - v

    return True if normal.dot(v_max) >= 0.0 else False


def collide_box_tri(box, triangle):
    """ Return True if AABB and triangle overlap """

    triangle_min_max = get_min_max(triangle)
    # check if overlap on box axis
    if not proj_overlap(box[0].x, box[1].x, triangle_min_max[0].x, triangle_min_max[1].x) \
    or not proj_overlap(box[0].y, box[1].y, triangle_min_max[0].y, triangle_min_max[1].y) \
    or not proj_overlap(box[0].z, box[1].z, triangle_min_max[0].z, triangle_min_max[1].z):
       return False

    pt_box = [
        Vector(box[0].xyz),
        Vector((box[0].x, box[1].y, box[0].z)),
        Vector((box[1].x, box[1].y, box[0].z)),
        Vector((box[1].x, box[0].y, box[0].z)),
        Vector(box[1].xyz),
        Vector((box[0].x, box[1].y, box[1].z)),
        Vector((box[1].x, box[1].y, box[1].z)),
        Vector((box[1].x, box[0].y, box[1].z))
    ]

    def check_overlaps(projected_box_min_max, projected_triangle_min_max):

        if not proj_overlap(projected_box_min_max[0].x,
                            projected_box_min_max[1].x,
                            projected_triangle_min_max[0].x,
                            projected_triangle_min_max[1].x) \
        or not proj_overlap(projected_box_min_max[0].y,
                            projected_box_min_max[1].y,
                            projected_triangle_min_max[0].y,
                            projected_triangle_min_max[1].y) \
        or not proj_overlap(projected_box_min_max[0].z,
                            projected_box_min_max[1].z,
                            projected_triangle_min_max[0].z,
                            projected_triangle_min_max[1].z):
            return True

        return False

    # project on edge 1 axis
    E0 = triangle[1] - triangle[0]
    pt_box_projected = []
    pt_triangle_projected = []

    for pt in pt_box:
        pt_box_projected.append(project_point(pt, E0))
    for pt in triangle:
        pt_triangle_projected.append(project_point(pt, E0))

    if check_overlaps(get_min_max(pt_box_projected), get_min_max(pt_triangle_projected)):
        return False

    # project on edge 2 axis
    E1 = triangle[2] - triangle[1]
    pt_box_projected = []
    pt_triangle_projected = []

    for pt in pt_box:
        pt_box_projected.append(project_point(pt, E1))
    for pt in triangle:
        pt_triangle_projected.append(project_point(pt, E1))

    if check_overlaps(get_min_max(pt_box_projected), get_min_max(pt_triangle_projected)):
        return False

   # project on edge 3 axis
    E2 = triangle[0] - triangle[2]
    pt_box_projected = []
    pt_triangle_projected = []
    for pt in pt_box:
        pt_box_projected.append(project_point(pt, E2))
    for pt in triangle:
        pt_triangle_projected.append(project_point(pt, E2))

    if check_overlaps(get_min_max(pt_box_projected), get_min_max(pt_triangle_projected)) \
    or not plane_box_overlap(E0.cross(E1), triangle[0], box):
        return False

    return True


def calculate_bounding_box(vertices):
    corner1 = Vector(vertices[0])
    corner2 = Vector(vertices[0])
    for v in vertices:
        if v[0] < corner1[0]:
            corner1[0] = v[0]
        elif v[0] > corner2[0]:
            corner2[0] = v[0]
        if v[1] < corner1[1]:
            corner1[1] = v[1]
        elif v[1] > corner2[1]:
            corner2[1] = v[1]
        if v[2] < corner1[2]:
            corner1[2] = v[2]
        elif v[2] > corner2[2]:
            corner2[2] = v[2]
    return corner1, corner2