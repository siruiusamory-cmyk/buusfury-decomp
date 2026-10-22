	CODE16
|sub_080097A6|
	LDMIA    r1!, {r3}
	STR      r3, [r0, #0x30]
	LDR      r1, [r1]
	STR      r1, [r0, #0x34]
	LDR      r1, [r0]
	ADD      r1, r1, r3
	ASR      r1, r1, #0xa
	STR      r1, [r0, #0x28]
	LDR      r1, [r0, #4]
	LDR      r2, [r0, #0x34]
	ADD      r1, r1, r2
	ASR      r1, r1, #0xa
	STR      r1, [r0, #0x2c]
	BX       lr
