	CODE16
|sub_08026F2A|
	PUSH     {r4}
	LDR      r1, [r0, #0x2c]
	LDR      r3, [pc, #0x5c]
	SUB      sp, #8
	ADD      r1, r1, r3
	LDR      r4, [r1]
	LDR      r3, [r0, #0x24]
	ADD      r2, r0, #0
	SUB      r3, r3, r4
	LDR      r4, [r0, #0x28]
	LDR      r1, [r1, #4]
	STR      r3, [sp]
	SUB      r1, r4, r1
	STR      r1, [sp, #4]
	ADD      r1, r3, #0
	LDR      r3, [sp, #4]
	ADD      r2, #0x1c
	STMIA    r2!, {r1, r3}
	LDR      r2, [pc, #0x40]
	LDR      r1, [r0, #0x1c]
	LDR      r3, [r2]
	CMP      r1, r3
	BLT      |sub_08026F74|
	LDR      r3, [r2, #8]
	CMP      r1, r3
	BGE      |sub_08026F74|
	LDR      r0, [r0, #0x20]
	LDR      r1, [r2, #4]
	CMP      r0, r1
	BLT      |sub_08026F74|
	LDR      r1, [r2, #0xc]
	CMP      r0, r1
	BGE      |sub_08026F74|
	MOV      r0, #1
	ADD      sp, #8
	POP      {r4}
	BX       lr
