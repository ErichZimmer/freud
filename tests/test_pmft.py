import numpy as np
import numpy.testing as npt
import freud
from freud.errors import FreudDeprecationWarning
import unittest
import warnings


class TestPMFTXYZ(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter("ignore", category=FreudDeprecationWarning)

    def test_box(self):
        boxSize = 20.0
        box = freud.box.Box.cube(boxSize)
        points = np.array([[-1.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
                          dtype=np.float32)
        orientations = np.array([[1, 0, 0, 0], [1, 0, 0, 0]], dtype=np.float32)
        maxX = 5.23
        nbinsX = 100
        maxY = 5.23
        nbinsY = 100
        maxZ = 5.23
        nbinsZ = 100
        myPMFT = freud.pmft.PMFTXYZ(maxX, maxY, maxZ, nbinsX, nbinsY, nbinsZ)
        myPMFT.accumulate(box, points, orientations, points, orientations)
        npt.assert_equal(myPMFT.box, freud.box.Box.cube(boxSize))
        npt.assert_equal(myPMFT.getBox(), freud.box.Box.cube(boxSize))

    def test_bins(self):
        maxX = 5.23
        nbinsX = 100
        maxY = 5.23
        nbinsY = 100
        maxZ = 5.23
        nbinsZ = 100
        dx = (2.0 * maxX / float(nbinsX))
        dy = (2.0 * maxY / float(nbinsY))
        dz = (2.0 * maxZ / float(nbinsZ))

        listX = np.zeros(nbinsX, dtype=np.float32)
        listY = np.zeros(nbinsY, dtype=np.float32)
        listZ = np.zeros(nbinsZ, dtype=np.float32)

        for i in range(nbinsX):
            x = float(i) * dx
            nextX = float(i + 1) * dx
            listX[i] = -maxX + ((x + nextX) / 2.0)

        for i in range(nbinsY):
            y = float(i) * dy
            nextY = float(i + 1) * dy
            listY[i] = -maxY + ((y + nextY) / 2.0)

        for i in range(nbinsZ):
            z = float(i) * dz
            nextZ = float(i + 1) * dz
            listZ[i] = -maxZ + ((z + nextZ) / 2.0)

        myPMFT = freud.pmft.PMFTXYZ(maxX, maxY, maxZ, nbinsX, nbinsY, nbinsZ)

        # Compare expected bins to the info from pmft
        npt.assert_almost_equal(myPMFT.X, listX, decimal=3)
        npt.assert_almost_equal(myPMFT.Y, listY, decimal=3)
        npt.assert_almost_equal(myPMFT.Z, listZ, decimal=3)

        npt.assert_equal(nbinsX, myPMFT.n_bins_X)
        npt.assert_equal(nbinsY, myPMFT.n_bins_Y)
        npt.assert_equal(nbinsZ, myPMFT.n_bins_Z)

        pcf = myPMFT.PCF
        npt.assert_equal(nbinsX, pcf.shape[2])
        npt.assert_equal(nbinsY, pcf.shape[1])
        npt.assert_equal(nbinsZ, pcf.shape[0])

    def test_shift_two_particles_dead_pixel(self):
        points = np.array([[1, 1, 1], [0, 0, 0]], dtype=np.float32)
        orientations = np.array([[1, 0, 0, 0], [1, 0, 0, 0]], dtype=np.float32)
        noshift = freud.pmft.PMFTXYZ(0.5, 0.5, 0.5, 3, 3, 3,
                                     shiftvec=[0, 0, 0])
        shift = freud.pmft.PMFTXYZ(0.5, 0.5, 0.5, 3, 3, 3,
                                   shiftvec=[1, 1, 1])

        for pm in [noshift, shift]:
            pm.compute(freud.box.Box.cube(3), points, orientations,
                       points, orientations, face_orientations=None)

        # Ignore warnings about NaNs
        warnings.simplefilter("ignore", category=RuntimeWarning)

        # Non-shifted pmft should have no non-inf valued voxels,
        # since the other point is outside the x/y/z max
        infcheck_noshift = np.isfinite(noshift.PMFT).sum()
        # Shifted pmft should have one non-inf valued voxel
        infcheck_shift = np.isfinite(shift.PMFT).sum()

        npt.assert_equal(infcheck_noshift, 0)
        npt.assert_equal(infcheck_shift, 1)


class TestPMFTR12(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter("ignore", category=FreudDeprecationWarning)

    def test_box(self):
        boxSize = 16.0
        box = freud.box.Box.square(boxSize)
        points = np.array([[-1.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
                          dtype=np.float32)
        angles = np.array([0.0, 0.0], dtype=np.float32)
        maxR = 5.23
        nbinsR = 10
        nbinsT1 = 20
        nbinsT2 = 30
        myPMFT = freud.pmft.PMFTR12(maxR, nbinsR, nbinsT1, nbinsT2)
        myPMFT.accumulate(box, points, angles, points, angles)
        npt.assert_equal(myPMFT.box, freud.box.Box.square(boxSize))
        npt.assert_equal(myPMFT.getBox(), freud.box.Box.square(boxSize))

    def test_bins(self):
        maxR = 5.23
        nbinsR = 10
        nbinsT1 = 20
        nbinsT2 = 30
        dr = (maxR / float(nbinsR))
        dT1 = (2.0 * np.pi / float(nbinsT1))
        dT2 = (2.0 * np.pi / float(nbinsT2))

        # make sure the radius for each bin is generated correctly
        listR = np.zeros(nbinsR, dtype=np.float32)
        listT1 = np.zeros(nbinsT1, dtype=np.float32)
        listT2 = np.zeros(nbinsT2, dtype=np.float32)

        for i in range(nbinsR):
            r = float(i) * dr
            nextr = float(i + 1) * dr
            listR[i] = 2.0/3.0 * (
                nextr*nextr*nextr - r*r*r)/(nextr*nextr - r*r)

        for i in range(nbinsT1):
            t = float(i) * dT1
            nextt = float(i + 1) * dT1
            listT1[i] = ((t + nextt) / 2.0)

        for i in range(nbinsT2):
            t = float(i) * dT2
            nextt = float(i + 1) * dT2
            listT2[i] = ((t + nextt) / 2.0)

        myPMFT = freud.pmft.PMFTR12(maxR, nbinsR, nbinsT1, nbinsT2)

        # Compare expected bins to the info from pmft
        npt.assert_almost_equal(myPMFT.R, listR, decimal=3)
        npt.assert_almost_equal(myPMFT.T1, listT1, decimal=3)
        npt.assert_almost_equal(myPMFT.T2, listT2, decimal=3)

        npt.assert_equal(nbinsR, myPMFT.n_bins_R)
        npt.assert_equal(nbinsT1, myPMFT.n_bins_T1)
        npt.assert_equal(nbinsT2, myPMFT.n_bins_T2)

        pcf = myPMFT.PCF
        npt.assert_equal(nbinsR, pcf.shape[0])
        npt.assert_equal(nbinsT1, pcf.shape[2])
        npt.assert_equal(nbinsT2, pcf.shape[1])


class TestPMFTXY2D(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter("ignore", category=FreudDeprecationWarning)

    def test_box(self):
        boxSize = 16.0
        box = freud.box.Box.square(boxSize)
        points = np.array([[-1.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
                          dtype=np.float32)
        angles = np.array([0.0, 0.0], dtype=np.float32)
        maxX = 3.0
        maxY = 3.0
        nbinsX = 100
        nbinsY = 100
        myPMFT = freud.pmft.PMFTXY2D(maxX, maxY, nbinsX, nbinsY)
        myPMFT.accumulate(box, points, angles, points, angles)
        npt.assert_equal(myPMFT.box, freud.box.Box.square(boxSize))
        npt.assert_equal(myPMFT.getBox(), freud.box.Box.square(boxSize))

    def test_two_particles(self):
        boxSize = 16.0
        box = freud.box.Box.square(boxSize)
        points = np.array([[-1.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
                          dtype=np.float32)
        angles = np.array([0.0, 0.0], dtype=np.float32)
        maxX = 3.0
        maxY = 3.0
        nbinsX = 100
        nbinsY = 100
        dx = (2.0 * maxX / float(nbinsX))
        dy = (2.0 * maxY / float(nbinsY))

        correct_bin_counts = np.zeros(shape=(nbinsY, nbinsX), dtype=np.int32)
        # calculation for array idxs
        # particle 0
        deltaX = points[0][0] - points[1][0]
        deltaY = points[0][1] - points[1][1]
        x = deltaX + maxX
        y = deltaY + maxY
        binX = int(np.floor(x / dx))
        binY = int(np.floor(y / dy))
        correct_bin_counts[binY, binX] = 1
        deltaX = points[1][0] - points[0][0]
        deltaY = points[1][1] - points[0][1]
        x = deltaX + maxX
        y = deltaY + maxY
        binX = int(np.floor(x / dx))
        binY = int(np.floor(y / dy))
        correct_bin_counts[binY, binX] = 1
        absoluteTolerance = 0.1

        myPMFT = freud.pmft.PMFTXY2D(maxX, maxY, nbinsX, nbinsY)
        myPMFT.accumulate(box, points, angles, points, angles)
        npt.assert_allclose(myPMFT.bin_counts, correct_bin_counts,
                            atol=absoluteTolerance)
        myPMFT.compute(box, points, angles, points, angles)
        npt.assert_allclose(myPMFT.bin_counts, correct_bin_counts,
                            atol=absoluteTolerance)
        myPMFT.reset()
        npt.assert_allclose(myPMFT.bin_counts, 0,
                            atol=absoluteTolerance)


if __name__ == '__main__':
    unittest.main()
