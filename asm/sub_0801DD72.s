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
