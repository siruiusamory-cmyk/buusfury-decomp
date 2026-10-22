	CODE16
|sub_08035D94|
	LDR      r2, [sp, #0x24]
	LDR      r1, [sp, #0x28]
	SUB      r2, #3
	ADD      r0, r0, r6
	SUB      r1, #0xf
	STR      r2, [sp, #0x14]
	STR      r2, [sp, #0x1c]
	MOV      r2, #0x37
	STR      r1, [sp, #0x20]
	STR      r0, [sp]
	STR      r2, [sp, #8]
	STR      r1, [sp, #0x18]
	MOV      r3, #4
	MOV      r0, #0
	ADD      r1, sp, #0x1c
	LDR      r2, [pc, #0x24]
	STR      r7, [sp, #4]
	BL       |inc_0x1c3f2_0x2ab4c| + 0xe42a
	LDR      r6, [pc, #0x18]
	ADD      r1, r0, #0
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	STRB     r5, [r4, #0x11]
	ADD      sp, #0x2c
	POP      {r4, r5, r6, r7, pc}
|sub_08035DCA|
|unk_08035DCA|
	INCBIN	baserom.gba_0x35dca_0x35dce.extracted
