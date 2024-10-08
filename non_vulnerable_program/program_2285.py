from numpy.lib._iotools import _is_string_like

_check_fill_value = np.ma.core._check_fill_value

__all__ = ['append_fields',
           'drop_fields',
           'find_duplicates',
           'get_fieldstructure',
           'join_by',
           'merge_arrays',
           'rec_append_fields', 'rec_drop_fields', 'rec_join',
           'recursive_fill_fields', 'rename_fields',
           'stack_arrays',
           ]


def recursive_fill_fields(input, output):
    """
    Fills fields from output with fields from input,
    with support for nested structures.

    Parameters
    ----------
    input : ndarray
        Input array.
    output : ndarray
        Output array.

    Notes
    -----
    * `output` should be at least the same size as `input`

    Examples
    --------
    >>> a = np.array([(1, 10.), (2, 20.)], dtype=[('A', int), ('B', float)])
    >>> b = np.zeros((3,), dtype=a.dtype)
    >>> recursive_fill_fields(a, b)
    np.array([(1, 10.), (2, 20.), (0, 0.)], dtype=[('A', int), ('B', float)])

    """
    newdtype = output.dtype
    for field in newdtype.names:
        try:
            current = input[field]
        except ValueError:
            continue
        if current.dtype.names:
            recursive_fill_fields(current, output[field])
        else:
            output[field][:len(current)] = current
    return output



def get_names(adtype):
    """
    Returns the field names of the input datatype as a tuple.

    Parameters
    ----------
    adtype : dtype
        Input datatype

    Examples
    --------
    >>> get_names(np.empty((1,), dtype=int)) is None
    True
    >>> get_names(np.empty((1,), dtype=[('A',int), ('B', float)]))
    ('A', 'B')
    >>> adtype = np.dtype([('a', int), ('b', [('ba', int), ('bb', int)])])
    >>> get_names(adtype)
    ('a', ('b', ('ba', 'bb')))
    """
    listnames = []
    names = adtype.names
    for name in names:
        current = adtype[name]
        if current.names:
            listnames.append((name, tuple(get_names(current))))
        else:
            listnames.append(name)
    return tuple(listnames) or None


def get_names_flat(adtype):
    """
    Returns the field names of the input datatype as a tuple. Nested structure
    are flattend beforehand.

    Parameters
    ----------
    adtype : dtype
        Input datatype

    Examples
    --------
    >>> get_names_flat(np.empty((1,), dtype=int)) is None
    True
    >>> get_names_flat(np.empty((1,), dtype=[('A',int), ('B', float)]))
    ('A', 'B')
    >>> adtype = np.dtype([('a', int), ('b', [('ba', int), ('bb', int)])])
    >>> get_names_flat(adtype)
    ('a', 'b', 'ba', 'bb')
    """
    listnames = []
    names = adtype.names
    for name in names:
        listnames.append(name)
        current = adtype[name]
        if current.names:
            listnames.extend(get_names_flat(current))
    return tuple(listnames) or None


def flatten_descr(ndtype):
    """
    Flatten a structured data-type description.

    Examples
    --------
    >>> ndtype = np.dtype([('a', '<i4'), ('b', [('ba', '<f8'), ('bb', '<i4')])])
    >>> flatten_descr(ndtype)
    (('a', dtype('int32')), ('ba', dtype('float64')), ('bb', dtype('int32')))

    """
    names = ndtype.names
    if names is None:
        return ndtype.descr
    else:
        descr = []
        for field in names:
            (typ, _) = ndtype.fields[field]
            if typ.names:
                descr.extend(flatten_descr(typ))
            else:
                descr.append((field, typ))
        return tuple(descr)


def zip_descr(seqarrays, flatten=False):
    """
    Combine the dtype description of a series of arrays.

    Parameters
    ----------
    seqarrays : sequence of arrays
        Sequence of arrays
    flatten : {boolean}, optional
        Whether to collapse nested descriptions.
    """
    newdtype = []
    if flatten:
        for a in seqarrays:
            newdtype.extend(flatten_descr(a.dtype))
    else:
        for a in seqarrays:
            current = a.dtype
            names = current.names or ()
            if len(names) > 1:
                newdtype.append(('', current.descr))
            else:
                newdtype.extend(current.descr)
    return np.dtype(newdtype).descr


