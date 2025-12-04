# EVOLVE-BLOCK-START
"""Deterministic staggered-hex constructor for n=26 circles (compact, high-sum)."""
import numpy as np

def construct_packing():
    """Place 26 equal circles in the unit square on a staggered hex lattice."""
    sqrt3 = np.sqrt(3.0)
    rows = [5,4,5,4,5,4]  # 27 candidate spots

    # Vertical fit for 6 staggered rows: 2*r + 5*sqrt3*r <= 1
    r_vert = 1.0 / (2.0 + 5.0 * sqrt3)

    # Horizontal constraints (row-dependent)
    r_horiz = min(
        (1.0 / (2.0 * m)) if (k % 2 == 0) else (1.0 / (2.0 * m + 1.0))
        for k, m in enumerate(rows)
    )

    r_max = min(r_vert, r_horiz)
    r = r_max * 0.99995  # tiny safety margin

    centers = []
    for k, m in enumerate(rows):
        y = r + k * sqrt3 * r
        if k % 2 == 0:
            xs = r + 2.0 * r * np.arange(m)
        else:
            xs = 2.0 * r + 2.0 * r * np.arange(m)
        for x in xs:
            centers.append((float(x), float(y)))
    centers = np.array(centers, dtype=float)  # 27 positions

    # Remove the top-right-most (largest x+y) to make 26
    idx_remove = int(np.argmax(centers.sum(axis=1)))
    centers = np.delete(centers, idx_remove, axis=0)

    radii = np.full(len(centers), float(r), dtype=float)
    return centers, radii, float(radii.sum())
# EVOLVE-BLOCK-END

# unchanged interface
def run_packing():
    centers, radii, sum_radii = construct_packing()
    return centers, radii, sum_radii

def visualize(centers, radii):
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle
    fig, ax = plt.subplots(figsize=(6,6))
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.set_aspect("equal")
    for i,(c,r) in enumerate(zip(centers, radii)):
        ax.add_patch(Circle(c, r, alpha=0.6, edgecolor='k'))
        ax.text(c[0], c[1], str(i), ha="center", va="center", fontsize=8)
    plt.title(f"n={len(centers)}, sum radii={sum(radii):.6f}")
    plt.show()

if __name__ == "__main__":
    centers, radii, sum_radii = run_packing()
    print(f"Sum of radii: {sum_radii:.6f}")
    # visualize(centers, radii)