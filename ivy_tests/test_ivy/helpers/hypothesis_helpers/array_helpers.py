# global
import math
import numpy as np
import hypothesis.extra.numpy as nph
from hypothesis import strategies as st
from functools import reduce
from operator import mul

# local
import ivy
from . import general_helpers as gh
from . import dtype_helpers, number_helpers
import ivy.functional.backends.numpy as ivy_np  # ToDo should be removed.


@st.composite
def array_bools(
    draw,
    *,
    num_arrays=st.shared(
        number_helpers.ints(min_value=1, max_value=4), key="num_arrays"
    ),
):
    """Draws a boolean list of a given size.

    Parameters
    ----------
    draw
        special function that draws data randomly (but is reproducible) from a given
        data-set (ex. list).
    num_arrays
        size of the list.

    Returns
    -------
    A strategy that draws a list.
    """
    size = num_arrays if isinstance(num_arrays, int) else draw(num_arrays)
    return draw(st.lists(st.booleans(), min_size=size, max_size=size))


def list_of_length(*, x, length):
    """Returns a random list of the given length from elements in x."""
    return st.lists(x, min_size=length, max_size=length)


@st.composite
def lists(draw, *, arg, min_size=None, max_size=None, size_bounds=None):
    """Draws a list from the dataset arg.

    Parameters
    ----------
    draw
        special function that draws data randomly (but is reproducible) from a given
        data-set (ex. list).
    arg
        dataset of elements.
    min_size
        least size of the list.
    max_size
        max size of the list.
    size_bounds
        if min_size or max_size is None, draw them randomly from the range
        [size_bounds[0], size_bounds[1]].

    Returns
    -------
    A strategy that draws a list.
    """
    integers = (
        number_helpers.ints(min_value=size_bounds[0], max_value=size_bounds[1])
        if size_bounds
        else number_helpers.ints()
    )
    if isinstance(min_size, str):
        min_size = draw(st.shared(integers, key=min_size))
    if isinstance(max_size, str):
        max_size = draw(st.shared(integers, key=max_size))
    return draw(st.lists(arg, min_size=min_size, max_size=max_size))


