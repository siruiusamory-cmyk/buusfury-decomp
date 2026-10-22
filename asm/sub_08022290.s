	CODE16
|sub_08022290|
	ADD      r0, #1
	CMP      ip, r0
	BGT      |loc_080221B6|
	LDR      r0, [r5]
	MOV      r4, #0
	CMP      r0, #0
	BLE      |loc_080222B6|
|loc_0802229E|
	LSL      r0, r4, #2
	ADD      r0, r0, r5
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r5]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_0802229E|
|loc_080222B6|
	LDR      r7, [pc, #0x24]
	LDR      r0, [r7, #4]
	BL       |inc_0x0158_0x143f2| + 0x11458
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, lr}
	LDR      r4, [pc, #0x14]
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x11426
	LDR      r0, [r4]
	LDRH     r0, [r0, #2]
	LSL      r0, r0, #0x1e
	ASR      r0, r0, #0x1f
	ADD      r0, #1
	POP      {r4, pc}
	BCS      |loc_0802239C|
	LSR      r4, r0, #0x20
	ADD      r6, pc, #0x3E0
	LSR      r2, r6, #1
|loc_080222E0|
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	SUB      sp, #4
	ADD      r4, r0, #0
	BNE      |sub_080222F8|
	MOV      r0, #0x3c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080222F8|
	ADD      r0, r4, #0
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
