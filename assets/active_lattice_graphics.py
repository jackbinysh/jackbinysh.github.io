"""Matplotlib port of ``ActiveLatticeGraphics_StaffPicks.wl``.

The geometry and spring formats are the same as in
``linear_odd_elastodynamics.py``.  Drawing functions add artists to an
existing Matplotlib Axes (or create one) and return that Axes.
"""

from __future__ import annotations

from itertools import product
from typing import Any, Callable, Iterable, Sequence

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patches import Arc, Circle, Polygon, Wedge


MATPLOTLIB_RED = "#d62728"
MATPLOTLIB_BLUE = "#1f77b4"
MATPLOTLIB_GREEN = "#2ca02c"


def _array(value: Any) -> np.ndarray:
    return np.asarray(value, dtype=float)


def _axes(ax: Axes | None) -> Axes:
    return ax if ax is not None else plt.subplots()[1]


def _position(
    primitive_vectors: Sequence[Sequence[float]],
    balls: Sequence[Sequence[float]],
    node_ref: Sequence[Any],
    lattice: Sequence[int] = (0, 0),
    *,
    index_base: int = 1,
) -> np.ndarray:
    prim = _array(primitive_vectors)
    node = int(node_ref[0]) - index_base
    return _array(balls[node]) + (_array(lattice) + _array(node_ref[1])) @ prim


def _finish(ax: Axes) -> Axes:
    ax.set_aspect("equal", adjustable="datalim")
    ax.autoscale_view()
    return ax


def ccw_orth(vector: Sequence[float]) -> np.ndarray:
    x, y = _array(vector)
    return np.array([-y, x])


def ccw_angle(first: Sequence[float], second: Sequence[float]) -> float:
    a = np.arctan2(first[1], first[0])
    b = np.arctan2(second[1], second[0])
    return float((b - a) % (2 * np.pi))


def _draw_direction_arrow(
    ax: Axes,
    first: np.ndarray,
    second: np.ndarray,
    *,
    color: Any,
    alpha: float = 0.8,
    mutation_scale: float = 10,
    linewidth: float = 1,
) -> None:
    start = first + 0.2 * (second - first)
    end = first + 0.8 * (second - first)
    ax.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops={
            "arrowstyle": "-|>",
            "color": color,
            "alpha": alpha,
            "linewidth": linewidth,
            "mutation_scale": mutation_scale,
        },
    )


def draw_regular_extensions(
    primitive_vectors: Sequence[Sequence[float]],
    balls: Sequence[Sequence[float]],
    springs: Sequence[Sequence[Sequence[Any]]],
    lattice: Sequence[int] = (0, 0),
    *,
    ax: Axes | None = None,
    color: Any = "black",
    linewidth: float = 1.5,
    index_base: int = 1,
    **_: Any,
) -> Axes:
    """Draw regular extension springs as straight line segments."""
    ax = _axes(ax)
    for spring in springs:
        points = np.vstack(
            [
                _position(
                    primitive_vectors,
                    balls,
                    ref,
                    lattice,
                    index_base=index_base,
                )
                for ref in spring
            ]
        )
        ax.plot(points[:, 0], points[:, 1], color=color, linewidth=linewidth)
    return _finish(ax)


def draw_polygon(
    primitive_vectors: Sequence[Sequence[float]],
    balls: Sequence[Sequence[float]],
    spring_chain: Sequence[Sequence[Sequence[Any]]],
    lattice: Sequence[int] = (0, 0),
    *,
    ax: Axes | None = None,
    color: Any = MATPLOTLIB_BLUE,
    alpha: float = 0.3,
    index_base: int = 1,
    **_: Any,
) -> Axes:
    """Fill the polygon traced by the second node of each chain spring."""
    ax = _axes(ax)
    points = [
        _position(
            primitive_vectors,
            balls,
            spring[1],
            lattice,
            index_base=index_base,
        )
        for spring in spring_chain
    ]
    ax.add_patch(Polygon(points, closed=True, facecolor=color, alpha=alpha))
    return _finish(ax)


