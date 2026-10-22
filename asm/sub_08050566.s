	CODE16
|sub_08050566|
	LSR      r4, r0, #0x20
	PUSH     {r3, lr}
	CMP      r0, #0
	BNE      |loc_08050578|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08050584|
|loc_08050578|
	MOV      r1, #0
	STR      r1, [r0, #4]
	MOV      r1, #0x10
	STR      r1, [r0, #8]
	LDR      r1, [pc, #4]
	STR      r1, [r0]
|loc_08050584|
	POP      {r3, pc}
	LSL      r0, r0, #0
	ADR      r4, |loc_0805086C|
	LSR      r4, r0, #0x20
	PUSH     {r3, lr}
	CMP      r0, #0
	BNE      |loc_0805059C|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080505AA|
|loc_0805059C|
	MOV      r1, #0xff
	ADD      r1, #1
	STR      r1, [r0, #4]
	MOV      r1, #0x10
	STR      r1, [r0, #8]
	LDR      r1, [pc, #4]
	STR      r1, [r0]
|loc_080505AA|
	POP      {r3, pc}
|sub_080505AC|
|unk_080505AC|
	INCBIN	baserom.gba_0x505ac_0x505ae.extracted
