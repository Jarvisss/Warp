import cv2
import os
import numpy as np
import csv


def calculateDelaunayTriangles(rect, points):
    subdiv = cv2.Subdiv2D(rect)

    for p in points:
        subdiv.insert(p)

    triangleList = subdiv.getTriangleList()

    delaunayTri = []

    pt = []

    count= 0

    for t in triangleList:
        pt.append((t[0], t[1]))
        pt.append((t[2], t[3]))
        pt.append((t[4], t[5]))

        pt1 = (t[0], t[1])
        pt2 = (t[2], t[3])
        pt3 = (t[4], t[5])

        if rectContains(rect, pt1) and rectContains(rect, pt2) and rectContains(rect, pt3):
            count = count + 1
            ind = []
            for j in range(0, 3):
                for k in range(0, len(points)):
                    if(abs(pt[j][0] - points[k][0]) < 1.0 and abs(pt[j][1] - points[k][1]) < 1.0):
                        ind.append(k)
            if len(ind) == 3:
                delaunayTri.append((ind[0], ind[1], ind[2]))

        pt = []


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



# Warps and alpha blends triangular regions from img1 and img2 to img
def morphTriangle(start_img, end_img, morph_img, start_tri, end_tri, morph_tri, alpha) :

    # Find bounding rectangle for each triangle
    r1 = cv2.boundingRect(np.float32([start_tri]))
    r2 = cv2.boundingRect(np.float32([end_tri]))
    r_morph = cv2.boundingRect(np.float32([morph_tri]))


    # Offset points by left top corner of the respective rectangles
    t1Rect = []
    t2Rect = []
    tRect = []


    for i in range(0, 3):
        tRect.append(((morph_tri[i][0] - r_morph[0]), (morph_tri[i][1] - r_morph[1])))
        t1Rect.append(((start_tri[i][0] - r1[0]), (start_tri[i][1] - r1[1])))
        t2Rect.append(((end_tri[i][0] - r2[0]), (end_tri[i][1] - r2[1])))


    # Get mask by filling triangle
    mask = np.zeros((r_morph[3], r_morph[2], 3), dtype = np.float32)
    cv2.fillConvexPoly(mask, np.int32(tRect), (1.0, 1.0, 1.0), 16, 0)

    # Apply warpImage to small rectangular patches
    startRect = start_img[r1[1]:r1[1] + r1[3], r1[0]:r1[0] + r1[2]]
    endRect = end_img[r2[1]:r2[1] + r2[3], r2[0]:r2[0] + r2[2]]

    size = (r_morph[2], r_morph[3])
    startImage = applyAffineTransform(startRect, t1Rect, tRect, size)
    endImage = applyAffineTransform(endRect, t2Rect, tRect, size)

    # Alpha blend rectangular patches
    imgRect = (1.0 - alpha) * startImage + alpha * endImage

    # Copy triangular region of the rectangular patch to the output image
    morph_img[r_morph[1]:r_morph[1] + r_morph[3], r_morph[0]:r_morph[0] + r_morph[2]] = morph_img[r_morph[1]:r_morph[1] + r_morph[3], r_morph[0]:r_morph[0] + r_morph[2]] * (1 - mask) + imgRect * mask