def draw_data_sharing_extensions(
    primitive_vectors: Sequence[Sequence[float]],
    balls: Sequence[Sequence[float]],
    spring_chain: Sequence[Sequence[Sequence[Any]]],
    lattice: Sequence[int] = (0, 0),
    *,
    ax: Axes | None = None,
    color: Any = MATPLOTLIB_RED,
    linewidth: float = 1.2,
    waves: int = 12,
    amplitude: float = 0.05,
    index_base: int = 1,
    **_: Any,
) -> Axes:
    """Draw data-sharing extension springs as wavy, directed segments."""
    ax = _axes(ax)
    midpoints = []
    for spring in spring_chain:
        first, second = [
            _position(
                primitive_vectors,
                balls,
                ref,
                lattice,
                index_base=index_base,
            )
            for ref in spring
        ]
        direction = second - first
        length = np.linalg.norm(direction)
        normal = ccw_orth(direction) if length else np.zeros(2)
        t = np.linspace(0, 1, 8 * waves + 1)
        points = (
            first[None, :]
            + t[:, None] * direction[None, :]
            + amplitude
            * np.sin(2 * np.pi * waves * t)[:, None]
            * normal[None, :]
        )
        ax.plot(points[:, 0], points[:, 1], color=color, linewidth=linewidth)
        midpoints.append((first + second) / 2)

    for first, second in zip(midpoints, midpoints[1:] + midpoints[:1]):
        _draw_direction_arrow(
            ax,
            first,
            second,
            color=color,
            linewidth=linewidth,
        )
    return _finish(ax)


def draw_regular_torsions(
    primitive_vectors: Sequence[Sequence[float]],
    balls: Sequence[Sequence[float]],
    springs: Sequence[Sequence[Sequence[Any]]],
    lattice: Sequence[int] = (0, 0),
    *,
    ax: Axes | None = None,
    color: Any = "lightgray",
    radius: float = 0.15,
    index_base: int = 1,
    **_: Any,
) -> Axes:
    """Draw regular torsion springs as filled angular sectors."""
    ax = _axes(ax)
    for first_ref, centre_ref, last_ref in springs:
        first, centre, last = [
            _position(
                primitive_vectors,
                balls,
                ref,
                lattice,
                index_base=index_base,
            )
            for ref in (first_ref, centre_ref, last_ref)
        ]
        r1, r2 = first - centre, last - centre
        theta1 = np.degrees(np.arctan2(r1[1], r1[0]))
        theta2 = theta1 + np.degrees(ccw_angle(r1, r2))
        shifted_centre = centre + 0.03 * (r1 + r2)
        ax.add_patch(
            Wedge(
                shifted_centre,
                radius * min(np.linalg.norm(r1), np.linalg.norm(r2)),
                theta1,
                theta2,
                facecolor=color,
                edgecolor="none",
            )
        )
    return _finish(ax)


def draw_data_sharing_torsions(
    primitive_vectors: Sequence[Sequence[float]],
    balls: Sequence[Sequence[float]],
    spring_chain: Sequence[Sequence[Sequence[Any]]],
    lattice: Sequence[int] = (0, 0),
    *,
    ax: Axes | None = None,
    color: Any = MATPLOTLIB_BLUE,
    linewidth: float = 1.5,
    arrow_size: float = 10,
    index_base: int = 1,
    **_: Any,
) -> Axes:
    """Draw data-sharing torsion springs as open, directed arcs."""
    ax = _axes(ax)
    chain_points = []
    for first_ref, centre_ref, last_ref in spring_chain:
        first, centre, last = [
            _position(
                primitive_vectors,
                balls,
                ref,
                lattice,
                index_base=index_base,
            )
            for ref in (first_ref, centre_ref, last_ref)
        ]
        r1, r2 = first - centre, last - centre
        scale = min(np.linalg.norm(r1), np.linalg.norm(r2))
        radius = 0.25 * scale
        theta1 = np.degrees(np.arctan2(r1[1], r1[0]))
        theta2 = theta1 + np.degrees(ccw_angle(r1, r2))
        arc_centre = centre + 0.03 * (r1 + r2)
        ax.add_patch(
            Arc(
                arc_centre,
                2 * radius,
                2 * radius,
                theta1=theta1,
                theta2=theta2,
                color=color,
                linewidth=linewidth,
            )
        )
        unit_sum = r1 / np.linalg.norm(r1) + r2 / np.linalg.norm(r2)
        if np.linalg.norm(unit_sum):
            unit_sum /= np.linalg.norm(unit_sum)
        chain_points.append(centre + radius * unit_sum)

    for first, second in zip(chain_points, chain_points[1:] + chain_points[:1]):
        _draw_direction_arrow(
            ax,
            first,
            second,
            color=color,
            alpha=0.7,
            mutation_scale=arrow_size,
            linewidth=linewidth,
        )
    return _finish(ax)


