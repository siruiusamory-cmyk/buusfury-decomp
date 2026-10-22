	CODE16
|loc_08011C0C|
	PUSH     {r0, r1, r2, r4, r5, r6, r7, lr}
	SUB      sp, #8
	ADD      r6, r1, #0
	LDR      r1, [sp, #8]
	ADD      r7, r2, #0
	LDR      r4, [r1, #4]
	MOV      r5, #0
	SUB      r4, #1
	BMI      |loc_08011C40|
	LDR      r1, [sp, #8]
	ADD      r1, #4
	STR      r1, [sp, #4]
|loc_08011C24|
	LDR      r1, [sp, #4]
	LSL      r0, r4, #2
	ADD      r0, r0, r1
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x24]
	ADD      r3, r2, r1
	ADD      r2, r7, #0
	ADD      r1, r6, #0
	BL       |inc_0x046118_0x049114| + 0x98e
	ORR      r5, r0
	SUB      r4, #1
	BPL      |loc_08011C24|
|loc_08011C40|
	LDR      r0, [pc, #0x160]
	LDR      r1, [sp, #8]
	ADD      r1, r1, r0
	STR      r1, [sp]
	LDR      r4, [r1]
	SUB      r4, #1
	BMI      |loc_08011C6A|
|loc_08011C4E|
	LDR      r1, [sp]
	LSL      r0, r4, #2
	ADD      r0, r0, r1
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x24]
	ADD      r3, r2, r1
	ADD      r2, r7, #0
	ADD      r1, r6, #0
	BL       |inc_0x046118_0x049114| + 0x98e
	ORR      r5, r0
	SUB      r4, #1
	BPL      |loc_08011C4E|
|loc_08011C6A|
	ADD      r0, r5, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
