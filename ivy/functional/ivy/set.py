# global
from typing import Union, NamedTuple, Optional

# local
import ivy
from ivy.func_wrapper import (
    to_native_arrays_and_back,
    handle_out_argument,
    handle_nestable,
)
from ivy.exceptions import handle_exceptions


# Array API Standard #
# -------------------#


@to_native_arrays_and_back
@handle_nestable
@handle_exceptions
def unique_all(x: Union[ivy.Array, ivy.NativeArray]) -> NamedTuple:
    """Returns the unique elements of an input array ``x``, the first occurring indices
    for each unique element in ``x``, the indices from the set of unique elements that
    reconstruct ``x``, and the corresponding counts for each unique element in ``x``.

    .. admonition:: Data-dependent output shape
        :class: important

        The shapes of two of the output arrays for this function depend on the data
        values in the input array; hence, array libraries which build computation graphs
        (e.g., JAX, Dask, etc.) may find this function difficult to implement without
        knowing array values. Accordingly, such libraries may choose to omit this
        function. See :ref:`data-dependent-output-shapes` section for more details.

    .. note::
       Uniqueness should be determined based on value equality (i.e., ``x_i == x_j``).
       For input arrays having floating-point data types, value-based equality implies
       the following behavior.

       -   As ``nan`` values compare as ``False``, ``nan`` values should be considered
           distinct.

       -   As ``-0`` and ``+0`` compare as ``True``, signed zeros should not be
           considered distinct, and the corresponding unique element will be
           implementation-dependent (e.g., an implementation could choose to return
           ``-0`` if ``-0`` occurs before ``+0``).

       As signed zeros are not distinct, using ``inverse_indices`` to reconstruct the
       input array is not guaranteed to return an array having the exact same values.

       Each ``nan`` value should have a count of one, while the counts for signed zeros
       should be aggregated as a single count.

    Parameters
    ----------
    x
        input array. If ``x`` has more than one dimension, the function must flatten
        ``x`` and return the unique elements of the flattened array.

    Returns
    -------
    ret
        a namedtuple ``(values, indices, inverse_indices, counts)`` whose
        - first element must have the field name ``values`` and must be an array
          containing the unique elements of ``x``. The array must have the same data
          type as ``x``.
        - second element must have the field name ``indices`` and must be an array
          containing the indices (first occurrences) of ``x`` that result in ``values``.
          The array must have the same shape as ``values`` and must have the default
          array index data type.
        - third element must have the field name ``inverse_indices`` and must be an
          array containing the indices of ``values`` that reconstruct ``x``. The array
          must have the same shape as ``x`` and must have the default array index data
          type.
        - fourth element must have the field name ``counts`` and must be an array
          containing the number of times each unique element occurs in ``x``. The
          returned array must have same shape as ``values`` and must have the default
          array index data type.

        .. note::
           The order of unique elements is not specified and may vary between
           implementations.

    This method conforms to the `Array API Standard
    <https://data-apis.org/array-api/latest/>`_. This docstring is an extension of
    the `docstring <https://data-apis.org/array-api/latest/API_specification/
    generated/signatures.elementwise_functions.tan.html>`_
    in the standard. The descriptions above assume an array input for simplicity, but
    the method also accepts :class:`ivy.Container` instances in place of
    :class:`ivy.Array` or :class:`ivy.NativeArray` instances, as shown in the type hints
    and also the examples below.

    Functional Examples
    -------------------

    With :class:`ivy.Array` input:

    >>> x = ivy.random_normal(mean=0.0, std=1.0, shape=(2, 2))
    >>> print(x)
    ivy.array([[0.607,1.14],[0.735,0.667]])ivy.array([0.607,0.667,0.735,1.14])

    >>> values, indices, inverse_indices, counts = ivy.unique_all(x)
    >>> print(values)
    ivy.array([0,3,2,1])ivy.array([[0,3],[2,1]])

    >>> print(indices)
    ivy.array([1,1,1,1])

    >>> print(inverse_indices)
    ivy.array([[1.52,0.381,0.857],[-0.0396,0.14,-0.166],[1.58,-0.828,-0.144]])

    >>> print(counts)
    ivy.array([-0.828,-0.166,-0.144,-0.0396,0.14,0.381,0.857,1.52,1.58])


    >>> x = ivy.random_normal(mean=0.0, std=1.0, shape=(3, 3))
    >>> print(x)
    ivy.array([[-0.40501155,  1.77361575, -1.97776199],
               [-0.36831157,  0.89148434, -0.9512272 ],
               [ 0.67542176, -0.41985657,  0.23478023]])

    >>> values, indices, inverse_indices, counts = ivy.unique_all(x)
    >>> print(values)
    ivy.array([-1.97776199, -0.9512272 , -0.41985657, -0.40501155, -0.36831157,
                0.23478023,  0.67542176,  0.89148434,  1.77361575])

    >>> print(indices)
    ivy.array([2, 5, 7, 0, 3, 8, 6, 4, 1])

    >>> print(inverse_indices)
    ivy.array([[3, 8, 0],
               [4, 7, 1],
               [6, 2, 5]])

    >>> print(counts)
    ivy.array([1, 1, 1, 1, 1, 1, 1, 1, 1])

    With :class:`ivy.NativeArray` input:

    >>> x = ivy.native_array([[ 2.1141,  0.8101,  0.9298,  0.8460],\
    [-1.2119, -0.3519, -0.6252,  0.4033],[ 0.7443,  0.2577, -0.3707, -0.0545],\
    [-0.3238,  0.5944,  0.0775, -0.4327]])
    >>> print(x)
    ivy.array([[ 2.1141,  0.8101,  0.9298,  0.8460],
               [-1.2119, -0.3519, -0.6252,  0.4033],
               [ 0.7443,  0.2577, -0.3707, -0.0545],
               [-0.3238,  0.5944,  0.0775, -0.4327]])

    >>> x[range(4), range(4)] = ivy.nan #Introduce NaN values
    >>> print(x)
    ivy.array([[    nan,  0.8101,  0.9298,  0.8460],
               [-1.2119,     nan, -0.6252,  0.4033],
               [ 0.7443,  0.2577,     nan, -0.0545],
               [-0.3238,  0.5944,  0.0775,     nan]])

    >>> values, indices, inverse_indices, counts = ivy.unique_all(x)
    >>> print(values)
    ivy.array([-1.2119, -0.6252,  0.4033,     nan,     nan,     nan,     nan, -0.3238,
               -0.0545,  0.0775,  0.2577,  0.5944,  0.7443,  0.8101,  0.8460,  0.9298])

    >>> print(indices)
    ivy.array([ 4,  6,  7,  0,  5, 10, 15, 12, 11, 14,  9, 13,  8,  1,  3,  2])

    >>> print(inverse_indices)
    ivy.array([[ 3, 13, 15, 14],
               [ 0,  3,  1,  2],
               [12, 10,  3,  8],
               [ 7, 11,  9,  3]])

    >>> print(counts)
    ivy.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

    Instance Method Examples
    ------------------------

    With :class:`ivy.Array` input:

    >>> x = ivy.array([[ 2.1141,  0.8101,  0.9298,  0.8460],\
    [-1.2119, -0.3519, -0.6252,  0.4033],\
    [ 0.7443,  0.2577, -0.3707, -0.0545],\
    [-0.3238,  0.5944,  0.0775, -0.4327]])
    >>> print(x)
    ivy.array([[ 2.1141,  0.8101,  0.9298,  0.8460],
               [-1.2119, -0.3519, -0.6252,  0.4033],
               [ 0.7443,  0.2577, -0.3707, -0.0545],
               [-0.3238,  0.5944,  0.0775, -0.4327]])

    >>> x[range(4), range(4)] = ivy.nan #Introduce NaN values
    >>> print(x)
    ivy.array([[    nan,  0.8101,  0.9298,  0.8460],
               [-1.2119,     nan, -0.6252,  0.4033],
               [ 0.7443,  0.2577,     nan, -0.0545],
               [-0.3238,  0.5944,  0.0775,     nan]])

    >>> values, indices, inverse_indices, counts = x.unique_all()
    >>> print(values)
    ivy.array([-1.2119, -0.6252,  0.4033,     nan,     nan,     nan,     nan, -0.3238,
               -0.0545,  0.0775,  0.2577,  0.5944,  0.7443,  0.8101,  0.8460,  0.9298])

    >>> print(indices)
    ivy.array([ 4,  6,  7,  0,  5, 10, 15, 12, 11, 14,  9, 13,  8,  1,  3,  2])

    >>> print(inverse_indices)
    ivy.array([[ 3, 13, 15, 14],
               [ 0,  3,  1,  2],
               [12, 10,  3,  8],
               [ 7, 11,  9,  3]])

    >>> print(counts)
    ivy.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

    With :class:`ivy.NativeArray` input:

    >>> x = ivy.native_array([[-2.176,  0.889,  1.175, -0.763],\
    [-0.071,  1.262, -0.456, -2.114],[-0.349,  0.615, -0.594, -1.335],\
    [ 0.212,  0.457, -0.827,  0.209]])
    >>> print(x)
    ivy.array([[-2.176,  0.889,  1.175, -0.763],
               [-0.071,  1.262, -0.456, -2.114],
               [-0.349,  0.615, -0.594, -1.335],
               [ 0.212,  0.457, -0.827,  0.209]])

    >>> x[range(4), range(4)] = ivy.nan #Introduce NaN values
    >>> print(x)
    ivy.array([[   nan,  0.889,  1.175, -0.763],
               [-0.071,    nan, -0.456, -2.114],
               [-0.349,  0.615,    nan, -1.335],
               [ 0.212,  0.457, -0.827,    nan]])

    >>> values, indices, inverse_indices, counts = x.unique_all()
    >>> print(values)
    ivy.array([-2.114, -1.335, -0.827, -0.763, -0.456,
               -0.349, -0.071,  0.212,  0.457,  0.615,
                0.889,  1.175,    nan,    nan,    nan,
                  nan])

    >>> print(indices)
    ivy.array([ 7, 11, 14,  3,  6,  8,  4, 12, 13,  9,  1,  2,  0,  5, 10, 15])

    >>> print(inverse_indices)
    ivy.array([[12, 10, 11,  3],
               [ 6, 12,  4,  0],
               [ 5,  9, 12,  1],
               [ 7,  8,  2, 12]])

    >>> print(counts)
    ivy.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

    """
    return ivy.current_backend(x).unique_all(x)


