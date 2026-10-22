	CODE16
|sub_0802172A|
	LSR      r2, r6, #1
	STR      r6, [sp, #0x200]
	LSR      r4, r0, #0x20
|unk_08021730|
	INCBIN	baserom.gba_0x21730_0x21732.extracted
	LSR      r4, r0, #0x20
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	LDMIA    r2!, {r7}
	LSR      r4, r0, #0x20
|unk_0802173C|
	INCBIN	baserom.gba_0x2173c_0x2173e.extracted
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	LDR      r2, [r0, #0x28]
	CMP      r2, r1
	BEQ      |loc_08021760|
	STR      r1, [r0, #0x28]
	LDRB     r3, [r1, #2]
	LDRB     r4, [r1, #3]
	LDRH     r0, [r0, #0xc]
	LDR      r1, [r1, #8]
	MUL      r3, r4
	ADD      r2, r3, #0
	LDR      r3, [pc, #0xd0]
	LSL      r0, r0, #5
	ADD      r0, r0, r3
	BL       |inc_0x049120_0x055620| + 0x18
|loc_08021760|
	POP      {r4, pc}
|loc_08021762|
	PUSH     {r4, r5, r6}
	LDR      r1, [r0, #0x28]
	MOV      r3, #0
	LDRSB    r4, [r1, r3]
	LDR      r2, [r0, #0x20]
	MOV      r3, #1
	SUB      r2, r2, r4
	STR      r2, [r0, #0x10]
	LDRSB    r5, [r1, r3]
	LDR      r4, [r0, #0x24]
	SUB      r3, r4, r5
	STR      r3, [r0, #0x14]
	LDRB     r4, [r1, #2]
	LDRB     r1, [r1, #3]
	LDR      r5, [pc, #0xac]
	ADD      r4, r2, r4
	ADD      r1, r3, r1
	STR      r1, [r0, #0x1c]
	STR      r4, [r0, #0x18]
	LDR      r6, [r5, #8]
	CMP      r2, r6
	BGE      |loc_080217A0|
	LDR      r2, [r5]
	CMP      r2, r4
	BGE      |loc_080217A0|
	LDR      r2, [r5, #0xc]
	CMP      r3, r2
	BGE      |loc_080217A0|
	LDR      r2, [r5, #4]
	CMP      r2, r1
	BLT      |sub_080217A6|
|loc_080217A0|
	MOV      r0, #0
	POP      {r4, r5, r6}
	BX       lr
