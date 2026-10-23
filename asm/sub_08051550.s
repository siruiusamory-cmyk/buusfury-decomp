	CODE16
|sub_08051550|
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	LDR      r0, [pc, #0x30]
	STR      r0, [r5]
	LDR      r4, [r5, #0xc]
	LDRB     r0, [r4]
	ADD      r0, #0xff
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	STRB     r0, [r4]
	BNE      |loc_08051580|
	LDRH     r0, [r4, #2]
	LDR      r1, [pc, #0x20]
	CMP      r0, r1
	BEQ      |loc_08051580|
	MOV      r3, #2
	LDR      r0, [pc, #0x1c]
	LDRSH    r1, [r4, r3]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
	MOV      r0, #0
	MVN      r0, r0
	STRH     r0, [r4, #2]
|loc_08051580|
	LDR      r0, [pc, #0x10]
	STR      r0, [r5]
	POP      {r3, r4, r5, pc}
|loc_08051586|
	DCW      0x0000
	DCW      0xaba0,0x0804,0xffff,0x0000,0x24f8,0x0807,0xe454
|loc_08051596|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_080515A6|
	BL       |GBARam_Free|
|loc_080515A6|
	POP      {r3, pc}
|sub_080515A8|
|unk_080515A8|
	INCBIN	baserom.gba_0x515a8_0x515aa.extracted
|sub_080515AA|
	DCW      0x0804