@to_native_arrays_and_back
@handle_nestable
@handle_exceptions
def unique_inverse(x: Union[ivy.Array, ivy.NativeArray]) -> NamedTuple:
    """Returns the unique elements of an input array ``x``, and the indices from the
     set of unique elements that reconstruct ``x``.

     .. admonition:: Data-dependent output shape
        :class: important

        The shapes of two of the output arrays for this function depend on the data
        values in the input array; hence, array libraries which build computation graphs
        (e.g., JAX, Dask, etc.) may find this function difficult to implement without
        knowing array values. Accordingly, such libraries may choose to omit this
        function. See :ref:`data-dependent-output-shapes` section for more details.

     .. note::
       Uniqueness should be determined based on value equality (i.e., ``x_i == x_j``).
       For input arrays having floating-point data types, value-based equality implies
       the following behavior.

       -   As ``nan`` values compare as ``False``, ``nan`` values should be considered
           distinct.

       -   As ``-0`` and ``+0`` compare as ``True``, signed zeros should not be
           considered distinct, and the corresponding unique element will be
           implementation-dependent (e.g., an implementation could choose to return
           ``-0`` if ``-0`` occurs before ``+0``).

       As signed zeros are not distinct, using ``inverse_indices`` to reconstruct the
       input array is not guaranteed to return an array having the exact same values.


    Parameters
    ----------
    x
        input array. If ``x`` has more than one dimension, the function must flatten
        ``x`` and return the unique elements of the flattened array.

    Returns
    -------
    ret

        a namedtuple ``(values, inverse_indices)`` whose
        - first element must have the field name ``values`` and must be an array
          containing the unique elements of ``x``. The array must have the same data
          type as ``x``.
        - second element must have the field name ``inverse_indices`` and must be an
          array containing the indices of ``values`` that reconstruct ``x``. The array
          must have the same shape as ``x`` and must have the default array index data
          type.

        .. note::
           The order of unique elements is not specified and may vary between
           implementations.

    This method conforms to the `Array API Standard
    <https://data-apis.org/array-api/latest/>`_. This docstring is an extension of
    the `docstring <https://data-apis.org/array-api/latest/API_specification/
    generated/signatures..set_functions.unique_inverse.html>`_
    in the standard. The descriptions above assume an array input for simplicity, but
    the method also accepts :class:`ivy.Container` instances in place of
    :class:`ivy.Array` or :class:`ivy.NativeArray` instances, as shown in the type hints

    Examples
    --------
    With :class:`ivy.Array` input:

    >>> x = ivy.array([4,5,3,2,4,1,3])
    >>> y = ivy.unique_inverse(x)
    >>> print(y)
    unique_inverse(values=ivy.array([1, 2, 3, 4, 5]),
    inverse_indices=ivy.array([3, 4, 2, 1, 3, 0, 2]))

    With :class:`ivy.NativeArray` input:

    >>> x = ivy.native_array([0.5,0.3,0.8,0.2,1.2,2.4,0.3])
    >>> y = ivy.ivy.unique_inverse(x)
    >>> print(y)
    unique_inverse(values=ivy.array([0.2, 0.3, 0.5, 0.8, 1.2, 2.4]),
    inverse_indices=ivy.array([2, 1, 3, 0, 4, 5, 1]))

    With :class:`ivy.Container` input:

    >>> x = ivy.Container(a=ivy.array([1., 4., 3. , 5. , 3. , 7.]), \
                          b=ivy.array([3,2,6,3,7,4,9]))
    >>> y = ivy.ivy.unique_inverse(x)
    >>> print(y)
    {
        a: (list[2], <class ivy.array.array.Array> shape=[5]),
        b: (list[2], <class ivy.array.array.Array> shape=[6])
    }



    """
    return ivy.current_backend(x).unique_inverse(x)


