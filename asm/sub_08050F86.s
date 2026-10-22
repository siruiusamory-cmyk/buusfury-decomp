	CODE16
|sub_08050F86|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	STR      r1, [r0]
	BX       lr
	LSL      r0, r0, #0
	STR      r3, [sp, #0x390]
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	STR      r1, [r0]
	BX       lr
	LSL      r0, r0, #0
	STR      r3, [sp, #0x390]
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08050FBA|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08050FBA|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08050FC8|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08050FC8|
	POP      {r3, r4, r5, pc}
|loc_08050FCA|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0xe200,0x0874,0xe454
|loc_08050FDA|
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDR      r0, [pc, #0x3c]
	ADD      r6, r1, #0
	STR      r0, [r5]
	LDR      r4, [r5, #0xc]
	LDRB     r0, [r4]
	ADD      r0, #0xff
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	STRB     r0, [r4]
	BNE      |loc_0805100E|
	LDRH     r0, [r4, #2]
	LDR      r1, [pc, #0x2c]
	CMP      r0, r1
	BEQ      |loc_0805100E|
	MOV      r3, #2
	LDR      r0, [pc, #0x28]
	LDRSH    r1, [r4, r3]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
	MOV      r0, #0
	MVN      r0, r0
	STRH     r0, [r4, #2]
|loc_0805100E|
	LDR      r0, [pc, #0x1c]
	CMP      r6, #0
	STR      r0, [r5]
	BEQ      |loc_0805101C|
	ADD      r0, r5, #0
	BL       |GBARam_Free|
|loc_0805101C|
	POP      {r4, r5, r6, pc}
|loc_0805101E|
	DCW      0x0000
	DCW      0xaba0,0x0804,0xffff,0x0000,0x24f8,0x0807,0xe454
|loc_0805102E|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_0805104A|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_0805104A|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08051058|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051058|
	POP      {r3, r4, r5, pc}
|loc_0805105A|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0xe228,0x0874,0xe454
|loc_0805106A|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_0805107A|
	BL       |GBARam_Free|
|loc_0805107A|
	POP      {r3, pc}
|sub_0805107C|
|unk_0805107C|
	INCBIN	baserom.gba_0x5107c_0x5107e.extracted