@st.composite
def dtype_and_values(
    draw,
    *,
    available_dtypes=ivy_np.valid_dtypes,
    num_arrays=1,
    abs_smallest_val=None,
    min_value=None,
    max_value=None,
    large_abs_safety_factor=1.1,
    small_abs_safety_factor=1.1,
    safety_factor_scale="linear",
    allow_inf=False,
    allow_nan=False,
    exclude_min=False,
    exclude_max=False,
    min_num_dims=0,
    max_num_dims=5,
    min_dim_size=1,
    max_dim_size=10,
    shape=None,
    shared_dtype=False,
    ret_shape=False,
    dtype=None,
):
    """Draws a list of arrays with elements from the given corresponding data types.

    Parameters
    ----------
    draw
        special function that draws data randomly (but is reproducible) from a given
        data-set (ex. list).
    available_dtypes
        if dtype is None, data types are drawn from this list randomly.
    num_arrays
        Number of arrays to be drawn.
    abs_smallest_val
        sets the absolute smallest value to be generated for float data types,
        this has no effect on integer data types. If none, the default data type
        absolute smallest value is used.
    min_value
        minimum value of elements in each array.
    max_value
        maximum value of elements in each array.
    large_abs_safety_factor
        A safety factor of 1 means that all values are included without limitation,

        when a "linear" safety factor scaler is used,  a safety factor of 2 means
        that only 50% of the range is included, a safety factor of 3 means that
        only 33% of the range is included etc.

        when a "log" safety factor scaler is used, a data type with maximum
        value of 2^32 and a safety factor of 2 transforms the maximum to 2^16.
    small_abs_safety_factor
        A safety factor of 1 means that all values are included without limitation,
        this has no effect on integer data types.

        when a "linear" safety factor scaler is used, a data type with minimum
        representable number of 0.0001 and a safety factor of 2 transforms the
        minimum to 0.0002, a safety factor of 3 transforms the minimum to 0.0003 etc.

        when a "log" safety factor scaler is used, a data type with minimum
        representable number of 0.5 * 2^-16 and a safety factor of 2 transforms the
        minimum to 0.5 * 2^-8, a safety factor of 3 transforms the minimum to 0.5 * 2^-4
    safety_factor_scale
        The operation to use when calculating the maximum value of the list. Can be
        "linear" or "log". Default value = "linear".
    allow_inf
        if True, allow inf in the arrays.
    allow_nan
        if True, allow Nans in the arrays.
    exclude_min
        if True, exclude the minimum limit.
    exclude_max
        if True, exclude the maximum limit.
    min_num_dims
        minimum size of the shape tuple.
    max_num_dims
        maximum size of the shape tuple.
    min_dim_size
        minimum value of each integer in the shape tuple.
    max_dim_size
        maximum value of each integer in the shape tuple.
    shape
        shape of the arrays in the list.
    shared_dtype
        if True, if dtype is None, a single shared dtype is drawn for all arrays.
    ret_shape
        if True, the shape of the arrays is also returned.
    dtype
        A list of data types for the given arrays.

    Returns
    -------
    A strategy that draws a list of dtype and arrays (as lists).
    """
    if isinstance(min_dim_size, st._internal.SearchStrategy):
        min_dim_size = draw(min_dim_size)
    if isinstance(max_dim_size, st._internal.SearchStrategy):
        max_dim_size = draw(max_dim_size)
    if isinstance(available_dtypes, st._internal.SearchStrategy):
        available_dtypes = draw(available_dtypes)
    if not isinstance(num_arrays, int):
        num_arrays = draw(num_arrays)
    if dtype is None:
        dtype = draw(
            dtype_helpers.array_dtypes(
                num_arrays=num_arrays,
                available_dtypes=available_dtypes,
                shared_dtype=shared_dtype,
            )
        )
    if shape is not None:
        if not isinstance(shape, (tuple, list)):
            shape = draw(shape)
    else:
        shape = draw(
            st.shared(
                gh.get_shape(
                    min_num_dims=min_num_dims,
                    max_num_dims=max_num_dims,
                    min_dim_size=min_dim_size,
                    max_dim_size=max_dim_size,
                ),
                key="shape",
            )
        )
    values = []
    for i in range(num_arrays):
        values.append(
            draw(
                array_values(
                    dtype=dtype[i],
                    shape=shape,
                    abs_smallest_val=abs_smallest_val,
                    min_value=min_value,
                    max_value=max_value,
                    allow_inf=allow_inf,
                    allow_nan=allow_nan,
                    exclude_min=exclude_min,
                    exclude_max=exclude_max,
                    large_abs_safety_factor=large_abs_safety_factor,
                    small_abs_safety_factor=small_abs_safety_factor,
                    safety_factor_scale=safety_factor_scale,
                )
            )
        )
    if ret_shape:
        return dtype, values, shape
    return dtype, values


