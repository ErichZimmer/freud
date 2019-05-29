# Copyright (c) 2010-2019 The Regents of the University of Michigan
# This file is from the freud project, released under the BSD 3-Clause License.

# Methods used throughout freud for convenience

import logging
import numpy as np
import freud.box

logger = logging.getLogger(__name__)


def convert_array(array, dimensions=None, dtype=np.float32):
    """Function which takes a given array, checks the dimensions,
    and converts to a supplied dtype and/or makes the array
    contiguous as required by the user.

    .. moduleauthor:: Eric Harper <harperic@umich.edu>

    Args:
        array (:class:`numpy.ndarray`): Array to check and convert.
        dimensions (int): Expected dimensions of the array.
        dtype: code:`dtype` to convert the array to if :code:`array.dtype`
            is different. If `None`, :code:`dtype` will not be changed.
            (Default value = `numpy.float32`).
        array. Default behavior casts to a contiguous array.

    Returns:
        py:class:`numpy.ndarray`: Array.
    """
    array = np.asarray(array)

    if dimensions is not None and array.ndim != dimensions:
        raise TypeError("array.ndim = {}; expected ndim = {}".format(
            array.ndim, dimensions))
    return np.require(array, dtype=dtype, requirements=['C'])


def convert_box(box):
    """Function which takes a box-like object and attempts to convert it to
    :class:`freud.box.Box`. Existing :class:`freud.box.Box` objects are
    used directly.

    .. moduleauthor:: Bradley Dice <bdice@bradleydice.com>

    Args:
      box (box-like object (see :meth:`freud.box.Box.from_box`)): Box to
          check and convert if needed.

    Returns:
      py:class:`freud.box.Box`: freud box.
    """
    if not isinstance(box, freud.box.Box):
        try:
            box = freud.box.Box.from_box(box)
        except ValueError:
            raise
    return box
