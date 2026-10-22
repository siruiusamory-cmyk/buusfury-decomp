	CODE16
|Irq_WriteEnable2|
	PUSH     {r4, lr}
	LDR      r2, [pc, #0x31c]
	LDR      r4, [pc, #0x324]
	STR      r2, [r0]
	LDRH     r2, [r4]
	MOV      r3, #2
	BIC      r2, r3
	STRH     r2, [r4]
	LDR      r2, [pc, #0x31c]
	CMP      r1, #0
	STR      r2, [r0]
	BEQ      |loc_08008190|
	BL       |GBARam_Free|
|loc_08008190|
	POP      {r4, pc}
