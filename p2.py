# EVOLVE-BLOCK-START
"""Compact explicit constructor for n=26 circles: tight hex rows with exact r.

We place a 6-row staggered hex pattern with row counts [5,4,5,4,5,4] and use
the exact vertical bound r = 1 / (2 + 5*sqrt(3)), minus a tiny epsilon to
avoid numerical touching. We remove the deterministic top-right position to
get 26 circles and assign a uniform radius r to all. This slightly improves
the sum of radii over margin-shrunk variants while remaining valid.
"""
import numpy as np

def construct_packing():
    s = np.sqrt(3.0)
    rows = [5,4,5,4,5,4]
    r = 1.0/(2.0+5.0*s)*(1.0-1e-12)
    centers = []
    for k,m in enumerate(rows):
        y = r + k*s*r
        x0 = r if (k%2==0) else 2.0*r
        for x in x0 + 2.0*r*np.arange(m):
            centers.append((float(x), float(y)))
    centers = np.array(centers, dtype=float)  # 27
    centers = np.delete(centers, int(np.argmax(centers.sum(axis=1))), axis=0)  # -> 26
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
        ax.add_patch(Circle(c, r, alpha=0.5))
        ax.text(c[0], c[1], str(i), ha="center", va="center", fontsize=8)
    plt.title(f"n={len(centers)}, sum radii={sum(radii):.6f}")
    plt.show()


if __name__ == "__main__":
    c, r, s = run_packing()
    print(f"Sum of radii: {s:.6f}")
    # visualize(c, r)