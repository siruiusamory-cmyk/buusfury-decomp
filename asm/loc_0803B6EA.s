	CODE16
|loc_0803B6EA|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	ADD      r7, r0, #0
	ADD      r0, r1, #0
	ADD      r0, #0xff
	ADD      r0, #0xa1
	ADD      r4, r1, #0
	LDR      r1, [r0, #4]
	LDR      r2, [r0]
	SUB      sp, #0x4c
	STR      r1, [sp, #0x48]
	LDR      r1, [sp, #0x54]
	STR      r2, [sp, #0x44]
	SUB      r1, r1, r2
	LDR      r2, [sp, #0x58]
	LDR      r3, [sp, #0x48]
	STR      r1, [sp, #0x24]
	SUB      r2, r2, r3
	STR      r2, [sp, #0x28]
	STR      r2, [sp, #0x30]
	CMP      r1, #0
	STR      r1, [sp, #0x2c]
	BLT      |sub_0803B71A|
	LDR      r1, [sp, #0x2c]
	B        |sub_0803B71E|
