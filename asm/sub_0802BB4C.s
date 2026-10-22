	IMPORT |GBARam_Malloc|
	CODE16
	EXPORT |sub_0802BB4C|
	EXPORT |loc_0802BB7C|
	EXPORT |loc_0802BBFA|
	EXPORT |sub_0802BC1A|
	EXPORT |sub_0802BC40|
	EXPORT |loc_0802BC64|
	EXPORT |sub_0802BCCE|
	EXPORT |sub_0802BD04|
	EXPORT |sub_0802BD20|
	EXPORT |sub_0802BD32|
	EXPORT |sub_0802BD36|
	EXPORT |loc_0802BD3C|
	EXPORT |loc_0802BD4C|
	EXPORT |sub_0802BD6A|
	EXPORT |sub_0802BD90|
	EXPORT |sub_0802BDAA|
	EXPORT |sub_0802BDBE|
	EXPORT |loc_0802BDE6|
	EXPORT |loc_0802BE8A|
	EXPORT |loc_0802BEC4|
	EXPORT |sub_0802BECC|
	EXPORT |sub_0802BEEA|
	EXPORT |sub_0802BFBC|
	EXPORT |loc_0802BFFE|
	EXPORT |loc_0802C038|
	EXPORT |sub_0802C054|
	EXPORT |sub_0802C066|
	EXPORT |sub_0802C0B0|
	EXPORT |sub_0802C12E|
	EXPORT |loc_0802C14C|
	EXPORT |loc_0802C178|
	EXPORT |loc_0802C18A|
	EXPORT |sub_0802C1D0|
	EXPORT |loc_0802C2EC|
	EXPORT |sub_0802C328|
	EXPORT |sub_0802C33C|
	EXPORT |sub_0802C340|
	EXPORT |loc_0802C3BA|
	EXPORT |loc_0802C3CE|
	EXPORT |sub_0802C3E6|
	EXPORT |loc_0802C400|
	EXPORT |sub_0802C446|
	EXPORT |loc_0802C456|
	EXPORT |loc_0802C482|
	EXPORT |loc_0802C4AE|
	EXPORT |sub_0802C4B8|
	EXPORT |sub_0802C4BA|
	EXPORT |loc_0802C4FA|
	EXPORT |sub_0802C5BA|
	EXPORT |sub_0802C630|
	EXPORT |sub_0802C640|
	EXPORT |sub_0802C644|
	EXPORT |loc_0802C64E|
	EXPORT |sub_0802C668|
	EXPORT |loc_0802C66A|
	EXPORT |loc_0802C66E|
	EXPORT |sub_0802C672|
	EXPORT |loc_0802C682|
	EXPORT |sub_0802C684|
	EXPORT |sub_0802C686|
	EXPORT |sub_0802C6B0|
	EXPORT |sub_0802C6EC|
	EXPORT |sub_0802C6FE|
	EXPORT |sub_0802C782|
	EXPORT |sub_0802C7AC|
	EXPORT |sub_0802C7EA|
	EXPORT |loc_0802C85C|
	EXPORT |sub_0802C868|
	EXPORT |sub_0802C8AE|
	EXPORT |sub_0802C8BE|
	EXPORT |loc_0802C8F4|
	EXPORT |sub_0802C8FE|
	EXPORT |Mosaic_WriteSize1|
	EXPORT |sub_0802C98E|
	EXPORT |loc_0802CA1A|
	EXPORT |Mosaic_WriteSize2|
	EXPORT |Bg_WriteControl0AndMosaic2|
	EXPORT |loc_0802CAA0|
	EXPORT |sub_0802CAF8|
	EXPORT |sub_0802CAFA|
	EXPORT |loc_0802CB3A|
	EXPORT |loc_0802CB42|
	EXPORT |sub_0802CB4E|
	EXPORT |sub_0802CB52|
	EXPORT |loc_0802CB64|
	EXPORT |loc_0802CB90|
	EXPORT |sub_0802CBAA|
	EXPORT |sub_0802CBAE|
	EXPORT |loc_0802CD0E|
	EXPORT |sub_0802CD10|
	EXPORT |sub_0802CD12|
	EXPORT |loc_0802CD40|
	EXPORT |sub_0802CD42|
	EXPORT |sub_0802CD78|
	EXPORT |sub_0802CD80|
	EXPORT |sub_0802CD82|
	EXPORT |loc_0802CDA4|
	EXPORT |sub_0802CDA6|
	EXPORT |sub_0802CDE4|
	EXPORT |loc_0802CDFA|
	EXPORT |sub_0802CE00|
	EXPORT |sub_0802D08C|
	EXPORT |loc_0802D0A8|
	EXPORT |loc_0802D0DA|
	EXPORT |sub_0802D102|
	EXPORT |sub_0802D168|
	EXPORT |loc_0802D18A|
	EXPORT |loc_0802D1B6|
	EXPORT |sub_0802D1BA|
	CODE16
