class Filter():
    """
    A filter that can be matched against signatures.

    *New in version 1.3.*
    """

    def __init__(self, single_filter, group_filter):
        self._single_filter = single_filter
        self._group_filter = group_filter

    def __and__(self, other):
        """
        Return a new filter that matches a signature if that signature matches this filter and the other filter.
        """

        single_filter = lambda signature: self._single_filter(signature) and other._single_filter(signature)
        group_filter = lambda archetypemap: self._group_filter(archetypemap) & other._group_filter(archetypemap)
        return Filter(single_filter, group_filter)

    def __or__(self, other):
        """
        Return a new filter that matches a signature if that signature matches this filter or the other filter.
        """

        single_filter = lambda signature: self._single_filter(signature) or other._single_filter(signature)
        group_filter = lambda archetypemap: self._group_filter(archetypemap) | other._group_filter(archetypemap)
        return Filter(single_filter, group_filter)

    def __invert__(self):
        """
        Return a new filter that matches a signature if that signature does not match this filter.
        """

        single_filter = lambda signature: not self._single_filter(signature)
        group_filter = lambda archetypemap: set.union(*archetypemap.values()) - self._group_filter(archetypemap)
        return Filter(single_filter, group_filter)

