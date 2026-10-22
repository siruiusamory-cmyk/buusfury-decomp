	CODE16
|Irq_WriteMaster1|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #0x1fc
	ADD      r5, r1, #0
	LDR      r0, [pc, #0xf8]
	MOV      r6, #0
	SUB      sp, #0x38
	STRH     r6, [r0, #8]
	LDR      r0, [pc, #0xf4]
	LDR      r0, [r0]
	BL       |loc_0803F26A|
	BL       GBARam_Init__Fv
	LDR      r0, [pc, #0xec]
	MOV      r2, #0xa0
	LSL      r1, r0, #0x18
	STRH     r0, [r1]
	LSR      r0, r1, #0x12
	STRH     r0, [r1, #0x20]
	STRH     r6, [r1, #0x22]
	STRH     r6, [r1, #0x24]
	STRH     r0, [r1, #0x26]
	MOV      r0, #0
	STR      r0, [r1, #0x28]
	STR      r0, [r1, #0x2c]
	MOV      r1, #0xf0
	ADD      r4, sp, #0x200
	ADD      r0, r4, #0
	BL       |loc_0803F540|
	MOV      r1, #0
	LDR      r0, [sp, #0x224]
	LDR      r2, [sp, #0x230]
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [pc, #0xbc]
	ADD      r3, sp, #0x200
	ADD      r0, #0x10
	STR      r0, [sp, #0x20c]
	MOV      r0, #1
	LDR      r1, [pc, #0xb8]
	STRB     r0, [r3, #2]
	STR      r1, [sp, #0x220]
	MOV      r1, #0xa
	STRB     r1, [r3, #1]
	STR      r1, [sp, #0x208]
	MOV      r2, #0x78
	STR      r2, [sp, #0x204]
	STRB     r0, [r3]
	MOV      r0, #4
	STRB     r0, [r3, #3]
	ADD      r0, r4, #0
	ADR      r1, |loc_0803E024|
	BL       |loc_0803DADA|
	ADD      r2, r5, #0
	ADR      r1, |loc_0803E04C|
	MOV      r7, sp
	MOV      r0, sp
	BL       |sub_0803DEFA|
	MOV      r5, #3
	MOV      r0, #0x1e
	STR      r0, [sp, #0x208]
	STR      r5, [sp, #0x204]
	ADD      r3, sp, #0x200
	STRB     r6, [r3]
	STRB     r5, [r3, #3]
	ADD      r0, r4, #0
	ADD      r1, pc, #0xB4
	BL       |loc_0803DADA|
	MOV      r6, #2
	ADD      r3, sp, #0x200
	ADD      r2, r7, #0
	MOV      r1, #0xdc
	ADD      r0, r4, #0
	STRB     r6, [r3, #3]
	BL       |loc_0803DD66|
	ADD      r3, sp, #0x200
	STRB     r5, [r3, #3]
	STR      r5, [sp, #0x204]
	ADD      r1, pc, #0xA8
	ADD      r0, r4, #0
	BL       |loc_0803DADA|
	ADD      r3, sp, #0x200
	STRB     r6, [r3, #3]
	LDR      r2, [sp, #0x23c]
	ADR      r1, |loc_0803E074|
	ADD      r0, r4, #0
	BL       |sub_0803DC96|
	ADD      r3, sp, #0x200
	STRB     r5, [r3, #3]
	LDR      r0, [sp, #0x240]
	CMP      r0, #0
	BEQ      |sub_0803DFDE|
	ADD      r1, pc, #0xA8
	B        |sub_0803DFE0|
