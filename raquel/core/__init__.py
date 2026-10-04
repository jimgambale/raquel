from .core_sync import Raquel
from .base import StopSubscription


def __getattr__(name: str):
    if name == "AsyncRaquel":
        from .core_async import AsyncRaquel

        return AsyncRaquel
    raise AttributeError(name)


__all__ = ["Raquel", "AsyncRaquel", "StopSubscription"]
