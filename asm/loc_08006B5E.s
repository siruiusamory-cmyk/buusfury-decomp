	CODE16
|loc_08006B5E|
	PUSH     {r4, lr}
	LDRB     r1, [r0]
	SUB      sp, #0x10
	ADD      r3, sp, #0
	STRB     r1, [r3]
	LDRB     r1, [r0, #1]
	MOV      r4, sp
	STRB     r1, [r3, #1]
	LDRB     r1, [r0, #2]
	STRB     r1, [r3, #2]
	LDRB     r1, [r0, #3]
	STRB     r1, [r3, #3]
	MOV      r1, #4
	BL       |inc_0x03d784_0x041118| + 0x24ca
	LDR      r1, [pc, #0x1c]
	MOV      r3, #8
	ADD      r0, r0, r1
	STR      r0, [sp, #4]
	LDR      r0, [pc, #0xc]
	ADD      r2, r4, #0
	MOV      r1, #0
	LDR      r0, [r0]
	BL       |inc_0x03d784_0x041118| + 0x245a
	ADD      sp, #0x10
	POP      {r4, pc}
|sub_08006B94|
|unk_08006B94|
	INCBIN	baserom.gba_0x6b94_0x6b96.extracted
