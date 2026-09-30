/*
 * src/probes/IwramQFormat.c
 *
 * A SHIM, not a second implementation. The lift harness compiles this entry
 * point and the real source separately, and the two must produce the same
 * token stream. Verify it by compiling both and comparing the sha1 of their
 * disassembly - never by assuming.
 */
#include "../IwramQFormat.c"
