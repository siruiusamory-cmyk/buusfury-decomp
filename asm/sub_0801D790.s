	CODE16
|sub_0801D790|
	MOV      r0, #0
	STR      r0, [r1, #8]
	POP      {r4, r5}
	BX       lr
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x1cc]
	SUB      sp, #0x14
	LDR      r6, [r0, #0x5c]
	LDR      r0, [r0, #0x68]
	MOV      r2, #0
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
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r5, r4, #0
	ADD      r5, #0xff
	ADD      r5, #0x41
	STR      r0, [r5]
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r7, [pc, #0x184]
	MOV      r1, #0
	LDR      r2, [r7, #8]
	STR      r1, [sp, #8]
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x1c
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x90
	MOV      r0, #0
	STR      r6, [sp]
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      r1, r6, #0
	LDR      r0, [r7, #8]
	BL       |inc_0x03d784_0x041118| + 0x2864
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	ADD      r6, r0, #0
	MOV      r1, #1
	ADD      r6, #0x1e
	MOV      r2, #0x84
	STR      r2, [sp]
	ADD      r3, r6, #0
	STR      r1, [sp, #4]
	STR      r1, [sp, #8]
	ADD      r1, r4, #0
	MOV      r2, #1
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r2, [r7, #8]
	MOV      r1, #0
	STR      r2, [sp, #0xc]
	LDR      r2, [sp, #0x10]
	STR      r1, [sp, #8]
	STR      r2, [sp]
	ADD      r2, r6, #0
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
	LDR      r1, [pc, #0xd8]
	MOV      r0, #0x84
	LDR      r3, [r1, r0]
	LDR      r2, [r7, #8]
	STR      r3, [sp]
	MOV      r1, #0
	MOV      r6, #0x14
	ADD      r3, r6, #0
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
	LDR      r0, [pc, #0xb0]
	MOV      r1, #2
	LDR      r3, [r0, #8]
	LDR      r2, [r7, #8]
	STR      r3, [sp]
	ADD      r3, r6, #0
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
	MOV      r0, #0xff
	ADD      r0, #0x51
	LDR      r0, [r0, r4]
	CMP      r0, #0
	BEQ      |sub_0801D94C|
	MOV      r2, #1
	STR      r2, [sp, #0xc]
	MOV      r2, #0x1e
	MOV      r1, #1
	MOV      r6, #0x9e
	ADD      r3, r6, #0
	STR      r1, [sp, #8]
	STR      r2, [sp]
	MOV      r0, #2
	STR      r0, [sp, #4]
	MOV      r2, #2
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	STR      r0, [r5, #4]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #1
	STR      r2, [sp, #0xc]
	MOV      r2, #0x4b
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
	STR      r0, [r5, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x153f2_0x1a3f2| + 0xe16
	ADD      r1, r0, #0
	STR      r0, [r5, #0xc]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
