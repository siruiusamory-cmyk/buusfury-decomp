	CODE16
|sub_0805324E|
	LSL      r0, r0, #0
	PUSH     {r4, r5, r6}
	ADD      r5, r2, #0
	ADD      r4, r1, #0
	SUB      sp, #0x10
	MOV      r6, sp
	LDMIA    r5!, {r1, r2, r3, r5}
	STMIA    r6!, {r1, r2, r3, r5}
	LDR      r2, [sp]
	LDR      r1, [r4]
	SUB      r6, #0x10
	CMP      r2, r1
	BGE      |loc_0805326A|
	STR      r1, [sp]
|loc_0805326A|
	LDR      r2, [sp, #4]
	LDR      r1, [r4, #4]
	CMP      r2, r1
	BGE      |loc_08053274|
	STR      r1, [sp, #4]
|loc_08053274|
	LDR      r2, [sp, #8]
	LDR      r1, [r4, #8]
	CMP      r2, r1
	BLE      |loc_0805327E|
	STR      r1, [sp, #8]
|loc_0805327E|
	LDR      r1, [sp, #0xc]
	LDR      r2, [r4, #0xc]
	CMP      r1, r2
	BLE      |loc_08053288|
	STR      r2, [sp, #0xc]
|loc_08053288|
	LDMIA    r6!, {r1, r2, r3, r6}
	STMIA    r0!, {r1, r2, r3, r6}
	ADD      sp, #0x10
	POP      {r4, r5, r6}
	BX       lr
	LSL      r0, r0, #0
	LDR      r3, [r0]
	LDR      r2, [r1]
	CMP      r3, r2
	BLE      |loc_0805329E|
	STR      r2, [r0]
|loc_0805329E|
	LDR      r3, [r0, #4]
	LDR      r2, [r1, #4]
	CMP      r3, r2
	BLE      |loc_080532A8|
	STR      r2, [r0, #4]
|loc_080532A8|
	LDR      r3, [r0, #8]
	LDR      r2, [r1]
	CMP      r3, r2
	BGE      |loc_080532B2|
	STR      r2, [r0, #8]
|loc_080532B2|
	LDR      r2, [r0, #0xc]
	LDR      r1, [r1, #4]
	CMP      r2, r1
	BGE      |loc_080532BC|
	STR      r1, [r0, #0xc]
|loc_080532BC|
	BX       lr
	LSL      r0, r0, #0
	LDR      r2, [r0]
	LDR      r3, [r1, #8]
	CMP      r2, r3
	BGE      |sub_080532E4|
	LDR      r2, [r1]
	LDR      r3, [r0, #8]
	CMP      r2, r3
	BGE      |sub_080532E4|
	LDR      r2, [r0, #4]
	LDR      r3, [r1, #0xc]
	CMP      r2, r3
	BGE      |sub_080532E4|
	LDR      r1, [r1, #4]
	LDR      r0, [r0, #0xc]
	CMP      r1, r0
	BGE      |sub_080532E4|
	MOV      r0, #1
	BX       lr
