	CODE16
|loc_08046AC0|
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [pc, #0x20]
	ADD      r5, pc
	LDR      r4, [pc, #0x20]
	ADD      r4, pc
	CMP      r5, r4
	BEQ      |loc_08046ADC|
|loc_08046ACE|
	SUB      r4, #4
	LDR      r0, [r4]
	ADD      r0, r4, r0
	BL       |loc_08046AA0|
	CMP      r5, r4
	BNE      |loc_08046ACE|
|loc_08046ADC|
	POP      {r3, r4, r5}
	POP      {r3}
	BX       r3
	LSL      r0, r0, #0
	MOV      r6, #0x30
	LSL      r0, r0, #0
	MOV      r6, #0x48
	LSL      r0, r0, #0
	PUSH     {r3, r4, r5, lr}
	LDR      r4, [pc, #0x20]
	ADD      r4, pc
	LDR      r5, [pc, #0x20]
	ADD      r5, pc
	CMP      r4, r5
	BEQ      |loc_08046B08|
|loc_08046AFA|
	LDR      r0, [r4]
	ADD      r0, r0, r4
	BL       |loc_08046AA0|
	ADD      r4, #4
	CMP      r4, r5
	BNE      |loc_08046AFA|
|loc_08046B08|
	POP      {r3, r4, r5}
	POP      {r3}
	BX       r3
	LSL      r0, r0, #0
	MOV      r3, #0xe4
	LSL      r0, r0, #0
	MOV      r6, #0
	LSL      r0, r0, #0
	BX       pc
	LSL      r0, r0, #0
