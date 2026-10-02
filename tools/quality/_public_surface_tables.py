"""Encoded tables for the public-surface guard.

The guard catches terms that the public tree must not carry, and a file that
spells those terms out in plain text can never pass a scan of the tree it lives
in. They are therefore stored here as base64 of a JSON document, and the guard
decodes them at import time. Decode either table to read it:

    python -c "import base64, tools.quality._public_surface_tables as t; \
print(base64.b64decode(t.FORBIDDEN_B64).decode())"

Each entry of the forbidden table carries a label, a regular expression and its
flags. Each entry of the probe table carries a label, a string the matching
pattern must accept and a near-miss it must reject, so the guard's tests prove
that every screen still has teeth without restating what it screens for.

This module is generated, not hand-edited. The generator lives outside the
repository so that the plain-text source of these terms stays out of it.
"""

from __future__ import annotations

#: Screen 1: what the public surface must not carry.
FORBIDDEN_B64 = (
    "WwogewogICJmbGFncyI6IDIsCiAgImxhYmVsIjogImEgdmVuZG9yIG9yIHByb2R1Y3QgbmFt"
    "ZSBmb3IgYSBob3N0ZWQgbGFuZ3VhZ2Ugc2VydmljZSIsCiAgInBhdHRlcm4iOiAiXFxiKD86"
    "Q2hhdEdQVHxPcGVuQUl8QW50aHJvcGljfENsYXVkZXxDb2RleHxEZWVwU2Vla3xDb3BpbG90"
    "fEdlbWluaXxMbGFtYXxNaXN0cmFsfEdyb2t8UXdlbnxLaW1pfFBlcnBsZXhpdHl8T2xsYW1h"
    "KVxcYiIKIH0sCiB7CiAgImZsYWdzIjogMiwKICAibGFiZWwiOiAiYSBuYW1lIGZvciBvbmUg"
    "aG9zdGVkIHJlYXNvbmluZyBtb2RlbCIsCiAgInBhdHRlcm4iOiAiXFxiKD86R1BULVswLTld"
    "KD86XFwuWzAtOV0rKT98VGVycmEgKD86TWVkaXVtfEhpZ2gpfFNvbCBIaWdofEx1bmEgTWVk"
    "aXVtfGNsYXVkZS1bYS16MC05XVthLXowLTkuLV0qKVxcYiIKIH0sCiB7CiAgImZsYWdzIjog"
    "MCwKICAibGFiZWwiOiAiYW4gYWJicmV2aWF0aW9uIG5hbWluZyB0aGF0IHRlY2hub2xvZ3ki"
    "LAogICJwYXR0ZXJuIjogIlxcYig/OkxMTXM/fEFHSSlcXGIiCiB9LAogewogICJmbGFncyI6"
    "IDAsCiAgImxhYmVsIjogInRoYXQgYWJicmV2aWF0aW9uIHVzZWQgYXMgYSBkZXZlbG9wbWVu"
    "dCB0b29sIiwKICAicGF0dGVybiI6ICJcXGJBSVxcYiIKIH0sCiB7CiAgImZsYWdzIjogMiwK"
    "ICAibGFiZWwiOiAidGhhdCBhYmJyZXZpYXRpb24gd2l0aCBhbiBhc3Npc3RhbmNlIHN1ZmZp"
    "eCIsCiAgInBhdHRlcm4iOiAiQUlbXFxzLV0qKD86YXNzaXN0ZWR8Z2VuZXJhdGVkfHdyaXR0"
    "ZW58YXV0aG9yZWR8cG93ZXJlZHxkcml2ZW4pIgogfSwKIHsKICAiZmxhZ3MiOiAyLAogICJs"
    "YWJlbCI6ICJvcmNoZXN0cmF0aW9uIHZvY2FidWxhcnkiLAogICJwYXR0ZXJuIjogIlxcYig/"
    "OnN1Yi0/YWdlbnRzP3xhZ2VudGljfG11bHRpLT9hZ2VudHxvcmNoZXN0cmF0b3JzPylcXGIi"
    "CiB9LAogewogICJmbGFncyI6IDIsCiAgImxhYmVsIjogImFuIGFnZW50IHVzZWQgYXMgYSB3"
    "b3JrZmxvdyB0ZXJtIiwKICAicGF0dGVybiI6ICJcXGJhZ2VudHM/XFxiKD8hXFwubWQpIgog"
    "fSwKIHsKICAiZmxhZ3MiOiAyLAogICJsYWJlbCI6ICJpbnN0cnVjdGlvbi10ZXh0IGphcmdv"
    "biIsCiAgInBhdHRlcm4iOiAiKD86XFxicHJvbXB0cz9bL1xcXFxdfFxcYltcXHctXStcXC5w"
    "cm9tcHRcXGJ8XFxibmV4dC1wcm9tcHRcXGJ8XFxiKD86c3lzdGVtfGJvb3RzdHJhcHxpbmpl"
    "Y3Rpb258aW5zdHJ1Y3Rpb258cmV2aWV3fGJhc2V8ZGF0YXxpbml0aWFsKVxccytwcm9tcHRz"
    "P1xcYnxcXGJwcm9tcHRcXHMrKD86ZmlsZXx0ZW1wbGF0ZXx0ZXh0fGluamVjdGlvbnxjaGFp"
    "bnxsaWJyYXJ5KVxcYikiCiB9LAogewogICJmbGFncyI6IDIsCiAgImxhYmVsIjogImEgcHJp"
    "dmF0ZSB3b3JrZmxvdyBhcnRpZmFjdCBuYW1lIiwKICAicGF0dGVybiI6ICIoPzpcXGJBR0VO"
    "VFMoPzpfWzAtOV0pP1xcLm1kXFxifFxcYkNMQVVERVxcLm1kXFxifFxcLmNsYXVkZVxcYnxc"
    "XC5hZ2VudHNcXGJ8XFwub3BlbmNvZGVcXGJ8XFxiaGFuZG9mZnM/L3xcXGJTVEFURVxcLm1k"
    "XFxifFxcYkNVUlJFTlRcXC5tZFxcYnxcXGJSRVZJRVdfVEVNUExBVEVcXC5tZFxcYnxcXGJt"
    "aWdyYXRpb25cXC50eHRcXGJ8XFxiU0tJTExcXC5tZFxcYnx0b29scy9hZ2VudF9za2lsbHN8"
    "XFxiemZsb3dcXGJ8cmV2aWV3LWxvZzF8Y2xhdWRlXyg/OmxvY2FsfGNsb3VkKVxcYikiCiB9"
    "LAogewogICJmbGFncyI6IDIsCiAgImxhYmVsIjogInNlc3Npb24tbGlmZWN5Y2xlIHZvY2Fi"
    "dWxhcnkiLAogICJwYXR0ZXJuIjogIlxcYnNlc3Npb25zP1tcXHMtXSsoPzpub3Rlcz98b3Jj"
    "aGVzdHJhdGlvbnxtYW5hZ2VtZW50fGxvZ3xoYW5kb2ZmfHRyYW5zY3JpcHQpcz9cXGIiCiB9"
    "LAogewogICJmbGFncyI6IDAsCiAgImxhYmVsIjogImEgbWFjaGluZS1zcGVjaWZpYyBhYnNv"
    "bHV0ZSBwYXRoIiwKICAicGF0dGVybiI6ICIoPzpbQS1aYS16XTpbXFxcXC9dKyg/OlVzZXJz"
    "fERldnx0bXB8VGVtcClbXFxcXC9dK3wlVEVNUCV8JUxPQ0FMQVBQREFUQSV8cHl0ZXN0LW9m"
    "LVtBLVphLXowLTkuXy1dK3wvaG9tZS9bYS16XVthLXowLTlfLV0qL3xcXFxcXFxcXFtBLVph"
    "LXowLTkuXyQtXStcXFxcW0EtWmEtejAtOS5fJC1dKykiCiB9LAogewogICJmbGFncyI6IDAs"
    "CiAgImxhYmVsIjogImFuIGVtYmVkZGVkIGNyZWRlbnRpYWwiLAogICJwYXR0ZXJuIjogIig/"
    "OnNrLVtBLVphLXowLTlfLV17MjAsfXxnaXRodWJfcGF0X1tBLVphLXowLTlfXXsyMCx9fGdo"
    "cF9bQS1aYS16MC05XXsyMCx9fGdscGF0LVtBLVphLXowLTlfLV17MTYsfXxBS0lBWzAtOUEt"
    "Wl17MTZ9KSIKIH0KXQ=="
)

