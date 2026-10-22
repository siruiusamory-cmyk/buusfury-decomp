	CODE16
|sub_08051F92|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |loc_08050D30|
	CMP      r5, #0
	BEQ      |loc_08051FAA|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051FAA|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08051FBA|
	BL       |GBARam_Free|
|loc_08051FBA|
	POP      {r3, pc}
|sub_08051FBC|
|unk_08051FBC|
	INCBIN	baserom.gba_0x51fbc_0x51fbe.extracted