@st.composite
def dtype_values_axis(
    draw,
    *,
    available_dtypes,
    abs_smallest_val=None,
    min_value=None,
    max_value=None,
    large_abs_safety_factor=1.1,
    small_abs_safety_factor=1.1,
    safety_factor_scale="linear",
    allow_inf=False,
    allow_nan=False,
    exclude_min=False,
    exclude_max=False,
    min_num_dims=0,
    max_num_dims=5,
    min_dim_size=1,
    max_dim_size=10,
    shape=None,
    shared_dtype=False,
    min_axis=None,
    max_axis=None,
    valid_axis=False,
    allow_neg_axes=True,
    min_axes_size=1,
    max_axes_size=None,
    force_int_axis=False,
    ret_shape=False,
):
    """Draws an array with elements from the given data type, and a random axis of
    the array.

    Parameters
    ----------
    draw
        special function that draws data randomly (but is reproducible) from a given
        data-set (ex. list).
    available_dtypes
        if dtype is None, data type is drawn from this list randomly.
    abs_smallest_val
        sets the absolute smallest value to be generated for float data types,
        this has no effect on integer data types. If none, the default data type
        absolute smallest value is used.
    min_value
        minimum value of elements in the array.
    max_value
        maximum value of elements in the array.
    large_abs_safety_factor
        A safety factor of 1 means that all values are included without limitation,

        when a "linear" safety factor scaler is used,  a safety factor of 2 means
        that only 50% of the range is included, a safety factor of 3 means that
        only 33% of the range is included etc.

        when a "log" safety factor scaler is used, a data type with maximum
        value of 2^32 and a safety factor of 2 transforms the maximum to 2^16.
    small_abs_safety_factor
        A safety factor of 1 means that all values are included without limitation,
        this has no effect on integer data types.

        when a "linear" safety factor scaler is used, a data type with minimum
        representable number of 0.0001 and a safety factor of 2 transforms the
        minimum to 0.0002, a safety factor of 3 transforms the minimum to 0.0003 etc.

        when a "log" safety factor scaler is used, a data type with minimum
        representable number of 0.5 * 2^-16 and a safety factor of 2 transforms the
        minimum to 0.5 * 2^-8, a safety factor of 3 transforms the minimum to 0.5 * 2^-4
    safety_factor_scale
        The operation to use when calculating the maximum value of the list. Can be
        "linear" or "log". Default value = "linear".
    allow_inf
        if True, allow inf in the array.
    allow_nan
        if True, allow Nans in the arrays.
    exclude_min
        if True, exclude the minimum limit.
    exclude_max
        if True, exclude the maximum limit.
    min_num_dims
        minimum size of the shape tuple.
    max_num_dims
        maximum size of the shape tuple.
    min_dim_size
        minimum value of each integer in the shape tuple.
    max_dim_size
        maximum value of each integer in the shape tuple.
    valid_axis
        if True, a valid axis will be drawn from the array dimensions.
    allow_neg_axes
        if True, returned axes may include negative axes.
    min_axes_size
        minimum size of the axis tuple.
    max_axes_size
        maximum size of the axis tuple.
    force_int_axis
        if True, and only one axis is drawn, the returned axis will be an integer.
    shape
        shape of the array. if None, a random shape is drawn.
    shared_dtype
        if True, if dtype is None, a single shared dtype is drawn for all arrays.
    min_axis
        if shape is None, axis is drawn from the range [min_axis, max_axis].
    max_axis
        if shape is None, axis is drawn from the range [min_axis, max_axis].
    ret_shape
        if True, the shape of the arrays is also returned.

    Returns
    -------
    A strategy that draws a dtype, an array (as list), and an axis.
    """
    results = draw(
        dtype_and_values(
            available_dtypes=available_dtypes,
            abs_smallest_val=abs_smallest_val,
            min_value=min_value,
            max_value=max_value,
            large_abs_safety_factor=large_abs_safety_factor,
            small_abs_safety_factor=small_abs_safety_factor,
            safety_factor_scale=safety_factor_scale,
            allow_inf=allow_inf,
            allow_nan=allow_nan,
            exclude_min=exclude_min,
            exclude_max=exclude_max,
            min_num_dims=min_num_dims,
            max_num_dims=max_num_dims,
            min_dim_size=min_dim_size,
            max_dim_size=max_dim_size,
            shape=shape,
            shared_dtype=shared_dtype,
            ret_shape=True,
        )
    )
    dtype, values, arr_shape = results
    if valid_axis or shape:
        if values[0].ndim == 0:
            axis = None
        else:
            axis = draw(
                gh.get_axis(
                    shape=arr_shape,
                    min_size=min_axes_size,
                    max_size=max_axes_size,
                    allow_neg=allow_neg_axes,
                    force_int=force_int_axis,
                )
            )
    else:
        axis = draw(number_helpers.ints(min_value=min_axis, max_value=max_axis))
    if ret_shape:
        return dtype, values, axis, shape
    return dtype, values, axis


