	CODE16
|sub_08007C12|
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	LDR      r3, [pc, #0x258]
	LDR      r5, [pc, #0x25c]
	ADD      sp, r3
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x258]
	LDMIA    r5!, {r1, r2, r3, r5}
	ADD      r0, sp
	STMIA    r0!, {r1, r2, r3, r5}
	SUB      r0, #0x10
	MOV      r5, #0
	MOV      r1, #0
|loc_08007C2A|
	MOV      r3, #1
	LSL      r3, r3, #0xb
	ADD      r3, sp
	LDR      r2, [r3, #0x20]
	LDR      r0, [r2, #4]
	ADD      r0, r0, r1
	MOV      ip, r0
	BMI      |loc_08007C42|
	LDR      r2, [r4, #8]
	LDRB     r2, [r2, #0x15]
	CMP      ip, r2
	BLT      |sub_08007C4C|
|loc_08007C42|
	LSL      r2, r1, #1
	MOV      r0, #3
	LSL      r0, r2
	ORR      r5, r0
	B        |loc_08007C98|
