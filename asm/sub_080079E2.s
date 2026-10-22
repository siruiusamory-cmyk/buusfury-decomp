	CODE16
|sub_080079E2|
|unk_080079E2|
		LDRB r0, [r4, #6]
		ADD r0, #0xff
		LSL r0, r0, #0x18
		LSR r0, r0, #0x18
		STRB r0, [r4, #6]
		BNE      |loc_08007A12|
		LDRB r0, [r4, #5]
		STRB r0, [r4, #6]
		BL       |loc_0803FAAC|
		MOV r6, #1
		LDRB r1, [r4, #4]
		LSL r6, r6, #0xf
		SUB r0, r0, r6
		MUL r0, r1
		ASR r0, r0, #0x13
		STR r0, [r4, #0xc]
		BL       |loc_0803FAAC|
		LDRB r1, [r4, #4]
		SUB r0, r0, r6
		MUL r0, r1
		ASR r0, r0, #0x13
		STR r0, [r4, #0x10]
|loc_08007A12|
		ADD r1, r4, #0
		ADD r1, #0xc
		LDR r0, [r5]
	INCBIN  baserom.gba_0x7a18_0x7a1a.extracted
|sub_08007A1A|
|unk_08007A1A|
	INCBIN	baserom.gba_0x7a1a_0x7a1e.extracted
	LSL      r0, r0, #0
	ADR      r7, |loc_08007AA4|
	LSR      r4, r0, #0x20
	LSL      r4, r6, #0x1f
	LSR      r7, r0, #0x20
	PUSH     {r3, lr}
	LDRB     r0, [r0, #4]
	LDR      r1, [pc, #0x28]
	MOV      r2, #1
	LSL      r0, r0, #0xb
	ADD      r0, r0, r1
	LSL      r2, r2, #0xb
	MOV      r1, #0
	BL       |inc_0x049120_0x055620| + 0xc
	POP      {r3, pc}
|sub_08007A3E|
|unk_08007A3E|
		BX       lr
