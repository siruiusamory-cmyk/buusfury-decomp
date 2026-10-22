#include "global.h"

typedef struct Unk03005294Cmd {
    u32 unk_00;
    u32 unk_04;
    u32 unk_08;
} Unk03005294Cmd;

typedef struct Unk03005294Buffer {
    u8 filler_00[4];
    u8 unk_04;
    u8 filler_05[0x1f];
    Unk03005294Cmd* unk_24;
} Unk03005294Buffer;

extern "C" Unk03005294Buffer* g_03005294;
extern "C" s32 loc_08045d8c(s32 request);
extern "C" void loc_08045b40(void);

extern "C" void sub_080461F8(u32 a, u32 b) {
    if (loc_08045d8c(0x31) == 0) {
        g_03005294->unk_04 = 1;
        g_03005294->unk_24->unk_04 = a | (b << 8);
        loc_08045b40();
    }
}

extern "C" void sub_08046222(u32 a, u32 b, u32 c) {
    if (loc_08045d8c(0x32) == 0) {
        g_03005294->unk_04 = 2;
        g_03005294->unk_24->unk_04 = (a << 16) | b;
        g_03005294->unk_24->unk_08 = c;
        loc_08045b40();
    }
}

extern "C" void sub_08046252(void) {
    if (loc_08045d8c(0x33) == 0) {
        g_03005294->unk_04 = 0;
        loc_08045b40();
    }
}

extern "C" void sub_0804626E(void) {
    if (loc_08045d8c(0x34) == 0) {
        g_03005294->unk_04 = 0;
        loc_08045b40();
    }
}

extern "C" void sub_0804628A(void) {
    if (loc_08045d8c(0x3d) == 0) {
        g_03005294->unk_04 = 0;
        loc_08045b40();
    }
}