@to_native_arrays_and_back
@handle_out_argument
@handle_nestable
@handle_exceptions
def unique_values(
    x: Union[ivy.Array, ivy.NativeArray],
    /,
    *,
    out: Optional[ivy.Array] = None,
) -> ivy.Array:
    """Returns the unique elements of an input array ``x``.

    .. admonition:: Data-dependent output shape
        :class: important

        The shapes of two of the output arrays for this function depend on the data
        values in the input array; hence, array libraries which build computation graphs
        (e.g., JAX, Dask, etc.) may find this function difficult to implement without
        knowing array values. Accordingly, such libraries may choose to omit this
        function. See :ref:`data-dependent-output-shapes` section for more details.

    .. note::
       Uniqueness should be determined based on value equality (i.e., ``x_i == x_j``).
       For input arrays having floating-point data types, value-based equality implies
       the following behavior.

       -   As ``nan`` values compare as ``False``, ``nan`` values should be considered
           distinct.
       -   As ``-0`` and ``+0`` compare as ``True``, signed zeros should not be
           considered distinct, and the corresponding unique element will be
           implementation-dependent (e.g., an implementation could choose to return
           ``-0`` if ``-0`` occurs before ``+0``).

    Parameters
    ----------
    x
        input array. If ``x`` has more than one dimension, the function must flatten
        ``x`` and return the unique elements of the flattened array.
    out
        optional output array, for writing the result to. It must have a shape that the
        inputs broadcast to.

    Returns
    -------
    ret
        an array containing the set of unique elements in ``x``. The returned array must
        have the same data type as ``x``.

        .. note::
           The order of unique elements is not specified and may vary between
           implementations.

    """
    return ivy.current_backend(x).unique_values(x, out=out)


