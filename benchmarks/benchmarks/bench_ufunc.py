from .common import Benchmark, get_squares_

import numpy as np


ufuncs = ['abs', 'absolute', 'add', 'arccos', 'arccosh', 'arcsin', 'arcsinh',
          'arctan', 'arctan2', 'arctanh', 'bitwise_and', 'bitwise_not',
          'bitwise_or', 'bitwise_xor', 'cbrt', 'ceil', 'conj', 'conjugate',
          'copysign', 'cos', 'cosh', 'deg2rad', 'degrees', 'divide', 'divmod',
          'equal', 'exp', 'exp2', 'expm1', 'fabs', 'float_power', 'floor',
          'floor_divide', 'fmax', 'fmin', 'fmod', 'frexp', 'gcd', 'greater',
          'greater_equal', 'heaviside', 'hypot', 'invert', 'isfinite',
          'isinf', 'isnan', 'isnat', 'lcm', 'ldexp', 'left_shift', 'less',
          'less_equal', 'log', 'log10', 'log1p', 'log2', 'logaddexp',
          'logaddexp2', 'logical_and', 'logical_not', 'logical_or',
          'logical_xor', 'matmul', 'maximum', 'minimum', 'mod', 'modf', 'multiply',
          'negative', 'nextafter', 'not_equal', 'positive', 'power',
          'rad2deg', 'radians', 'reciprocal', 'remainder', 'right_shift',
          'rint', 'sign', 'signbit', 'sin', 'sinh', 'spacing', 'sqrt',
          'square', 'subtract', 'tan', 'tanh', 'true_divide', 'trunc']


for name in dir(np):
    if isinstance(getattr(np, name, None), np.ufunc) and name not in ufuncs:
        print("Missing ufunc %r" % (name,))


class Broadcast(Benchmark):
    def setup(self):
        self.d = np.ones((50000, 100), dtype=np.float64)
        self.e = np.ones((100,), dtype=np.float64)

    def time_broadcast(self):
        self.d - self.e


class At(Benchmark):
    def setup(self):
        self.vals = np.random.rand(1_000_000)
        self.idx = np.random.randint(1000, size=1_000_000).astype(np.intp)
        self.res = np.zeros(1000, dtype=self.vals.dtype)

    def time_sum_at(self):
        np.add.at(self.res, self.idx, self.vals)


class UFunc(Benchmark):
    params = [ufuncs]
    param_names = ['ufunc']
    timeout = 10

    def setup(self, ufuncname):
        np.seterr(all='ignore')
        try:
            self.f = getattr(np, ufuncname)
        except AttributeError:
            raise NotImplementedError()
        self.args = []
        for t, a in get_squares_().items():
            arg = (a,) * self.f.nin
            try:
                self.f(*arg)
            except TypeError:
                continue
            self.args.append(arg)

    def time_ufunc_types(self, ufuncname):
        [self.f(*arg) for arg in self.args]

class UFuncSmall(Benchmark):
    """  Benchmark for a selection of ufuncs on a small arrays and scalars 

    Since the arrays and scalars are small, we are benchmarking the overhead 
    of the numpy ufunc functionality
    """
    params = ['abs', 'sqrt', 'cos']
    param_names = ['ufunc']
    timeout = 10

    def setup(self, ufuncname):
        np.seterr(all='ignore')
        try:
            self.f = getattr(np, ufuncname)
        except AttributeError:
            raise NotImplementedError()
        self.array_5 = np.array([1., 2., 10., 3., 4.])
        self.array_int_3 = np.array([1, 2, 3])
        self.float64 = np.float64(1.1)
        self.python_float = 1.1
        
    def time_ufunc_small_array(self, ufuncname):
        self.f(self.array_5)

    def time_ufunc_small_array_inplace(self, ufuncname):
        self.f(self.array_5, out = self.array_5)

    def time_ufunc_small_int_array(self, ufuncname):
        self.f(self.array_int_3)

    def time_ufunc_numpy_scalar(self, ufuncname):
        self.f(self.float64)

    def time_ufunc_python_float(self, ufuncname):
        self.f(self.python_float)
        

class Custom(Benchmark):
    def setup(self):
        self.b = np.ones(20000, dtype=bool)
        self.b_small = np.ones(3, dtype=bool)

    def time_nonzero(self):
        np.nonzero(self.b)

    def time_not_bool(self):
        (~self.b)

    def time_and_bool(self):
        (self.b & self.b)

    def time_or_bool(self):
        (self.b | self.b)

    def time_and_bool_small(self):
        (self.b_small & self.b_small)


class CustomInplace(Benchmark):
    def setup(self):
        self.c = np.ones(500000, dtype=np.int8)
        self.i = np.ones(150000, dtype=np.int32)
        self.f = np.zeros(150000, dtype=np.float32)
        self.d = np.zeros(75000, dtype=np.float64)
        # fault memory
        self.f *= 1.
        self.d *= 1.

    def time_char_or(self):
        np.bitwise_or(self.c, 0, out=self.c)
        np.bitwise_or(0, self.c, out=self.c)

    def time_char_or_temp(self):
        0 | self.c | 0

    def time_int_or(self):
        np.bitwise_or(self.i, 0, out=self.i)
        np.bitwise_or(0, self.i, out=self.i)

    def time_int_or_temp(self):
        0 | self.i | 0

    def time_float_add(self):
        np.add(self.f, 1., out=self.f)
        np.add(1., self.f, out=self.f)

    def time_float_add_temp(self):
        1. + self.f + 1.

    def time_double_add(self):
        np.add(self.d, 1., out=self.d)
        np.add(1., self.d, out=self.d)

    def time_double_add_temp(self):
        1. + self.d + 1.


