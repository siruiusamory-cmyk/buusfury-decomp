	CODE16
|sub_0802A7A8|
|unk_0802A7A8|
; cited by 0x0802A5C2 (a pc-relative load targets 0x0802A7AC)
		MOV r0, #0
		BX       lr
	INCBIN  baserom.gba_0x2a7ac_0x2a7b2.extracted
|sub_0802A7B2|
|unk_0802A7B2|
	INCBIN  baserom.gba_0x2a7b2_0x2a7b4.extracted
		PUSH {r4, lr}
	ADD      r4, r0, #0
	LDR      r1, [r4, #0x40]
	LDR      r0, [r0, #0x38]
	ADD      r1, r0, r1
	STR      r1, [r4, #0x38]
	LSR      r0, r1, #0x10
	BEQ      |loc_0802A7EA|
	ASR      r1, r1, #0x10
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LDR      r0, [r4, #0x34]
	LSL      r1, r1, #2
	ADD      r1, r0, r1
	STR      r1, [r4, #0x34]
	LDR      r0, [r4, #0x44]
	LDR      r2, [r4, #0x3c]
	LSL      r3, r2, #1
	ADD      r2, r3, r2
	LSL      r2, r2, #2
	ADD      r2, r0, r2
	CMP      r2, r1
	BHI      |loc_0802A7E4|
	STR      r0, [r4, #0x34]
|loc_0802A7E4|
	ADD      r0, r4, #0
	BL       |loc_0802A7F4|
|loc_0802A7EA|
	LDR      r0, [r4, #0x38]
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STR      r0, [r4, #0x38]
	POP      {r4, pc}
|loc_0802A7F4|
	PUSH     {r4, r5}
	LDR      r1, [r0, #0x34]
	MOV      r3, #0
	LDRSB    r4, [r1, r3]
	LDR      r2, [r0, #0x10]
	MOV      r3, #1
	SUB      r2, r2, r4
	STR      r2, [r0, #0x20]
	LDRSB    r5, [r1, r3]
	LDR      r4, [r0, #0x14]
	SUB      r4, r4, r5
	STR      r4, [r0, #0x24]
	LDRB     r3, [r1, #2]
	LDRB     r1, [r1, #3]
	ADD      r2, r2, r3
	ADD      r1, r4, r1
	STR      r1, [r0, #0x2c]
	STR      r2, [r0, #0x28]
	POP      {r4, r5}
	BX       lr
|loc_0802A81C|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #4
	LDR      r5, [sp, #0x2c]
	LDR      r6, [sp, #0x30]
	LDR      r7, [sp, #0x28]
	ADD      r4, r0, #0
	BNE      |sub_0802A83A|
	MOV      r0, #0x44
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0802A83A|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
