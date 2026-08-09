"""SymPy port of ``LinearOddElastodynamics_StaffPicks.m``.

The public functions accept the Wolfram package's original data representation::

    geom = [
        primitive_vectors,
        [ball_positions, masses],
        [["extension", "regular"], extension_springs, spring_constants],
        [["torsion", "data-sharing"], torsion_springs, spring_constants],
        ...
    ]

A node reference is ``[node_number, [cell_1, cell_2]]``.  Node numbers remain
1-based by default, so Mathematica geometry literals can be copied directly.

The module deliberately keeps expressions symbolic.  Use ``expr.evalf()`` or
``numpy.asarray(expr, dtype=float)`` only at the numerical boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any, Iterable, Sequence

import sympy as sp
from sympy.tensor.array import MutableDenseNDimArray


q1, q2 = sp.symbols("q1 q2", real=True)
kx, ky = sp.symbols("kx ky", real=True)

TAU = (
    sp.eye(2),
    sp.Matrix([[0, -1], [1, 0]]),
    sp.diag(1, -1),
    sp.Matrix([[0, 1], [1, 0]]),
)


def _matrix(value: Any) -> sp.Matrix:
    return value if isinstance(value, sp.MatrixBase) else sp.Matrix(value)


def _simplify_matrix(matrix: sp.MatrixBase) -> sp.Matrix:
    return matrix.applyfunc(sp.simplify)


def _node_index(node_ref: Sequence[Any], index_base: int) -> int:
    return int(node_ref[0]) - index_base


def _cell_shift(node_ref: Sequence[Any]) -> sp.Matrix:
    return _matrix(node_ref[1])


def _position(
    primitive_vectors: sp.MatrixBase,
    balls: Sequence[Sequence[Any]],
    node_ref: Sequence[Any],
    *,
    index_base: int = 1,
) -> sp.Matrix:
    return _matrix(balls[_node_index(node_ref, index_base)]) + (
        _cell_shift(node_ref).T * primitive_vectors
    ).T


def _phase(node_ref: Sequence[Any], wavevector: Sequence[Any]) -> sp.Expr:
    return sp.exp(sp.I * (_cell_shift(node_ref).dot(_matrix(wavevector))))


def ccw_orth(vector: Sequence[Any]) -> sp.Matrix:
    """Rotate a two-dimensional vector counter-clockwise by 90 degrees."""
    x, y = _matrix(vector)
    return sp.Matrix([-y, x])


def shift_matrix(n: int, shift: int) -> sp.Matrix:
    """Return the cyclic shift matrix used by the original package."""
    return sp.Matrix(n, n, lambda i, j: int(i == (j + shift) % n))


def generate_tsprings(node: Sequence[Any], neighbours: Sequence[Sequence[Any]]) -> list:
    """Make successive torsion triples around ``node``."""
    if not neighbours:
        return []
    return [
        [neighbours[i], list(node), neighbours[(i + 1) % len(neighbours)]]
        for i in range(len(neighbours))
    ]


def generate_all_tsprings(
    primitive_vectors: Sequence[Sequence[Any]],
    balls: Sequence[Sequence[Any]],
    springs: Sequence[Sequence[Sequence[Any]]],
    *,
    index_base: int = 1,
) -> list:
    """Generate all torsion springs implied by an extension-spring network."""
    prim = _matrix(primitive_vectors)
    adjacency: dict[int, list] = {}
    zero = [0, 0]

    for first, second in springs:
        i = _node_index(first, index_base)
        j = _node_index(second, index_base)
        si = _cell_shift(first)
        sj = _cell_shift(second)
        adjacency.setdefault(i, []).append(
            [j + index_base, list(sj - si)]
        )
        adjacency.setdefault(j, []).append(
            [i + index_base, list(si - sj)]
        )

    result = []
    for centre, neighbours in adjacency.items():
        centre_pos = _matrix(balls[centre])

        def polar_angle(ref: Sequence[Any]) -> float:
            displacement = _position(
                prim, balls, ref, index_base=index_base
            ) - centre_pos
            return float(sp.atan2(displacement[1], displacement[0]).evalf())

        ordered = sorted(neighbours, key=polar_angle)
        result.extend(
            generate_tsprings([centre + index_base, zero], ordered)
        )
    return result


def super_lattice(geom: Sequence[Any], repeats: Sequence[int]) -> list:
    """Build a supercell containing ``repeats[0] * repeats[1]`` unit cells."""
    n1, n2 = map(int, repeats)
    if n1 < 1 or n2 < 1:
        raise ValueError("repeats must contain two positive integers")

    primitive = _matrix(geom[0])
    balls, masses = geom[1]
    nballs = len(balls)
    cells = list(product(range(n1), range(n2)))

    new_primitive = sp.Matrix(
        [n1 * primitive.row(0), n2 * primitive.row(1)]
    )
    new_balls = [
        list(_matrix(ball) + (sp.Matrix(cell).T * primitive).T)
        for cell in cells
        for ball in balls
    ]

    if isinstance(masses, (list, tuple)):
        new_masses = list(masses) * len(cells)
    else:
        new_masses = masses

    cell_to_number = {cell: number for number, cell in enumerate(cells)}

    def translate_ref(ref: Sequence[Any], source_cell: tuple[int, int]) -> list:
        node = int(ref[0]) - 1
        shift = [int(v) for v in ref[1]]
        raw = (source_cell[0] + shift[0], source_cell[1] + shift[1])
        wrapped = (raw[0] % n1, raw[1] % n2)
        outer = [raw[0] // n1, raw[1] // n2]
        new_node = node + nballs * cell_to_number[wrapped] + 1
        return [new_node, outer]

    new_groups = []
    for header, springs, constants in geom[2:]:
        translated = [
            [translate_ref(ref, cell) for ref in spring]
            for cell in cells
            for spring in springs
        ]
        new_constants = (
            list(constants) * len(cells)
            if isinstance(constants, (list, tuple))
            else constants
        )
        new_groups.append([list(header), translated, new_constants])

    return [new_primitive.tolist(), [new_balls, new_masses], *new_groups]


def lengths(
    primitive_vectors: Sequence[Sequence[Any]],
    balls: Sequence[Sequence[Any]],
    springs: Sequence[Sequence[Sequence[Any]]],
    *,
    index_base: int = 1,
) -> list[sp.Expr]:
    """Return extension-spring rest lengths."""
    prim = _matrix(primitive_vectors)
    return [
        sp.simplify(
            (
                _position(prim, balls, spring[1], index_base=index_base)
                - _position(prim, balls, spring[0], index_base=index_base)
            ).norm()
        )
        for spring in springs
    ]


def angles(
    primitive_vectors: Sequence[Sequence[Any]],
    balls: Sequence[Sequence[Any]],
    torsion_springs: Sequence[Sequence[Sequence[Any]]],
    *,
    index_base: int = 1,
) -> list[sp.Expr]:
    """Return torsion-spring rest angles in the range [0, pi]."""
    prim = _matrix(primitive_vectors)
    result = []
    for first, centre, last in torsion_springs:
        r1 = _position(prim, balls, first, index_base=index_base) - _position(
            prim, balls, centre, index_base=index_base
        )
        r2 = _position(prim, balls, last, index_base=index_base) - _position(
            prim, balls, centre, index_base=index_base
        )
        result.append(
            sp.acos(sp.simplify(r1.dot(r2) / (r1.norm() * r2.norm())))
        )
    return result


def extension_rigidity_matrix(
    primitive_vectors: Sequence[Sequence[Any]],
    balls: Sequence[Sequence[Any]],
    springs: Sequence[Sequence[Sequence[Any]]],
    wavevector: Sequence[Any] = (q1, q2),
    *,
    index_base: int = 1,
) -> sp.Matrix:
    """Return the extension rigidity matrix Q_L(q)."""
    prim = _matrix(primitive_vectors)
    n = len(balls)
    rows = []
    for first, second in springs:
        r = _position(prim, balls, second, index_base=index_base) - _position(
            prim, balls, first, index_base=index_base
        )
        direction = r / r.norm()
        delta = sp.zeros(n, 1)
        delta[_node_index(second, index_base)] += _phase(second, wavevector)
        delta[_node_index(first, index_base)] -= _phase(first, wavevector)
        rows.append(list(sp.kronecker_product(delta.T, direction.T)))
    return sp.Matrix(rows) if rows else sp.zeros(0, 2 * n)


def torsion_rigidity_matrix(
    primitive_vectors: Sequence[Sequence[Any]],
    balls: Sequence[Sequence[Any]],
    springs: Sequence[Sequence[Sequence[Any]]],
    wavevector: Sequence[Any] = (q1, q2),
    *,
    index_base: int = 1,
) -> sp.Matrix:
    """Return the torsion rigidity matrix Q_Theta(q)."""
    prim = _matrix(primitive_vectors)
    n = len(balls)
    rows = []

    def delta(first: Sequence[Any], second: Sequence[Any]) -> sp.Matrix:
        value = sp.zeros(n, 1)
        value[_node_index(second, index_base)] += _phase(second, wavevector)
        value[_node_index(first, index_base)] -= _phase(first, wavevector)
        return value

    for first, centre, last in springs:
        r21 = _position(prim, balls, first, index_base=index_base) - _position(
            prim, balls, centre, index_base=index_base
        )
        r23 = _position(prim, balls, last, index_base=index_base) - _position(
            prim, balls, centre, index_base=index_base
        )
        row = -sp.kronecker_product(
            delta(centre, first).T, (ccw_orth(r21) / r21.dot(r21)).T
        ) + sp.kronecker_product(
            delta(centre, last).T, (ccw_orth(r23) / r23.dot(r23)).T
        )
        rows.append(list(row))
    return sp.Matrix(rows) if rows else sp.zeros(0, 2 * n)


def dynamical_matrix_part(
    primitive_vectors: Sequence[Sequence[Any]],
    ball_data: Sequence[Any],
    spring_data: Sequence[Any],
    wavevector: Sequence[Any] = (q1, q2),
    *,
    index_base: int = 1,
) -> sp.Matrix:
    """Return one spring group's contribution to the dynamical matrix."""
    balls = ball_data[0]
    header, springs, constants = spring_data
    n = len(balls)
    m = len(springs)
    if m == 0:
        return sp.zeros(2 * n)

    spring_type, coupling = header
    if spring_type == "extension":
        qmat = extension_rigidity_matrix(
            primitive_vectors, balls, springs, wavevector, index_base=index_base
        )
    elif spring_type == "torsion":
        qmat = torsion_rigidity_matrix(
            primitive_vectors, balls, springs, wavevector, index_base=index_base
        )
    else:
        raise NotImplementedError(f"spring type {spring_type!r} is not implemented")

    if isinstance(constants, (list, tuple)):
        if len(constants) != m:
            raise ValueError("spring-constant list must match the spring count")
        kmat = sp.diag(*constants)
    else:
        kmat = sp.sympify(constants) * sp.eye(m)

    if coupling == "regular":
        coupled_q = qmat
    elif coupling == "data-sharing":
        coupled_q = qmat[-1:, :].col_join(qmat[:-1, :]) - qmat[
            1:, :
        ].col_join(qmat[:1, :])
    else:
        raise NotImplementedError(f"coupling {coupling!r} is not implemented")

    return sp.conjugate(qmat).T * kmat * coupled_q


