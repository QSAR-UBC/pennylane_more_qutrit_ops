# Copyright 2018-2022 Xanadu Quantum Technologies Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
This submodule contains the qutrit quantum operations
that do not depend on any parameters.
"""
# pylint:disable=arguments-differ
import numpy as np

import pennylane as qml
from pennylane.operation import AdjointUndefinedError, Operation
from pennylane.wires import Wires

from .parametric_ops import validate_subspace

OMEGA = np.exp(2 * np.pi * 1j / 3)
ZETA = OMEGA ** (1 / 3)  # ZETA will be used as a phase for later non-parametric operations


class TShift(Operation):
    r"""TShift(wires)
    The qutrit shift operator

    The construction of this operator is based on equation 1 from
    `Yeh et al. (2022) <https://arxiv.org/abs/2204.00552>`_.

    .. math:: TShift = \begin{bmatrix}
                        0 & 0 & 1 \\
                        1 & 0 & 0 \\
                        0 & 1 & 0
                    \end{bmatrix}

    **Details:**

    * Number of wires: 1
    * Number of parameters: 0

    Args:
        wires (Sequence[int] or int): the wire the operation acts on
    """

    num_wires = 1
    """int: Number of wires that the operator acts on."""

    num_params = 0
    """int: Number of trainable parameters that the operator depends on."""

    @staticmethod
    def compute_matrix():
        r"""Representation of the operator as a canonical matrix in the computational basis (static method).

        The canonical matrix is the textbook matrix representation that does not consider wires.
        Implicitly, this assumes that the wires of the operator correspond to the global wire order.

        .. seealso:: :meth:`~.TShift.matrix`

        Returns:
            ndarray: matrix

        **Example**

        >>> print(qml.TShift.compute_matrix())
        [[0 0 1]
         [1 0 0]
         [0 1 0]]
        """
        return np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]])

    @staticmethod
    def compute_eigvals():
        r"""Eigenvalues of the operator in the computational basis (static method).

        If :attr:`diagonalizing_gates` are specified and implement a unitary :math:`U^{\dagger}`,
        the operator can be reconstructed as

        .. math:: O = U \Sigma U^{\dagger},

        where :math:`\Sigma` is the diagonal matrix containing the eigenvalues.

        Otherwise, no particular order for the eigenvalues is guaranteed.

        .. seealso:: :meth:`~.TShift.eigvals`

        Returns:
            array: eigenvalues

        **Example**

        >>> print(qml.TShift.compute_eigvals())
        [ -0.5+0.8660254j -0.5-0.8660254j 1. +0.j         ]
        """
        return np.array([OMEGA, OMEGA**2, 1])

    # TODO: Add compute_decomposition once parametric ops are added.

    def pow(self, z):
        return super().pow(z % 3)


class TClock(Operation):
    r"""TClock(wires)
    Ternary Clock gate

    The construction of this operator is based on equation 1 from
    `Yeh et al. (2022) <https://arxiv.org/abs/2204.00552>`_.

    .. math:: TClock = \begin{bmatrix}
                        1 & 0      & 0        \\
                        0 & \omega & 0        \\
                        0 & 0      & \omega^2
                    \end{bmatrix}

    where :math:`\omega = e^{2 \pi i / 3}`.

    **Details:**

    * Number of wires: 1
    * Number of parameters: 0

    Args:
        wires (Sequence[int] or int): the wire the operation acts on
    """

    num_wires = 1
    """int: Number of wires that the operator acts on."""

    num_params = 0
    """int: Number of trainable parameters that the operator depends on."""

    @staticmethod
    def compute_matrix():
        r"""Representation of the operator as a canonical matrix in the computational basis (static method).

        The canonical matrix is the textbook matrix representation that does not consider wires.
        Implicitly, this assumes that the wires of the operator correspond to the global wire order.

        .. seealso:: :meth:`~.TClock.matrix`

        Returns:
            ndarray: matrix

        **Example**

        >>> print(qml.TClock.compute_matrix())
        [[ 1. +0.j         0. +0.j         0. +0.j       ]
         [ 0. +0.j        -0.5+0.8660254j  0. +0.j       ]
         [ 0. +0.j         0. +0.j        -0.5-0.8660254j]]
        """
        return np.diag([1, OMEGA, OMEGA**2])

    @staticmethod
    def compute_eigvals():
        r"""Eigenvalues of the operator in the computational basis (static method).

        If :attr:`diagonalizing_gates` are specified and implement a unitary :math:`U^{\dagger}`,
        the operator can be reconstructed as

        .. math:: O = U \Sigma U^{\dagger},

        where :math:`\Sigma` is the diagonal matrix containing the eigenvalues.
        Otherwise, no particular order for the eigenvalues is guaranteed.

        .. seealso:: :meth:`~.TClock.eigvals`

        Returns:
            array: eigenvalues

        **Example**

        >>> print(qml.TClock.compute_eigvals())
        [ 1. +0.j        -0.5+0.8660254j -0.5-0.8660254j]
        """
        return np.array([1, OMEGA, OMEGA**2])

    # TODO: Add compute_decomposition() once parametric ops are added.

    def pow(self, z):
        return super().pow(z % 3)


class TAdd(Operation):
    r"""TAdd(wires)
    The 2-qutrit controlled add gate

    The construction of this operator is based on definition 7 from
    `Yeh et al. (2022) <https://arxiv.org/abs/2204.00552>`_.
    It performs the controlled :class:`~.TShift` operation, and sends
    :math:`\hbox{TAdd} \vert i \rangle \vert j \rangle = \vert i \rangle \vert i + j \rangle`,
    where addition is taken modulo 3. The matrix representation is

    .. math:: TAdd = \begin{bmatrix}
                        1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
                        0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
                        0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 \\
                        0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 \\
                        0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 \\
                        0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\
                        0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 \\
                        0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 \\
                        0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 & 0
                    \end{bmatrix}

    .. note:: The first wire provided corresponds to the **control qutrit**.

    **Details:**

    * Number of wires: 2
    * Number of parameters: 0

    Args:
        wires (Sequence[int]): the wires the operation acts on
    """

    num_wires = 2
    """int: Number of wires that the operator acts on."""

    num_params = 0
    """int: Number of trainable parameters that the operator depends on."""

    @staticmethod
    def compute_matrix():
        r"""Representation of the operator as a canonical matrix in the computational basis (static method).

        The canonical matrix is the textbook matrix representation that does not consider wires.
        Implicitly, this assumes that the wires of the operator correspond to the global wire order.

        .. seealso:: :meth:`~.TAdd.matrix`

        Returns:
            ndarray: matrix

        **Example**

        >>> print(qml.TAdd.compute_matrix())
        [[1 0 0 0 0 0 0 0 0]
         [0 1 0 0 0 0 0 0 0]
         [0 0 1 0 0 0 0 0 0]
         [0 0 0 0 0 1 0 0 0]
         [0 0 0 1 0 0 0 0 0]
         [0 0 0 0 1 0 0 0 0]
         [0 0 0 0 0 0 0 1 0]
         [0 0 0 0 0 0 0 0 1]
         [0 0 0 0 0 0 1 0 0]]
        """
        return np.array(
            [
                [1, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 1],
                [0, 0, 0, 0, 0, 0, 1, 0, 0],
            ]
        )

    @staticmethod
    def compute_eigvals():
        r"""Eigenvalues of the operator in the computational basis (static method).

        If :attr:`diagonalizing_gates` are specified and implement a unitary :math:`U^{\dagger}`,
        the operator can be reconstructed as

        .. math:: O = U \Sigma U^{\dagger},

        where :math:`\Sigma` is the diagonal matrix containing the eigenvalues.
        Otherwise, no particular order for the eigenvalues is guaranteed.

        .. seealso:: :meth:`~.TAdd.eigvals`

        Returns:
            array: eigenvalues

        **Example**

        >>> print(qml.TAdd.compute_eigvals())
        [-0.5+0.8660254j -0.5-0.8660254j  1. +0.j        -0.5+0.8660254j -0.5-0.8660254j  1. +0.j         1. +0.j         1. +0.j         1. +0.j       ]
        """
        return np.array([OMEGA, OMEGA**2, 1, OMEGA, OMEGA**2, 1, 1, 1, 1])

    # TODO: Add compute_decomposition() once parametric ops are added.

    def pow(self, z):
        return super().pow(z % 3)

    @property
    def control_wires(self):
        return Wires(self.wires[0])


class TSWAP(Operation):
    r"""TSWAP(wires)
    The ternary swap operator.

    This operation is analogous to the qubit SWAP and acts on two-qutrit computational basis states
    according to :math:`TSWAP\vert i, j\rangle = \vert j, i \rangle`. Its matrix representation is

    .. math:: TSWAP = \begin{bmatrix}
                1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
                0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 \\
                0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 \\
                0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
                0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\
                0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 \\
                0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 \\
                0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 \\
                0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 \\
            \end{bmatrix}

    **Details:**

    * Number of wires: 2
    * Number of parameters: 0

    Args:
        wires (Sequence[int]): the wires the operation acts on
    """

    num_wires = 2
    num_params = 0
    """int: Number of trainable parameters that the operator depends on."""

    def label(self, decimals=None, base_label=None, cache=None):
        return base_label or "TSWAP"

    @staticmethod
    def compute_matrix():  # pylint: disable=arguments-differ
        r"""Representation of the operator as a canonical matrix in the computational basis (static method).

        The canonical matrix is the textbook matrix representation that does not consider wires.
        Implicitly, this assumes that the wires of the operator correspond to the global wire order.

        .. seealso:: :meth:`~.TSWAP.matrix`

        Returns:
            ndarray: matrix

        **Example**

        >>> print(qml.TSWAP.compute_matrix())
        [[1 0 0 0 0 0 0 0 0]
         [0 0 0 1 0 0 0 0 0]
         [0 0 0 0 0 0 1 0 0]
         [0 1 0 0 0 0 0 0 0]
         [0 0 0 0 1 0 0 0 0]
         [0 0 0 0 0 0 0 1 0]
         [0 0 1 0 0 0 0 0 0]
         [0 0 0 0 0 1 0 0 0]
         [0 0 0 0 0 0 0 0 1]]
        """
        return np.array(
            [
                [1, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 0, 0],
                [0, 1, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 1, 0],
                [0, 0, 1, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 1],
            ]
        )

    @staticmethod
    def compute_eigvals():
        r"""Eigenvalues of the operator in the computational basis (static method).

        If :attr:`diagonalizing_gates` are specified and implement a unitary :math:`U^{\dagger}`,
        the operator can be reconstructed as

        .. math:: O = U \Sigma U^{\dagger},

        where :math:`\Sigma` is the diagonal matrix containing the eigenvalues.
        Otherwise, no particular order for the eigenvalues is guaranteed.

        .. seealso:: :meth:`~.TSWAP.eigvals`

        Returns:
            array: eigenvalues

        **Example**

        >>> print(qml.TSWAP.compute_eigvals())
        [ 1. -1.  1. -1.  1. -1.  1.  1.  1.]
        """
        return np.array([1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, 1.0, 1.0])

    # TODO: Add compute_decomposition()

    def pow(self, z):
        return super().pow(z % 2)

    def adjoint(self):
        return TSWAP(wires=self.wires)


class TCNOT(Operation):
    r"""TCNOT(wires, subspace)
    The ternary controlled-NOT operator
    Performs the controlled-NOT operation on the specified 2D subspace. The operation is controlled
    on the :math:`|2\rangle` state.
    The subspace is given as a keyword argument and determines which two of three single-qutrit basis
    states of the target wire the operation applies to.
    The construction of this operator is based on section 2 of
    `Di et al. (2012) <https://arxiv.org/abs/1105.5485>`_.
    .. note:: The first wire provided corresponds to the **control qutrit**.
    **Details:**
    * Number of wires: 2
    * Number of parameters: 0
    Args:
        wires (Sequence[int] or int): the wire the operation acts on
        subspace (Sequence[int]): the 2D subspace on which to apply operation
    **Example**
    The specified subspace will determine which basis states the operation actually
    applies to:
    >>> qml.TCNOT(wires=[0, 1], subspace=[0, 1]).matrix()
    array([[1., 0., 0., 0., 0., 0., 0., 0., 0.],
           [0., 1., 0., 0., 0., 0., 0., 0., 0.],
           [0., 0., 1., 0., 0., 0., 0., 0., 0.],
           [0., 0., 0., 1., 0., 0., 0., 0., 0.],
           [0., 0., 0., 0., 1., 0., 0., 0., 0.],
           [0., 0., 0., 0., 0., 1., 0., 0., 0.],
           [0., 0., 0., 0., 0., 0., 0., 1., 0.],
           [0., 0., 0., 0., 0., 0., 1., 0., 0.],
           [0., 0., 0., 0., 0., 0., 0., 0., 1.]])
    >>> qml.TCNOT(wires=[0, 1], subspace=[0, 2]).matrix()
    array([[1., 0., 0., 0., 0., 0., 0., 0., 0.],
           [0., 1., 0., 0., 0., 0., 0., 0., 0.],
           [0., 0., 1., 0., 0., 0., 0., 0., 0.],
           [0., 0., 0., 1., 0., 0., 0., 0., 0.],
           [0., 0., 0., 0., 1., 0., 0., 0., 0.],
           [0., 0., 0., 0., 0., 1., 0., 0., 0.],
           [0., 0., 0., 0., 0., 0., 0., 0., 1.],
           [0., 0., 0., 0., 0., 0., 0., 1., 0.],
           [0., 0., 0., 0., 0., 0., 1., 0., 0.]])
    >>> qml.TCNOT(wires=[0, 1], subspace=[1, 2]).matrix()
    array([[1., 0., 0., 0., 0., 0., 0., 0., 0.],
           [0., 1., 0., 0., 0., 0., 0., 0., 0.],
           [0., 0., 1., 0., 0., 0., 0., 0., 0.],
           [0., 0., 0., 1., 0., 0., 0., 0., 0.],
           [0., 0., 0., 0., 1., 0., 0., 0., 0.],
           [0., 0., 0., 0., 0., 1., 0., 0., 0.],
           [0., 0., 0., 0., 0., 0., 1., 0., 0.],
           [0., 0., 0., 0., 0., 0., 0., 0., 1.],
           [0., 0., 0., 0., 0., 0., 0., 1., 0.]])
    """

    num_wires = 2
    num_params = 0
    """int: Number of trainable parameters that the operator depends on."""

    def label(self, decimals=None, base_label=None, cache=None):
        return base_label or "TX"

    def __init__(self, wires, subspace=[0, 1], control_value=2):
        if not hasattr(subspace, "__iter__"):
            raise ValueError(
                "The subspace must be a sequence with two unique elements from the set {0, 1, 2}."
            )

        self._subspace = subspace
        self._control_value = control_value
        self._hyperparameters = {
            "subspace": self.subspace,
            "control_value": self.control_value,
        }
        super().__init__(wires=wires)

    @property
    def subspace(self):
        """The single-qutrit basis states which the operator acts on
        This property returns the 2D subspace on which the operator acts. This subspace
        determines which two single-qutrit basis states the operator acts on. The remaining
        basis state is not affected by the operator.
        Returns:
            tuple[int]: subspace on which operator acts
        """
        return tuple(sorted(self._subspace))

    @property
    def control_value(self):
        """The single-qutrit basis states which the operator acts on
        This property returns the 2D subspace on which the operator acts. This subspace
        determines which two single-qutrit basis states the operator acts on. The remaining
        basis state is not affected by the operator.
        Returns:
            tuple[int]: subspace on which operator acts
        """
        return int(self._control_value)

    @staticmethod
    def compute_matrix(subspace=[0, 1], control_value=2):  # pylint: disable=arguments-differ
        r"""Representation of the operator as a canonical matrix in the computational basis (static method).
        The canonical matrix is the textbook matrix representation that does not consider wires.
        Implicitly, this assumes that the wires of the operator correspond to the global wire order.
        .. seealso:: :meth:`~.TCNOT.matrix`
        Args:
            subspace (Sequence[int]): the 2D subspace on which to apply operation
        Returns:
            ndarray: matrix
        **Example**
        >>> print(qml.TCNOT.compute_matrix(subspace=[1, 2]))
        array([[1., 0., 0., 0., 0., 0., 0., 0., 0.],
               [0., 1., 0., 0., 0., 0., 0., 0., 0.],
               [0., 0., 1., 0., 0., 0., 0., 0., 0.],
               [0., 0., 0., 1., 0., 0., 0., 0., 0.],
               [0., 0., 0., 0., 1., 0., 0., 0., 0.],
               [0., 0., 0., 0., 0., 1., 0., 0., 0.],
               [0., 0., 0., 0., 0., 0., 1., 0., 0.],
               [0., 0., 0., 0., 0., 0., 0., 0., 1.],
               [0., 0., 0., 0., 0., 0., 0., 1., 0.]])
        """

        # The usual checks for correctness on `subspace` aren't done since `TX.compute_matrix`
        # performs them

        op_mat = qml.TX.compute_matrix(subspace=subspace)
        mat = np.eye(9)
        if control_value == 0:
            mat[0:3, 0:3] = op_mat
        elif control_value == 1:
            mat[3:6, 3:6] = op_mat
        else:
            mat[6:, 6:] = op_mat
        return mat

    def adjoint(self):
        return TCNOT(wires=self.wires, subspace=self.subspace, control_value=self.control_value)

    def pow(self, z):
        if not isinstance(z, int):
            return super().pow(z)

        return super().pow(z % 2)

    @property
    def control_wires(self):
        return Wires(self.wires[0])


class TX(Operation):
    r"""TX(wires, subspace)
    Ternary X operation

    Performs the Pauli X operation on the specified 2D subspace. The subspace is
    given as a keyword argument and determines which two of three single-qutrit
    basis states the operation applies to.

    The construction of this operator is based on section 2 of
    `Di et al. (2012) <https://arxiv.org/abs/1105.5485>`_.

    **Details:**

    * Number of wires: 1
    * Number of parameters: 0

    Args:
        wires (Sequence[int] or int): the wire the operation acts on
        subspace (Sequence[int]): the 2D subspace on which to apply operation

    **Example**

    The specified subspace will determine which basis states the operation actually
    applies to:

    >>> qml.TX(wires=0, subspace=[0, 1]).matrix()
    array([[0., 1., 0.],
           [1., 0., 0.],
           [0., 0., 1.]])

    >>> qml.TX(wires=0, subspace=[0, 2]).matrix()
    array([[0., 0., 1.],
           [0., 1., 0.],
           [1., 0., 0.]])

    >>> qml.TX(wires=0, subspace=[1, 2]).matrix()
    array([[1., 0., 0.],
           [0., 0., 1.],
           [0., 1., 0.]])
    """

    num_wires = 1
    num_params = 0
    """int: Number of trainable parameters that the operator depends on."""

    def label(self, decimals=None, base_label=None, cache=None):
        return base_label or "TX"

    def __init__(self, wires, subspace=[0, 1]):
        if not hasattr(subspace, "__iter__"):
            raise ValueError(
                "The subspace must be a sequence with two unique elements from the set {0, 1, 2}."
            )

        self._subspace = subspace
        self._hyperparameters = {
            "subspace": self.subspace,
        }
        super().__init__(wires=wires)

    @property
    def subspace(self):
        """The single-qutrit basis states which the operator acts on

        This property returns the 2D subspace on which the operator acts. This subspace
        determines which two single-qutrit basis states the operator acts on. The remaining
        basis state is not affected by the operator.

        Returns:
            tuple[int]: subspace on which operator acts
        """
        return tuple(sorted(self._subspace))

    @staticmethod
    def compute_matrix(subspace=[0, 1]):  # pylint: disable=arguments-differ
        r"""Representation of the operator as a canonical matrix in the computational basis (static method).

        The canonical matrix is the textbook matrix representation that does not consider wires.
        Implicitly, this assumes that the wires of the operator correspond to the global wire order.

        .. seealso:: :meth:`~.TX.matrix`

        Args:
            subspace (Sequence[int]): the 2D subspace on which to apply operation

        Returns:
            ndarray: matrix

        **Example**

        >>> print(qml.TX.compute_matrix(subspace=[0, 2]))
        array([[0., 0., 1.],
               [0., 1., 0.],
               [1., 0., 0.]])
        """

        if len(subspace) != 2:
            raise ValueError(
                "The subspace must be a sequence with two unique elements from the set {0, 1, 2}."
            )

        if not all([s in {0, 1, 2} for s in subspace]):
            raise ValueError("Elements of the subspace must be 0, 1, or 2.")

        if subspace[0] == subspace[1]:
            raise ValueError("Elements of subspace list must be unique.")

        subspace = tuple(sorted(subspace))

        mat = np.zeros((3, 3))

        unused_ind = list({0, 1, 2}.difference(set(subspace))).pop()
        mat[subspace[0], subspace[1]] = 1
        mat[subspace[1], subspace[0]] = 1
        mat[unused_ind, unused_ind] = 1

        return mat

    def adjoint(self):
        return TX(wires=self.wires, subspace=self.subspace)

    def pow(self, z):
        if not isinstance(z, int):
            return super().pow(z)

        return super().pow(z % 2)

    # TODO: Add _controlled() method once TCNOT is added


class TY(Operation):
    r"""TY(wires, subspace)
    Ternary Y operation

    Performs the Pauli Y operation on the specified 2D subspace. The subspace is
    given as a keyword argument and determines which two of three single-qutrit
    basis states the operation applies to.

    The construction of this operator is based on section 2 of
    `Di et al. (2012) <https://arxiv.org/abs/1105.5485>`_.

    **Details:**

    * Number of wires: 1
    * Number of parameters: 0

    Args:
        wires (Sequence[int] or int): the wire the operation acts on
        subspace (Sequence[int]): the 2D subspace on which to apply operation

    **Example**

    The specified subspace will determine which basis states the operation actually
    applies to:

    >>> qml.TY(wires=0, subspace=[0, 1]).matrix()
    array([[ 0.+0.j, -0.-1.j,  0.+0.j],
           [ 0.+1.j,  0.+0.j,  0.+0.j],
           [ 0.+0.j,  0.+0.j,  1.+0.j]])

    >>> qml.TY(wires=0, subspace=[0, 2]).matrix()
    array([[ 0.+0.j,  0.+0.j, -0.-1.j],
           [ 0.+0.j,  1.+0.j,  0.+0.j],
           [ 0.+1.j,  0.+0.j,  0.+0.j]])

    >>> qml.TY(wires=0, subspace=[1, 2]).matrix()
    array([[ 1.+0.j,  0.+0.j,  0.+0.j],
           [ 0.+0.j,  0.+0.j, -0.-1.j],
           [ 0.+0.j,  0.+1.j,  0.+0.j]])
    """

    num_wires = 1
    num_params = 0
    """int: Number of trainable parameters that the operator depends on."""

    def label(self, decimals=None, base_label=None, cache=None):
        return base_label or "TY"

    def __init__(self, wires, subspace=[0, 1]):
        if not hasattr(subspace, "__iter__"):
            raise ValueError(
                "The subspace must be a sequence with two unique elements from the set {0, 1, 2}."
            )

        self._subspace = subspace
        self._hyperparameters = {
            "subspace": self.subspace,
        }
        super().__init__(wires=wires)

    @property
    def subspace(self):
        """The single-qutrit basis states which the operator acts on

        This property returns the 2D subspace on which the operator acts. This subspace
        determines which two single-qutrit basis states the operator acts on. The remaining
        basis state is not affected by the operator.

        Returns:
            tuple[int]: subspace on which operator acts
        """
        return tuple(sorted(self._subspace))

    @staticmethod
    def compute_matrix(subspace=[0, 1]):  # pylint: disable=arguments-differ
        r"""Representation of the operator as a canonical matrix in the computational basis (static method).

        The canonical matrix is the textbook matrix representation that does not consider wires.
        Implicitly, this assumes that the wires of the operator correspond to the global wire order.

        .. seealso:: :meth:`~.TY.matrix`

        Args:
            subspace (Sequence[int]): the 2D subspace on which to apply operation

        Returns:
            ndarray: matrix

        **Example**

        >>> print(qml.TY.compute_matrix(subspace=[0, 2]))
        array([[ 0.+0.j,  0.+0.j, -0.-1.j],
               [ 0.+0.j,  1.+0.j,  0.+0.j],
               [ 0.+1.j,  0.+0.j,  0.+0.j]])
        """

        if len(subspace) != 2:
            raise ValueError(
                "The subspace must be a sequence with two unique elements from the set {0, 1, 2}."
            )

        if not all([s in {0, 1, 2} for s in subspace]):
            raise ValueError("Elements of the subspace must be 0, 1, or 2.")

        if subspace[0] == subspace[1]:
            raise ValueError("Elements of subspace list must be unique.")

        subspace = tuple(sorted(subspace))

        mat = np.zeros((3, 3), dtype=np.complex128)

        unused_ind = list({0, 1, 2}.difference(set(subspace))).pop()
        mat[subspace[0], subspace[1]] = -1j
        mat[subspace[1], subspace[0]] = 1j
        mat[unused_ind, unused_ind] = 1

        return mat

    def adjoint(self):
        return TY(wires=self.wires, subspace=self.subspace)

    def pow(self, z):
        if not isinstance(z, int):
            return super().pow(z)

        return super().pow(z % 2)


class TZ(Operation):
    r"""TZ(wires, subspace)
    Ternary Z operation

    Performs the Pauli Z operation on the specified 2D subspace. The subspace is
    given as a keyword argument and determines which two of three single-qutrit
    basis states the operation applies to. The second element of the subspace will
    determine which basis state the local -1 phase applies to

    The construction of this operator is based on section 2 of
    `Di et al. (2012) <https://arxiv.org/abs/1105.5485>`_.

    **Details:**

    * Number of wires: 1
    * Number of parameters: 0

    Args:
        wires (Sequence[int] or int): the wire the operation acts on
        subspace (Sequence[int]): the 2D subspace on which to apply operation

    **Example**

    The specified subspace will determine which basis states the operation actually
    applies to, with the second element of the subspace determining which basis state
    the local -1 phase applies to:

    >>> qml.TZ(wires=0, subspace=[0, 1]).matrix()
    array([[ 1.,  0.,  0.],
           [ 0., -1.,  0.],
           [ 0.,  0.,  1.]])

    >>> qml.TZ(wires=0, subspace=[1, 0]).matrix()
    array([[-1.,  0.,  0.],
           [ 0.,  1.,  0.],
           [ 0.,  0.,  1.]])

    >>> qml.TZ(wires=0, subspace=[2, 1]).matrix()
    array([[ 1.,  0.,  0.],
           [ 0., -1.,  0.],
           [ 0.,  0.,  1.]])
    """

    num_wires = 1
    num_params = 0
    """int: Number of trainable parameters that the operator depends on."""

    def label(self, decimals=None, base_label=None, cache=None):
        return base_label or "TZ"

    def __init__(self, wires, subspace=[0, 1]):
        if not hasattr(subspace, "__iter__"):
            raise ValueError(
                "The subspace must be a sequence with two unique elements from the set {0, 1, 2}."
            )

        self._subspace = subspace
        self._hyperparameters = {
            "subspace": self.subspace,
        }
        super().__init__(wires=wires)

    @property
    def subspace(self):
        """The single-qutrit basis states which the operator acts on

        This property returns the 2D subspace on which the operator acts. This subspace
        determines which two single-qutrit basis states the operator acts on. The remaining
        basis state is not affected by the operator.

        Returns:
            tuple[int]: subspace on which operator acts
        """
        return tuple(self._subspace)

    @staticmethod
    def compute_matrix(subspace=[0, 1]):  # pylint: disable=arguments-differ
        r"""Representation of the operator as a canonical matrix in the computational basis (static method).

        The canonical matrix is the textbook matrix representation that does not consider wires.
        Implicitly, this assumes that the wires of the operator correspond to the global wire order.

        .. seealso:: :meth:`~.TZ.matrix`

        Args:
            subspace (Sequence[int]): the 2D subspace on which to apply operation

        Returns:
            ndarray: matrix

        **Example**

        >>> print(qml.TZ.compute_matrix(subspace=[0, 2]))
        array([[ 1.,  0.,  0.],
               [ 0.,  1.,  0.],
               [ 0.,  0., -1.]])
        """

        if len(subspace) != 2:
            raise ValueError(
                "The subspace must be a sequence with two unique elements from the set {0, 1, 2}."
            )

        if not all([s in {0, 1, 2} for s in subspace]):
            raise ValueError("Elements of the subspace must be 0, 1, or 2.")

        if subspace[0] == subspace[1]:
            raise ValueError("Elements of subspace list must be unique.")

        subspace = tuple(subspace)

        mat = np.eye(3)
        mat[subspace[1], subspace[1]] = -1

        return mat

    def adjoint(self):
        return TZ(wires=self.wires, subspace=self.subspace)

    def pow(self, z):
        if not isinstance(z, int):
            return super().pow(z)

        return super().pow(z % 2)


class TH(Operation):
    r"""TH(wires, subspace)
    The ternary subspace Hadamard operator

    Performs the Hadamard operation on the specified 2D subspace. The subspace is
    given as a keyword argument and determines which two of three single-qutrit
    basis states the operation applies to.

    The construction of this operator is based on section 2 of
    `Di et al. (2012) <https://arxiv.org/abs/1105.5485>`_.

    **Details:**

    * Number of wires: 1
    * Number of parameters: 0

    Args:
        wires (Sequence[int] or int): the wire the operation acts on
        subspace (Sequence[int]): the 2D subspace on which to apply operation

    **Example**

    The specified subspace will determine which basis states the operation actually
    applies to:

    >>> qml.TH(wires=0, subspace=[0, 1]).matrix()
    array([[ 1.,  1.,  0.],
           [ 1., -1.,  0.],
           [ 0.,  0.,  1.]])

    >>> qml.TH(wires=0, subspace=[0, 2]).matrix()
    array([[ 1.,  0.,  1.],
           [ 0.,  1.,  0.],
           [ 1.,  0., -1.]])

    >>> qml.TH(wires=0, subspace=[1, 2]).matrix()
    array([[ 1.,  0.,  0.],
           [ 0.,  1.,  1.],
           [ 0.,  1., -1.]])
    """

    num_wires = 1
    num_params = 0
    """int: Number of trainable parameters that the operator depends on."""

    def label(self, decimals=None, base_label=None, cache=None):
        return base_label or "TH"

    def __init__(self, wires, subspace=[0, 1]):
        if not hasattr(subspace, "__iter__"):
            raise ValueError(
                "The subspace must be a sequence with two unique elements from the set {0, 1, 2}."
            )

        self._subspace = subspace
        self._hyperparameters = {
            "subspace": self.subspace,
        }
        super().__init__(wires=wires)

    @property
    def subspace(self):
        """The single-qutrit basis states which the operator acts on

        This property returns the 2D subspace on which the operator acts. This subspace
        determines which two single-qutrit basis states the operator acts on. The remaining
        basis state is not affected by the operator.

        Returns:
            tuple[int]: subspace on which operator acts
        """
        return tuple(sorted(self._subspace))

    @staticmethod
    def compute_matrix(subspace=[0, 1]):  # pylint: disable=arguments-differ
        r"""Representation of the operator as a canonical matrix in the computational basis (static method).

        The canonical matrix is the textbook matrix representation that does not consider wires.
        Implicitly, this assumes that the wires of the operator correspond to the global wire order.

        .. seealso:: :meth:`~.TH.matrix`

        Args:
            subspace (Sequence[int]): the 2D subspace on which to apply operation

        Returns:
            ndarray: matrix

        **Example**

        >>> print(qml.TH.compute_matrix(subspace=[0, 2]))
        array([[ 1.,  0.,  1.],
               [ 0.,  1.,  0.],
               [ 1.,  0., -1.]])
        """

        if len(subspace) != 2:
            raise ValueError(
                "The subspace must be a sequence with two unique elements from the set {0, 1, 2}."
            )

        if not all([s in {0, 1, 2} for s in subspace]):
            raise ValueError("Elements of the subspace must be 0, 1, or 2.")

        if subspace[0] == subspace[1]:
            raise ValueError("Elements of subspace list must be unique.")

        subspace = tuple(sorted(subspace))

        mat = np.eye(3, dtype=np.complex128)

        unused_ind = list({0, 1, 2}.difference(set(subspace))).pop()

        mat[unused_ind, unused_ind] = np.sqrt(2)
        mat[subspace[0], subspace[1]] = 1
        mat[subspace[1], subspace[0]] = 1
        mat[subspace[1], subspace[1]] = -1

        return mat / np.sqrt(2)

    def adjoint(self):
        return TH(wires=self.wires, subspace=self.subspace)

    def pow(self, z):
        if not isinstance(z, int):
            return super().pow(z)

        return super().pow(z % 2)


class TS(Operation):
    r"""TS(wires)

    The single-qutrit phase gate

    The construction of this operator is based on definition 3 from
    `Yeh et al. (2022) <https://arxiv.org/abs/2204.00552>`_.

    .. math:: TS = \zeta^8 \begin{bmatrix}
                1 & 0 & 0 \\
                0 & 1 & 0 \\
                0 & 0 & \omega
                \end{bmatrix}
            \omega = \exp{2 \pi i / 3},
            \zeta = \omega^{1 / 3} = \exp{2 \pi i / 9}

    **Details:**

    * Number of wires: 1
    * Number of parameters: 0

    Args:
        wires (Sequence[int] or int): the wire the operation acts on
    """

    num_wires = 1
    num_params = 0
    """int: Number of trainable parameters that the operator depends on."""

    def __init__(self, wires, subspace=None):
        if not hasattr(subspace, "__iter__"):
            raise ValueError(
                "The subspace must be a sequence with two unique elements from the set {0, 1, 2}."
            )

        self._subspace = subspace
        self._hyperparameters = {
            "subspace": self.subspace,
        }
        super().__init__(wires=wires)

    @property
    def subspace(self):
        """The single-qutrit basis states which the operator acts on

        This property returns the 2D subspace on which the operator acts. This subspace
        determines which two single-qutrit basis states the operator acts on. The remaining
        basis state is not affected by the operator.

        Returns:
            tuple[int]: subspace on which operator acts
        """
        return tuple(sorted(self._subspace))

    @staticmethod
    def compute_matrix(subspace=None):  # pylint: disable=arguments-differ
        r"""Representation of the operator as a canonical matrix in the computational basis (static method).

        The canonical matrix is the textbook matrix representation that does not consider wires.
        Implicitly, this assumes that the wires of the operator correspond to the global wire order.

        .. seealso:: :meth:`~.TS.matrix`

        Returns:
            ndarray: matrix

        **Example**

        >>> print(qml.TS.compute_matrix())
        array([[0.76604444-0.64278761j, 0.        +0.j        , 0.        +0.j        ],
               [0.        +0.j        , 0.76604444-0.64278761j, 0.        +0.j        ],
               [0.        +0.j        , 0.        +0.j        , 0.17364818+0.98480775j]])
        """
        if subspace is None:
            return ZETA**8 * np.diag([1, 1, OMEGA])

        mat = np.eye(3, dtype=np.complex128)
        mat[subspace[0], subspace[0]] = 1
        mat[subspace[1], subspace[1]] = 1j
        """ PHASE MATTERS """
        # mat[subspace[0], subspace[0]] = np.exp(-1j*np.pi/4)
        # mat[subspace[1], subspace[1]] = np.exp(1j*np.pi/4)

        return mat

    def adjoint(self):
        raise AdjointUndefinedError
        # op = TS(wires=self.wires)
        # op.inverse = not self.inverse
        # return op


class TT(Operation):
    r"""TT(wires, subspace)
    The single qutrit T gate
	If subspace is not specified, then
    The construction of this operator is based on definition 8 from
    `Yeh et al. (2022) <https://arxiv.org/abs/2204.00552>`_.

    .. math:: TT = \begin{bmatrix}
                1 & 0 & 0 \\
                0 & \zeta & 0 \\
                0 & 0 & \zeta^8 \\
                \end{bmatrix}
                \zeta = \exp{2 \pi i / 9}

    **Details:**

    * Number of wires: 1
    * Number of parameters: 0

    Args:
        wires (Sequence[int] or int): the wire the operation acts on
    """

    num_wires = 1
    num_params = 0
    """int: Number of trainable parameters that the operator depends on."""

    def __init__(self, wires, subspace=None):
        if not hasattr(subspace, "__iter__"):
            raise ValueError(
                "The subspace must be a sequence with two unique elements from the set {0, 1, 2}."
            )

        self._subspace = subspace
        self._hyperparameters = {
            "subspace": self.subspace,
        }
        super().__init__(wires=wires)

    @property
    def subspace(self):
        """The single-qutrit basis states which the operator acts on

        This property returns the 2D subspace on which the operator acts. This subspace
        determines which two single-qutrit basis states the operator acts on. The remaining
        basis state is not affected by the operator.

        Returns:
            tuple[int]: subspace on which operator acts
        """
        return tuple(sorted(self._subspace))

    @staticmethod
    def compute_matrix(subspace=None):  # pylint: disable=arguments-differ
        r"""Representation of the operator as a canonical matrix in the computational basis (static method).

        The canonical matrix is the textbook matrix representation that does not consider wires.
        Implicitly, this assumes that the wires of the operator correspond to the global wire order.

        .. seealso:: :meth:`~.TT.matrix`

        Returns:
            ndarray: matrix

        **Example**

        >>> print(qml.TT.compute_matrix())
        array([[1.        +0.j        , 0.        +0.j        , 0.        +0.j        ],
               [0.        +0.j        , 0.76604444+0.64278761j, 0.        +0.j        ],
               [0.        +0.j        , 0.        +0.j        , 0.76604444-0.64278761j]])
        """
        if subspace is None:
            return np.diag([1, ZETA, ZETA**8])

        mat = np.eye(3, dtype=np.complex128)
        mat[subspace[0], subspace[0]] = 1
        mat[subspace[1], subspace[1]] = np.exp(1j * np.pi / 4)

        """ PHASE MATTERS """
        # mat[subspace[0], subspace[0]] = np.exp(-1j*np.pi/8)
        # mat[subspace[1], subspace[1]] = np.exp(1j*np.pi/8)

        return mat

    def adjoint(self):
        raise AdjointUndefinedError
        # op = TT(wires=self.wires)
        # op.inverse = not self.inverse
        # return op
