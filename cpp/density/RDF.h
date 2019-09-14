// Copyright (c) 2010-2019 The Regents of the University of Michigan
// This file is from the freud project, released under the BSD 3-Clause License.

#ifndef RDF_H
#define RDF_H

#include <memory>

#include "Box.h"
#include "NeighborList.h"
#include "NeighborQuery.h"
#include "PMFT.h"
#include "ThreadStorage.h"
#include "VectorMath.h"
#include "Histogram.h"

/*! \file RDF.h
    \brief Routines for computing radial density functions.
*/

namespace freud { namespace density {
class RDF
{
public:
    //! Constructor
    RDF(unsigned int bins, float r_max, float r_min = 0);

    //! Destructor
    ~RDF() {};

    //! Reset the RDF array to all zeros
    void reset();

    //! Compute the RDF
    void accumulate(const freud::locality::NeighborQuery* neighbor_query,
                    const vec3<float>* query_points, unsigned int n_query_points,
                    const freud::locality::NeighborList* nlist, freud::locality::QueryArgs qargs);

    //! Implementing pure virtual function from parent class.
    virtual void reduce();

    //
    //! Return :code:`thing_to_return` after reducing.
    template<typename T>
    T &reduceAndReturn(T &thing_to_return)
    {
        if (m_reduce == true)
        {
            reduce();
        }
        m_reduce = false;
        return thing_to_return;
    }

    //! \internal
    // Wrapper to do accumulation.
    /*! \param neighbor_query NeighborQuery object to iterate over
        \param query_points Points
        \param n_query_points Number of query_points
        \param nlist Neighbor List. If not NULL, loop over it. Otherwise, use neighbor_query
           appropriately with given qargs.
        \param qargs Query arguments
        \param cf An object with operator(NeighborBond) as input.
    */
    template<typename Func>
    void accumulateGeneral(const locality::NeighborQuery* neighbor_query,
                           const vec3<float>* query_points, unsigned int n_query_points,
                           const locality::NeighborList* nlist,
                           freud::locality::QueryArgs qargs,
                           Func cf)
    {
        m_box = neighbor_query->getBox();
        locality::loopOverNeighbors(neighbor_query, query_points, n_query_points, qargs, nlist, cf);
        m_frame_counter++;
        m_n_points = neighbor_query->getNPoints();
        m_n_query_points = n_query_points;
        m_reduce = true;
    }

    //! Get the simulation box
    const box::Box& getBox() const
    {
        return m_box;
    }

    const util::ManagedArray<float> &getRDF()
    {
        return reduceAndReturn(m_pcf);
    }

    //! Get a reference to the PCF array
    const util::ManagedArray<unsigned int> &getBinCounts()
    {
        return m_histogram.getBinCounts();
    }

    //! Get a reference to the N_r array.
    /*! Mathematically, m_N_r[i] is the average number of points
     *  contained within a ball of radius getBins()[i+1] centered at a given
     *  query_point, averaged over all query_points.
     */
    const util::ManagedArray<float> &getNr()
    {
        return reduceAndReturn(m_N_r);
    }

    float getRMax() const
    {
        return m_r_max;
    }

    float getRMin() const
    {
        return m_r_min;
    }

    //! Get bin centers.
    std::vector<float> getR()
    {
        return m_histogram.getBinCenters()[0];
    }

    //! Return the bin boundaries.
    std::vector<float> getBins() const
    {
        // RDFs are always 1D histograms, so we just return the first element.
        return m_histogram.getBinBoundaries()[0];
    }

private:
    box::Box m_box;
    unsigned int m_frame_counter;            //!< Number of frames calculated.
    unsigned int m_n_points;                 //!< The number of points.
    unsigned int m_n_query_points;           //!< The number of query points.
    bool m_reduce;                           //!< Whether or not the histogram needs to be reduced.

    float m_r_max;                           //!< Maximum r at which to compute g(r)
    float m_r_min;                           //!< Minimum r at which to compute g(r)
    unsigned int m_bins;                     //!< Number of r bins to compute g(r) over

    util::ManagedArray<float> m_pcf;         //!< The computed pair correlation function.
    util::Histogram m_histogram;             //!< Histogram of interparticle distances (bond lengths).
    util::ManagedArray<float> m_N_r;         //!< Cumulative bin sum N(r) (the average number of points in a ball of radius r).
    util::ManagedArray<float> m_vol_array2D; //!< Areas of concentric rings corresponding to the histogram bins in 2D.
    util::ManagedArray<float> m_vol_array3D; //!< Areas of concentric spherical shells corresponding to the histogram bins in 3D.

    util::Histogram::ThreadLocalHistogram m_local_histograms;   //!< Thread local bin counts for TBB parallelism
};

}; }; // end namespace freud::density

#endif // RDF_H
