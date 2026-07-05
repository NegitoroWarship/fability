import sys


def compute(numbers):
    return {
        "count": len(numbers),
        "mean": sum(numbers) / len(numbers),
        "min": min(numbers),
        "max": max(numbers),
    }


def main():
    path = sys.argv[1]
    numbers = [float(line) for line in open(path) if line.strip()]
    s = compute(numbers)
    print(f"count: {s['count']}")
    print(f"mean: {s['mean']:.2f}")
    print(f"min: {s['min']}")
    print(f"max: {s['max']}")


if __name__ == "__main__":
    main()
