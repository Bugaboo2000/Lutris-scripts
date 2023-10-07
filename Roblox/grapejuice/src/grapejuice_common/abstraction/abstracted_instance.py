from grapejuice_common.abstraction.abstract_grapejuice import AbstractGrapejuice

instance = None


def abstract_grapejuice() -> AbstractGrapejuice:
    global instance

    if instance is None:
        from grapejuice_common.abstraction.abstract_grapejuice_impl import AbstractGrapejuiceImpl
        instance = AbstractGrapejuiceImpl()

    return instance
