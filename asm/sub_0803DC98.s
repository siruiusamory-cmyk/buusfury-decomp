	CODE16
|sub_0803DC98|
	PUSH     {r4, r5, lr}
	SUB      sp, #0x1fc
	SUB      sp, #8
	ADD      r5, r0, #0
	ADD      r0, sp, #0x218
	STR      r0, [sp, #0x200]
	MOV      r0, sp
	ADD      r2, sp, #0x200
	MOV      r4, sp
	LDR      r1, [sp, #0x214]
	BL       |sub_0803DB7C|
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |loc_0803DADA|
	ADD      sp, #0x1fc
	ADD      sp, #8
	POP      {r4, r5}
	POP      {r3}
	ADD      sp, #0x10
	BX       r3
