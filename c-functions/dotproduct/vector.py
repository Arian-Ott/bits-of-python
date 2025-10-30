from typing import Iterable, Union
import ctypes
import os
Number = Union[int, float]


class Vector:
    def __init__(self, vector: Iterable[Number]):
        self.vector = list(vector)

    def __iter__(self):
        return iter(self.vector)

    def __mul__(self, other):
        # Scalar multiplication
        if isinstance(other, (int, float)):
            return Vector([x * other for x in self.vector])
        # Dot product
        elif isinstance(other, Vector):
            return self._dot(other)
        else:
            raise TypeError(
                f"Unsupported operand type(s) for *: 'Vector' and '{type(other).__name__}'"
            )

    def _dot(self, other: "Vector") -> Number:
        if len(self.vector) != len(other.vector):
            raise ValueError("Vectors must be of same length for dot product.")
        return sum(i * j for i, j in zip(self.vector, other.vector))

    def __repr__(self):
        return f"Vector({self.vector})"


class CVector(Vector):
    def __init__(self, vector: Iterable[Number]):
        super().__init__(vector)

        # Load the shared library with an absolute path (important for pytest)
        dll_path = os.path.join(os.path.dirname(__file__), "functions", "dot.so")
        self._cdll = ctypes.CDLL(dll_path)

        # Match your C signature: int dot(int, int*, int*)
        self._cdll.dot.argtypes = [
            ctypes.c_int32,
            ctypes.POINTER(ctypes.c_int32),
            ctypes.POINTER(ctypes.c_int32),
        ]
        self._cdll.dot.restype = ctypes.c_int64

        # Cache the C array once (avoid rebuilding each call)
        self._n = len(self.vector)
        array_type = ctypes.c_int * self._n
        self._c_array = array_type(*map(int, self.vector))

    def _dot(self, other: "CVector") -> int:
        # Safety: ensure both are CVector and same length
        if not isinstance(other, CVector):
            raise TypeError("CVector can only perform dot with another CVector.")
        if self._n != other._n:
            raise ValueError("Vectors must have the same length for dot product.")

        return self._cdll.dot(self._n, self._c_array, other._c_array)