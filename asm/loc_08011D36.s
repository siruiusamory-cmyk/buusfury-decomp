	CODE16
|loc_08011D36|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	MOV      r0, #0
	SUB      sp, #0x84
	STR      r0, [sp]
	ADD      r0, sp, #4
	MOV      r7, sp
	MOV      r2, #0x80
	LDR      r1, [pc, #0x64]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #0x61
	LSL      r0, r0, #4
	ADD      r5, r5, r0
	LDR      r0, [r5]
	MOV      r4, #0
	CMP      r0, #0
	BLE      |loc_08011D96|
|loc_08011D5A|
	LSL      r0, r4, #2
	ADD      r6, r0, r5
	ADD      r6, #4
	LDR      r0, [r6]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |loc_08011D7E|
	LDR      r0, [r6]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	B        |loc_08011D8E|
|loc_08011D7E|
	LDR      r1, [r6]
	LDR      r0, [sp]
	LDR      r2, [sp]
	ADD      r0, #1
	STR      r0, [sp]
	LSL      r0, r2, #2
	ADD      r0, r0, r7
	STR      r1, [r0, #4]
|loc_08011D8E|
	LDR      r0, [r5]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_08011D5A|
|loc_08011D96|
	MOV      r2, #0x84
	ADD      r1, r7, #0
	ADD      r0, r5, #0
	BL       |inc_0x046118_0x049114| + 0xcb8
	ADD      sp, #0x84
	POP      {r4, r5, r6, r7, pc}
|sub_08011DA4|
|unk_08011DA4|
	INCBIN	baserom.gba_0x11da4_0x11da6.extracted
