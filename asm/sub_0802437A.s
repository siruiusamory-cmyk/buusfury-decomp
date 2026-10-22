	CODE16
|sub_0802437A|
|unk_0802437A|
		LDR r1, [r6, #0x20]
		STR r1, [sp, #4]
		LDR r1, [r6, #0x24]
		STR r1, [sp, #8]
		DCW     0xF019
		DCW     0xF919
		ADD r4, r0, #0
		BEQ      |loc_080243E4|
		LDR r0, [pc, #0x1cc]
		MOV r1, #0xff
		STR r0, [r4]
		ADD r1, #0x15
		STRB r5, [r1, r4]
		ADD r5, r4, #0
		ADD r5, #0xff
		ADD r5, #1
		STR r7, [r5, #0x1c]
		MOV r1, #0
		MVN r1, r1
		STR r7, [r5, #0x20]
		ADD r0, r4, #0
		MOV r2, #0x80
		ADD r0, #0x84
		STR r7, [r5, #0x18]
		BL       |sub_0804912C|
		MOV r2, #0x10
		MOV r1, #0
		ADD r0, r5, #4
		BL       |sub_0804912C|
		LDR r0, [pc, #0x1a0]
		LDR r1, [pc, #0x1b0]
		STR r0, [r5, #0x24]
		LDR r0, [pc, #0x1a0]
		STR r7, [r0]
		LDR r0, [pc, #0x1a0]
		STR r7, [r0]
		LDR r0, [pc, #0x1a0]
		STR r0, [r4]
		MOV r0, #0
		MVN r0, r0
		STR r7, [r5, #0x38]
		STR r0, [r1]
		LDR r0, [sp, #4]
		STR r0, [r5, #0x30]
		LDR r0, [sp, #8]
		STR r0, [r5, #0x34]
		MOV r0, #0xff
		ADD r0, #0x41
		STR r7, [r5, #0x3c]
		STR r7, [r0, r4]
		STR r7, [r1, #4]
|loc_080243E4|
		ADD r0, r4, #0
	INCBIN  baserom.gba_0x243e6_0x243e8.extracted
|sub_080243E8|
|unk_080243E8|
	INCBIN	baserom.gba_0x243e8_0x243ec.extracted
	PUSH     {r3, lr}
	BL       |sub_0802426E|
	POP      {r3, pc}
	LDR      r1, [pc, #0x168]
	PUSH     {r3, lr}
	LDR      r2, [r1]
	CMP      r2, #0
	BEQ      |sub_08024406|
	MOV      r0, #0
	STR      r0, [r1]
	MOV      r0, #1
	POP      {r3, pc}
