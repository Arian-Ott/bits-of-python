import time
import numpy as np
import random
import platform
import statistics
import psutil
from datetime import datetime
from vector import Vector, CVector

# ============================================================
#  CONFIGURATION
# ============================================================
TARGET_REL_HALF_WIDTH = 0.05  # ±5% confidence interval target
CONFIDENCE_Z = 1.96  # 95% confidence
MIN_RUNS = 10
MAX_RUNS = 50
WARMUPS = 3
VECTOR_SIZES = [10_000, 100_000, 1_000_000, 10_000_000, 100_000_000]
MAX_VALUE = 100_000
OUTPUT_FILE = "benchmark_results.txt"
SEED = 42
# ============================================================


def generate_data(n: int, max_val=MAX_VALUE):
    """Generate two random integer vectors of length n."""
    a = [random.randint(1, max_val) for _ in range(n)]
    b = [random.randint(1, max_val) for _ in range(n)]
    return a, b


def time_once(func, *args):
    """Run one timing trial and return runtime in ms."""
    t1 = time.perf_counter_ns()
    func(*args)
    t2 = time.perf_counter_ns()
    return (t2 - t1) / 1e6  # ms


def measure_until_precise(
    func,
    *args,
    warmups=WARMUPS,
    min_runs=MIN_RUNS,
    max_runs=MAX_RUNS,
    rel_halfwidth=TARGET_REL_HALF_WIDTH,
):
    """Run until mean runtime has ±rel_halfwidth CI or max_runs reached."""
    # Warm-up
    for _ in range(warmups):
        func(*args)

    samples = []
    while True:
        samples.append(time_once(func, *args))
        n = len(samples)
        if n < min_runs:
            continue
        mean = statistics.fmean(samples)
        sd = statistics.pstdev(samples) if n > 1 else 0.0
        halfwidth = CONFIDENCE_Z * sd / (n**0.5)
        if mean > 0 and (halfwidth / mean) <= rel_halfwidth:
            break
        if n >= max_runs:
            break
    return samples, mean, sd, halfwidth


def benchmark_single_size(n: int):
    """Benchmark Vector, CVector, and NumPy for one vector size."""
    print(f"\nRunning benchmarks for n = {n:,} ...")

    # Generate identical data for fair comparison
    a, b = generate_data(n)
    np_a = np.array(a, dtype=np.int64)
    np_b = np.array(b, dtype=np.int64)
    v1, v2 = Vector(a), Vector(b)
    cv1, cv2 = CVector(a), CVector(b)

    # Correctness verification
    expected = np.dot(np_a, np_b)
    if not (expected == v1 * v2 == cv1 * cv2):
        raise AssertionError("Dot product mismatch!")

    # Measure all methods adaptively
    numpy_samples, numpy_mean, numpy_sd, numpy_hw = measure_until_precise(
        np.dot, np_a, np_b
    )
    c_samples, c_mean, c_sd, c_hw = measure_until_precise(lambda: cv1 * cv2)
    py_samples, py_mean, py_sd, py_hw = measure_until_precise(lambda: v1 * v2)

    # Collect results
    return {
        "n": n,
        "numpy_mean": numpy_mean,
        "numpy_hw": numpy_hw,
        "numpy_sd": numpy_sd,
        "numpy_n": len(numpy_samples),
        "c_mean": c_mean,
        "c_hw": c_hw,
        "c_sd": c_sd,
        "c_n": len(c_samples),
        "py_mean": py_mean,
        "py_hw": py_hw,
        "py_sd": py_sd,
        "py_n": len(py_samples),
    }


def main():
    random.seed(SEED)

    header = (
        f"Benchmark run: {datetime.now()}\n"
        f"Python version: {platform.python_version()}\n"
        f"Platform: {platform.system()} {platform.release()} ({platform.machine()})\n"
        f"CPU: {platform.processor()}\n"
        f"Total RAM: {round(psutil.virtual_memory().total / 1e9, 2)} GB\n"
        f"Target CI precision: ±{int(TARGET_REL_HALF_WIDTH * 100)}%\n"
        f"Confidence level: 95%\n"
        f"Min runs: {MIN_RUNS}, Max runs: {MAX_RUNS}, Warmups: {WARMUPS}\n"
        f"Vector sizes: {VECTOR_SIZES}\n"
        f"{'-' * 90}\n"
    )

    results = []
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(header)
        print(header)

        for n in VECTOR_SIZES:
            try:
                res = benchmark_single_size(n)
                results.append(res)
            except MemoryError:
                print(f"⚠️ Skipping n={n:,} (out of memory)")
                continue

            line = (
                f"n={n:,}\n"
                f"  NumPy   : {res['numpy_mean']:.3f} ± {res['numpy_hw']:.3f} ms (n={res['numpy_n']})\n"
                f"  CVector : {res['c_mean']:.3f} ± {res['c_hw']:.3f} ms (n={res['c_n']})\n"
                f"  Vector  : {res['py_mean']:.3f} ± {res['py_hw']:.3f} ms (n={res['py_n']})\n"
                f"  Speedup (Vector/CVector): {res['py_mean'] / res['c_mean']:.1f}×\n"
                f"  Speedup (NumPy/CVector) : {res['numpy_mean'] / res['c_mean']:.2f}×\n"
                f"{'-' * 90}\n"
            )
            print(line)
            f.write(line)

        # Summary table
        f.write("\n=== Summary (mean ± CI half-width, ms) ===\n")
        f.write(f"{'Size':>12} {'NumPy':>20} {'CVector':>20} {'Vector':>20}\n")
        for r in results:
            f.write(
                f"{r['n']:12,} "
                f"{r['numpy_mean']:10.3f} ± {r['numpy_hw']:<8.3f} "
                f"{r['c_mean']:10.3f} ± {r['c_hw']:<8.3f} "
                f"{r['py_mean']:10.3f} ± {r['py_hw']:<8.3f}\n"
            )

    print(f"\n✅ Benchmark completed successfully. Results saved to '{OUTPUT_FILE}'")


if __name__ == "__main__":
    main()
