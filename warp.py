import cv2
import numpy as np
from cvhelper import rectContains

def calculateDelaunayTriangles(rect, points):
    subdiv = cv2.Subdiv2D(rect)

    for p in points:
        subdiv.insert(p)

    triangleList = subdiv.getTriangleList()

    delaunayTri = []

    #### Transform from 6 coordinates to 3 indexes
    for t in triangleList:
        pt = []
        pt.append((t[0], t[1]))
        pt.append((t[2], t[3]))
        pt.append((t[4], t[5]))

        pt1 = (t[0], t[1])
        pt2 = (t[2], t[3])
        pt3 = (t[4], t[5])

        if rectContains(rect, pt1) and rectContains(rect, pt2) and rectContains(rect, pt3):
            ind = []
            for j in range(0, 3):
                for k in range(0, len(points)):
                    if(abs(pt[j][0] - points[k][0]) < 1.0 and abs(pt[j][1] - points[k][1]) < 1.0):
                        ind.append(k)
            if len(ind) == 3:
                delaunayTri.append((ind[0], ind[1], ind[2]))
    ####

    return delaunayTri


# Apply affine transform calculated using srcTri and dstTri to src and
# output an image of size.
def applyAffineTransform(src, srcTri, dstTri, size):
    # Given a pair of triangles, find the affine transform.
    warpMat = cv2.getAffineTransform(np.float32(srcTri), np.float32(dstTri))

    # Apply the Affine Transform just found to the src image
    dst = cv2.warpAffine(src, warpMat, (size[0], size[1]), None, flags=cv2.INTER_LINEAR,
                         borderMode=cv2.BORDER_REFLECT_101)

    return dst

def warpTriangle(img, iw, t, tw) :

    # Find bounding rectangle for each triangle
    r = cv2.boundingRect(np.float32([t]))
    rw = cv2.boundingRect(np.float32([tw]))


    # Offset points by left top corner of the respective rectangles
    t_offset = []
    tw_offset = []
    for i in range(0, 3):
        tw_offset.append(((tw[i][0] - rw[0]), (tw[i][1] - rw[1])))
        t_offset.append(((t[i][0] - r[0]), (t[i][1] - r[1])))

    # Get dst mask by filling triangle
    mask = np.zeros((rw[3], rw[2], 3), dtype = np.float32)
    cv2.fillConvexPoly(mask, np.int32(tw_offset), (1.0, 1.0, 1.0), 16, 0)

    # Apply warpImage to small rectangular patches
    startRect = img[r[1]:r[1] + r[3], r[0]:r[0] + r[2]]

    size = (rw[2], rw[3])
    startImage = applyAffineTransform(startRect, t_offset, tw_offset, size)

    # Copy triangular region of the rectangular patch to the output image
    iw[rw[1]:rw[1] + rw[3], rw[0]:rw[0] + rw[2]] = iw[rw[1]:rw[1] + rw[3], rw[0]:rw[0] + rw[2]] * (1 - mask) + startImage * mask

def draw_triangulation(img, pts, indexes, color):
    ####
    # CV.line needs INT coordinates
    ####
    pts_int = []
    for pt in pts:
        pts_int.append((int(round(pt[0])),int(round(pt[1]))))

    ####
    # Draw Delaunay triangles
    ####
    for (i,j,k) in indexes:
        # if rectContains(rect, pts[i]) and rectContains(rect, pts[j]) and rectContains(rect, pts[k]):
        cv2.line(img, pts_int[i], pts_int[j], color, thickness=2)
        cv2.line(img, pts_int[j], pts_int[k], color, thickness=2)
        cv2.line(img, pts_int[k], pts_int[i], color, thickness=2)