def get_fieldstructure(adtype, lastname=None, parents=None,):
    """
    Returns a dictionary with fields as keys and a list of parent fields as values.

    This function is used to simplify access to fields nested in other fields.

    Parameters
    ----------
    adtype : np.dtype
        Input datatype
    lastname : optional
        Last processed field name (used internally during recursion).
    parents : dictionary
        Dictionary of parent fields (used interbally during recursion).

    Examples
    --------
    >>> ndtype =  np.dtype([('A', int), 
    ...                     ('B', [('BA', int),
    ...                            ('BB', [('BBA', int), ('BBB', int)])])])
    >>> get_fieldstructure(ndtype)
    {'A': [], 'B': [], 'BA': ['B'], 'BB': ['B'],
     'BBA': ['B', 'BB'], 'BBB': ['B', 'BB']}
    
    """
    if parents is None:
        parents = {}
    names = adtype.names
    for name in names:
        current = adtype[name]
        if current.names:
            if lastname:
                parents[name] = [lastname,]
            else:
                parents[name] = []
            parents.update(get_fieldstructure(current, name, parents))
        else:
            lastparent = [_ for _ in (parents.get(lastname, []) or [])]
            if lastparent:
#                if (lastparent[-1] != lastname):
                    lastparent.append(lastname)
            elif lastname:
                lastparent = [lastname,]
            parents[name] = lastparent or []
    return parents or None


def _izip_fields_flat(iterable):
    """
    Returns an iterator of concatenated fields from a sequence of arrays,
    collapsing any nested structure.
    """
    for element in iterable:
        if isinstance(element, np.void):
            for f in _izip_fields_flat(tuple(element)):
                yield f
        else:
            yield element


def _izip_fields(iterable):
    """
    Returns an iterator of concatenated fields from a sequence of arrays.
    """
    for element in iterable:
        if hasattr(element, '__iter__') and not isinstance(element, basestring):
            for f in _izip_fields(element):
                yield f
        elif isinstance(element, np.void) and len(tuple(element)) == 1:
            for f in _izip_fields(element):
                yield f
        else:
            yield element


def izip_records(seqarrays, fill_value=None, flatten=True):
    """
    Returns an iterator of concatenated items from a sequence of arrays.

    Parameters
    ----------
    seqarray : sequence of arrays
        Sequence of arrays.
    fill_value : {None, integer}
        Value used to pad shorter iterables.
    flatten : {True, False}, 
        Whether to 
    """
    # OK, that's a complete ripoff from Python2.6 itertools.izip_longest
    def sentinel(counter = ([fill_value]*(len(seqarrays)-1)).pop):
        "Yields the fill_value or raises IndexError"
        yield counter()
    #
    fillers = iterrepeat(fill_value)
    iters = [iterchain(it, sentinel(), fillers) for it in seqarrays] 
    # Should we flatten the items, or just use a nested approach
    if flatten:
        zipfunc = _izip_fields_flat
    else:
        zipfunc = _izip_fields
    #
    try:
        for tup in iterizip(*iters):
            yield tuple(zipfunc(tup))
    except IndexError:
        pass


def _fix_output(output, usemask=True, asrecarray=False):
    """
    Private function: return a recarray, a ndarray, a MaskedArray
    or a MaskedRecords depending on the input parameters
    """
    if not isinstance(output, MaskedArray):
        usemask = False
    if usemask:
        if asrecarray:
            output = output.view(MaskedRecords)
    else:
        output = ma.filled(output)
        if asrecarray:
            output = output.view(recarray)
    return output


def _fix_defaults(output, defaults=None):
    """
    Update the fill_value and masked data of `output`
    from the default given in a dictionary defaults.
    """
    names = output.dtype.names
    (data, mask, fill_value) = (output.data, output.mask, output.fill_value)
    for (k, v) in (defaults or {}).iteritems():
        if k in names:
            fill_value[k] = v
            data[k][mask[k]] = v
    return output


