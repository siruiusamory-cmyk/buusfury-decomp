	CODE16
|sub_08016C5C|
	LDR      r3, [pc, #0x6c]
	PUSH     {r4, lr}
	LDR      r1, [r3]
	LDRH     r2, [r1, #4]
	LSL      r1, r2, #0x1c
	LSR      r4, r1, #0x1f
	MOV      r1, #0
	CMP      r4, #0
	BEQ      |loc_08016C84|
	LDR      r4, [pc, #0x60]
	LDR      r0, [r3, #4]
	ADD      r3, r1, #0
	ADD      r1, r4, #0
	LDR      r4, [pc, #0x5c]
	MOV      r2, #0x40
	ADD      r0, r0, r4
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r0, #1
	POP      {r4, pc}
|loc_08016C84|
	LSL      r2, r2, #0x1a
	LSR      r4, r2, #0x1f
	ADD      r0, #0xff
	ADD      r0, #1
	MOV      r2, #1
	CMP      r4, #0
	BEQ      |loc_08016CA8|
	LDR      r4, [r0, #0x1c]
	CMP      r4, #0
	BEQ      |loc_08016CA8|
	STR      r1, [r0, #0x1c]
	STR      r1, [r0, #0x20]
	STR      r1, [r0, #0x24]
	LDR      r4, [r0, #0x14]
	STR      r2, [r4, #0x38]
	LDR      r4, [r0, #0x18]
	STR      r1, [r4, #0x38]
	STR      r1, [r0, #0x10]
|loc_08016CA8|
	LDR      r3, [r3]
	LDRH     r3, [r3, #4]
	LSL      r3, r3, #0x1b
	LSR      r3, r3, #0x1f
	BEQ      |loc_08016CC8|
	LDR      r3, [r0, #0x1c]
	CMP      r3, #1
	BEQ      |loc_08016CC8|
	STR      r1, [r0, #0x20]
	STR      r2, [r0, #0x1c]
	STR      r1, [r0, #0x24]
	LDR      r3, [r0, #0x14]
	STR      r1, [r3, #0x38]
	LDR      r3, [r0, #0x18]
	STR      r2, [r3, #0x38]
	STR      r1, [r0, #0x10]
|loc_08016CC8|
	MOV      r0, #0
	POP      {r4, pc}
|sub_08016CCC|
|unk_08016CCC|
	INCBIN	baserom.gba_0x16ccc_0x16cce.extracted
