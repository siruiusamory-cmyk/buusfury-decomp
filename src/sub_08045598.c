#include "global.h"

extern "C" void loc_08043b66(s32 zero);
extern "C" void loc_080437c2(s32 first, s32 second);

extern "C" void sub_08045598(s32 first, s32 second) {
    if (second == 0) {
        loc_08043b66(0);
    }
    loc_080437c2(first, second);
}
