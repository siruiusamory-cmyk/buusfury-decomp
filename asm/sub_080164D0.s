	CODE16
|sub_080164D0|
	ADD      r1, r0, #0
	ADD      r1, #0xff
	PUSH     {r4, r5, r6}
	ADD      r1, #0x35
	MOV      r2, #0xa1
	LSL      r2, r2, #2
	MOV      r3, #0
	ADD      r2, r0, r2
	STR      r3, [r1]
	LDR      r5, [pc, #0x2ac]
	LDR      r4, [pc, #0x2a4]
	STR      r3, [r2]
	MOV      r0, #0
|loc_080164EA|
	LDR      r3, [r4, #0xc]
	ADD      r3, r3, r0
	LDRB     r3, [r3, #2]
	CMP      r3, #0
	BEQ      |loc_0801651A|
	MOV      r3, #0x34
	MUL      r3, r0
	ADD      r3, r3, r5
	LDRB     r3, [r3]
	LSL      r3, r3, #0x1f
	BEQ      |loc_0801650E|
	LDR      r3, [r2]
	ADD      r6, r3, #1
	LSL      r3, r3, #2
	ADD      r3, r3, r2
	STR      r6, [r2]
	STR      r0, [r3, #4]
	B        |loc_0801651A|
|loc_0801650E|
	LDR      r3, [r1]
	ADD      r6, r3, #1
	LSL      r3, r3, #2
	ADD      r3, r3, r1
	STR      r6, [r1]
	STR      r0, [r3, #4]
|loc_0801651A|
	ADD      r0, #1
	CMP      r0, #0x53
	BLT      |loc_080164EA|
	POP      {r4, r5, r6}
	BX       lr
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BNE      |loc_0801653A|
	MOV      r0, #0xf5
	LSL      r0, r0, #2
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_0801653A|
	ADD      r0, r4, #0
	POP      {r4, pc}
|loc_0801653A|
	LDR      r0, [pc, #0x258]
	MOV      r1, #0
	STMIA    r4!, {r0, r1}
	SUB      r4, #8
	ADD      r0, r4, #0
	ADD      r0, #0xff
	ADD      r0, #1
	STR      r1, [r0, #0xc]
	STR      r1, [r0, #8]
	LDR      r2, [pc, #0x248]
	STR      r1, [r0, #0x10]
	STR      r2, [r4]
	MOV      r2, #0xff
	ADD      r2, #0x35
	STR      r1, [r2, r4]
	MOV      r2, #0xa1
	LSL      r2, r2, #2
	ADD      r2, r4, r2
	STR      r1, [r2]
	STR      r1, [r0, #0x1c]
	STR      r1, [r0, #0x24]
	STR      r1, [r0, #0x20]
	MOV      r1, #2
	STR      r1, [r0, #0xc]
	ADD      r0, r4, #0
	BL       |sub_080164D0|
	ADD      r0, r4, #0
	POP      {r4, pc}
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r7, [pc, #0x224]
	ADD      r4, r0, #0
	LDR      r0, [r7, #0x68]
	LDR      r5, [r7, #0x5c]
	SUB      sp, #0x24
	STR      r0, [sp, #0x20]
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #0x84
	STR      r2, [sp]
	MOV      r0, #0
	MOV      r1, #1
	STR      r1, [sp, #8]
	MOV      r2, #0
	MOV      r3, #0xc
	ADD      r1, r4, #0
	STR      r0, [sp, #4]
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r6, [pc, #0x1e4]
	MOV      r1, #0
	LDR      r2, [r6, #8]
	STR      r1, [sp, #8]
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x1c
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x90
	MOV      r0, #0
	STR      r5, [sp]
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      r1, r5, #0
	LDR      r0, [r6, #8]
	BL       |inc_0x03d784_0x041118| + 0x2864
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	ADD      r5, r0, #0
	MOV      r1, #1
	ADD      r5, #0x1e
	MOV      r2, #0x84
	STR      r2, [sp]
	ADD      r3, r5, #0
	STR      r1, [sp, #4]
	STR      r1, [sp, #8]
	ADD      r1, r4, #0
	MOV      r2, #1
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r2, [r6, #8]
	MOV      r1, #0
	STR      r2, [sp, #0xc]
	LDR      r2, [sp, #0x20]
	STR      r1, [sp, #8]
	STR      r2, [sp]
	ADD      r2, r5, #0
	ADD      r2, #0x10
	MOV      r0, #5
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x90
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #8
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r2, [sp]
	MOV      r0, #6
	STR      r0, [sp, #4]
	MOV      r2, #6
	ADD      r1, r4, #0
	MOV      r3, #8
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #8
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r2, [sp]
	MOV      r0, #7
	STR      r0, [sp, #4]
	MOV      r2, #7
	ADD      r1, r4, #0
	MOV      r3, #0xd0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r3, [r7, #0x70]
	LDR      r2, [r6, #8]
	STR      r3, [sp]
	MOV      r1, #0
	MOV      r5, #0x14
	ADD      r3, r5, #0
	STR      r1, [sp, #8]
	MOV      r0, #2
	STR      r2, [sp, #0xc]
	MOV      r2, #0x22
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r3, #0x90
	LDR      r3, [r7, r3]
	LDR      r2, [r6, #8]
	MOV      r1, #2
	STR      r3, [sp]
	ADD      r3, r5, #0
	STR      r1, [sp, #4]
	STR      r1, [sp, #8]
	STR      r2, [sp, #0xc]
	MOV      r2, #0xce
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #1
	STR      r2, [sp, #0xc]
	MOV      r2, #0x28
	MOV      r1, #1
	MOV      r6, #0xd4
	ADD      r3, r6, #0
	STR      r1, [sp, #8]
	STR      r2, [sp]
	MOV      r0, #2
	STR      r0, [sp, #4]
	MOV      r2, #2
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r5, r4, #0
	ADD      r5, #0xff
	ADD      r5, #1
	STR      r0, [r5, #0x28]
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #1
	STR      r2, [sp, #0xc]
	MOV      r2, #0x70
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r2, [sp]
	MOV      r0, #3
	ADD      r3, r6, #0
	ADD      r1, r4, #0
	STR      r0, [sp, #4]
	MOV      r2, #3
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	STR      r0, [r5, #0x2c]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r0, #0x20
	STR      r0, [sp, #0x14]
	MOV      r0, #1
	MOV      r1, #1
	STR      r1, [sp, #0x18]
	MOV      r1, #0x22
	MOV      r2, #0
	STR      r2, [sp, #0x1c]
	STR      r1, [sp, #0xc]
|unk_08016714|
	INCBIN	baserom.gba_0x16714_0x16718.extracted
	MOV      r2, #0x18
	STR      r2, [sp, #0x10]
	STR      r1, [sp]
	ADD      r3, r6, #0
	ADD      r1, r4, #0
	MOV      r2, #0
	STR      r0, [sp, #8]
	MOV      r0, #0
	STR      r6, [sp, #4]
	BL       |loc_08015C62|
	ADD      r1, r0, #0
	STR      r0, [r5, #0x14]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r0, [r5, #0x14]
	MOV      r2, #1
	LDR      r1, [r0, #0x28]
	LDR      r0, [r0, #0x20]
	STR      r2, [sp, #0x1c]
	SUB      r3, r1, r0
	MOV      r0, #0x20
	STR      r0, [sp, #0x14]
|unk_08016748|
	INCBIN	baserom.gba_0x16748_0x1674a.extracted
	MOV      r1, #0
	STR      r1, [sp, #0x18]
	MOV      r1, #0x23
	STR      r1, [sp, #0xc]
	ADD      r3, #0x1c
	STR      r3, [sp, #0x10]
	ADD      r1, r0, #0
	MOV      r2, #0
	STR      r2, [sp, #4]
	STR      r1, [sp]
	ADD      r3, r6, #0
	ADD      r1, r4, #0
	MOV      r2, #1
	STR      r0, [sp, #8]
	MOV      r0, #0
	BL       |loc_08015C62|
	ADD      r1, r0, #0
	STR      r0, [r5, #0x18]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |loc_08016208|
	ADD      r1, r0, #0
	STR      r0, [r5, #0x30]
	ADD      r0, r4, #0
|loc_08016784|
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
|sub_0801678C|
|unk_0801678C|
	INCBIN	baserom.gba_0x1678c_0x1678e.extracted
