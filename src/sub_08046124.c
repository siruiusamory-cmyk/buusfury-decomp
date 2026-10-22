#include "global.h"

typedef struct Unk03005294Buffer {
    u8 filler_00[4];
    u8 unk_04;
    u8 filler_05[0x1f];
    u8* unk_24;
} Unk03005294Buffer;

extern "C" Unk03005294Buffer* g_03005294;
extern "C" s32 loc_08045d8c(s32 request);
extern "C" void loc_08045b40(void);

extern "C" void sub_08046124(void) {
    if (loc_08045d8c(0x27) == 0) {
        g_03005294->unk_04 = 0;
        loc_08045b40();
    }
}

extern "C" void sub_08046140(s32 value) {
    if (loc_08045d8c(0x28) == 0) {
        if (value == 0) {
            g_03005294->unk_04 = 0;
        } else {
            u8* p;

            g_03005294->unk_04 = 1;
            p = &g_03005294->unk_24[4];
            *p = value;
            p++;
            *p = 0;
            p++;
            *p = 0;
            p++;
            *p = 0;
        }
        loc_08045b40();
    }
}

extern "C" void sub_0804617E(u8 a, u8 b) {
    if (loc_08045d8c(0x29) == 0) {
        u8* p;

        g_03005294->unk_04 = 1;
        p = &g_03005294->unk_24[4];
        *p = a;
        p++;
        *p = b;
        p++;
        *p = 0;
        p++;
        *p = 0;
        loc_08045b40();
    }
}

extern "C" void sub_080461B2(void) {
    if (loc_08045d8c(0x37) == 0) {
        g_03005294->unk_04 = 0;
        loc_08045b40();
    }
}

extern "C" void sub_080461CE(u32 value) {
    if (loc_08045d8c(0x30) == 0) {
        g_03005294->unk_04 = 1;
        *(u32*)&g_03005294->unk_24[4] = value;
        loc_08045b40();
    }
}
