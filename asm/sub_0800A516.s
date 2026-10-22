	CODE16
|sub_0800A516|
|unk_0800A516|
		LDR r1, [pc, #0x274]
		ADD r0, #0x38
		LDR r1, [r1]
		ADD r1, #0x80
		LDR r1, [r1, #0x28]
	INCBIN  baserom.gba_0xa520_0xa522.extracted
|sub_0800A522|
|unk_0800A522|
	INCBIN	baserom.gba_0xa522_0xa526.extracted
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x264]
	SUB      sp, #0x14
	LDR      r1, [r0]
	CMP      r1, #0
	BEQ      |sub_0800A560|
	ADD      r0, sp, #4
	BL       |sub_0800FDFA|
	LDR      r0, [sp, #4]
	LDR      r1, [r4, #0x40]
	CMP      r0, r1
	BGE      |sub_0800A560|
	LDR      r0, [r4, #0x38]
	LDR      r1, [sp, #0xc]
	CMP      r0, r1
	BGE      |sub_0800A560|
	LDR      r0, [sp, #8]
	LDR      r1, [r4, #0x44]
	CMP      r0, r1
	BGE      |sub_0800A560|
	LDR      r0, [r4, #0x3c]
	LDR      r1, [sp, #0x10]
	CMP      r0, r1
	BGE      |sub_0800A560|
	MOV      r0, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
