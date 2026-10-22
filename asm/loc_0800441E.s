	CODE16
|loc_0800441E|
	PUSH     {r4, r5}
	ADD      r3, r0, #0
	ADD      r3, #0xe4
	LDR      r5, [r3]
	MOV      r0, #0
	MOV      r2, #0
	CMP      r5, #0
	BLE      |loc_08004444|
|loc_0800442E|
	LSL      r4, r2, #2
	ADD      r4, r4, r3
	LDR      r4, [r4, #4]
	LSL      r4, r4, #4
	LSR      r4, r4, #4
	CMP      r4, r1
	BNE      |loc_0800443E|
	ADD      r0, #1
|loc_0800443E|
	ADD      r2, #1
	CMP      r5, r2
	BGT      |loc_0800442E|
|loc_08004444|
	POP      {r4, r5}
	BX       lr
