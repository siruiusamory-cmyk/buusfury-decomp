#ifndef GUARD_GLOBAL_H
#define GUARD_GLOBAL_H

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;

typedef volatile u8 vu8;
typedef volatile u16 vu16;
typedef volatile u32 vu32;

typedef u8 bool8;
typedef u32 bool32;

#define ARRAY_COUNT(array) (sizeof(array) / sizeof((array)[0]))

#define EWRAM_BASE 0x02000000
#define IWRAM_BASE 0x03000000
#define ROM_BASE 0x08000000

#endif
