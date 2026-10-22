	CODE16
|loc_08008598|
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	SUB      sp, #0x1fc
	SUB      sp, #0x1fc
	SUB      sp, #0x34
	ADD      r7, sp, #0x3fc
	ADD      r4, r0, #0
	ADD      r7, #8
	MOV      r6, #0
	MVN      r6, r6
	ADD      r3, sp, #0x3fc
	LDR      r0, [r3, #0x34]
	LDR      r0, [r0, #4]
	ADD      r2, r0, r6
	LDR      r0, [r4, #4]
	LDRB     r0, [r0, #5]
	BPL      |sub_080085BC|
	ADD      r2, r2, r0
	B        |sub_080085C2|
