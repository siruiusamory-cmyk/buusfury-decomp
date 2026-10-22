	CODE16
|sub_08018752|
|unk_08018752|
		LDR r0, [r0, #0x10]
		CMP r0, #0
		BEQ      |loc_0801877E|
		LDR r4, [r0, #8]
		LDRB r0, [r4]
		ADD r0, #0xff
		LSL r0, r0, #0x18
		LSR r0, r0, #0x18
		STRB r0, [r4]
		BNE      |loc_0801877E|
		LDRH r0, [r4, #2]
		LDR r1, [pc, #0x1c]
		CMP r0, r1
		BEQ      |loc_0801877E|
		MOV r3, #2
		LDRSH r1, [r4, r3]
		LDR r0, [r2]
		BL       |loc_0801142A|
		MOV r0, #0
		MVN r0, r0
		STRH r0, [r4, #2]
|loc_0801877E|
		ADD r0, r6, #0
		B        |inc_0x153f2_0x1a3f2| + 0x335e
|loc_08018782|
|unk_08018782|
; cited by 0x080184DE (a pc-relative load targets 0x08018788)
		ADD r0, r6, #0
		B        |inc_0x153f2_0x1a3f2| + 0x335e
	INCBIN  baserom.gba_0x18786_0x187a2.extracted
|sub_080187A2|
|unk_080187A2|
	INCBIN	baserom.gba_0x187a2_0x187a6.extracted
	ADD      r1, r2, #0
	PUSH     {r3, lr}
	LDR      r2, [r2, #4]
	CMP      r2, #0
	BNE      |sub_080187B4|
	MOV      r0, #0
	POP      {r3, pc}