def dynamical_matrix(
    geom: Sequence[Any],
    wavevector: Sequence[Any] = (q1, q2),
    *,
    index_base: int = 1,
    simplify: bool = True,
) -> sp.Matrix:
    """Return the complete dynamical matrix D(q)."""
    n = len(geom[1][0])
    total = sp.zeros(2 * n)
    for spring_data in geom[2:]:
        total += dynamical_matrix_part(
            geom[0], geom[1], spring_data, wavevector, index_base=index_base
        )
    return _simplify_matrix(total) if simplify else total


def _matrix_derivative(matrix: sp.MatrixBase, variable: sp.Symbol) -> sp.Matrix:
    return matrix.applyfunc(lambda value: sp.diff(value, variable))


def _second_derivative_tensor(
    matrix: sp.MatrixBase, variables: Sequence[sp.Symbol]
) -> MutableDenseNDimArray:
    result = MutableDenseNDimArray.zeros(matrix.rows, matrix.cols, 2, 2)
    for a in range(matrix.rows):
        for b in range(matrix.cols):
            for i, first in enumerate(variables):
                for j, second in enumerate(variables):
                    result[a, b, i, j] = sp.simplify(
                        sp.diff(matrix[a, b], first, second) / 2
                    )
    return result


def _first_derivative_tensor(
    matrix: sp.MatrixBase, variables: Sequence[sp.Symbol]
) -> MutableDenseNDimArray:
    result = MutableDenseNDimArray.zeros(matrix.rows, matrix.cols, 2)
    for a in range(matrix.rows):
        for b in range(matrix.cols):
            for i, variable in enumerate(variables):
                result[a, b, i] = sp.simplify(
                    sp.diff(matrix[a, b], variable)
                )
    return result