def draw_primitive_cell(
    primitive_vectors: Sequence[Sequence[float]],
    balls: Sequence[Sequence[float]],
    *,
    ax: Axes | None = None,
    color: Any = MATPLOTLIB_GREEN,
    linewidth: float = 1,
    **_: Any,
) -> Axes:
    """Shade the primitive parallelogram used by the Wolfram routine."""
    ax = _axes(ax)
    prim = _array(primitive_vectors)
    centre = _array(balls).mean(axis=0) + prim.sum(axis=0) / 2
    vertices = [
        centre,
        centre + prim[0],
        centre + prim[0] + prim[1],
        centre + prim[1],
    ]
    ax.add_patch(
        Polygon(
            vertices,
            closed=True,
            facecolor=color,
            edgecolor=color,
            linestyle="--",
            linewidth=linewidth,
            alpha=0.2,
        )
    )
    return _finish(ax)


def draw_balls(
    primitive_vectors: Sequence[Sequence[float]],
    balls: Sequence[Sequence[float]],
    lattice: Sequence[int] = (0, 0),
    *,
    ax: Axes | None = None,
    color: Any = "black",
    size: float = 28,
    **_: Any,
) -> Axes:
    """Draw all sites in one translated unit cell."""
    ax = _axes(ax)
    translation = _array(lattice) @ _array(primitive_vectors)
    points = _array(balls) + translation
    ax.scatter(points[:, 0], points[:, 1], color=color, s=size, zorder=10)
    return _finish(ax)


_DRAWERS = {
    ("extension", "regular"): draw_regular_extensions,
    ("extension", "data-sharing"): draw_data_sharing_extensions,
    ("torsion", "regular"): draw_regular_torsions,
    ("torsion", "data-sharing"): draw_data_sharing_torsions,
}


def draw_unit_cell(
    geom: Sequence[Any],
    *,
    lattice: Sequence[int] = (0, 0),
    spring_types: Iterable[Sequence[str]] = _DRAWERS.keys(),
    polygon_types: Iterable[Sequence[str]] = (),
    ax: Axes | None = None,
    **style: Any,
) -> Axes:
    """Draw selected spring groups, polygons, and sites for one unit cell."""
    ax = _axes(ax)
    spring_types = {tuple(header) for header in spring_types}
    polygon_types = {tuple(header) for header in polygon_types}

    for header, springs, _ in geom[2:]:
        key = tuple(header)
        if key in spring_types:
            try:
                drawer = _DRAWERS[key]
            except KeyError as error:
                raise NotImplementedError(
                    f"spring type {header!r} is not graphically implemented"
                ) from error
            drawer(geom[0], geom[1][0], springs, lattice, ax=ax, **style)
        if key in polygon_types:
            draw_polygon(geom[0], geom[1][0], springs, lattice, ax=ax, **style)

    draw_balls(geom[0], geom[1][0], lattice, ax=ax, **style)
    return _finish(ax)


