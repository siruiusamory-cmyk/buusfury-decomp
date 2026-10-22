#include "global.h"

typedef struct Unk0802AD88Object {
    u8 filler_00[0x1CC];
    u32 unk_1CC;
} Unk0802AD88Object;

extern u32 unk_03003014;
extern u32 unk_0300302C;

extern "C" void loc_0800ECDA(Unk0802AD88Object* object, u32 index);
extern "C" void loc_0800ED18(Unk0802AD88Object* object, void* handler);

extern "C" void sub_0802AD88(u32 unused, Unk0802AD88Object* object) {
    loc_0800ECDA(object, 0x13);
    loc_0800ED18(object, (void*)&unk_03003014);
    unk_0300302C = 0;
    object->unk_1CC = 0;
}

extern "C" u32 sub_0802ADAA(void) {
    return 0;
}

extern "C" u32 sub_0802ADAE(void) {
    return (u32)&unk_03003014 - 4;
}