def merge_arrays(seqarrays,
                 fill_value=-1, flatten=False, usemask=True, asrecarray=False):
    """
    Merge arrays field by field.

    Parameters
    ----------
    seqarrays : sequence of ndarrays
        Sequence of arrays
    fill_value : {float}, optional
        Filling value used to pad missing data on the shorter arrays.
    flatten : {False, True}, optional
        Whether to collapse nested fields.
    usemask : {False, True}, optional
        Whether to return a masked array or not.
    asrecarray : {False, True}, optional
        Whether to return a recarray (MaskedRecords) or not.

    Examples
    --------
    >>> merge_arrays((np.array([1, 2]), np.array([10., 20., 30.])))
    masked_array(data = [(1, 10.0) (2, 20.0) (--, 30.0)],
          mask = [(False, False) (False, False) (True, False)],
          fill_value=(999999, 1e+20)
          dtype=[('f0', '<i4'), ('f1', '<f8')])
    >>> merge_arrays((np.array([1, 2]), np.array([10., 20., 30.])),
    ...              usemask=False)
    array(data = [(1, 10.0) (2, 20.0) (-1, 30.0)],
          dtype=[('f0', '<i4'), ('f1', '<f8')])
    >>> merge_arrays((np.array([1, 2]).view([('a', int)]),
                      np.array([10., 20., 30.])),
                     usemask=False, asrecarray=True)
    rec.array(data = [(1, 10.0) (2, 20.0) (-1, 30.0)],
              dtype=[('a', int), ('f1', '<f8')])
    """
    if (len(seqarrays) == 1):
        seqarrays = seqarrays[0]
    if isinstance(seqarrays, ndarray):
        seqdtype = seqarrays.dtype
        if (not flatten) or \
           (zip_descr((seqarrays,), flatten=True) == seqdtype.descr):
            seqarrays = seqarrays.ravel()
            if not seqdtype.names:
                seqarrays = seqarrays.view([('', seqdtype)])
            if usemask:
                if asrecarray:
                    return seqarrays.view(MaskedRecords)
                return seqarrays.view(MaskedArray)
            elif asrecarray:
                return seqarrays.view(recarray)
            return seqarrays
        else:
            seqarrays = (seqarrays,)
    # Get the dtype
    newdtype = zip_descr(seqarrays, flatten=flatten)
    # Get the data and the fill_value from each array
    seqdata = [ma.getdata(a.ravel()) for a in seqarrays]
    seqmask = [ma.getmaskarray(a).ravel() for a in seqarrays]
    fill_value = [_check_fill_value(fill_value, a.dtype) for a in seqdata]
    # Make an iterator from each array, padding w/ fill_values
    maxlength = max(len(a) for a in seqarrays)
    for (i, (a, m, fval)) in enumerate(zip(seqdata, seqmask, fill_value)):
        # Flatten the fill_values if there's only one field
        if isinstance(fval, (ndarray, np.void)):
            fmsk = ma.ones((1,), m.dtype)[0]
            if len(fval.dtype) == 1:
                fval = fval.item()[0]
                fmsk = True
            else:
                # fval and fmsk should be np.void objects
                fval = np.array([fval,], dtype=a.dtype)[0]
#                fmsk = np.array([fmsk,], dtype=m.dtype)[0]
        else:
            fmsk = True
        nbmissing = (maxlength-len(a))
        seqdata[i] = iterchain(a, [fval]*nbmissing)
        seqmask[i] = iterchain(m, [fmsk]*nbmissing)
    #
    data = izip_records(seqdata, flatten=flatten)
    data = tuple(data)
    if usemask:
        mask = izip_records(seqmask, fill_value=True, flatten=flatten)
        mask = tuple(mask)
        output = ma.array(np.fromiter(data, dtype=newdtype))
        output._mask[:] = list(mask)
        if asrecarray:
            output = output.view(MaskedRecords)
    else:
        output = np.fromiter(data, dtype=newdtype)
        if asrecarray:
            output = output.view(recarray)
    return output



