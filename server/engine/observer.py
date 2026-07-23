"""Generic publish/subscribe mechanism - no game knowledge at all.

Deliberately duplicated verbatim in client/state/observer.py rather than
imported from here, so server/ stays importable/testable with zero knowledge
that client/ exists.
"""


class Subject:
    """Notifies every subscribed callback, in order, whenever an event is published."""

    def __init__(self):
        self._subscribers = []

    def subscribe(self, callback) -> None:
        self._subscribers.append(callback)

    def publish(self, event) -> None:
        for callback in self._subscribers:
            callback(event)