def warpTriangle(img, iw, t, tw) :

    # Find bounding rectangle for each triangle
    r = cv2.boundingRect(np.float32([t]))
    rw = cv2.boundingRect(np.float32([tw]))


    # Offset points by left top corner of the respective rectangles
    tRect = []
    twRect = []

    for i in range(0, 3):
        twRect.append(((tw[i][0] - rw[0]), (tw[i][1] - rw[1])))
        tRect.append(((t[i][0] - r[0]), (t[i][1] - r[1])))

    # Get mask by filling triangle
    mask = np.zeros((rw[3], rw[2], 3), dtype = np.float32)
    cv2.fillConvexPoly(mask, np.int32(twRect), (1.0, 1.0, 1.0), 16, 0)

    # Apply warpImage to small rectangular patches
    startRect = start_img[r[1]:r[1] + r[3], r[0]:r[0] + r[2]]

    size = (rw[2], rw[3])
    startImage = applyAffineTransform(startRect, tRect, twRect, size)


    # Copy triangular region of the rectangular patch to the output image
    iw[r[1]:r[1] + r[3], r[0]:r[0] + r[2]] = iw[r[1]:r[1] + r[3], r[0]:r[0] + r[2]] * (1 - mask) + imgRect * mask
    # r1 = cv2.boundingRect(np.float32([t]))
    # r2 = cv2.boundingRect(np.float32([tw]))
    #
    # t1Rect = []
    # t2Rect = []
    # t2RectInt = []
    #
    # for i in range(0, 3):
    #     t1Rect.append(((t1[i][0] - r1[0]),(t1[i][1] - r1[1])))
    #     t2Rect.append(((t2[i][0] - r2[0]),(t2[i][1] - r2[1])))
    #     t2RectInt.append(((t2[i][0] - r2[0]),(t2[i][1] - r2[1])))
    #
    #
    # mask = np.zeros((r2[3], r2[2], 3), dtype = np.float32)
    # cv2.fillConvexPoly(mask, np.int32(t2RectInt), (1.0, 1.0, 1.0), 16, 0);
    #
    # img1Rect = img1[r1[1]:r1[1] + r1[3], r1[0]:r1[0] + r1[2]]
    #
    # size = (r2[2], r2[3])
    #
    # img2Rect = applyAffineTransform(img1Rect, t1Rect, t2Rect, size)
    #
    # img2Rect = img2Rect * mask
    #
    # img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] = img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] * ( (1.0, 1.0, 1.0) - mask )
    #
    # img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] = img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] + img2Rect

def read_image(path):
    img = cv2.imread(path)
    return img

def read_pts(csv_path, start, end):
    p_start = []
    p_end = []
    pt_col = 5
    with open(csv_path,'r') as f:
        f_csv = csv.reader(f)
        for row in f_csv:
            if row[0] == '{0}.jpg'.format(start):
                p_start.append((eval(row[pt_col])['cx'],eval(row[pt_col])['cy']))
            elif row[0] == '{0}.jpg'.format(end):
                p_end.append((eval(row[pt_col])['cx'],eval(row[pt_col])['cy']))
    return p_start,p_end

def visualize_pts(img, pts):
    for i in range(len(pts)):
        cv2.circle(img, pts[i], 1, (0, 0, 255), thickness=2)

    cv2.imshow('1', img)
    cv2.waitKey()
    return


def sample_lines_points(samples, pstart, pend):
    pts = []
    segments = samples+1
    delta = (pend[0] - pstart[0], pend[1]-pstart[1])
    delta_step = (delta[0] / segments, delta[1] / segments)
    for i in range(1, samples+1):
        pts.append((int(pstart[0]+delta_step[0]*i), int(pstart[1]+delta_step[1]*i)))

    return pts




def get_corner_points_and_half_points(rect, samples):
    (left, top, w, h) = rect
    pts = []

    right = left + w - 1
    bottom = top + h - 1

    pts.append((left,top))
    pts.append((left,bottom))
    pts.append((right,bottom))
    pts.append((right,top))

    pts = pts + sample_lines_points(samples, (left, top), (left, bottom))
    pts = pts + sample_lines_points(samples, (left, bottom), (right, bottom))
    pts = pts + sample_lines_points(samples, (right, bottom), (right, top))
    pts = pts + sample_lines_points(samples, (right, top), (left, top))

    return pts

def rectContains(rect,pt):
    logic = rect[0] <= pt[0] < rect[0]+rect[2] and rect[1] <= pt[1] < rect[1]+rect[3]
    return logic

