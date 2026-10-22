	CODE16
|sub_080378B6|
|unk_080378B6|
		MOV r1, #1
		ADD r0, #0x40
		STRB r1, [r0]
		LDR r0, [r2]
		LDR r5, [pc, #0x100]
		LDR r2, [pc, #0x100]
		ADD r1, r5, #0
		ADD r1, #0x24
		ADD r0, r0, r2
		ADD r4, r0, #0
		BL       |inc_0x03d784_0x041118| + 0xb7e
		ADD r1, r5, #0
		ADD r1, #0xff
		ADD r1, #0x81
		MOV r3, #0
		MOV r2, #0x40
		ADD r0, r4, #0
	INCBIN  baserom.gba_0x378da_0x378dc.extracted
|sub_080378DC|
|unk_080378DC|
	INCBIN	baserom.gba_0x378dc_0x378e0.extracted
	PUSH     {r3, lr}
	MOV      r1, #0x40
	LDRB     r1, [r1, r0]
	CMP      r1, #2
	BNE      |sub_080378EE|
	MOV      r0, #0
	POP      {r3, pc}
|sub_080378EE|
|unk_080378EE|
	INCBIN	baserom.gba_0x378ee_0x378f0.extracted
|sub_080378F0|
|unk_080378F0|
	INCBIN	baserom.gba_0x378f0_0x378f4.extracted
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	CMP      r1, #0
	SUB      sp, #0x28
	BNE      |loc_080379B2|
	MOV      r0, #0x40
	LDRB     r0, [r0, r4]
	CMP      r0, #1
	BNE      |loc_080379AE|
	LDR      r0, [r2, #0x30]
	CMP      r0, r4
	BNE      |sub_08037912|
	MOV      r0, #0
	ADD      sp, #0x28
	POP      {r4, r5, r6, pc}
