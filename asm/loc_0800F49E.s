	CODE16
|loc_0800F49E|
|unk_0800F49E|
		LDR r0, [r4, #0x58]
		CMP r0, r2
		BNE      |loc_0800F4A8|
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0xf2e8
|loc_0800F4A8|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0xf2e8
|loc_0800F4AC|
|unk_0800F4AC|
		ADD r0, r5, #0
		B        |inc_0x0158_0x143f2| + 0xf2e8
	INCBIN  baserom.gba_0xf4b0_0xf4b2.extracted
|sub_0800F4B2|
|unk_0800F4B2|
	INCBIN	baserom.gba_0xf4b2_0xf4b6.extracted
	LSL      r1, r0, #0x18
	SUB      r0, r5, r6
	LSL      r0, r0, #0xc
	MOV      r5, #0xf0
	LSR      r7, r0, #0x20
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |loc_0800F4DA|
	CMP      r4, #0xe
	BLT      |sub_0800F4E2|
	MOV      r0, #2
	POP      {r4, pc}
|loc_0800F4DA|
	CMP      r4, #0xd
	BLT      |sub_0800F4E2|
	MOV      r0, #2
	POP      {r4, pc}
