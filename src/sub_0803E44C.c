#include "global.h"

#include "unk_0803E44C.h"

extern "C" void* GBARam_Malloc(s32 size);
extern "C" void sub_08049138(Unk0803E44CEntry* dst, Unk0803E44CEntry* src, s32 size);

extern "C" Unk0803E44CEntry* sub_0803E44C(Unk0803E44CEntry* source) {
    Unk0803E44CEntry* result = (Unk0803E44CEntry*)GBARam_Malloc(0x400);
    Unk0803E44CEntry* dst;
    s32 i;
    s32 flagBit;

    i = 0;
    while (i < 0x10) {
        result[i].unk_10.bytes[0] = 0;
        i++;
    }
    dst = result;
    i = 0;
    flagBit = 1;
    while (i < 0x10) {
        if ((source[i].unk_10.all & 0x101) == 0x101) {
            source[i].unk_10.bytes[0] = source[i].unk_10.bytes[0] & ~1;
            sub_08049138(dst, &source[i], 0x40);
            dst->unk_10.bytes[0] |= flagBit;
            dst++;
        }
        i++;
    }
    return result;
}