def draw_triangulation(img, pts, indexes, color):
    size = img.shape
    pts_int = []
    for pt in pts:
        pts_int.append((int(round(pt[0])),int(round(pt[1]))))
    # pts = pts.astype(np.int)
    for (i,j,k) in indexes:
        # if rectContains(rect, pts[i]) and rectContains(rect, pts[j]) and rectContains(rect, pts[k]):
        cv2.line(img, pts_int[i], pts_int[j], color, thickness=2)
        cv2.line(img, pts_int[j], pts_int[k], color, thickness=2)
        cv2.line(img, pts_int[k], pts_int[i], color, thickness=2)


if __name__ == '__main__':
    start = 'shuihu'
    end = 'qie'

    edge_samples = 1
    start_path = './samples/1/{0}.jpg'.format(start)
    end_path = './samples/1/{0}.jpg'.format(end)
    save_dir = './samples/1/results'

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    csv_path = './samples/1/via_export_csv.csv'


    morph_alpha = 0
    n_frames = 20
    warp_alpha = np.linspace(0, 100, n_frames)

    start_img = read_image(start_path)
    end_img = read_image(end_path)

    pt_start, pt_end = read_pts(csv_path, start=start, end=end)
    assert(len(pt_end) == len(pt_start))

    # visualize_pts(start_img,pt_start)

    # Add Corner points to features
    size1, size2 = start_img.shape, end_img.shape
    rect1,rect2 = (0,0,size1[1],size1[0]), (0,0,size2[1],size2[0])
    pt_end = pt_end + get_corner_points_and_half_points(rect1,edge_samples)
    pt_start = pt_start + get_corner_points_and_half_points(rect2,edge_samples)


    # Get delaunay indexes
    delaunay_indexes1 = calculateDelaunayTriangles(rect1, pt_end)
    delaunay_indexes2 = calculateDelaunayTriangles(rect2, pt_start)


    for (f,a) in enumerate(warp_alpha):
        print(a)
        aa = a / 100
        warp_pts = []
        start_warp = np.zeros(size1, dtype=start_img.dtype)
        end_warp = np.zeros(size1, dtype=start_img.dtype)
        imgMorph = np.zeros(size1, dtype=start_img.dtype)
        for i in range(0, len(pt_end)):
            x = (1 - aa) * pt_start[i][0] + aa * pt_end[i][0]
            y = (1 - aa) * pt_start[i][1] + aa * pt_end[i][1]
            warp_pts.append((x, y))


        # for each triangle, do the morph in the bounding rect
        for (i,j,k) in delaunay_indexes1:
            t1 = [pt_start[i], pt_start[j], pt_start[k]]
            t2 = [pt_end[i], pt_end[j], pt_end[k]]
            t = [warp_pts[i], warp_pts[j], warp_pts[k]]
            morphTriangle(start_img, end_img, start_warp, t1, t2, t, 0)
            morphTriangle(start_img, end_img, end_warp, t1, t2, t, 1)

            # warpTriangle(img1,img2,t1,t2)
        aa=0.5
        imgMorph = (1-aa) * start_warp + aa * end_warp
        save_total = np.vstack((start_warp, end_warp, imgMorph))
        # draw_triangulation(imgMorph, warp_pts, delaunay_indexes1, (255,0,0))
        cv2.imwrite(os.path.join(save_dir,'{0}_start.jpg'.format(f)), cv2.resize(start_warp, (start_warp.shape[1] // 3, start_warp.shape[0] // 3)))
        cv2.imwrite(os.path.join(save_dir,'{0}_end.jpg'.format(f)), cv2.resize(end_warp, (end_warp.shape[1] // 3, end_warp.shape[0] // 3)))
        cv2.imwrite(os.path.join(save_dir,'{0}_morph.jpg'.format(f)), cv2.resize(imgMorph, (imgMorph.shape[1] // 3, imgMorph.shape[0] // 3)))
        cv2.imwrite(os.path.join(save_dir,'{0}_total.jpg'.format(f)), cv2.resize(save_total, (save_total.shape[1] // 3, save_total.shape[0] // 3)))
        # cv2.imshow("Morphed", cv2.resize(imgMorph, (imgMorph.shape[1] // 3, end_img.shape[0] // 3)))
        # cv2.waitKey(60)

    pass