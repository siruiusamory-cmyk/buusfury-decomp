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
    "b3JrZmxvdyB0ZXJtIiwKICAicGF0dGVybiI6ICIoPzwhdXNlci0pKD88IXVzZXIgKVxcYmFn"
    "ZW50cz9cXGIoPyFcXC5tZCkiCiB9LAogewogICJmbGFncyI6IDIsCiAgImxhYmVsIjogImlu"
    "c3RydWN0aW9uLXRleHQgamFyZ29uIiwKICAicGF0dGVybiI6ICIoPzpcXGJwcm9tcHRzP1sv"
    "XFxcXF18XFxiW1xcdy1dK1xcLnByb21wdFxcYnxcXGJuZXh0LXByb21wdFxcYnxcXGIoPzpz"
    "eXN0ZW18Ym9vdHN0cmFwfGluamVjdGlvbnxpbnN0cnVjdGlvbnxyZXZpZXd8YmFzZXxkYXRh"
    "fGluaXRpYWwpXFxzK3Byb21wdHM/XFxifFxcYnByb21wdFxccysoPzpmaWxlfHRlbXBsYXRl"
    "fHRleHR8aW5qZWN0aW9ufGNoYWlufGxpYnJhcnkpXFxiKSIKIH0sCiB7CiAgImZsYWdzIjog"
    "MiwKICAibGFiZWwiOiAiYSBwcml2YXRlIHdvcmtmbG93IGFydGlmYWN0IG5hbWUiLAogICJw"
    "YXR0ZXJuIjogIig/OlxcYkFHRU5UUyg/Ol9bMC05XSk/XFwubWRcXGJ8XFxiQ0xBVURFXFwu"
    "bWRcXGJ8XFwuY2xhdWRlXFxifFxcLmFnZW50c1xcYnxcXC5vcGVuY29kZVxcYnxcXGJoYW5k"
    "b2Zmcz8vfFxcYlNUQVRFXFwubWRcXGJ8XFxiQ1VSUkVOVFxcLm1kXFxifFxcYlJFVklFV19U"
    "RU1QTEFURVxcLm1kXFxifFxcYm1pZ3JhdGlvblxcLnR4dFxcYnxcXGJTS0lMTFxcLm1kXFxi"
    "fHRvb2xzL2FnZW50X3NraWxsc3xcXGJ6Zmxvd1xcYnxyZXZpZXctbG9nMXxjbGF1ZGVfKD86"
    "bG9jYWx8Y2xvdWQpXFxiKSIKIH0sCiB7CiAgImZsYWdzIjogMiwKICAibGFiZWwiOiAic2Vz"
    "c2lvbi1saWZlY3ljbGUgdm9jYWJ1bGFyeSIsCiAgInBhdHRlcm4iOiAiXFxic2Vzc2lvbnM/"
    "W1xccy1dKyg/Om5vdGVzP3xvcmNoZXN0cmF0aW9ufG1hbmFnZW1lbnR8bG9nfGhhbmRvZmZ8"
    "dHJhbnNjcmlwdClzP1xcYiIKIH0sCiB7CiAgImZsYWdzIjogMCwKICAibGFiZWwiOiAiYSBt"
    "YWNoaW5lLXNwZWNpZmljIGFic29sdXRlIHBhdGgiLAogICJwYXR0ZXJuIjogIig/OltBLVph"
    "LXpdOltcXFxcL10rKD86VXNlcnN8RGV2fHRtcHxUZW1wKVtcXFxcL10rfCVURU1QJXwlTE9D"
    "QUxBUFBEQVRBJXxweXRlc3Qtb2YtW0EtWmEtejAtOS5fLV0rfC9ob21lL1thLXpdW2EtejAt"
    "OV8tXSovfFxcXFxcXFxcW0EtWmEtejAtOS5fJC1dK1xcXFxbQS1aYS16MC05Ll8kLV0rKSIK"
    "IH0sCiB7CiAgImZsYWdzIjogMCwKICAibGFiZWwiOiAiYW4gZW1iZWRkZWQgY3JlZGVudGlh"
    "bCIsCiAgInBhdHRlcm4iOiAiKD86c2stW0EtWmEtejAtOV8tXXsyMCx9fGdpdGh1Yl9wYXRf"
    "W0EtWmEtejAtOV9dezIwLH18Z2hwX1tBLVphLXowLTldezIwLH18Z2xwYXQtW0EtWmEtejAt"
    "OV8tXXsxNix9fEFLSUFbMC05QS1aXXsxNn0pIgogfQpd"
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
    "Z2VudCBmaWxlZCB0aGUgcmVwb3J0IiwKICAidGhlIHJlYWdlbnQgd2FzIGNvbnN1bWVkOyBV"
    "c2VyLWFnZW50OiAqIGFsbG93cyBldmVyeSBjcmF3bGVyIgogXSwKIFsKICAiaW5zdHJ1Y3Rp"
    "b24tdGV4dCBqYXJnb24iLAogICJwYXN0ZSB0aGlzIGludG8gdGhlIGJvb3RzdHJhcCBwcm9t"
    "cHQiLAogICJ0aGUgcmVwbHkgY2FtZSBwcm9tcHRseSBmcm9tIHRoZSBTY3JpcHRpbmcgcHJv"
    "bXB0IGNvbnRyb2wiCiBdLAogWwogICJhIHByaXZhdGUgd29ya2Zsb3cgYXJ0aWZhY3QgbmFt"
    "ZSIsCiAgInNlZSBBR0VOVFMubWQgZm9yIHRoZSBydWxlcyIsCiAgInNlZSBNWUFHRU5UUy5t"
    "ZCBmb3IgdGhlIHJ1bGVzIgogXSwKIFsKICAic2Vzc2lvbi1saWZlY3ljbGUgdm9jYWJ1bGFy"
    "eSIsCiAgInRoZSBzZXNzaW9uIHRyYW5zY3JpcHQgd2FzIGF0dGFjaGVkIiwKICAidGhlIHNl"
    "c3Npb24gc3RhdGUgd2FzIHJlbG9hZGVkIgogXSwKIFsKICAiYSBtYWNoaW5lLXNwZWNpZmlj"
    "IGFic29sdXRlIHBhdGgiLAogICJyZWFkIEM6XFxVc2Vyc1xcc29tZW9uZVxccHJvamVjdFxc"
    "ZmlsZS50eHQiLAogICJVc2VycyBhcmUgbGlzdGVkIGluIHRoZSBtYW51YWwiCiBdLAogWwog"
    "ICJhbiBlbWJlZGRlZCBjcmVkZW50aWFsIiwKICAidGhlIGtleSBzay1hYmNkZWZnaGlqa2xt"
    "bm9wcXJzdHV2d3ggd2FzIHJvdGF0ZWQiLAogICJ0aGUga2V5IHNrLXNob3J0IHdhcyByb3Rh"
    "dGVkIgogXQpd"
)