def drop_fields(base, drop_names, usemask=True, asrecarray=False):
    """
    Return a new array with fields in `drop_names` dropped.

    Nested fields are supported.

    Parameters
    ----------
    base : array
        Input array
    drop_names : string or sequence
        String or sequence of strings corresponding to the names of the fields
        to drop.
    usemask : {False, True}, optional
        Whether to return a masked array or not.
    asrecarray : string or sequence
        Whether to return a recarray or a mrecarray (`asrecarray=True`) or
        a plain ndarray or masked array with flexible dtype (`asrecarray=False`)

    Examples
    --------
    >>> a = np.array([(1, (2, 3.0)), (4, (5, 6.0))],
                     dtype=[('a', int), ('b', [('ba', float), ('bb', int)])])
    >>> drop_fields(a, 'a')
    array([((2.0, 3),), ((5.0, 6),)], 
          dtype=[('b', [('ba', '<f8'), ('bb', '<i4')])])
    >>> drop_fields(a, 'ba')
    array([(1, (3,)), (4, (6,))], 
          dtype=[('a', '<i4'), ('b', [('bb', '<i4')])])
    >>> drop_fields(a, ['ba', 'bb'])
    array([(1,), (4,)], 
          dtype=[('a', '<i4')])
    """
    if _is_string_like(drop_names):
        drop_names = [drop_names,]
    else:
        drop_names = set(drop_names)
    #
    def _drop_descr(ndtype, drop_names):
        names = ndtype.names
        newdtype = []
        for name in names:
            current = ndtype[name]
            if name in drop_names:
                continue
            if current.names:
                descr = _drop_descr(current, drop_names)
                if descr:
                    newdtype.append((name, descr))
            else:
                newdtype.append((name, current))
        return newdtype
    #
    newdtype = _drop_descr(base.dtype, drop_names)
    if not newdtype:
        return None
    #
    output = np.empty(base.shape, dtype=newdtype)
    output = recursive_fill_fields(base, output)
    return _fix_output(output, usemask=usemask, asrecarray=asrecarray)


def rec_drop_fields(base, drop_names):
    """
    Returns a new numpy.recarray with fields in `drop_names` dropped.
    """
    return drop_fields(base, drop_names, usemask=False, asrecarray=True)



def rename_fields(base, namemapper):
    """
    Rename the fields from a flexible-datatype ndarray or recarray.

    Nested fields are supported.

    Parameters
    ----------
    base : ndarray
        Input array whose fields must be modified.
    namemapper : dictionary
        Dictionary mapping old field names to their new version.

    Examples
    --------
    >>> a = np.array([(1, (2, [3.0, 30.])), (4, (5, [6.0, 60.]))],
                      dtype=[('a', int),
                             ('b', [('ba', float), ('bb', (float, 2))])])
    >>> rename_fields(a, {'a':'A', 'bb':'BB'})
    array([(1, (2.0, 3)), (4, (5.0, 6))], 
          dtype=[('A', '<i4'), ('b', [('ba', '<f8'), ('BB', '<i4')])])

    """
    def _recursive_rename_fields(ndtype, namemapper):
        newdtype = []
        for name in ndtype.names:
            newname = namemapper.get(name, name)
            current = ndtype[name]
            if current.names:
                newdtype.append((newname,
                                 _recursive_rename_fields(current, namemapper)))
            else:
                newdtype.append((newname, current))
        return newdtype
    newdtype = _recursive_rename_fields(base.dtype, namemapper)
    return base.view(newdtype)


def append_fields(base, names, data=None, dtypes=None, 
                  fill_value=-1, usemask=True, asrecarray=False):
    """
    Add new fields to an existing array.

    The names of the fields are given with the `names` arguments,
    the corresponding values with the `data` arguments.
    If a single field is appended, `names`, `data` and `dtypes` do not have
    to be lists but just values.

    Parameters
    ----------
    base : array
        Input array to extend.
    names : string, sequence
        String or sequence of strings corresponding to the names
        of the new fields.
    data : array or sequence of arrays
        Array or sequence of arrays storing the fields to add to the base.
    dtypes : sequence of datatypes
        Datatype or sequence of datatypes.
        If None, the datatypes are estimated from the `data`.
    fill_value : {float}, optional
        Filling value used to pad missing data on the shorter arrays.
    usemask : {False, True}, optional
        Whether to return a masked array or not.
    asrecarray : {False, True}, optional
        Whether to return a recarray (MaskedRecords) or not.

    """
    # Check the names
    if isinstance(names, (tuple, list)):
        if len(names) != len(data):
            err_msg = "The number of arrays does not match the number of names"
            raise ValueError(err_msg)
    elif isinstance(names, basestring):
        names = [names,]
        data = [data,]
    #
    if dtypes is None:
        data = [np.array(a, copy=False, subok=True) for a in data]
        data = [a.view([(name, a.dtype)]) for (name, a) in zip(names, data)]
    elif not hasattr(dtypes, '__iter__'):
        dtypes = [dtypes,]
        if len(data) != len(dtypes):
            if len(dtypes) == 1:
                dtypes = dtypes * len(data)
            else:
                msg = "The dtypes argument must be None, "\
                      "a single dtype or a list."
                raise ValueError(msg)
        data = [np.array(a, copy=False, subok=True, dtype=d).view([(n, d)])
                for (a, n, d) in zip(data, names, dtypes)]
    #
    base = merge_arrays(base, usemask=usemask, fill_value=fill_value)
    if len(data) > 1:
        data = merge_arrays(data, flatten=True, usemask=usemask,
                            fill_value=fill_value)
    else:
        data = data.pop()
    #
    output = ma.masked_all(max(len(base), len(data)),
                           dtype=base.dtype.descr + data.dtype.descr)
    output = recursive_fill_fields(base, output)
    output = recursive_fill_fields(data, output)
    #
    return _fix_output(output, usemask=usemask, asrecarray=asrecarray)



