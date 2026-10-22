	CODE16
|loc_08040918|
	PUSH     {lr}
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	MOV      r2, #1
	BL       |loc_0804092C|
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	POP      {r1}
	BX       r1
