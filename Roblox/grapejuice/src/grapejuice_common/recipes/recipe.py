import logging
from abc import ABC
from typing import Callable, Union, List

from grapejuice_common.wine.wineprefix import Wineprefix

log = logging.getLogger(__name__)

RecipeIndicator = Callable[[Wineprefix], bool]
RecipeIndicatorList = List[RecipeIndicator]


class CannotMakeRecipe(RuntimeError):
    ...


class Recipe(ABC):
    _indicators: RecipeIndicatorList

    def __init__(self, indicators: Union[RecipeIndicatorList, None] = None):
        self._indicators = indicators or []

    def _run_indicators(self, prefix: Wineprefix) -> bool:
        results = list(map(lambda fn: fn(prefix), self._indicators))
        v = all(results)

        return v

    def exists_in(self, prefix: Wineprefix) -> bool:
        """
        Should we execute this recipe?
        If the indicators return true, we should not make the recipe.
        :param prefix: Prefix to run the recipe for
        :return:
        """
        return self._run_indicators(prefix)

    def _make_in(self, prefix: Wineprefix):
        """
        Actually make the recipe. To be implemented by an inheriting class
        :param prefix: Prefix to run the recipe for
        :return: None
        """
        raise NotImplementedError()

    def _can_make_in(self, prefix: Wineprefix):
        """
        Check if the prefix has the actual requirements for making the recipe.
        If the prefix does not meet the requirements, the recipe cannot be made.
        :param prefix:
        :return:
        """
        log.debug(f"Returning True for _can_make_in prefix {prefix}")
        return True

    def make_in(self, prefix: Wineprefix):
        """
        Public interface for making the recipe.
        Not to be overridden by inheriting classes.
        :param prefix: Prefix to run the recipe for
        :return: None
        """
        if not self._can_make_in(prefix):
            raise CannotMakeRecipe()

        self._make_in(prefix)
