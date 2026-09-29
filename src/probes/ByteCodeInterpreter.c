/*
 * src/probes/ByteCodeInterpreter.c - probe-path shim
 *
 * The reconstruction lives in the product tree at src/ByteCodeInterpreter.c.
 * This file exists so the lift loop keeps a stable entry point:
 *
 *   src/probes/bci_selftest.c        #includes "ByteCodeInterpreter.c"
 *   config/lift_targets.json         names this as the target's probe source
 *   tools/buusfury/lift.py           compiles the decomp source for the compare
 *
 * It is a plain #include, so the translation unit a compiler sees is the same
 * token stream either way. The implementation is at
 * src/ByteCodeInterpreter.c. Edit that file, not this one.
 */

#include "../ByteCodeInterpreter.c"