@st.composite
def array_n_indices_n_axis(
    draw,
    *,
    array_dtypes,
    indices_dtypes=ivy_np.valid_int_dtypes,
    disable_random_axis=False,
    boolean_mask=False,
    allow_inf=False,
    min_num_dims=1,
    max_num_dims=5,
    min_dim_size=1,
    max_dim_size=10,
    first_dimension_only=False,
):
    """Generates two arrays x & indices, the values in the indices array are indices
    of the array x. Draws an integers randomly from the minimum and maximum number of
    positional arguments a given function can take.

    Parameters
    ----------
    array_dtypes
        list of data type to draw the array dtype from.
    indices_dtypes
        list of data type to draw the indices dtype from.
    disable_random_axis
        axis is set to -1 when True. Randomly generated with hypothesis if False.
    allow_inf
        inf values are allowed to be generated in the values array when True.
    min_num_dims
        The minimum number of dimensions the arrays can have.
    max_num_dims
        The maximum number of dimensions the arrays can have.
    min_dim_size
        The minimum size of the dimensions of the arrays.
    max_dim_size
        The maximum size of the dimensions of the arrays.

    Returns
    -------
    A strategy that can be used in the @given hypothesis decorator
    which generates arrays of values and indices.

    Examples
    --------
    @given(
        array_n_indices_n_axis=array_n_indices_n_axis(
            array_dtypes=helpers.get_dtypes("valid"),
            indices_dtypes=helpers.get_dtypes("integer"),
            boolean_mask=False,
            min_num_dims=1,
            max_num_dims=5,
            min_dim_size=1,
            max_dim_size=10
            )
    )
    """
    x_dtype, x, x_shape = draw(
        dtype_and_values(
            available_dtypes=array_dtypes,
            allow_inf=allow_inf,
            ret_shape=True,
            min_num_dims=min_num_dims,
            max_num_dims=max_num_dims,
            min_dim_size=min_dim_size,
            max_dim_size=max_dim_size,
        )
    )
    if disable_random_axis:
        axis = -1
    else:
        axis = draw(
            number_helpers.ints(
                min_value=-1 * len(x_shape),
                max_value=len(x_shape) - 1,
            )
        )
    if boolean_mask:
        indices_dtype, indices = draw(
            dtype_and_values(
                dtype=["bool"],
                min_num_dims=min_num_dims,
                max_num_dims=max_num_dims,
                min_dim_size=min_dim_size,
                max_dim_size=max_dim_size,
            )
        )
    else:
        max_axis = max(x_shape[axis] - 1, 0)
        if first_dimension_only:
            max_axis = max(x_shape[0] - 1, 0)
        indices_dtype, indices = draw(
            dtype_and_values(
                available_dtypes=indices_dtypes,
                allow_inf=False,
                min_value=0,
                max_value=max_axis,
                min_num_dims=min_num_dims,
                max_num_dims=max_num_dims,
                min_dim_size=min_dim_size,
                max_dim_size=max_dim_size,
            )
        )
    return [x_dtype, indices_dtype], x, indices, axis


@st.composite
def arrays_and_axes(
    draw,
    allow_none=False,
    min_num_dims=0,
    max_num_dims=5,
    min_dim_size=1,
    max_dim_size=10,
    num=2,
):
    shapes = list()
    for _ in range(num):
        shape = draw(
            gh.get_shape(
                allow_none=False,
                min_num_dims=min_num_dims,
                max_num_dims=max_num_dims,
                min_dim_size=min_dim_size,
                max_dim_size=max_dim_size,
            )
        )
        shapes.append(shape)
    arrays = list()
    for shape in shapes:
        arrays.append(
            draw(
                array_values(dtype="int32", shape=shape, min_value=-200, max_value=200)
            )
        )
    all_axes_ranges = list()
    for shape in shapes:
        if None in all_axes_ranges:
            all_axes_ranges.append(st.integers(0, len(shape) - 1))
        else:
            all_axes_ranges.append(st.one_of(st.none(), st.integers(0, len(shape) - 1)))
    axes = draw(st.tuples(*all_axes_ranges))
    return arrays, axes


def _clamp_value(x, dtype_info):
    if x > dtype_info.max:
        return dtype_info.max
    if x < dtype_info.min:
        return dtype_info.min
    return x


