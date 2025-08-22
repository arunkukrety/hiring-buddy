from __future__ import annotations

from portia import DefaultToolRegistry


class RecruitingToolRegistry(DefaultToolRegistry):
    """small caps: bundles tools needed for recruiting workflow"""

    def __init__(self, *_, **__):
        super().__init__(*_, **__)
        # future: register custom wrappers here

