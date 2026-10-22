	CODE16
|sub_0802736A|
|unk_0802736A|
		LDR r1, [r0, #0x58]
		LDRB r2, [r1]
		CMP r2, #1
		DCW     0xD9FA
		LDR r1, [r1, #0x58]
		CMP r1, #0
		DCW     0xD0F7
|loc_08027378|
|unk_08027378|
		LDR r1, [pc, #0x10]
	INCBIN  baserom.gba_0x2737a_0x2737c.extracted
|sub_0802737C|
|unk_0802737C|
	INCBIN	baserom.gba_0x2737c_0x27380.extracted
	SUB      r4, r1, r4
	LSL      r0, r0, #0xc
	LDMIA    r6!, {r2, r3, r4, r5, r6}
	LSR      r4, r0, #0x20
	BCC      |loc_08027444|
	LSR      r4, r6, #1
	SUB      r0, r3, r5
	LSL      r0, r0, #0xc
|loc_08027390|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_080273AA|
	MOV      r0, #0xff
	ADD      r0, #0x91
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080273AA|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