def rec_append_fields(base, names, data, dtypes=None):
    """
    Add new fields to an existing array.

    The names of the fields are given with the `names` arguments,
    the corresponding values with the `data` arguments.
    If a single field is appended, `names`, `data` and `dtypes` do not have
    to be lists but just values.
    
    Parameters
    ----------
    base : array
        Input array to extend.
    names : string, sequence
        String or sequence of strings corresponding to the names
        of the new fields.
    data : array or sequence of arrays
        Array or sequence of arrays storing the fields to add to the base.
    dtypes : sequence of datatypes, optional
        Datatype or sequence of datatypes.
        If None, the datatypes are estimated from the `data`.
    
    See Also
    --------
    append_fields

    Returns
    -------
    appended_array : np.recarray
    """
    return append_fields(base, names, data=data, dtypes=dtypes,
                         asrecarray=True, usemask=False)



def stack_arrays(arrays, defaults=None, usemask=True, asrecarray=False):
    """
    Superposes arrays fields by fields

    Parameters
    ----------
    seqarrays : array or sequence
        Sequence of input arrays.
    defaults : dictionary, optional
        Dictionary mapping field names to the corresponding default values.
    usemask : {True, False}, optional
        Whether to return a MaskedArray (or MaskedRecords is `asrecarray==True`)
        or a ndarray.
    asrecarray : {False, True}, optional
        Whether to return a recarray (or MaskedRecords if `usemask==True`) or
        just a flexible-type ndarray.

    Examples
    --------
    >>> x = np.array([1, 2,])
    >>> stack_arrays(x) is x
    True
    >>> z = np.array([('A', 1), ('B', 2)], dtype=[('A', '|S3'), ('B', float)])
    >>> zz = np.array([('a', 10., 100.), ('b', 20., 200.), ('c', 30., 300.)],
                      dtype=[('A', '|S3'), ('B', float), ('C', float)])
    >>> test = stack_arrays((z,zz))
    >>> masked_array(data = [('A', 1.0, --) ('B', 2.0, --) ('a', 10.0, 100.0)
    ... ('b', 20.0, 200.0) ('c', 30.0, 300.0)],
    ...       mask = [(False, False, True) (False, False, True) (False, False, False)
    ... (False, False, False) (False, False, False)],
    ...       fill_value=('N/A', 1e+20, 1e+20)
    ...       dtype=[('A', '|S3'), ('B', '<f8'), ('C', '<f8')])

    """
    if isinstance(arrays, ndarray):
        return arrays
    elif len(arrays) == 1:
        return arrays[0]
    seqarrays = [np.asanyarray(a).ravel() for a in arrays]
    nrecords = [len(a) for a in seqarrays]
    ndtype = [a.dtype for a in seqarrays]
    fldnames = [d.names for d in ndtype]
    #
    dtype_l = ndtype[0]
    newdescr = dtype_l.descr
    names = list(dtype_l.names or ()) or ['']
    for dtype_n in ndtype[1:]:
        for descr in dtype_n.descr:
            name = descr[0] or ''
            if name not in names:
                newdescr.append(descr)
                names.append(name)
            elif descr[1] != dict(newdescr)[name]:
                raise TypeError("Incompatible type '%s' <> '%s'" %\
                                (dict(newdescr)[name], descr[1]))
    # Only one field: use concatenate
    if len(newdescr) == 1:
        output = ma.concatenate(seqarrays)
    else:
        #
        output = ma.masked_all((np.sum(nrecords),), newdescr)
        offset = np.cumsum(np.r_[0, nrecords])
        seen = []
        for (a, n, i, j) in zip(seqarrays, fldnames, offset[:-1], offset[1:]):
            names = a.dtype.names
            if names is None:
                output['f%i' % len(seen)][i:j] = a
            else:
                for name in n:
                    output[name][i:j] = a[name]
                    if name not in seen:
                        seen.append(name)
    #
    return _fix_output(_fix_defaults(output, defaults),
                       usemask=usemask, asrecarray=asrecarray)



