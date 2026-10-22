	CODE16
|sub_08005740|
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r6, [pc, #0x26c]
	ADD      r4, r0, #0
	LDR      r0, [r6, #0x1c]
	SUB      sp, #0x14
	BL       |loc_08011B04|
	LDR      r0, [r6, #0x1c]
	BL       |loc_080115B0|
	LDR      r0, [r6, #0x1c]
	BL       |loc_0801157E|
	LDR      r0, [pc, #0x258]
	MOV      r2, #0
	LDR      r7, [r0, #0x5c]
	LDR      r0, [r0, #0x68]
	STR      r2, [sp, #0xc]
	MOV      r2, #0x84
	STR      r0, [sp, #0x10]
	MOV      r0, #0
	STR      r2, [sp]
	MOV      r1, #1
	STR      r1, [sp, #8]
	MOV      r2, #0
	MOV      r3, #0xc
	ADD      r1, r4, #0
	STR      r0, [sp, #4]
	BL       |loc_08013E64|
	MOV      r1, #5
	LSL      r1, r1, #7
	ADD      r5, r4, r1
	STR      r0, [r5, #0x34]
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800664E|
	LDR      r2, [r6, #8]
	MOV      r1, #0
	STR      r1, [sp, #8]
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x1c
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x90
	MOV      r0, #0
	STR      r7, [sp]
	BL       |Object_Construct1|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800664E|
	ADD      r1, r7, #0
	LDR      r0, [r6, #8]
	BL       |inc_0x03d784_0x041118| + 0x2864
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	ADD      r7, r0, #0
	MOV      r1, #1
	ADD      r7, #0x1e
	MOV      r2, #0x84
	STR      r2, [sp]
	ADD      r3, r7, #0
	STR      r1, [sp, #4]
	STR      r1, [sp, #8]
	ADD      r1, r4, #0
	MOV      r2, #1
	MOV      r0, #0
	BL       |loc_08013E64|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800664E|
	LDR      r2, [r6, #8]
	MOV      r1, #0
	STR      r2, [sp, #0xc]
	LDR      r2, [sp, #0x10]
	STR      r1, [sp, #8]
	STR      r2, [sp]
	ADD      r2, r7, #0
	ADD      r2, #0x10
	MOV      r0, #5
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x90
	MOV      r0, #0
	BL       |Object_Construct1|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800664E|
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #0x1e
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
	BL       |loc_08013E64|
	STR      r0, [r5, #0x2c]
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #0x74
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r2, [sp]
	MOV      r0, #3
	ADD      r3, r6, #0
	ADD      r1, r4, #0
	STR      r0, [sp, #4]
	MOV      r2, #3
	MOV      r0, #0
	BL       |loc_08013E64|
	STR      r0, [r5, #0x30]
	LDR      r1, [r5, #0x2c]
	ADD      r0, r4, #0
	BL       |loc_0800664E|
	ADD      r0, r4, #0
	LDR      r1, [r5, #0x30]
	BL       |loc_0800664E|
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x153f2_0x1a3f2| + 0xe16
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800664E|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x144]
	LDR      r0, [r0, #0x1c]
	BL       |loc_08011B04|
	ADD      r0, r4, #0
	BEQ      |loc_08005880|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08005880|
	POP      {r4, pc}
	MOV      r2, #0x10
	ADD      r0, #0xff
	ADD      r0, #1
	STR      r2, [r1]
	LDR      r2, [r0, #0xc]
	LDR      r0, [r0, #0x28]
	MOV      r3, #0x34
	SUB      r0, r2, r0
	MUL      r0, r3
	ADD      r0, #0x26
	STR      r0, [r1, #4]
	MOV      r0, #1
	BX       lr
	PUSH     {r3, lr}
	BL       |sub_080067D6|
	LDR      r0, [pc, #0x10c]
	LDR      r0, [r0, #0x1c]
	BL       |loc_080115B0|
	POP      {r3, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r4, [pc, #0x100]
	ADD      r5, r0, #0
	LDR      r0, [r4, #0x1c]
	BL       |loc_0801157E|
	LDR      r0, [r4, #0x1c]
	BL       |sub_08011A1E|
	ADD      r0, r5, #0
	BL       |loc_080067F4|
	POP      {r3, r4, r5, pc}
