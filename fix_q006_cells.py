"""Fix Q-P006 _cells file location."""
import shutil, os

src_dir = r"03_INVESTIGATIONS\PHYSICS\percolation\Q-P005_exponents\CODE\RESULTS"
dst_dir = r"03_INVESTIGATIONS\PHYSICS\percolation\Q-P006\CODE\RESULTS"
os.makedirs(dst_dir, exist_ok=True)

for L, n in [(512, 200), (1024, 100), (2048, 50)]:
    src = os.path.join(src_dir, f"_cells_L{L}_n{n}.npz")
    dst = os.path.join(dst_dir, f"_cells_L{L}_n{n}.npz")
    if os.path.exists(src):
        shutil.copy2(src, dst)
        size = os.path.getsize(dst)
        print(f"Copied _cells_L{L}_n{n}.npz -> {dst} ({size:,} bytes)")
    else:
        print(f"NOT FOUND: {src}")

print("\nVerification:")
import numpy as np
for L, n in [(512, 200), (1024, 100), (2048, 50)]:
    p = os.path.join(dst_dir, f"_cells_L{L}_n{n}.npz")
    if os.path.exists(p):
        z = np.load(p, allow_pickle=True)
        print(f"  L={L}: keys={list(z.keys())}, N={z['N']}, masses shape={z['masses'].shape}")
    else:
        print(f"  L={L}: MISSING")