def find_duplicates(a, key=None, ignoremask=True, return_index=False):
    """
    Find the duplicates in a structured array along a given key

    Parameters
    ----------
    a : array-like
        Input array
    key : {string, None}, optional
        Name of the fields along which to check the duplicates.
        If None, the search is performed by records
    ignoremask : {True, False}, optional
        Whether masked data should be discarded or considered as duplicates.
    return_index : {False, True}, optional
        Whether to return the indices of the duplicated values.

    Examples
    --------
    >>> ndtype = [('a', int)]
    >>> a = ma.array([1, 1, 1, 2, 2, 3, 3], 
    ...         mask=[0, 0, 1, 0, 0, 0, 1]).view(ndtype)
    >>> find_duplicates(a, ignoremask=True, return_index=True)
    """
    a = np.asanyarray(a).ravel()
    # Get a dictionary of fields
    fields = get_fieldstructure(a.dtype)
    # Get the sorting data (by selecting the corresponding field)
    base = a
    if key:
        for f in fields[key]:
            base = base[f]
        base = base[key]
    # Get the sorting indices and the sorted data
    sortidx = base.argsort()
    sortedbase = base[sortidx]
    sorteddata = sortedbase.filled()
    # Compare the sorting data
    flag = (sorteddata[:-1] == sorteddata[1:])
    # If masked data must be ignored, set the flag to false where needed
    if ignoremask:
        sortedmask = sortedbase.recordmask
        flag[sortedmask[1:]] = False
    flag = np.concatenate(([False], flag))
    # We need to take the point on the left as well (else we're missing it)
    flag[:-1] = flag[:-1] + flag[1:]
    duplicates = a[sortidx][flag]
    if return_index:
        return (duplicates, sortidx[flag])
    else:
        return duplicates



