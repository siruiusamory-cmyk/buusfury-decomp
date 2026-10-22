	CODE16
|sub_08012588|
	PUSH     {r4, lr}
	SUB      sp, #0x38
	ADD      r3, sp, #0
	MOV      r2, #0
	STRH     r2, [r3, #0x34]
	LDR      r3, [pc, #0x44]
	STR      r1, [sp]
	ADD      r1, r0, #0
	ADD      r4, sp, #8
	ADD      r3, #4
	ADD      r0, r4, #0
	ADD      r2, sp, #0x34
	BL       |loc_0801246E|
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080125B4|
	LDR      r1, [pc, #0x2c]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_080125B4|
	BL       |inc_0x03d784_0x041118| + 0x11c
	LDR      r1, [pc, #0x18]
	MOV      r2, #0
	LDR      r0, [r1, #4]
	SUB      r0, #1
	STR      r0, [r1, #4]
	LDR      r0, [pc, #0x14]
	MOV      r1, #0x10
	LDR      r0, [r0]
	BL       |loc_08011C0C|
	ADD      sp, #0x38
	POP      {r4, pc}
|sub_080125D0|
|unk_080125D0|
	INCBIN	baserom.gba_0x125d0_0x125d2.extracted
