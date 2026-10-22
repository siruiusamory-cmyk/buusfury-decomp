	CODE16
|sub_08027BE6|
	PUSH     {r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	LDR      r1, [r0, #0x1c]
	SUB      sp, #0x24
	ADD      r0, sp, #0xc
	BL       |inc_0x0158_0x143f2| + 0xfcdc
	LDR      r0, [sp, #0xc]
	LDR      r1, [sp, #0x14]
	LDR      r3, [sp, #0x18]
	ADD      r1, r0, r1
	LDR      r0, [sp, #0x10]
	STR      r1, [sp, #4]
	ADD      r0, r0, r3
	STR      r0, [sp, #8]
	ASR      r1, r1, #1
	ASR      r0, r0, #1
	STR      r1, [sp, #4]
	STR      r1, [sp, #0x1c]
	ADD      r1, r5, #0
	STR      r0, [sp, #8]
	STR      r0, [sp, #0x20]
	ADD      r0, r4, #0
	ADD      r2, sp, #0x1c
	BL       |sub_08027B4C|
	ADD      sp, #0x24
	POP      {r4, r5, pc}
|sub_08027C20|
|unk_08027C20|
		ADD r2, r0, #0
		ADD r2, #0x1c
		B        |sub_08027B4C|
