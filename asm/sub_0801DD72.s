	CODE16
|sub_0801DD72|
	MOV      r0, #0xff
	ADD      r0, #0x19
	LDR      r4, [r5, #0x14]
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801DD9A|
	LDR      r1, [pc, #0x210]
	MOV      r3, #0
	STMIA    r0!, {r1, r3}
	SUB      r0, #8
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r3, [r1, #0xc]
	STR      r3, [r1, #8]
	LDR      r2, [pc, #0x208]
	STR      r3, [r1, #0x10]
	STR      r2, [r0]
	STR      r4, [r1, #0x14]
|loc_0801DD9A|
	BL       |inc_0x03d784_0x041118| + 0xcc
	MOV      r0, #1
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0801DDA2|
|unk_0801DDA2|
	INCBIN  baserom.gba_0x1dda2_0x1ddec.extracted
|loc_0801DDEC|
		B        |loc_0801DF7E|
	INCBIN  baserom.gba_0x1ddee_0x1df7e.extracted
|loc_0801DF7E|
		MOV r0, #0
		DCW     0xE70E
	CODE16
|dat_0801DF82|
	DCW      0x0000
	DCW      0xe9d8
	DCW      0x0871
	DCW      0x82ec
	DCW      0x086f
	DCW      0x9488
	DCW      0x0831
	DCW      0x05c4
	DCW      0x0000
	DCW      0x920c
	DCW      0x0804
	DCW      0xa8c8
	DCW      0x0804
	DCW      0x9588
	DCW      0x0804
|unk_0801DFA0|
	INCBIN	baserom.gba_0x1dfa0_0x1dfa2.extracted
	LSR      r4, r0, #0x20
	LDR      r0, [sp, #0x3c0]
	LSR      r4, r0, #0x20
	ADD      r4, r2, r4
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #0x24]
	PUSH     {r4, lr}
	LDR      r1, [r0]
	LDRH     r1, [r1, #4]
	LSL      r1, r1, #0x1c
	LSR      r1, r1, #0x1f
	BEQ      |sub_0801DFCE|
	LDR      r0, [r0, #4]
	LDR      r4, [pc, #0x1c]
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r0, r4
	LDR      r1, [pc, #0x10]
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r0, #1
	POP      {r4, pc}