|sub_0802BB4C|
	LSL      r0, r6, #2
	LDR      r1, [pc, #0xb0]
	ADD      r0, r0, r6
	LSL      r0, r0, #2
	SUB      r1, #0x64
	ADD      r5, r0, r1
	ADD      r0, r7, r6
	LDRB     r1, [r0, #0x15]
	LDRB     r2, [r0, #0x10]
	CMP      r1, r2
	BEQ      |loc_0802BB7C|
	STRB     r1, [r0, #0x10]
	LDRH     r0, [r7, #0xc]
	LDR      r2, [pc, #0x94]
	LSL      r0, r0, #5
	ADD      r0, r0, r2
	LDR      r2, [r5]
	ADD      r0, r0, r2
	LDR      r2, [r5, #8]
	LDR      r3, [r5, #4]
	MUL      r1, r2
	ADD      r1, r1, r3
	BL       |inc_0x049120_0x055620| + 0x18
|loc_0802BB7C|
	LDR      r0, [r5, #0x10]
	LDR      r2, [pc, #0x98]
	STR      r0, [r4]
	LDRB     r1, [r5, #0xc]
	AND      r0, r2
	ADD      r6, #1
	ADD      r1, #8
	LSL      r1, r1, #0x10
	ORR      r0, r1
	STR      r0, [r4]
	LDRB     r1, [r5, #0xd]
	LSR      r0, r0, #8
	LSL      r0, r0, #8
	ADD      r1, #8
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x18
	ORR      r0, r1
	STR      r0, [r4]
	LDR      r0, [r4, #4]
	MOV      r1, #3
	LSL      r1, r1, #0xa
	BIC      r0, r1
	MOV      r1, #1
	LSL      r1, r1, #0xa
	ADD      r0, r0, r1
	STR      r0, [r4, #4]
	LDRH     r1, [r7, #0xc]
	LDR      r2, [r5]
	LSR      r0, r0, #0xa
	ASR      r2, r2, #5
	ADD      r1, r1, r2
	LSL      r1, r1, #0x16
	LSR      r1, r1, #0x16
	LSL      r0, r0, #0xa
	ORR      r0, r1
	STR      r0, [r4, #4]
	ADD      r4, #8
	CMP      r6, #5
	BLT      |sub_0802BB4C|
	LDR      r0, [pc, #0x50]
	MOV      r1, #3
	STR      r0, [r4]
	LDR      r0, [r4, #4]
	LSL      r1, r1, #0xa
	BIC      r0, r1
	MOV      r1, #1
	LSL      r1, r1, #0xa
	ADD      r0, r0, r1
	STR      r0, [r4, #4]
	LDRH     r1, [r7, #0xc]
	LSR      r0, r0, #0xa
	LSL      r0, r0, #0xa
	LSL      r1, r1, #0x16
	LSR      r1, r1, #0x16
	ORR      r0, r1
	STR      r0, [r4, #4]
	ADD      r0, r4, #0
	LDR      r1, [sp, #8]
	ADD      r0, #8
	STR      r0, [r1]
	ADD      sp, #0xc
	MOV      r0, #0
	POP      {r4, r5, r6, r7, pc}
|loc_0802BBFA|
	DCW      0x0000
	DCW      0x0000,0x0601,0x3008,0x0875,0x9680,0x0804,0xb400,0x0804
	DCW      0xffff,0x7fff,0x0271,0x0000,0xf424,0x0000,0xffff
|sub_0802BC1A|
|unk_0802BC1A|
	INCBIN	baserom.gba_0x2bc1a_0x2bc1e.extracted
	STRH     r0, [r1]
	PUSH     {r3, lr}
	CMP      r1, #0xb
	BEQ      |sub_0802BC40|
	CMP      r1, #0x1b
	BNE      |loc_0802BC64|
	ADD      r0, #0x1c
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #3
	ADD      r0, r1, r0
	ADD      r0, #4
	LDMIA    r2!, {r1, r2}
	STMIA    r0!, {r1, r2}
	MOV      r0, #1
	POP      {r3, pc}
