	CODE16
|loc_0804251E|
|unk_0804251E|
; cited by 0x08042240 (a pc-relative load targets 0x08042564)
		MOV r7, #0x13
		CMP r6, #0x32
		BEQ      |inc_0x042118_0x049114| + 0x4d8
		BGT      |loc_08042550|
		LDR r1, [pc, #0x138]
		ADD r1, #0x10
		CMP r6, #0x20
		BEQ      |inc_0x042118_0x049114| + 0x4ec
		CMP r6, #0x21
		BEQ      |inc_0x042118_0x049114| + 0x4ee
		CMP r6, #0x27
		BNE      |sub_080425B0|
		CMP r4, #0
		BNE      |sub_080425B0|
		CMP r0, #0x16
		BNE      |inc_0x042118_0x049114| + 0x4f0
		LDRB r0, [r5, #0x11]
		MOV r7, #1
		STRB r0, [r5, #4]
		LDRB r0, [r5, #0x12]
		STRB r0, [r5, #5]
		STRB r7, [r5, #2]
		MOV r1, #0
		MOV r0, #0x41
		B        |inc_0x042118_0x049114| + 0x75e
|loc_08042550|
		CMP r6, #0x33
		BEQ      |inc_0x042118_0x049114| + 0x520
		CMP r6, #0x34
		BEQ      |inc_0x042118_0x049114| + 0x522
		CMP r6, #0x3d
		BNE      |sub_080425B0|
		CMP r4, #0
		BNE      |sub_080425B0|
		MOV r7, #0
		STRB r7, [r5, #5]
		MOV r1, #0
		MOV r0, #0x42
		STRB r7, [r5, #4]
		B        |inc_0x042118_0x049114| + 0x75e
	INCBIN  baserom.gba_0x4256c_0x42592.extracted