@dataclass(frozen=True)
class CenterOfMassDynamicalMatrix:
    """Small-wavevector blocks returned for a multi-site unit cell."""

    Duu: MutableDenseNDimArray
    DuV: MutableDenseNDimArray | None = None
    DVu: MutableDenseNDimArray | None = None
    DVV: sp.Matrix | None = None


def dynamical_matrix_cm(
    geom: Sequence[Any],
    *,
    index_base: int = 1,
) -> CenterOfMassDynamicalMatrix:
    """Expand D in physical wavevector and separate internal coordinates."""
    balls, masses = geom[1]
    n = len(balls)
    if not isinstance(masses, (list, tuple)):
        masses = [masses] * n
    if len(masses) != n:
        raise ValueError("mass list must match the number of balls")

    primitive = _matrix(geom[0])
    physical_q = [
        sp.Matrix([kx, ky]).dot(primitive.row(i))
        for i in range(2)
    ]
    dm = dynamical_matrix(
        geom, physical_q, index_base=index_base, simplify=False
    )
    variables = (kx, ky)

    if n == 1:
        duu = _second_derivative_tensor(dm, variables)
        duu = duu.applyfunc(
            lambda value: sp.simplify(value.subs({kx: 0, ky: 0}))
        )
        return CenterOfMassDynamicalMatrix(
            duu
        )

    mass_vector = sp.Matrix(1, n, list(masses)) / sum(masses)
    basis_rows = [mass_vector]
    for j in range(1, n):
        basis_rows.append(sp.eye(n).row(j) - mass_vector)
    transform = sp.kronecker_product(sp.Matrix.vstack(*basis_rows), sp.eye(2))
    transformed = transform * dm * transform.inv()

    cm = [0, 1]
    internal = list(range(2, 2 * n))
    top_left = transformed.extract(cm, cm)
    top_right = transformed.extract(cm, internal)
    bottom_left = transformed.extract(internal, cm)
    bottom_right = transformed.extract(internal, internal)
    origin = {kx: 0, ky: 0}

    duu = _second_derivative_tensor(top_left, variables)
    duv = _first_derivative_tensor(top_right, variables)
    dvu = _first_derivative_tensor(bottom_left, variables)
    duu = duu.applyfunc(lambda value: sp.simplify(value.subs(origin)))
    duv = duv.applyfunc(lambda value: sp.simplify(value.subs(origin)))
    dvu = dvu.applyfunc(lambda value: sp.simplify(value.subs(origin)))
    dvv = _simplify_matrix(bottom_right.subs(origin))
    return CenterOfMassDynamicalMatrix(duu, duv, dvu, dvv)


