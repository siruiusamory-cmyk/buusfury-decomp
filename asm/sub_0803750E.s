	CODE16
|sub_0803750E|
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x364]
	ADD      r6, r1, #0
	LDR      r1, [pc, #0x374]
	STR      r0, [r4]
	LDRB     r0, [r1]
	LDR      r5, [pc, #0x360]
	ADD      r0, #0xff
	STRB     r0, [r1]
	MOV      r0, #0x40
	LDRB     r1, [r0, r4]
	LDR      r0, [pc, #0x360]
	LDR      r2, [r5]
	ADD      r0, r2, r0
	LDR      r2, [pc, #0x354]
	SUB      r2, #0x24
	CMP      r1, #0
	BEQ      |sub_08037564|
	CMP      r1, #1
	BNE      |loc_08037542|
	ADD      r1, r2, #0
	ADD      r1, #0xff
	ADD      r1, #0x81
	BL       |inc_0x03d784_0x041118| + 0xb7e
|loc_08037542|
	LDR      r0, [pc, #0x34c]
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x348]
	CMP      r1, r0
	BEQ      |loc_08037554|
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08037554|
	LDR      r0, [pc, #0x340]
	CMP      r6, #0
	STR      r0, [r4]
	BEQ      |loc_08037562|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08037562|
	POP      {r4, r5, r6, pc}
