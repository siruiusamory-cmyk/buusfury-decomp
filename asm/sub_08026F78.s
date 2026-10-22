	CODE16
|sub_08026F78|
	STR      r6, [sp, #0x200]
	LSR      r4, r0, #0x20
	LDMIA    r7!, {r3, r5}
	LSR      r4, r6, #1
	BVS      |loc_08026FEC|
	LSR      r4, r0, #0x20
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	BPL      |loc_08026EB4|
	LSR      r4, r0, #0x20
	STRH     r4, [r5]
	LSL      r0, r0, #0
	BEQ      |loc_08026FEC|
	LSR      r4, r6, #1
|loc_08026F94|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	BNE      |sub_08026FA8|
	LDR      r0, [pc, #0x210]
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08026FA8|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
