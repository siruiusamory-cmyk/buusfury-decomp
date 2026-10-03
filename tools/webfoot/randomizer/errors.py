"""The refusal families every randomizer product shares.

One vocabulary for the questions a *product* has to answer around a randomizer
core, so the two shipped windows cannot answer the same question with two
different sentences and a third window does not invent a fourth:

* :class:`UnsupportedRomError` - this image is not one this build randomizes;
* :class:`OutputAlreadyExistsError` - the output is taken and was not confirmed;
* :class:`OutputPathRefusedError` - the requested write is not allowed;
* :class:`SeedRefusedError` - the core cannot use this seed;
* :class:`SourceChangedError` - the input moved underneath the run;
* :class:`ManifestWriteError` - the image exists but its record does not.

:class:`ModuleRefusedError` is the one addition the module registry needs: a
module that refuses a *settings* combination (or an image it cannot plan against)
has to say so in the same register as the rest, rather than raising a bare
``ValueError`` the window would report as a crash.

Every message is user-facing prose. A ``randomizer`` refusal reaching a window is
a sentence for a person, and a programmer error is not - which is exactly why the
two are separate exception roots here and the window treats anything outside this
family as a defect worth a traceback.
"""

from __future__ import annotations


class RandomizerAppError(ValueError):
    """Base error for the application layer. The message is user-facing."""


class UnsupportedRomError(RandomizerAppError):
    """The selected file is not the verified supported image."""


class OutputAlreadyExistsError(RandomizerAppError):
    """The output or one of its companion files exists and was not confirmed."""


class OutputPathRefusedError(RandomizerAppError):
    """The requested output location cannot be written, or is not allowed."""


class SeedRefusedError(RandomizerAppError):
    """The seed is one the core cannot use."""


class SourceChangedError(RandomizerAppError):
    """The input image changed during the run; the run fails closed."""


class ManifestWriteError(RandomizerAppError):
    """The ROM was written but its manifest or spoiler could not be."""


class ModuleRefusedError(RandomizerAppError):
    """A module cannot run against this image or these settings.

    Raised by a module's own ``validate`` or ``plan``. It is a *user* refusal,
    not a defect: the window shows the sentence and offers no traceback.
    """


class ModuleConflictError(RandomizerAppError):
    """Two modules would write the same bytes.

    Fail closed. "Last module wins" is not a resolution: a combined run whose
    modules disagree about a byte has no defensible answer, and silently picking
    one would make the manifest describe an image neither module planned.
    """
