	CODE16
|sub_08042D00|
|unk_08042D00|
		LDRB r5, [r4, #4]
		MOV r2, #8
		SUB r5, #5
		CMP r5, #0xe
		BHS      |sub_08042D72|
		ADR      r3, |loc_08042D14|
		LDRB r3, [r3, r5]
		LSL r3, r3, #1
		ADD pc, r3
		LSL r0, r0, #0
|loc_08042D14|
		LSR r7, r0, #0xc
		ADD r2, #0xb
		ASR r7, r1, #0xc
		ASR r3, r2, #0x1c
		SUB r3, r3, r4
		ADD r2, r6, #4
		CMP r4, #0x2c
		STRB r2, [r4, #4]
		STRB r1, [r4, #5]
		MOV r0, #0x13
		B        |inc_0x042118_0x049114| + 0xc60
	INCBIN  baserom.gba_0x42d2a_0x42d72.extracted