@st.composite
def array_values(
    draw,
    *,
    dtype,
    shape,
    abs_smallest_val=None,
    min_value=None,
    max_value=None,
    allow_nan=False,
    allow_subnormal=False,
    allow_inf=False,
    exclude_min=True,
    exclude_max=True,
    large_abs_safety_factor=1.1,
    small_abs_safety_factor=1.1,
    safety_factor_scale="linear",
):
    """Draws a list (of lists) of a given shape containing values of a given data type.

    Parameters
    ----------
    draw
        special function that draws data randomly (but is reproducible) from a given
        data-set (ex. list).
    dtype
        data type of the elements of the list.
    shape
        shape of the required list.
    abs_smallest_val
        sets the absolute smallest value to be generated for float data types,
        this has no effect on integer data types. If none, the default data type
        absolute smallest value is used.
    min_value
        minimum value of elements in the list.
    max_value
        maximum value of elements in the list.
    allow_nan
        if True, allow Nans in the list.
    allow_subnormal
        if True, allow subnormals in the list.
    allow_inf
        if True, allow inf in the list.
    exclude_min
        if True, exclude the minimum limit.
    exclude_max
        if True, exclude the maximum limit.
    large_abs_safety_factor
        A safety factor of 1 means that all values are included without limitation,

        when a "linear" safety factor scaler is used,  a safety factor of 2 means
        that only 50% of the range is included, a safety factor of 3 means that
        only 33% of the range is included etc.

        when a "log" safety factor scaler is used, a data type with maximum
        value of 2^32 and a safety factor of 2 transforms the maximum to 2^16.
    small_abs_safety_factor
        A safety factor of 1 means that all values are included without limitation,
        this has no effect on integer data types.

        when a "linear" safety factor scaler is used, a data type with minimum
        representable number of 0.0001 and a safety factor of 2 transforms the
        minimum to 0.0002, a safety factor of 3 transforms the minimum to 0.0003 etc.

        when a "log" safety factor scaler is used, a data type with minimum
        representable number of 0.5 * 2^-16 and a safety factor of 2 transforms the
        minimum to 0.5 * 2^-8, a safety factor of 3 transforms the minimum to 0.5 * 2^-4
    safety_factor_scale
        The operation to use when calculating the maximum value of the list. Can be
        "linear" or "log". Default value = "linear".

    In the case of min_value or max_value is not in the valid range
    the invalid value will be replaced by data type limit, the range
    of the numbers in that case is not preserved.

    Returns
    -------
        A strategy that draws a list.
    """
    assert small_abs_safety_factor >= 1, "small_abs_safety_factor must be >= 1"
    assert large_abs_safety_factor >= 1, "large_value_safety_factor must be >= 1"

    size = 1
    if isinstance(shape, int):
        size = shape
    else:
        for dim in shape:
            size *= dim

    if isinstance(dtype, st._internal.SearchStrategy):
        dtype = draw(dtype)
        dtype = dtype[0] if isinstance(dtype, list) else draw(dtype)

    if "float" in dtype:
        kind_dtype = "float"
        dtype_info = ivy.finfo(dtype)
    elif "int" in dtype:
        kind_dtype = "int"
        dtype_info = ivy.iinfo(dtype)
    elif "bool" in dtype:
        kind_dtype = "bool"
    else:
        raise TypeError(
            f"{dtype} is not a valid data type that can be generated,"
            f" only integers, floats and booleans are allowed."
        )

    if kind_dtype != "bool":
        if min_value is None:
            min_value = dtype_info.min
            b_scale_min = True
        else:
            min_value = _clamp_value(min_value, dtype_info)
            b_scale_min = False

        if max_value is None:
            max_value = dtype_info.max
            b_scale_max = True
        else:
            max_value = _clamp_value(max_value, dtype_info)
            b_scale_max = False

        assert max_value >= min_value

        # Scale the values
        if safety_factor_scale == "linear":
            if b_scale_min:
                min_value = min_value / large_abs_safety_factor
            if b_scale_max:
                max_value = max_value / large_abs_safety_factor
            if kind_dtype == "float" and not abs_smallest_val:
                abs_smallest_val = dtype_info.smallest_normal * small_abs_safety_factor
        elif safety_factor_scale == "log":
            if b_scale_min:
                min_sign = math.copysign(1, min_value)
                min_value = abs(min_value) ** (1 / large_abs_safety_factor) * min_sign
            if b_scale_max:
                max_sign = math.copysign(1, max_value)
                max_value = abs(max_value) ** (1 / large_abs_safety_factor) * max_sign
            if kind_dtype == "float" and not abs_smallest_val:
                m, e = math.frexp(dtype_info.smallest_normal)
                abs_smallest_val = m * (2 ** (e / small_abs_safety_factor))
        else:
            raise ValueError(
                f"{safety_factor_scale} is not a valid safety factor scale."
                f" use 'log' or 'linear'."
            )

        if kind_dtype == "int":
            if exclude_min:
                min_value += 1
            if exclude_max:
                max_value -= 1
            values = draw(
                list_of_length(
                    x=st.integers(int(min_value), int(max_value)), length=size
                )
            )
        elif kind_dtype == "float":
            floats_info = {
                "float16": {"cast_type": "float16", "width": 16},
                "bfloat16": {"cast_type": "float32", "width": 32},
                "float32": {"cast_type": "float32", "width": 32},
                "float64": {"cast_type": "float64", "width": 64},
            }
            # The smallest possible value is determined by one of the arguments
            if min_value > -abs_smallest_val or max_value < abs_smallest_val:
                float_strategy = st.floats(
                    # Using np.array to assert that value
                    # can be represented of compatible width.
                    min_value=np.array(
                        min_value, dtype=floats_info[dtype]["cast_type"]
                    ).tolist(),
                    max_value=np.array(
                        max_value, dtype=floats_info[dtype]["cast_type"]
                    ).tolist(),
                    allow_nan=allow_nan,
                    allow_subnormal=allow_subnormal,
                    allow_infinity=allow_inf,
                    width=floats_info[dtype]["width"],
                    exclude_min=exclude_min,
                    exclude_max=exclude_max,
                )
            else:
                float_strategy = st.one_of(
                    st.floats(
                        min_value=np.array(
                            min_value, dtype=floats_info[dtype]["cast_type"]
                        ).tolist(),
                        max_value=np.array(
                            -abs_smallest_val, dtype=floats_info[dtype]["cast_type"]
                        ).tolist(),
                        allow_nan=allow_nan,
                        allow_subnormal=allow_subnormal,
                        allow_infinity=allow_inf,
                        width=floats_info[dtype]["width"],
                        exclude_min=exclude_min,
                        exclude_max=exclude_max,
                    ),
                    st.floats(
                        min_value=np.array(
                            abs_smallest_val, dtype=floats_info[dtype]["cast_type"]
                        ).tolist(),
                        max_value=np.array(
                            max_value, dtype=floats_info[dtype]["cast_type"]
                        ).tolist(),
                        allow_nan=allow_nan,
                        allow_subnormal=allow_subnormal,
                        allow_infinity=allow_inf,
                        width=floats_info[dtype]["width"],
                        exclude_min=exclude_min,
                        exclude_max=exclude_max,
                    ),
                )
            values = draw(
                list_of_length(
                    x=float_strategy,
                    length=size,
                )
            )
    else:
        values = draw(list_of_length(x=st.booleans(), length=size))

    array = np.asarray(values, dtype=dtype)
    if isinstance(shape, (tuple, list)):
        return array.reshape(shape)
    return np.asarray(array)