@to_native_arrays_and_back
@handle_nestable
@handle_exceptions
def unique_counts(x: Union[ivy.Array, ivy.NativeArray]) -> NamedTuple:
    """
    Returns the unique elements of an input array ``x`` and the corresponding counts for
    each unique element in ``x``.

    .. admonition:: Data-dependent output shape
        :class: important

        The shapes of two of the output arrays for this function depend on the data
        values in the input array; hence, array libraries which build computation graphs
        (e.g., JAX, Dask, etc.) may find this function difficult to implement without
        knowing array values. Accordingly, such libraries may choose to omit this
        function. See :ref:`data-dependent-output-shapes` section for more details.

    .. note::
       Uniqueness should be determined based on value equality (i.e., ``x_i == x_j``).
       For input arrays having floating-point data types, value-based equality implies
       the following behavior.

       -   As ``nan`` values compare as ``False``, ``nan`` values should be considered
           distinct.
       -   As ``-0`` and ``+0`` compare as ``True``, signed zeros should not be
           considered distinct, and the corresponding unique element will be
           implementation-dependent (e.g., an implementation could choose to return
           ``-0`` if ``-0`` occurs before ``+0``).

    Parameters
    ----------
    x
        input array. If ``x`` has more than one dimension, the function must flatten
        ``x`` and return the unique elements of the flattened array.

    Returns
    -------
    ret
        a namedtuple ``(values, counts)`` whose

        - first element must have the field name ``values`` and must be an
          array containing the unique elements of ``x``.
          The array must have the same data type as ``x``.
        - second element must have the field name ``counts`` and must be an array
          containing the number of times each unique element occurs in ``x``.
          The returned array must have same shape as ``values`` and must
          have the default array index data type.

    .. note::
           The order of unique elements is not specified and may vary between
           implementations.

    This method conforms to the `Array API Standard
    <https://data-apis.org/array-api/latest/>`. This docstring is an extension of
    the `docstring <https://data-apis.org/array-api/latest/API_specification/
    generated/signatures.set_functions.unique_counts.html>` in the standard.
    The descriptions above assume an array input for simplicity, but
    the method also accepts :class:`ivy.Container` instances in place of
    :class:`ivy.Array` or :class:`ivy.NativeArray` instances, as shown in the type hints
    and also the examples below.

    Examples
    --------
    With :class:`ivy.Array` input:

    >>> x = ivy.array([1,2,1,3,4,1,3])
    >>> y = unique_counts(x)
    >>> print(y)
    Tuple([1,2,3,4],[3,1,2,1])

    >>> x = ivy.asarray([1,2,3,4],[2,3,4,5],[3,4,5,6])
    >>> y = unique_counts(x)
    >>> print(y)
    Tuple([1,2,3,4,5,6],[1,2,3,3,2,1])

    With :class:`ivy.NativeArray` input:

    >>> x = ivy.native_array([0.2,0.3,0.4,0.2,1.4,2.3,0.2])
    >>> y = ivy.unique_counts(x)
    >>> print(y)
    Tuple([0.2,0.3,0.4,1.4,2.3],[3,1,1,1,1]

    With :class:`ivy.Container` input:

    >>> x = ivy.Container(a=ivy.array([0., 1., 3. , 2. , 1. , 0.]), \
                          b=ivy.array([1,2,1,3,4,1,3]))
    >>> y = ivy.unique_counts(x)
    >>> print(y)
    {
        a: (list[2],<classivy.array.array.Array>shape=[4]),
        b: (list[2],<classivy.array.array.Array>shape=[4])
    }
    """
    return ivy.current_backend(x).unique_counts(x)
