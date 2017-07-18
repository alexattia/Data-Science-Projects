import cv2
import numpy as np
import sys
import os
import imp
import glob
from sklearn.cluster import KMeans
import skimage.filters as skf
import skimage.color as skc
import skimage.morphology as skm
from skimage.measure import label

class Back():
    """
    Two algorithms are used together to separate background and foreground.
    One consider as background all pixel whose color is close to the pixels
    in the corners. This part is impacted by the `max_distance' and
    `use_lab' settings.
    The second one computes the edges of the image and uses a flood fill
    starting from all corners.
    """
    def __init__(self, max_distance=5, use_lab=True):
        """
        The possible settings are:
            - max_distance: The maximum distance for two colors to be
              considered closed. A higher value will yield to a more aggressive
              background removal.
              (default: 5)
            - use_lab: Whether to use the LAB color space to perform
              background removal. More expensive but closer to eye perception.
              (default: True)
        """
        self._settings= {
            'max_distance': max_distance,
            'use_lab': use_lab,
        }

    def get(self, img):
        f = self._floodfill(img)
        g = self._global(img)
        m = f | g

        if np.count_nonzero(m) < 0.90 * m.size:
            return m

        ng, nf = np.count_nonzero(g), np.count_nonzero(f)

        if ng < 0.90 * g.size and nf < 0.90 * f.size:
            return g if ng > nf else f
        if ng < 0.90 * g.size:
            return g
        if nf < 0.90 * f.size:
            return f

        return np.zeros_like(m)

    def _global(self, img):
        h, w = img.shape[:2]
        mask = np.zeros((h, w), dtype=np.bool)
        max_distance = self._settings['max_distance']

        if self._settings['use_lab']:
            img = skc.rgb2lab(img)

        # Compute euclidean distance of each corner against all other pixels.
        corners = [(0, 0), (-1, 0), (0, -1), (-1, -1)]
        for color in (img[i, j] for i, j in corners):
            norm = np.sqrt(np.sum(np.square(img - color), 2))
            # Add to the mask pixels close to one of the corners.
            mask |= norm < max_distance

        return mask

    def _floodfill(self, img):
        back = self._scharr(img)
        # Binary thresholding.
        back = back > 0.05

        # Thin all edges to be 1-pixel wide.

        back = skm.skeletonize(back)
        # Edges are not detected on the borders, make artificial ones.
        back[0, :] = back[-1, :] = True
        back[:, 0] = back[:, -1] = True

        # Label adjacent pixels of the same color.
        labels = label(back, background=-1, connectivity=1)

        # Count as background all pixels labeled like one of the corners.
        corners = [(1, 1), (-2, 1), (1, -2), (-2, -2)]
        for l in (labels[i, j] for i, j in corners):
            back[labels == l] = True

        # Remove remaining inner edges.
        return skm.opening(back)

    def _scharr(self, img):
        # Invert the image to ease edge detection.
        img = 1. - img
        grey = skc.rgb2grey(img)
        return skf.scharr(grey)

class ColorExtractor():
    def __init__(self):
        self._back = Back(max_distance=10, n_clusters=3)

    def get_bar_hist(self, filepath, full_return=False):
        image = cv2.imread(filepath)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        back_mask = self._back.get(image)
        image_noback = np.zeros(image.shape)
        image_noback[~back_mask] = image[~back_mask] /255
        image_array = image[~back_mask]
        clt = KMeans(n_clusters = n_clusters)
        clt.fit(image_array)
        hist = self.centroid_histogram(clt)
        if full_return:
            bar = self.plot_colors(hist, clt.cluster_centers_)
            return image, image_noback, bar, hist
        else:
            return image, hist


    def centroid_histogram(self, clt):
        # grab the number of different clusters and create a histogram
        # based on the number of pixels assigned to each cluster
        numLabels = np.arange(0, len(np.unique(clt.labels_)) + 1)
        (hist, _) = np.histogram(clt.labels_, bins = numLabels)

        # normalize the histogram, such that it sums to one
        hist /= hist.astype("float").sum()

        # return the histogram
        return hist

    def plot_colors(self, hist, centroids):
        # initialize the bar chart representing the relative frequency
        # of each of the colors
        bar = np.zeros((50, 300, 3), dtype = "uint8")
        startX = 0

        zipped = zip(hist, centroids)
        zipped = sorted(zipped, reverse=True, key=lambda x : x[0])

        # loop over the percentage of each cluster and the color of
        # each cluster
        for (percent, color) in zipped:
            # plot the relative percentage of each cluster
            endX = startX + (percent * 300)
            cv2.rectangle(bar, (int(startX), 0), (int(endX), 50),
                color.astype("uint8").tolist(), -1)
            startX = endX

        # return the bar chart
        return bar