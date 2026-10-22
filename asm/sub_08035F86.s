	CODE16
|sub_08035F86|
	LSR      r5, r6, #1
	ADD      r2, #0x74
	LSL      r0, r0, #0xc
	MOV      r0, #0
	STRH     r0, [r1, #0x12]
	MOV      r2, #0x38
	STRB     r2, [r1, #8]
	STRB     r0, [r1, #0x11]
	ADD      r1, #0xff
	ADD      r1, #0xc1
	STR      r0, [r1, #0xc]
	BX       lr
|sub_08035F9E|
|unk_08035F9E|
		PUSH {r3, lr}
		LDRH r2, [r1, #0x12]
		MOV r0, #1
		ADD r2, r2, r0
		LSL r2, r2, #0x10
		LSR r2, r2, #0x10
		STRH r2, [r1, #0x12]
		CMP r2, #8
		BHS      |loc_08035FB4|
		LSR r0, r2, #2
		B        |loc_08035FBC|
|loc_08035FB4|
		CMP r2, #0x8c
		BLO      |loc_08035FBC|
		SUB r2, #0x84
		ASR r0, r2, #2
|loc_08035FBC|
		LDRB r2, [r1, #0x11]
		CMP r2, r0
		BEQ      |loc_08035FDA|
		ADD r2, r1, #0
		ADD r2, #0xff
		ADD r2, #0xc1
		CMP r0, #1
		BNE      |sub_08035FD2|
		MOV r3, #1
		STR r3, [r2, #0xc]
		B        |loc_08035FDA|
