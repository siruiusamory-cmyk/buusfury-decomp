#include "global.h"

#include "unk_0803E44C.h"

extern "C" void GBARam_Free(void* pointer);
extern "C" void Thunk_VramCopy(Unk0803E44CEntry* dst, Unk0803E44CEntry* src, s32 size);

extern "C" void sub_0803E4A0(Unk0803E44CEntry* table, Unk0803E44CEntry* source) {
    s32 i;
    s32 j;

    for (i = 0; i < 0x10; i++) {
        if ((source[i].unk_10.all & 0x101) == 0x101) {
            for (j = 0; j < 0x10; j++) {
                if (!((u32)table[j].unk_10.bytes[0] << 31)) {
                    Thunk_VramCopy(&table[j], &source[i], 0x40);
                    break;
                }
            }
        }
    }
    GBARam_Free(source);
}
