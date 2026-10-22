	CODE16
|sub_08030FB8|
	PUSH     {r4}
	LDR      r2, [pc, #0x40]
	ADD      r1, #0x10
	LDR      r2, [r2]
	LDR      r3, [pc, #0x3c]
	LSL      r2, r2, #3
	ADD      r1, r2, r1
	ADD      r1, #4
	LDR      r2, [r1]
	LDR      r4, [r3]
	LDR      r1, [r1, #4]
	LDR      r3, [r3, #4]
	SUB      sp, #8
	ADD      r2, r2, r4
	ADD      r1, r1, r3
	STR      r1, [sp, #4]
	ADD      r1, r2, #0
	STR      r2, [sp]
	LDR      r2, [sp, #4]
	STMIA    r0!, {r1, r2}
	ADD      sp, #8
	POP      {r4}
	BX       lr
|loc_08030FE6|
	DCW      0x0000
	DCW      0x0b6d,0x0803,0x9154,0x0875,0xabd8,0x0804,0x0040,0x0400
	DCW      0xe454
|loc_08030FFA|
	LSR      r4, r0, #0x20
	CMP      r2, #0x60
	LSL      r0, r0, #0xc
	LSR      r0, r2, #0x1d
	LSL      r0, r0, #0xc
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x240]
	ADD      r5, r1, #0
	LDR      r1, [r0]
	SUB      sp, #0x44
	CMP      r1, #0
	BNE      |sub_0803101A|
	MOV      r0, #0
	ADD      sp, #0x44
	POP      {r4, r5, r6, r7, pc}
