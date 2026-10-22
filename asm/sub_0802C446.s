	CODE16
|sub_0802C446|
	PUSH     {r3, lr}
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0802C456|
	LDR      r1, [pc, #0xc]
	STR      r1, [r0]
|loc_0802C456|
	POP      {r3, pc}
	LDR      r1, [pc, #0xe0]
	LSR      r5, r6, #1
	BLS      |loc_0802C400|
	LSR      r7, r5, #1
	POP      {r3, r4, r7, pc}
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	LDR      r0, [pc, #0x50]
	SUB      sp, #0x10
	ADD      r4, r1, #0
	LDR      r0, [r0]
	MOV      r1, #0
	LDR      r2, [pc, #0x48]
	STR      r1, [sp, #8]
	CMP      r4, #0
	STR      r0, [sp, #0xc]
	STR      r2, [sp, #4]
	BEQ      |loc_0802C482|
	ADD      r1, r4, #0
	ADD      r1, #0xff
	ADD      r1, #0x8d
|loc_0802C482|
	ADD      r0, sp, #4
	BL       |inc_0x153f2_0x1a3f2| + 0x5aa
	MOV      r1, #0x12
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #0x2c]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r0, [pc, #0x28]
	STR      r0, [sp, #4]
	LDR      r0, [sp, #8]
	CMP      r0, #0
	BEQ      |loc_0802C4AE|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0802C4AE|
	ADD      sp, #0x10
	POP      {r4, pc}
	LDR      r0, [pc, #0xc]
	SUB      r0, #4
	BX       lr
|sub_0802C4B8|
|unk_0802C4B8|
	INCBIN	baserom.gba_0x2c4b8_0x2c4ba.extracted
