	CODE16
|sub_08041022|
	MOV      r5, #1
	STR      r6, [r4, #4]
	ADD      r0, r5, #0
	POP      {r4, r5, r6, pc}
	LDR      r1, [pc, #0xf8]
	LDR      r0, [r1]
	LDR      r2, [pc, #0xf8]
	LDR      r3, [r2]
	CMP      r0, r3
	BCS      |loc_0804103A|
	LDR      r0, [r1]
	STR      r0, [r2]
|loc_0804103A|
	LDR      r0, [pc, #0xe4]
	LDR      r0, [r0]
	LSL      r3, r0, #0x13
	BMI      |loc_08041056|
	LSL      r3, r0, #0x10
	BPL      |loc_08041052|
	LSL      r3, r0, #0x14
	LSR      r3, r3, #0x1c
	LSL      r0, r0, #0x1c
	LSR      r0, r0, #0x1c
	EOR      r3, r0
	BNE      |loc_08041056|
|loc_08041052|
	LDR      r0, [r1]
	STR      r0, [r2]
|loc_08041056|
	LDR      r0, [r1]
	LDR      r1, [r2]
	SUB      r0, r0, r1
	CMP      r0, #0xb4
	BCS      |sub_08041064|
	MOV      r0, #1
	BX       lr