def stiffness_tensor(
    geom: Sequence[Any],
    *,
    index_base: int = 1,
    numerical_inverse: bool = False,
) -> MutableDenseNDimArray:
    """Return C[i,j,k,l], with internal modes relaxed."""
    balls = geom[1][0]
    n, dim = len(balls), len(balls[0])
    if dim != 2:
        raise ValueError("this port, like the original package, is two-dimensional")
    volume = sp.Abs(_matrix(geom[0]).det())
    blocks = dynamical_matrix_cm(geom, index_base=index_base)
    result = MutableDenseNDimArray.zeros(dim, dim, dim, dim)

    if n > 1:
        assert blocks.DuV is not None
        assert blocks.DVu is not None
        assert blocks.DVV is not None
        dvv = blocks.DVV.evalf() if numerical_inverse else blocks.DVV
        dvv_inverse = dvv.inv()

    for i1, i2, i3, i4 in product(range(dim), repeat=4):
        value = blocks.Duu[i2, i4, i1, i3]
        if n > 1:
            left = sp.Matrix(
                1, blocks.DVV.rows, lambda _, j: blocks.DuV[i2, j, i1]
            )
            right = sp.Matrix(
                blocks.DVV.rows, 1, lambda j, _: blocks.DVu[j, i4, i3]
            )
            value -= (left * dvv_inverse * right)[0]
        result[i1, i2, i3, i4] = sp.simplify(n * value / volume)
    return result


def tensor_to_matrix(tensor: MutableDenseNDimArray) -> sp.Matrix:
    """Project a rank-four Cartesian tensor onto the TAU basis."""
    return sp.Matrix(
        4,
        4,
        lambda alpha, beta: sp.simplify(
            sum(
                sp.Rational(1, 2)
                * TAU[alpha][i1, i2]
                * tensor[i1, i2, i3, i4]
                * TAU[beta][i3, i4]
                for i1, i2, i3, i4 in product(range(2), repeat=4)
            )
        ),
    )