#      From array-api repo     #
# ---------------------------- #


def _broadcast_shapes(shape1, shape2):
    """Broadcasts `shape1` and `shape2`"""
    N1 = len(shape1)
    N2 = len(shape2)
    N = max(N1, N2)
    shape = [None for _ in range(N)]
    i = N - 1
    while i >= 0:
        n1 = N1 - N + i
        if N1 - N + i >= 0:
            d1 = shape1[n1]
        else:
            d1 = 1
        n2 = N2 - N + i
        if N2 - N + i >= 0:
            d2 = shape2[n2]
        else:
            d2 = 1

        if d1 == 1:
            shape[i] = d2
        elif d2 == 1:
            shape[i] = d1
        elif d1 == d2:
            shape[i] = d1
        else:
            raise Exception("Broadcast error")

        i = i - 1

    return tuple(shape)


# from array-api repo
def broadcast_shapes(*shapes):
    if len(shapes) == 0:
        raise ValueError("shapes=[] must be non-empty")
    elif len(shapes) == 1:
        return shapes[0]
    result = _broadcast_shapes(shapes[0], shapes[1])
    for i in range(2, len(shapes)):
        result = _broadcast_shapes(result, shapes[i])
    return result


# np.prod and others have overflow and math.prod is Python 3.8+ only
def prod(seq):
    return reduce(mul, seq, 1)


# from array-api repo
def mutually_broadcastable_shapes(
    num_shapes: int,
    *,
    base_shape=(),
    min_dims: int = 1,
    max_dims: int = 4,
    min_side: int = 1,
    max_side: int = 4,
):
    if max_dims is None:
        max_dims = min(max(len(base_shape), min_dims) + 5, 32)
    if max_side is None:
        max_side = max(base_shape[-max_dims:] + (min_side,)) + 5
    return (
        nph.mutually_broadcastable_shapes(
            num_shapes=num_shapes,
            base_shape=base_shape,
            min_dims=min_dims,
            max_dims=max_dims,
            min_side=min_side,
            max_side=max_side,
        )
        .map(lambda BS: BS.input_shapes)
        .filter(lambda shapes: all(prod(i for i in s if i > 0) < 1000 for s in shapes))
    )


@st.composite
def array_and_broadcastable_shape(draw, dtype):
    """Returns an array and a shape that the array can be broadcast to"""
    in_shape = draw(nph.array_shapes(min_dims=1, max_dims=4))
    x = draw(nph.arrays(shape=in_shape, dtype=dtype))
    to_shape = draw(
        mutually_broadcastable_shapes(1, base_shape=in_shape)
        .map(lambda S: S[0])
        .filter(lambda s: broadcast_shapes(in_shape, s) == s),
        label="shape",
    )
    return x, to_shape
