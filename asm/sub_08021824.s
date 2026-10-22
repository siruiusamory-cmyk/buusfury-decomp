	CODE16
|sub_08021824|
|unk_08021824|
; cited by 0x08021756 (a pc-relative load targets 0x08021828)
		MOV r0, #0
		POP {r4, pc}
	INCBIN  baserom.gba_0x21828_0x21832.extracted
|sub_08021832|
|unk_08021832|
	INCBIN  baserom.gba_0x21832_0x21834.extracted
		PUSH {r4, lr}
	ADD      r4, r0, #0
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x34]
	LDR      r2, [r4, #0x2c]
	LDR      r0, [r0]
	SUB      sp, #8
	ADD      r0, #0x28
	LDR      r3, [r0]
	ADD      r1, #0x20
	SUB      r2, r2, r3
	LDR      r3, [r4, #0x30]
	LDR      r0, [r0, #4]
	STR      r2, [sp]
	SUB      r0, r3, r0
	STR      r0, [sp, #4]
	ADD      r0, r2, #0
	LDR      r2, [sp, #4]
	STMIA    r1!, {r0, r2}
	ADD      r0, r4, #0
	BL       |loc_08021762|
	CMP      r0, #0
	BNE      |sub_08021868|
	ADD      sp, #8
	POP      {r4, pc}