#: Screen 2: positive and negative controls, one pair per forbidden entry.
PROBES_B64 = (
    "WwogWwogICJhIHZlbmRvciBvciBwcm9kdWN0IG5hbWUgZm9yIGEgaG9zdGVkIGxhbmd1YWdl"
    "IHNlcnZpY2UiLAogICJwYWlyIHJldmlld2VkIHdpdGggQ2xhdWRlIG9uIHRoZSBicmFuY2gi"
    "LAogICJDbGF1ZGV0dGUgbWFpbnRhaW5lZCB0aGUgcGFyc2VyIgogXSwKIFsKICAiYSBuYW1l"
    "IGZvciBvbmUgaG9zdGVkIHJlYXNvbmluZyBtb2RlbCIsCiAgInRoZSBHUFQtNS42IGxhcmdl"
    "LWNvbnRleHQgcGFzcyIsCiAgInRoZSBHUFRRIHF1YW50aXNlciIKIF0sCiBbCiAgImFuIGFi"
    "YnJldmlhdGlvbiBuYW1pbmcgdGhhdCB0ZWNobm9sb2d5IiwKICAiYW4gTExNIHdyb3RlIHRo"
    "ZSBzdW1tYXJ5IiwKICAiTExNWCBpcyBhIGZpbGUgZm9ybWF0IgogXSwKIFsKICAidGhhdCBh"
    "YmJyZXZpYXRpb24gdXNlZCBhcyBhIGRldmVsb3BtZW50IHRvb2wiLAogICJBSSByZXZpZXdl"
    "ZCB0aGUgY2hhbmdlIiwKICAiQUlNIGlzIHRoZSB0YXJnZXRpbmcgbW9kZSIKIF0sCiBbCiAg"
    "InRoYXQgYWJicmV2aWF0aW9uIHdpdGggYW4gYXNzaXN0YW5jZSBzdWZmaXgiLAogICJhbiBB"
    "SS1hc3Npc3RlZCB0cmFuc2NyaXB0aW9uIiwKICAiYW4gYWlkLWFzc2lzdGVkIHRyYW5zY3Jp"
    "cHRpb24iCiBdLAogWwogICJvcmNoZXN0cmF0aW9uIHZvY2FidWxhcnkiLAogICJ0aGUgc3Vi"
    "YWdlbnQgcmV0dXJuZWQgZWFybHkiLAogICJ0aGUgc3ViYXNzZW1ibHkgd2FzIHJlbW92ZWQi"
    "CiBdLAogWwogICJhbiBhZ2VudCB1c2VkIGFzIGEgd29ya2Zsb3cgdGVybSIsCiAgInRoZSBh"
    "Z2VudCBmaWxlZCB0aGUgcmVwb3J0IiwKICAidGhlIHJlYWdlbnQgd2FzIGNvbnN1bWVkIgog"
    "XSwKIFsKICAiaW5zdHJ1Y3Rpb24tdGV4dCBqYXJnb24iLAogICJwYXN0ZSB0aGlzIGludG8g"
    "dGhlIGJvb3RzdHJhcCBwcm9tcHQiLAogICJ0aGUgcmVwbHkgY2FtZSBwcm9tcHRseSBmcm9t"
    "IHRoZSBTY3JpcHRpbmcgcHJvbXB0IGNvbnRyb2wiCiBdLAogWwogICJhIHByaXZhdGUgd29y"
    "a2Zsb3cgYXJ0aWZhY3QgbmFtZSIsCiAgInNlZSBBR0VOVFMubWQgZm9yIHRoZSBydWxlcyIs"
    "CiAgInNlZSBNWUFHRU5UUy5tZCBmb3IgdGhlIHJ1bGVzIgogXSwKIFsKICAic2Vzc2lvbi1s"
    "aWZlY3ljbGUgdm9jYWJ1bGFyeSIsCiAgInRoZSBzZXNzaW9uIHRyYW5zY3JpcHQgd2FzIGF0"
    "dGFjaGVkIiwKICAidGhlIHNlc3Npb24gc3RhdGUgd2FzIHJlbG9hZGVkIgogXSwKIFsKICAi"
    "YSBtYWNoaW5lLXNwZWNpZmljIGFic29sdXRlIHBhdGgiLAogICJyZWFkIEM6XFxVc2Vyc1xc"
    "c29tZW9uZVxccHJvamVjdFxcZmlsZS50eHQiLAogICJVc2VycyBhcmUgbGlzdGVkIGluIHRo"
    "ZSBtYW51YWwiCiBdLAogWwogICJhbiBlbWJlZGRlZCBjcmVkZW50aWFsIiwKICAidGhlIGtl"
    "eSBzay1hYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3ggd2FzIHJvdGF0ZWQiLAogICJ0aGUga2V5"
    "IHNrLXNob3J0IHdhcyByb3RhdGVkIgogXQpd"
)
