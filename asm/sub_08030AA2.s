	CODE16
|sub_08030AA2|
	LSL      r0, r0, #0
	STRH     r4, [r6, #0xe]
	LSR      r5, r6, #1
	BCS      |loc_08030AC4|
	LSR      r4, r0, #0x20
	LSR      r0, r2, #0x1e
	LSL      r0, r0, #0xc
	PUSH     {r4, r5, r6, lr}
	LDR      r5, [r1, #4]
	LDR      r1, [r0, #8]
	SUB      sp, #0x38
	ADD      r1, #1
	STR      r1, [r0, #8]
	LSL      r2, r1, #0x1d
	BNE      |loc_08030AD4|
	ASR      r4, r1, #3
	LDR      r2, [r0, #0x10]
|loc_08030AC4|
	MOV      r1, #1
	CMP      r2, #0
	BEQ      |sub_08030AD8|
	CMP      r4, #8
	BLT      |loc_08030AE4|
	MOV      r2, #0
	STR      r2, [r5, #0x1c]
	STR      r1, [r0, #0xc]
|loc_08030AD4|
	ADD      sp, #0x38
	POP      {r4, r5, r6, pc}
