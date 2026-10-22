	CODE16
|loc_08047A08|
|unk_08047A08|
		PUSH {r3, lr}
	MOV      r1, #0
	BL       |sub_08047FD4|
	ADD      sp, #4
	POP      {r3}
	MOV      r0, #0
	BX       r3
	BX       pc
	LSL      r0, r0, #0
