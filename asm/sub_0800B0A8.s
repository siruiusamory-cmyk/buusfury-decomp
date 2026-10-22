	CODE16
|sub_0800B0A8|
	PUSH     {r3, r4, r5, lr}
	LDR      r2, [pc, #0x264]
	ADD      r4, r0, #0
	LDR      r0, [r2]
	LDRH     r0, [r0, #4]
	LSL      r1, r0, #0x1f
	BNE      |loc_0800B0BC|
	LSL      r0, r0, #0x1e
	LSR      r0, r0, #0x1f
	BEQ      |loc_0800B0C0|
|loc_0800B0BC|
	MOV      r0, #1
	B        |loc_0800B0C2|
|loc_0800B0C0|
	MOV      r0, #0
|loc_0800B0C2|
	STR      r0, [r4, #0x30]
	LDR      r3, [r4, #0x38]
	CMP      r3, #0
	BEQ      |loc_0800B0F4|
	LDR      r1, [r2]
	LDRH     r1, [r1, #4]
	LSL      r1, r1, #0x19
	LSR      r1, r1, #0x1f
	BEQ      |loc_0800B0DE|
	LDR      r1, [r4, #0x34]
	CMP      r1, #0
	BEQ      |loc_0800B0DE|
	SUB      r1, #1
	STR      r1, [r4, #0x34]
|loc_0800B0DE|
	LDR      r1, [r2]
	LDRH     r1, [r1, #4]
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x1f
	BEQ      |loc_0800B0F4|
	LDR      r1, [r4, #0x34]
	SUB      r3, #1
	CMP      r1, r3
	BGE      |loc_0800B0F4|
	ADD      r1, #1
	STR      r1, [r4, #0x34]
|loc_0800B0F4|
	LDR      r1, [r2]
	LDRH     r1, [r1, #2]
	LSL      r1, r1, #0x16
	LSR      r1, r1, #0x1f
	BEQ      |loc_0800B108|
	LDR      r1, [r4, #0x60]
	CMP      r1, #0x22
	BLE      |loc_0800B108|
	SUB      r1, #2
	STR      r1, [r4, #0x60]
|loc_0800B108|
	LDR      r1, [r2]
	LDRH     r1, [r1, #2]
	LSL      r1, r1, #0x17
	LSR      r1, r1, #0x1f
	BEQ      |loc_0800B11C|
	LDR      r1, [r4, #0x60]
	CMP      r1, #0x7e
	BGE      |loc_0800B11C|
	ADD      r1, #2
	STR      r1, [r4, #0x60]
|loc_0800B11C|
	LDR      r1, [r2, #8]
	MOV      r5, #1
	LDRB     r1, [r1]
	CMP      r1, #4
	BGE      |sub_0800B140|
	CMP      r0, #0
	BNE      |loc_0800B142|
	MOV      r0, #5
	SUB      r0, r0, r1
	LDR      r1, [r4, #0x58]
	ADD      r1, #1
	STR      r1, [r4, #0x58]
	BL       |inc_0x046118_0x049114| + 0xd40
	CMP      r1, #0
	BEQ      |loc_0800B142|
	MOV      r0, #0
	POP      {r3, r4, r5, pc}
