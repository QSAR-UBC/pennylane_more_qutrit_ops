# Copyright 2018-2021 Xanadu Quantum Technologies Inc.

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
This submodule contains the discrete-variable quantum operations concerned
with preparing a certain state on the qutrit device.
"""
# pylint:disable=abstract-method,arguments-differ,protected-access,no-member
import numpy as np

from pennylane import math
from pennylane.operation import AnyWires, StatePrepBase
from pennylane.templates.state_preparations import QutritBasisStatePreparation
from pennylane.wires import WireError, Wires

state_prep_ops = {"QutritBasisState"}


class QutritBasisState(StatePrepBase):
    r"""QutritBasisState(n, wires)
    Prepares a single computational basis state for a qutrit system.

    **Details:**

    * Number of wires: Any (the operation can act on any number of wires)
    * Number of parameters: 1
    * Gradient recipe: None (integer parameters not supported)

    .. note::

        If the ``QutritBasisState`` operation is not supported natively on the
        target device, PennyLane will attempt to decompose the operation
        into :class:`~.TShift` operations.

    .. note::

        When called in the middle of a circuit, the action of the operation is defined
        as :math:`U|0\rangle = |\psi\rangle`

    Args:
        n (array): prepares the basis state :math:`\ket{n}`, where ``n`` is an
            array of integers from the set :math:`\{0, 1, 2\}`, i.e.,
            if ``n = np.array([0, 1, 0])``, prepares the state :math:`|010\rangle`.
        wires (Sequence[int] or int): the wire(s) the operation acts on

    **Example**

    >>> dev = qml.device('default.qutrit', wires=2)
    >>> @qml.qnode(dev)
    ... def example_circuit():
    ...     qml.QutritBasisState(np.array([2, 2]), wires=range(2))
    ...     return qml.state()
    >>> print(example_circuit())
    [0.+0.j 0.+0.j 0.+0.j 0.+0.j 0.+0.j 0.+0.j 0.+0.j 0.+0.j 1.+0.j]
    """

    num_wires = AnyWires
    num_params = 1
    """int: Number of trainable parameters that the operator depends on."""

    ndim_params = (1,)
    """int: Number of dimensions per trainable parameter of the operator."""

    @staticmethod
    def compute_decomposition(n, wires):
        r"""Representation of the operator as a product of other operators (static method). :

        .. math:: O = O_1 O_2 \dots O_n.

        .. seealso:: :meth:`~.BasisState.decomposition`.

        Args:
            n (array): prepares the basis state :math:`\ket{n}`, where ``n`` is an
                array of integers from the set :math:`\{0, 1, 2\}`
            wires (Iterable, Wires): the wire(s) the operation acts on

        Returns:
            list[Operator]: decomposition into lower level operations

        **Example:**

        >>> qml.QutritBasisState.compute_decomposition([1,0], wires=(0,1))
        [QutritBasisStatePreparation(array([1, 0]), wires=[0, 1])]

        """
        return [QutritBasisStatePreparation(n, wires)]

    def state_vector(self, wire_order=None):
        """Returns a statevector of shape ``(3,) * num_wires``."""
        prep_vals = self.parameters[0]
        if any(i not in [0, 1, 2] for i in prep_vals):
            raise ValueError("QutritBasisState parameter must consist of 0, 1 or 2 integers.")

        if (num_wires := len(self.wires)) != len(prep_vals):
            raise ValueError("QutritBasisState parameter and wires must be of equal length.")

        if wire_order is None:
            indices = prep_vals
        else:
            if not Wires(wire_order).contains_wires(self.wires):
                raise WireError("Custom wire_order must contain all QutritBasisState wires")
            num_wires = len(wire_order)
            indices = [0] * num_wires
            for base_wire_label, value in zip(self.wires, prep_vals):
                indices[wire_order.index(base_wire_label)] = value

        ket = np.zeros((3,) * num_wires)
        ket[tuple(indices)] = 1
        return math.convert_like(ket, prep_vals)

class QutritStateVector(StatePrepBase):

    num_wires = AnyWires
    num_params = 1
    """int: Number of trainable parameters that the operator depends on."""

    ndim_params = (1,)
    """int: Number of dimensions per trainable parameter of the operator."""

    def __init__(self, state, wires, id=None):
        super().__init__(state, wires=wires, id=id)
        state = self.parameters[0]

        if len(state.shape) == 1:
            state = math.reshape(state, (1, state.shape[0]))
        if state.shape[1] != 3 ** len(self.wires):
            raise ValueError("State vector must have shape (3**wires,) or (batch_size, 3**wires).")

        param = math.cast(state, np.complex128)
        if not math.is_abstract(param):
            norm = math.linalg.norm(param, axis=-1, ord=2)
            if not math.allclose(norm, 1.0, atol=1e-10):
                raise ValueError("Sum of amplitudes-squared does not equal one.")

    @staticmethod
    def compute_decomposition(state, wires):
        r"""Representation of the operator as a product of other operators (static method). :

        .. math:: O = O_1 O_2 \dots O_n.


        .. seealso:: :meth:`~.StatePrep.decomposition`.

        Args:
            state (array[complex]): a state vector of size 3**len(wires)
            wires (Iterable, Wires): the wire(s) the operation acts on

        Returns:
            list[Operator]: decomposition into lower level operations

        **Example:**

        >>> qml.StatePrep.compute_decomposition(np.array([1, 0, 0, 0]), wires=range(2))
        [MottonenStatePreparation(tensor([1, 0, 0, 0], requires_grad=True), wires=[0, 1])]

        """
        pass

    def state_vector(self, wire_order=None):
        num_op_wires = len(self.wires)
        op_vector_shape = (-1,) + (3,) * num_op_wires if self.batch_size else (3,) * num_op_wires
        op_vector = math.reshape(self.parameters[0], op_vector_shape)

        if wire_order is None or Wires(wire_order) == self.wires:
            return op_vector

        wire_order = Wires(wire_order)
        if not wire_order.contains_wires(self.wires):
            raise WireError(f"Custom wire_order must contain all {self.name} wires")

        # add zeros for each wire that isn't being set
        extra_wires = Wires(set(wire_order) - set(self.wires))
        for _ in extra_wires:
            op_vector = math.stack([op_vector, math.zeros_like(op_vector)], axis=-1)

        # transpose from operator wire order to provided wire order
        current_wires = self.wires + extra_wires
        transpose_axes = [current_wires.index(w) for w in wire_order]
        if self.batch_size:
            transpose_axes = [0] + [a + 1 for a in transpose_axes]
        return math.transpose(op_vector, transpose_axes)
