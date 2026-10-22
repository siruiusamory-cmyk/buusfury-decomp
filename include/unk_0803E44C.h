#ifndef GUARD_UNK_0803E44C_H
#define GUARD_UNK_0803E44C_H

#include "global.h"

typedef union Unk0803E44CFlags {
    u16 all;
    u8 bytes[2];
} Unk0803E44CFlags;

typedef struct Unk0803E44CEntry {
    u8 filler_00[0x10];
    Unk0803E44CFlags unk_10;
    u8 filler_12[0x2e];
} Unk0803E44CEntry;

#endif
