	CODE16
|sub_0801794C|
	PUSH     {r3, lr}
	LDR      r1, [r0, #0x10]
	ADD      r1, #1
	STR      r1, [r0, #0x10]
	LSL      r1, r1, #0x1c
	BPL      |sub_0801795C|
	MOV      r0, #0
	POP      {r3, pc}
