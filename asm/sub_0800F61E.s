	CODE16
|sub_0800F61E|
|unk_0800F61E|
; cited by 0x0800F5BC (a pc-relative load targets 0x0800F624)
		BL       |inc_0x0158_0x143f2| + 0xf368
		B        |inc_0x0158_0x143f2| + 0xf4c4
	INCBIN  baserom.gba_0xf624_0xf62c.extracted
		PUSH {r4, r5, r6, r7, lr}
		ADD r4, r0, #0
		LDR r1, [r4, #8]
		LDR r0, [pc, #0x2c8]
		LDR r2, [r4, #0xc]
		SUB sp, #0xdc
		STMIA r0!, {r1, r2}
		LDR r1, [r4, #0x10]
		LDR r2, [pc, #0x2c0]
		LDR r5, [pc, #0x2c8]
		STR r1, [r2]
		LDR r0, [r4, #0x14]
		STR r0, [r2, #4]
		LDR r0, [pc, #0x2bc]
		LDR r3, [r4, #0x20]
		LDR r0, [r0]
		ADD r1, r0, #4
		LDR r6, [r1]
		MOV r0, #0
		CMP r6, #0
		BLE      |inc_0x0158_0x143f2| + 0xf512
|loc_0800F656|
		LSL r2, r0, #2
		ADD r2, r2, r1
		LDR r2, [r2, #4]
		CMP r2, r3
		BEQ      |sub_0800F668|
		ADD r0, #1
		CMP r6, r0
		BGT      |loc_0800F656|
		B        |inc_0x0158_0x143f2| + 0xf512