def draw_lattice(
    geom: Sequence[Any],
    *,
    lattice_cells: Iterable[Sequence[int]] | None = None,
    shade_unit_cell: bool = True,
    ax: Axes | None = None,
    **style: Any,
) -> Axes:
    """Draw a finite patch of the periodic lattice."""
    ax = _axes(ax)
    cells = (
        list(product(range(4), repeat=2))
        if lattice_cells is None
        else list(lattice_cells)
    )
    for cell in cells:
        draw_unit_cell(geom, lattice=cell, ax=ax, **style)
    if shade_unit_cell:
        draw_primitive_cell(geom[0], geom[1][0], ax=ax, **style)
    return _finish(ax)


def compute_angles_phi(
    input_positions: Sequence[Sequence[float]],
    permutation: Sequence[int] = tuple(range(6)),
) -> tuple[float, float, float, np.ndarray, np.ndarray]:
    """Compute the two shear coordinates and bulk coordinate of a hexagon."""
    positions = _array(input_positions)
    if positions.shape != (6, 2):
        raise ValueError("input_positions must contain six 2D points")
    complex_positions = positions[:, 0] + 1j * positions[:, 1]
    edges = np.roll(complex_positions, -1) - complex_positions
    theta = np.mod(np.angle(-edges / np.roll(edges, 1)), 2 * np.pi)
    angle_data = (theta - 4 * np.pi / 6)[list(permutation)]
    s1 = (angle_data[0] - angle_data[2]) / np.sqrt(2)
    s2 = (angle_data[0] + angle_data[2] - 2 * angle_data[4]) / np.sqrt(5)
    bulk = (angle_data[0] + angle_data[2] + angle_data[4]) / np.sqrt(3)
    return float(s1), float(s2), float(bulk), theta, angle_data


def get_hex_positions(
    primitive_vectors: Sequence[Sequence[float]],
    balls: Sequence[Sequence[float]],
    hexagon: Sequence[Sequence[Any]],
    lattice: Sequence[int] = (0, 0),
    *,
    index_base: int = 1,
) -> np.ndarray:
    """Resolve a six-node, cell-aware hexagon specification to positions."""
    return np.vstack(
        [
            _position(
                primitive_vectors,
                balls,
                ref,
                lattice,
                index_base=index_base,
            )
            for ref in hexagon
        ]
    )


def draw_unit_cell_polygons(
    geom: Sequence[Any],
    lattice: Sequence[int],
    input_hexagons: Sequence[Sequence[Any]],
    colormap: Callable[[float], Any],
    *,
    ax: Axes | None = None,
    index_base: int = 1,
) -> Axes:
    """Color hexagons by shear magnitude and mark active plaquettes."""
    ax = _axes(ax)
    primitive, balls = geom[0], geom[1][0]
    for hexagon, active in input_hexagons:
        positions = get_hex_positions(
            primitive,
            balls,
            hexagon,
            lattice,
            index_base=index_base,
        )
        s1, s2, _, _, _ = compute_angles_phi(positions)
        ax.add_patch(
            Polygon(
                positions,
                closed=True,
                facecolor=colormap(np.hypot(s1, s2)),
                edgecolor="black",
                linewidth=0.5,
            )
        )
        if active == 1:
            centroid = positions.mean(axis=0)
            radius = 0.5 * np.linalg.norm(
                positions - centroid, axis=1
            ).mean()
            ax.add_patch(
                Circle(
                    centroid,
                    radius,
                    facecolor="black",
                    edgecolor="black",
                    linewidth=0.5,
                )
            )
    return _finish(ax)


# Wolfram-style compatibility aliases.
CcwOrth = ccw_orth
CcwAngle = ccw_angle
DrawExtR = draw_regular_extensions
DrawExtDS = draw_data_sharing_extensions
DrawTrsR = draw_regular_torsions
DrawTrsDS = draw_data_sharing_torsions
DrawPrim = draw_primitive_cell
DrawBalls = draw_balls
DrawPoly = draw_polygon
DrawUC = draw_unit_cell
DrawLattice = draw_lattice
ComputeAnglesPhi = compute_angles_phi
getHexPositions = get_hex_positions
DrawUCPoly = draw_unit_cell_polygons
