	CODE16
|sub_0803B4FC|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #0x54
	ADD      r4, r1, #0
	ADD      r1, sp, #0x78
	LDMIA    r1!, {r0, r1}
	STR      r0, [sp, #0x4c]
	STR      r0, [sp, #0x44]
	STR      r1, [sp, #0x50]
	STR      r1, [sp, #0x48]
	LDR      r1, [sp, #0x78]
	LDR      r0, [sp, #0x7c]
	STR      r1, [sp, #0x40]
|unk_0803B514|
	INCBIN	baserom.gba_0x3b514_0x3b516.extracted
	STR      r0, [sp, #0x3c]
	ADD      r1, sp, #0x78
	STR      r3, [sp, #0x28]
	STR      r3, [sp, #0x30]
	STR      r2, [sp, #0x24]
	STR      r2, [sp, #0x2c]
	LDMIA    r1!, {r0, r1}
|unk_0803B524|
	INCBIN	baserom.gba_0x3b524_0x3b526.extracted
	MOV      r6, #0
	MOV      r5, #0
	MOV      r7, #0xff
	STR      r0, [sp, #0x38]
	STR      r1, [sp, #0x34]
|loc_0803B530|
	LDR      r0, [sp, #0x2c]
	LDR      r1, [sp, #0x3c]
	ADD      r0, r0, r1
	STR      r0, [sp, #0x2c]
	LDR      r0, [sp, #0x30]
	LDR      r1, [sp, #0x40]
	ADD      r0, r0, r1
	STR      r0, [sp, #0x30]
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x54]
	ADD      r2, r2, r1
	ADD      r1, sp, #0x2c
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BNE      |sub_0803B57E|
	LDR      r0, [sp, #0x2c]
	LDR      r1, [sp, #0x3c]
	SUB      r0, r0, r1
	STR      r0, [sp, #0x2c]
	LDR      r0, [sp, #0x30]
	LDR      r1, [sp, #0x40]
	SUB      r0, r0, r1
	STR      r0, [sp, #0x30]
	LDR      r0, [sp, #0x3c]
	STR      r1, [sp, #0x20]
	STR      r0, [sp, #0x1c]
	LDR      r0, [sp, #0x4c]
	LDR      r1, [sp, #0x50]
|unk_0803B56C|
	INCBIN	baserom.gba_0x3b56c_0x3b56e.extracted
	STR      r0, [sp, #0x3c]
	LDR      r0, [sp, #0x1c]
|unk_0803B572|
	INCBIN	baserom.gba_0x3b572_0x3b574.extracted
	STR      r1, [sp, #0x40]
	STR      r0, [sp, #0x4c]
	LDR      r0, [sp, #0x20]
	STR      r0, [sp, #0x50]
	B        |sub_0803B5AA|
