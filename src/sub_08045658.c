#include "global.h"

extern "C" void loc_080437c2(s32 value);

extern "C" void sub_08045658(s32 value, s32 which) {
    if (which != 0) {
        value = 0x24;
    } else if (value != 0xff) {
        return;
    }
    loc_080437c2(value);
}