def stiffness_matrix(
    geom: Sequence[Any],
    *,
    index_base: int = 1,
    numerical_inverse: bool = False,
) -> sp.Matrix:
    """Return the gauge-fixed 4x4 stiffness matrix."""
    tensor = stiffness_tensor(
        geom, index_base=index_base, numerical_inverse=numerical_inverse
    )
    chi = sp.symbols("chi_00 chi_01 chi_10 chi_11")
    chi_matrix = sp.Matrix(2, 2, chi)
    epsilon = sp.Matrix([[0, 1], [-1, 0]])
    augmented = MutableDenseNDimArray.zeros(2, 2, 2, 2)
    for i1, i2, i3, i4 in product(range(2), repeat=4):
        augmented[i1, i2, i3, i4] = (
            tensor[i1, i2, i3, i4] + epsilon[i1, i3] * chi_matrix[i2, i4]
        )

    matrix = tensor_to_matrix(augmented)
    solutions = sp.solve(list(matrix[:, 1]), chi, dict=True)
    if not solutions:
        raise ValueError("could not fix the stiffness-matrix rotational gauge")
    return _simplify_matrix(matrix.subs(solutions[0]))


def bulk_modulus(geom: Sequence[Any], **kwargs: Any) -> sp.Expr:
    return sp.simplify(stiffness_matrix(geom, **kwargs)[0, 0] / 2)


def shear_modulus(geom: Sequence[Any], **kwargs: Any) -> sp.Expr:
    return sp.simplify(stiffness_matrix(geom, **kwargs)[2, 2] / 2)


def odd_bulk_modulus(geom: Sequence[Any], **kwargs: Any) -> sp.Expr:
    return sp.simplify(stiffness_matrix(geom, **kwargs)[1, 0] / 2)


def odd_shear_modulus(geom: Sequence[Any], **kwargs: Any) -> sp.Expr:
    return sp.simplify(stiffness_matrix(geom, **kwargs)[2, 3] / 2)


def active_density(geom: Sequence[Any]) -> sp.Expr:
    active_count = sum(
        len(springs)
        for header, springs, _ in geom[2:]
        if header[1] != "regular"
    )
    return sp.simplify(active_count / _matrix(geom[0]).det())


def odd_ratio(geom: Sequence[Any], **kwargs: Any) -> sp.Expr:
    return sp.simplify(
        odd_shear_modulus(geom, **kwargs) / shear_modulus(geom, **kwargs)
    )


def odd_ratio_efficiency(geom: Sequence[Any], **kwargs: Any) -> sp.Expr:
    return sp.simplify(odd_ratio(geom, **kwargs) / active_density(geom))


def _relaxed_component(
    geom: Sequence[Any],
    d_output: tuple[int, int],
    d_input: tuple[int, int],
    *,
    index_base: int = 1,
    use_adjugate: bool = True,
) -> sp.Expr:
    n = len(geom[1][0])
    volume = sp.Abs(_matrix(geom[0]).det())
    blocks = dynamical_matrix_cm(geom, index_base=index_base)
    out_component, out_derivative = d_output
    in_component, in_derivative = d_input
    value = blocks.Duu[out_component, in_component, out_derivative, in_derivative]
    if n > 1:
        assert blocks.DuV is not None and blocks.DVu is not None
        assert blocks.DVV is not None
        left = sp.Matrix(
            1, blocks.DVV.rows,
            lambda _, j: blocks.DuV[out_component, j, out_derivative],
        )
        right = sp.Matrix(
            blocks.DVV.rows, 1,
            lambda j, _: blocks.DVu[j, in_component, in_derivative],
        )
        if use_adjugate:
            correction = (left * blocks.DVV.adjugate() * right)[0] / sp.factor(
                blocks.DVV.det()
            )
        else:
            correction = (left * blocks.DVV.inv() * right)[0]
        value -= correction
    return sp.simplify(n * value / volume)


def shear_modulus_fast(geom: Sequence[Any], **kwargs: Any) -> sp.Expr:
    return _relaxed_component(geom, (1, 0), (1, 0), **kwargs)


def odd_shear_modulus_fast(geom: Sequence[Any], **kwargs: Any) -> sp.Expr:
    return _relaxed_component(geom, (0, 0), (1, 0), **kwargs)


def sum_even_moduli_fast(geom: Sequence[Any], **kwargs: Any) -> sp.Expr:
    return _relaxed_component(geom, (0, 0), (0, 0), **kwargs)


