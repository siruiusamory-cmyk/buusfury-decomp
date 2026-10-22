	CODE16
|sub_08030950|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r1, #0
	LDR      r1, [pc, #0x94]
	LSL      r0, r0, #2
	LDR      r4, [r1, r0]
	LDR      r6, [pc, #0x80]
	ADD      r1, r4, #0
	LDR      r0, [r6, #4]
	BL       |inc_0x03d784_0x041118| + 0x2864
	ADD      r0, #0x21
	LSR      r5, r0, #5
	LSL      r5, r5, #5
	LSL      r1, r5, #4
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x115da
	ADD      r3, r7, #0
	ADD      r2, r4, #0
	ADD      r1, r5, #0
	MOV      r0, #0
	BL       |loc_08030860|
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, r7}
	LDR      r2, [r1]
	LDR      r4, [r0, #0x10]
	MOV      r3, #0
	CMP      r4, #0
	BLE      |loc_080309CE|
	MOV      r6, #3
	LDR      r7, [pc, #0x60]
	LSL      r6, r6, #0xa
|loc_08030992|
	STR      r7, [r2]
	LDR      r4, [r0, #0x14]
	ADD      r4, r4, r3
	LSL      r4, r4, #0x17
	LSR      r4, r4, #7
	ORR      r4, r7
	STR      r4, [r2]
	LDR      r5, [r0, #0x18]
	LSR      r4, r4, #8
	LSL      r5, r5, #0x18
	LSR      r5, r5, #0x18
	LSL      r4, r4, #8
	ORR      r4, r5
	STR      r4, [r2]
	LDRH     r4, [r0, #0xc]
	ASR      r5, r3, #1
	ADD      r3, #0x20
	ADD      r4, r4, r5
	LDR      r5, [r2, #4]
	LSL      r4, r4, #0x16
	LSR      r5, r5, #0xa
	LSL      r5, r5, #0xa
	LSR      r4, r4, #0x16
	ORR      r4, r5
	BIC      r4, r6
	STR      r4, [r2, #4]
	LDR      r4, [r0, #0x10]
	ADD      r2, #8
	CMP      r4, r3
	BGT      |loc_08030992|
|loc_080309CE|
	STR      r2, [r1]
	POP      {r4, r5, r6, r7}
	MOV      r0, #0
	BX       lr
|loc_080309D6|
	DCW      0x0000
	DCW      0x9680,0x0804,0x81e4,0x0875,0xaf78,0x0804,0xf70d
|loc_080309E6|
	LSR      r3, r0, #0x20
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	STR      r0, [r0]
	STRH     r0, [r0]
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_08030A0C|
	MOV      r0, #0x30
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08030A0C|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
