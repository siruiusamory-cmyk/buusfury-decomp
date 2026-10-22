#include "global.h"

typedef struct Unk0802B960Object {
    u8 filler_00[0x38];
    s32 unk_38;
} Unk0802B960Object;

typedef struct Unk0802B960Other {
    u8 filler_00[0x04];
    Unk0802B960Object* unk_04;
} Unk0802B960Other;

typedef struct Unk0802B960Self {
    u8 filler_00[0x08];
    s32 unk_08;
} Unk0802B960Self;

extern "C" void sub_0800EECC(void* object, s32 value);

extern "C" void sub_0802B960(Unk0802B960Self* self, Unk0802B960Other* other) {
    Unk0802B960Object* object = other->unk_04;
    s32 value = self->unk_08;
    if (object->unk_38 != value) {
        sub_0800EECC(object, value);
    }
}