class CustomScalar(Benchmark):
    params = [np.float32, np.float64]
    param_names = ['dtype']

    def setup(self, dtype):
        self.d = np.ones(20000, dtype=dtype)

    def time_add_scalar2(self, dtype):
        np.add(self.d, 1)

    def time_divide_scalar2(self, dtype):
        np.divide(self.d, 1)

    def time_divide_scalar2_inplace(self, dtype):
        np.divide(self.d, 1, out=self.d)


class CustomComparison(Benchmark):
    params = (np.int8,  np.int16,  np.int32,  np.int64, np.uint8, np.uint16,
              np.uint32, np.uint64, np.float32, np.float64, np.bool_)
    param_names = ['dtype']

    def setup(self, dtype):
        self.x = np.ones(50000, dtype=dtype)
        self.y = np.ones(50000, dtype=dtype)
        self.s = np.ones(1, dtype=dtype)

    def time_less_than_binary(self, dtype):
        (self.x < self.y)

    def time_less_than_scalar1(self, dtype):
        (self.s < self.x)

    def time_less_than_scalar2(self, dtype):
        (self.x < self.s)


class CustomScalarFloorDivideInt(Benchmark):
    params = (np.sctypes['int'] + np.sctypes['uint'], [8, -8, 43, -43])
    param_names = ['dtype', 'divisors']

    def setup(self, dtype, divisor):
        if dtype in np.sctypes['uint'] and divisor < 0:
            raise NotImplementedError(
                    "Skipping test for negative divisor with unsigned type")

        iinfo = np.iinfo(dtype)
        self.x = np.random.randint(
                    iinfo.min, iinfo.max, size=10000, dtype=dtype)

    def time_floor_divide_int(self, dtype, divisor):
        self.x // divisor

class CustomArrayFloorDivideInt(Benchmark):
    params = (np.sctypes['int'] + np.sctypes['uint'], [100, 10000, 1000000])
    param_names = ['dtype', 'size']

    def setup(self, dtype, size):
        iinfo = np.iinfo(dtype)
        self.x = np.random.randint(
                    iinfo.min, iinfo.max, size=size, dtype=dtype)
        self.y = np.random.randint(2, 32, size=size, dtype=dtype)

    def time_floor_divide_int(self, dtype, size):
        self.x // self.y


class Scalar(Benchmark):
    def setup(self):
        self.x = np.asarray(1.0)
        self.y = np.asarray((1.0 + 1j))
        self.z = complex(1.0, 1.0)

    def time_add_scalar(self):
        (self.x + self.x)

    def time_add_scalar_conv(self):
        (self.x + 1.0)

    def time_add_scalar_conv_complex(self):
        (self.y + self.z)


class ArgPack:
    __slots__ = ['args', 'kwargs']
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    def __repr__(self):
        return '({})'.format(', '.join(
            [repr(a) for a in self.args] +
            ['{}={}'.format(k, repr(v)) for k, v in self.kwargs.items()]
        ))


class ArgParsing(Benchmark):
    # In order to benchmark the speed of argument parsing, all but the
    # out arguments are chosen such that they have no effect on the
    # calculation.  In particular, subok=True and where=True are
    # defaults, and the dtype is the correct one (the latter will
    # still have some effect on the search for the correct inner loop).
    x = np.array(1.)
    y = np.array(2.)
    out = np.array(3.)
    param_names = ['arg_kwarg']
    params = [[
        ArgPack(x, y),
        ArgPack(x, y, out),
        ArgPack(x, y, out=out),
        ArgPack(x, y, out=(out,)),
        ArgPack(x, y, out=out, subok=True, where=True),
        ArgPack(x, y, subok=True),
        ArgPack(x, y, subok=True, where=True),
        ArgPack(x, y, out, subok=True, where=True)
    ]]

    def time_add_arg_parsing(self, arg_pack):
        np.add(*arg_pack.args, **arg_pack.kwargs)


class ArgParsingReduce(Benchmark):
    # In order to benchmark the speed of argument parsing, all but the
    # out arguments are chosen such that they have minimal effect on the
    # calculation.
    a = np.arange(2.)
    out = np.array(0.)
    param_names = ['arg_kwarg']
    params = [[
        ArgPack(a,),
        ArgPack(a, 0),
        ArgPack(a, axis=0),
        ArgPack(a, 0, None),
        ArgPack(a, axis=0, dtype=None),
        ArgPack(a, 0, None, out),
        ArgPack(a, axis=0, dtype=None, out=out),
        ArgPack(a, out=out)
    ]]

    def time_add_reduce_arg_parsing(self, arg_pack):
        np.add.reduce(*arg_pack.args, **arg_pack.kwargs)

class BinaryBench(Benchmark):
    def setup(self):
        N = 1000000
        self.a32 = np.random.rand(N).astype(np.float32)
        self.b32 = np.random.rand(N).astype(np.float32)
        self.a64 = np.random.rand(N).astype(np.float64)
        self.b64 = np.random.rand(N).astype(np.float64)
    
    def time_pow_32(self):
        np.power(self.a32, self.b32)

    def time_pow_64(self):
        np.power(self.a64, self.b64)

    def time_atan2_32(self):
        np.arctan2(self.a32, self.b32)

    def time_atan2_64(self):
        np.arctan2(self.a64, self.b64)
