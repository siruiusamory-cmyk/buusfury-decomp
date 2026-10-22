	CODE16
|sub_0803B934|
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	LDR      r0, [pc, #0x2e0]
	ADD      r4, r1, #0
	LDR      r0, [r0]
	SUB      sp, #0x44
	ADD      r0, #0xff
	ADD      r0, #0xa1
	LDR      r1, [r0, #4]
	LDR      r2, [r0]
	STR      r1, [sp, #0x40]
	STR      r2, [sp, #0x3c]
	LDR      r2, [sp, #0x44]
	ADD      r5, r4, #0
	ADD      r2, #0xc
	LDMIA    r2!, {r1}
	ADD      r5, #0xff
	STR      r1, [r0]
	LDR      r2, [r2]
	ADD      r5, #0xa1
	STR      r2, [r0, #4]
	LDR      r2, [r0]
	LDR      r3, [r0, #4]
	ASR      r2, r2, #8
	ASR      r3, r3, #8
	STR      r3, [sp, #0x20]
	STR      r3, [sp, #0x28]
	STR      r2, [sp, #0x1c]
	STR      r2, [sp, #0x24]
	LDR      r2, [r5]
	LDR      r3, [r5, #4]
	ASR      r2, r2, #8
	ASR      r3, r3, #8
	STR      r2, [sp, #0x2c]
	STR      r3, [sp, #0x20]
	STR      r3, [sp, #0x30]
	STR      r2, [sp, #0x1c]
	LDR      r2, [sp, #0x24]
	LDR      r3, [sp, #0x2c]
	LDR      r7, [sp, #0x30]
	SUB      r2, r2, r3
	LDR      r3, [sp, #0x28]
	ADD      r6, r5, #4
	SUB      r3, r3, r7
	ADD      r7, r2, #0
	ADD      r1, r0, #4
	CMP      r2, #0
	STR      r3, [sp, #0x20]
	STR      r3, [sp, #0x38]
	STR      r2, [sp, #0x1c]
	STR      r2, [sp, #0x34]
	BGE      |loc_0803B99C|
|unk_0803B99A|
	INCBIN	baserom.gba_0x3b99a_0x3b99c.extracted
