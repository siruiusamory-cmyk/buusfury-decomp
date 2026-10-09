"""DragonByte Z: the desktop application for the Webfoot Dragon Ball Z games.

It presents the Webfoot SDK through one window: a session over a verified image
and an authored project, a strip of destinations, one shared inspector and one
status line. The SDK stays the only authority on ROM content; this package holds
no format constant, address or record stride of its own.

Development command::

    python -m tools.dragonbyte

The application is the only entry point here, and it is not the SDK: the
shipping package under ``tools/webfoot`` must never import this one.
"""
