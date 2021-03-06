# canonical.py - functions for converting systems to canonical forms
# RMM, 10 Nov 2012

from .exception import ControlNotImplemented
from .lti import issiso
from .statesp import StateSpace
from .statefbk import ctrb

from numpy import zeros, shape, poly
from numpy.linalg import inv

__all__ = ['canonical_form', 'reachable_form']

def canonical_form(xsys, form='reachable'):
    """Convert a system into canonical form

    Parameters
    ----------
    xsys : StateSpace object
        System to be transformed, with state 'x'
    form : String
        Canonical form for transformation.  Chosen from:
          * 'reachable' - reachable canonical form
          * 'observable' - observable canonical form [not implemented]
          * 'modal' - modal canonical form [not implemented]

    Returns
    -------
    zsys : StateSpace object
        System in desired canonical form, with state 'z'
    T : matrix
        Coordinate transformation matrix, z = T * x
    """

    # Call the appropriate tranformation function
    if form == 'reachable':
        return reachable_form(xsys)
    else:
        raise ControlNotImplemented(
            "Canonical form '%s' not yet implemented" % form)


# Reachable canonical form
def reachable_form(xsys):
    """Convert a system into reachable canonical form

    Parameters
    ----------
    xsys : StateSpace object
        System to be transformed, with state `x`

    Returns
    -------
    zsys : StateSpace object
        System in reachable canonical form, with state `z`
    T : matrix
        Coordinate transformation: z = T * x
    """
    # Check to make sure we have a SISO system
    if not issiso(xsys):
        raise ControlNotImplemented(
            "Canonical forms for MIMO systems not yet supported")

    # Create a new system, starting with a copy of the old one
    zsys = StateSpace(xsys)

    # Generate the system matrices for the desired canonical form
    zsys.B = zeros(shape(xsys.B))
    zsys.B[0, 0] = 1
    zsys.A = zeros(shape(xsys.A))
    Apoly = poly(xsys.A)                # characteristic polynomial
    for i in range(0, xsys.states):
        zsys.A[0, i] = -Apoly[i+1] / Apoly[0]
        if (i+1 < xsys.states):
            zsys.A[i+1, i] = 1

    # Compute the reachability matrices for each set of states
    Wrx = ctrb(xsys.A, xsys.B)
    Wrz = ctrb(zsys.A, zsys.B)

    # Transformation from one form to another
    Tzx = Wrz * inv(Wrx)

    # Finally, compute the output matrix
    zsys.C = xsys.C * inv(Tzx)

    return zsys, Tzx
