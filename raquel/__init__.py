from .core import Raquel, StopSubscription
from .models import Job, QueueStats


def __getattr__(name: str):
    if name == "AsyncRaquel":
        from .core import AsyncRaquel

        return AsyncRaquel
    raise AttributeError(name)


__all__ = ["Raquel", "AsyncRaquel", "StopSubscription", "Job", "QueueStats"]
