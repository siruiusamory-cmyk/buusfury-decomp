#include "global.h"

typedef struct Unk0803431CBody {
    u8 filler_00[0x10];
    u32 unk_10;
} Unk0803431CBody;

typedef struct Unk0803431CHead {
    Unk0803431CBody* unk_00;
} Unk0803431CHead;

extern "C" void Thunk_JumpRegister1(Unk0803431CHead* self, s32 one, u32 address);

extern "C" void sub_0803431C(Unk0803431CHead* self) {
    if (self != 0) {
        Unk0803431CBody* body = self->unk_00;
        Thunk_JumpRegister1(self, 1, (u32)body + body->unk_10);
    }
}
