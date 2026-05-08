"""Phase-component decomposition: count and label disconnected components of
the allowed region in a 2D sweep.

Disconnected components correspond to genuinely different *phases* of UV
completion — theories in different components cannot be continuously
deformed into each other through the constraint-satisfying parameter region,
which means they constitute different equivalence classes of physics.

Implementation: connected-component labeling on the feasibility grid
(4-connectivity, BFS)."""

from collections import deque
from dataclasses import dataclass

import numpy as np


@dataclass
class PhaseDecomposition:
    n_components: int
    component_sizes: list[int]
    label_grid: np.ndarray   # int grid; 0 = excluded, 1..n = component labels


def phase_components(sweep) -> PhaseDecomposition:
    g = sweep.feasibility_grid
    nx, ny = g.shape
    labels = np.zeros((nx, ny), dtype=int)
    sizes: list[int] = []
    next_label = 0
    for i in range(nx):
        for j in range(ny):
            if g[i, j] and labels[i, j] == 0:
                next_label += 1
                size = 0
                queue: deque[tuple[int, int]] = deque([(i, j)])
                labels[i, j] = next_label
                while queue:
                    ci, cj = queue.popleft()
                    size += 1
                    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ni, nj = ci + di, cj + dj
                        if (
                            0 <= ni < nx
                            and 0 <= nj < ny
                            and g[ni, nj]
                            and labels[ni, nj] == 0
                        ):
                            labels[ni, nj] = next_label
                            queue.append((ni, nj))
                sizes.append(size)
    return PhaseDecomposition(
        n_components=next_label,
        component_sizes=sizes,
        label_grid=labels,
    )