def sum_odd_moduli_fast(geom: Sequence[Any], **kwargs: Any) -> sp.Expr:
    return _relaxed_component(geom, (0, 1), (1, 1), **kwargs)


def odd_ratio_fast(geom: Sequence[Any], **kwargs: Any) -> sp.Expr:
    return sp.simplify(
        odd_shear_modulus_fast(geom, **kwargs)
        / shear_modulus_fast(geom, **kwargs)
    )


def odd_ratio_efficiency_fast(geom: Sequence[Any], **kwargs: Any) -> sp.Expr:
    return sp.simplify(odd_ratio_fast(geom, **kwargs) / active_density(geom))


def internal_displacements(
    geom: Sequence[Any],
    *,
    index_base: int = 1,
    numerical_inverse: bool = False,
) -> list[sp.Matrix]:
    """Return internal displacements for dilation, rotation and two shears."""
    primitive = _matrix(geom[0])
    n = len(geom[1][0])
    if n < 2:
        return [sp.zeros(n, 2) for _ in TAU]

    dm = dynamical_matrix(geom, (q1, q2), index_base=index_base)
    pcm = sp.kronecker_product(
        sp.ones(1, n) / n, sp.eye(2)
    )
    internal_basis = (-sp.ones(n) + n * sp.eye(n))[1:, :] / n
    pint = sp.kronecker_product(internal_basis, sp.eye(2))
    pint_pinv = pint.pinv()
    pcm_pinv = pcm.pinv()
    internal_dm = pint * dm.subs({q1: 0, q2: 0}) * pint_pinv
    if numerical_inverse:
        internal_dm = internal_dm.evalf()
    response = pint_pinv * internal_dm.inv() * pint
    derivatives = [
        _matrix_derivative(dm, q1).subs({q1: 0, q2: 0}),
        _matrix_derivative(dm, q2).subs({q1: 0, q2: 0}),
    ]

    answers = []
    for strain in TAU:
        forcing = sp.zeros(2 * n, 1)
        for direction in range(2):
            affine = strain.T * primitive.row(direction).T
            forcing += sp.I * derivatives[direction] * pcm_pinv * affine
        displacement = _simplify_matrix(response * forcing)
        answers.append(sp.Matrix(n, 2, list(displacement)))
    return answers


# Wolfram-style compatibility aliases.
CcwOrth = ccw_orth
ShiftMatrix = shift_matrix
GenerateTSprings = generate_tsprings
GenerateAllTSprings = generate_all_tsprings
SuperLattice = super_lattice
Lengths = lengths
Angles = angles
DeltaLDeltaX = extension_rigidity_matrix
DeltaThetaDeltaX = torsion_rigidity_matrix
DynMatPart = dynamical_matrix_part
DynMat = dynamical_matrix
DynMatCM = dynamical_matrix_cm
StiffnessTensor = stiffness_tensor
StiffnessMatrix = stiffness_matrix
StiffnessTensorNumerical = lambda geom, **kw: stiffness_tensor(
    geom, numerical_inverse=True, **kw
)
StiffnessMatrixNumerical = lambda geom, **kw: stiffness_matrix(
    geom, numerical_inverse=True, **kw
)
BulkModulus = bulk_modulus
ShearModulus = shear_modulus
OddBulkModulus = odd_bulk_modulus
OddShearModulus = odd_shear_modulus
BulkModulusNumerical = lambda geom, **kw: bulk_modulus(
    geom, numerical_inverse=True, **kw
)
ShearModulusNumerical = lambda geom, **kw: shear_modulus(
    geom, numerical_inverse=True, **kw
)
OddBulkModulusNumerical = lambda geom, **kw: odd_bulk_modulus(
    geom, numerical_inverse=True, **kw
)
OddShearModulusNumerical = lambda geom, **kw: odd_shear_modulus(
    geom, numerical_inverse=True, **kw
)
ActiveDensity = active_density
OddRatio = odd_ratio
OddRatioEff = odd_ratio_efficiency
ShearModulusFast = shear_modulus_fast
OddShearModulusFast = odd_shear_modulus_fast
SumEvenModuliFast = sum_even_moduli_fast
SumOddModuliFast = sum_odd_moduli_fast
OddRatioFast = odd_ratio_fast
OddRatioEffFast = odd_ratio_efficiency_fast
dXinternal = internal_displacements
dXinternalNumerical = lambda geom, **kw: internal_displacements(
    geom, numerical_inverse=True, **kw
)
