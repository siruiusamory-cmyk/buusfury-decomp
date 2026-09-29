/*
 * src/probes/GBARam.c - probe-path shim
 *
 * The reconstruction has been PROMOTED into the real decomp source tree and now
 * lives at src/GBARam.c, at the path the surviving original build command names.
 * This file exists only so the probe harness keeps a stable entry point:
 *
 *   config/compiler_probes.json           records src/probes/GBARam.c as the
 *                                         translation unit's source candidate
 *   src/probes/gbaram_selftest.c          #includes "GBARam.c"
 *   tools/buusfury/compiler_probe.py      compiles it for the ADS probe
 *
 * It is a plain #include, so the translation unit a compiler sees is the SAME
 * TOKEN STREAM as before the promotion. Nothing in the probe path changed and
 * no probe result can be affected by the move.
 *
 * The implementation is at src/GBARam.c. Edit that file, not this one.
 */

#include "../GBARam.c"
