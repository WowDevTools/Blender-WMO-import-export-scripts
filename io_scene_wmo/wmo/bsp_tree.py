from . import wmo_format
from .wmo_format import *

from . import collision
from .collision import *

import mathutils
from mathutils import *

import sys


class BSPTree:
    def __init__(self):
        self.Nodes = []
        self.Faces = []
        pass

    # split box in two smaller, at dist calculated internally
    def split_box(self, box, facesInBox, vertices, indices, axis):
        # compute average of vertice positions
        """count = 0
        sum = 0
        for iFace in range(len(facesInBox)):
            sum += vertices[indices[facesInBox[iFace] * 3]][axis]
            sum += vertices[indices[facesInBox[iFace] * 3 + 1]][axis]
            sum += vertices[indices[facesInBox[iFace] * 3 + 2]][axis]
            count += 1
        splitDist = sum / count

        # if split is out of box, just split in half
        if(splitDist <= box[0][axis] or splitDist >= box[1][axis]):"""
        split_dist = (box[0][axis] + box[1][axis]) / 2

        new_box1 = (Vector((box[0][0], box[0][1], box[0][2])), Vector((box[1][0], box[1][1], box[1][2])))
        new_box1[1][axis] = split_dist

        new_box2 = (Vector((box[0][0], box[0][1], box[0][2])), Vector((box[1][0], box[1][1], box[1][2])))
        new_box2[0][axis] = split_dist

        # split dist absolute coordinate on split axis
        # ret_splitDist = splitDist - ((box[0][axis] + box[1][axis]) / 2)
        return split_dist, new_box1, new_box2

    # return index of add
    def add_node(self, box, faces_in_box, vertices, indices, max_face_count):

        node = BSP_Node()

        i_node = len(self.Nodes)
        self.Nodes.append(node)

        # part contain less than 30 polygons, lets end this, add final node
        if len(faces_in_box) <= max_face_count:
            node.PlaneType = BSP_PLANE_TYPE.Leaf
            node.Children = (-1, -1)
            node.NumFaces = len(faces_in_box)
            node.FirstFace = len(self.Faces)
            node.Dist = 0

            self.Faces.extend(faces_in_box)
            return i_node

        # split bigger side
        box_size_x = box[1][0] - box[0][0]
        box_size_y = box[1][1] - box[0][1]
        box_size_z = box[1][2] - box[0][2]

        if box_size_x > box_size_y and box_size_x > box_size_z:
            # split on axis X (YZ plane)
            plane_type = BSP_PLANE_TYPE.YZ_plane
        elif box_size_y > box_size_x and box_size_y > box_size_z:
            # split on axis Y (XZ plane)
            plane_type = BSP_PLANE_TYPE.XZ_plane
        else:
            # split on axis Z (XY plane)
            plane_type = BSP_PLANE_TYPE.XY_plane

        split_result = self.split_box(box, faces_in_box, vertices, indices, plane_type)

        split_dist = split_result[0]

        child1_box = split_result[1]
        child1_faces = []

        # calculate faces in child1 box
        for f in faces_in_box:
            tri = (Vector((vertices[indices[f * 3]])),
                   Vector((vertices[indices[f * 3 + 1]])),
                   Vector((vertices[indices[f * 3 + 2]])))

            if collide_box_tri(child1_box, tri):
                child1_faces.append(f)

        child2_box = split_result[2]
        child2_faces = []

        # calculate faces in child2 box
        for f in faces_in_box:
            tri = (Vector((vertices[indices[f * 3]])),
                   Vector((vertices[indices[f * 3 + 1]])),
                   Vector((vertices[indices[f * 3 + 2]])))

            if collide_box_tri(child2_box, tri):
                child2_faces.append(f)

        # dont add child if there is no faces inside
        if len(child1_faces) == 0:
            i_child1 = -1
        else:
            i_child1 = self.add_node(child1_box, child1_faces, vertices, indices, max_face_count)

        if len(child2_faces) == 0:
            i_child2 = -1
        else:
            i_child2 = self.add_node(child2_box, child2_faces, vertices, indices, max_face_count)

        # node = BSP_Node()
        node.PlaneType = plane_type
        node.Children = (i_child1, i_child2)
        node.NumFaces = 0
        node.FirstFace = 0
        node.Dist = split_dist

        return i_node

    def GenerateBSP(self, vertices, indices, max_face_count):
        resurs_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(100000)

        faces = []
        for iFace in range(len(indices) // 3):
            faces.append(iFace)

        box = calculate_bounding_box(vertices)
        self.add_node(box, faces, vertices, indices, max_face_count)

        sys.setrecursionlimit(resurs_limit)