def join_by(key, r1, r2, jointype='inner', r1postfix='1', r2postfix='2',
                defaults=None, usemask=True, asrecarray=False):
    """
    Join arrays `r1` and `r2` on key `key`.

    The key should be either a string or a sequence of string corresponding
    to the fields used to join the array.
    An exception is raised if the `key` field cannot be found in the two input
    arrays.
    Neither `r1` nor `r2` should have any duplicates along `key`: the presence
    of duplicates will make the output quite unreliable. Note that duplicates
    are not looked for by the algorithm.

    Parameters
    ----------
    key : {string, sequence}
        A string or a sequence of strings corresponding to the fields used
        for comparison.
    r1, r2 : arrays
        Structured arrays.
    jointype : {'inner', 'outer', 'leftouter'}, optional
        If 'inner', returns the elements common to both r1 and r2.
        If 'outer', returns the common elements as well as the elements of r1
        not in r2 and the elements of not in r2.
        If 'leftouter', returns the common elements and the elements of r1 not
        in r2.
    r1postfix : string, optional
        String appended to the names of the fields of r1 that are present in r2
        but absent of the key.
    r2postfix : string, optional
        String appended to the names of the fields of r2 that are present in r1
        but absent of the key.
    defaults : {dictionary}, optional
        Dictionary mapping field names to the corresponding default values.
    usemask : {True, False}, optional
        Whether to return a MaskedArray (or MaskedRecords is `asrecarray==True`)
        or a ndarray.
    asrecarray : {False, True}, optional
        Whether to return a recarray (or MaskedRecords if `usemask==True`) or
        just a flexible-type ndarray.

    Notes
    -----
    * The output is sorted along the key.
    * A temporary array is formed by dropping the fields not in the key for the
      two arrays and concatenating the result. This array is then sorted, and
      the common entries selected. The output is constructed by filling the fields
      with the selected entries. Matching is not preserved if there are some
      duplicates...

    """
    # Check jointype
    if jointype not in ('inner', 'outer', 'leftouter'):
        raise ValueError("The 'jointype' argument should be in 'inner', "\
                         "'outer' or 'leftouter' (got '%s' instead)" % jointype)
    # If we have a single key, put it in a tuple
    if isinstance(key, basestring):
        key = (key, )

    # Check the keys
    for name in key:
        if name not in r1.dtype.names:
            raise ValueError('r1 does not have key field %s'%name)
        if name not in r2.dtype.names:
            raise ValueError('r2 does not have key field %s'%name)

    # Make sure we work with ravelled arrays
    r1 = r1.ravel()
    r2 = r2.ravel()
    (nb1, nb2) = (len(r1), len(r2))
    (r1names, r2names) = (r1.dtype.names, r2.dtype.names)

    # Make temporary arrays of just the keys
    r1k = drop_fields(r1, [n for n in r1names if n not in key])
    r2k = drop_fields(r2, [n for n in r2names if n not in key])

    # Concatenate the two arrays for comparison
    aux = ma.concatenate((r1k, r2k))
    idx_sort = aux.argsort(order=key)
    aux = aux[idx_sort]
    #
    # Get the common keys
    flag_in = ma.concatenate(([False], aux[1:] == aux[:-1]))
    flag_in[:-1] = flag_in[1:] + flag_in[:-1]
    idx_in = idx_sort[flag_in]
    idx_1 = idx_in[(idx_in < nb1)]
    idx_2 = idx_in[(idx_in >= nb1)] - nb1
    (r1cmn, r2cmn) = (len(idx_1), len(idx_2))
    if jointype == 'inner':
        (r1spc, r2spc) = (0, 0)
    elif jointype == 'outer':
        idx_out = idx_sort[~flag_in]
        idx_1 = np.concatenate((idx_1, idx_out[(idx_out < nb1)]))
        idx_2 = np.concatenate((idx_2, idx_out[(idx_out >= nb1)] - nb1))
        (r1spc, r2spc) = (len(idx_1) - r1cmn, len(idx_2) - r2cmn)
    elif jointype == 'leftouter':
        idx_out = idx_sort[~flag_in]
        idx_1 = np.concatenate((idx_1, idx_out[(idx_out < nb1)]))
        (r1spc, r2spc) = (len(idx_1) - r1cmn, 0)
    # Select the entries from each input
    (s1, s2) = (r1[idx_1], r2[idx_2])
    #
    # Build the new description of the output array .......
    # Start with the key fields
    ndtype = [list(_) for _ in r1k.dtype.descr]
    # Add the other fields
    ndtype.extend(list(_) for _ in r1.dtype.descr if _[0] not in key)
    # Find the new list of names (it may be different from r1names)
    names = list(_[0] for _ in ndtype)
    for desc in r2.dtype.descr:
        desc = list(desc)
        name = desc[0]
        # Have we seen the current name already ?
        if name in names:
            nameidx = names.index(name)
            current = ndtype[nameidx]
            # The current field is part of the key: take the largest dtype
            if name in key:
                current[-1] = max(desc[1], current[-1])
            # The current field is not part of the key: add the suffixes
            else:
                current[0] += r1postfix
                desc[0] += r2postfix
                ndtype.insert(nameidx+1, desc)
        #... we haven't: just add the description to the current list
        else:
            names.extend(desc[0])
            ndtype.append(desc)
    # Revert the elements to tuples
    ndtype = [tuple(_) for _ in ndtype]
    # Find the largest nb of common fields : r1cmn and r2cmn should be equal, but...
    cmn = max(r1cmn, r2cmn)
    # Construct an empty array
    output = ma.masked_all((cmn + r1spc + r2spc,), dtype=ndtype)
    names = output.dtype.names
    for f in r1names:
        selected = s1[f]
        if f not in names:
            f += r1postfix
        current = output[f]
        current[:r1cmn] = selected[:r1cmn]
        if jointype in ('outer', 'leftouter'):
            current[cmn:cmn+r1spc] = selected[r1cmn:]
    for f in r2names:
        selected = s2[f]
        if f not in names:
            f += r2postfix
        current = output[f]
        current[:r2cmn] = selected[:r2cmn]
        if (jointype == 'outer') and r2spc:
            current[-r2spc:] = selected[r2cmn:]
    # Sort and finalize the output
    output.sort(order=key)
    kwargs = dict(usemask=usemask, asrecarray=asrecarray)
    return _fix_output(_fix_defaults(output, defaults), **kwargs)


def rec_join(key, r1, r2, jointype='inner', r1postfix='1', r2postfix='2',
             defaults=None):
    """
    Join arrays `r1` and `r2` on keys.
    Alternative to join_by, that always returns a np.recarray.

    See Also
    --------
    join_by : equivalent function
    """
    kwargs = dict(jointype=jointype, r1postfix=r1postfix, r2postfix=r2postfix,
                  defaults=defaults, usemask=False, asrecarray=True)
    return join_by(key, r1, r2, **kwargs)



