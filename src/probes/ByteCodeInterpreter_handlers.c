/*
 * src/probes/ByteCodeInterpreter_handlers.c - probe-path shim
 *
 * The reconstruction lives in the product tree at
 * src/ByteCodeInterpreter_handlers.c. This file exists so the lift loop keeps a
 * stable entry point:
 *
 *   src/probes/handler2_selftest.c   #includes "ByteCodeInterpreter_handlers.c"
 *   config/lift_targets.json         names this as the target's probe source
 *
 * It is a plain #include, so the translation unit a compiler sees is the same
 * token stream either way. Edit the implementation, not this file.
 */

#include "../ByteCodeInterpreter_handlers.c"
