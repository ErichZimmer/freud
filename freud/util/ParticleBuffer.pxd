# Copyright (c) 2010-2018 The Regents of the University of Michigan
# This file is from the freud project, released under the BSD 3-Clause License.

from freud.util cimport _ParticleBuffer

cdef class ParticleBuffer:
    cdef _ParticleBuffer.ParticleBuffer * thisptr
