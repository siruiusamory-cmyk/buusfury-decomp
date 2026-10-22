	CODE16
|sub_08004212|
	LSR      r3, r7, #0x20
	ADR      r4, |loc_08004228|
	LSR      r4, r0, #0x20
	STR      r2, [sp, #0x30]
	LSR      r4, r0, #0x20
	BX       lr
	PUSH     {lr}
	LDR      r1, [r0, #4]
	MOV      r0, #0
	SUB      sp, #0x6c
	STR      r0, [sp]
|loc_08004228|
	STR      r0, [sp, #0x44]
	MOV      r0, sp
	MOV      r2, #0
	BL       |loc_08004038|
	ADD      sp, #0x6c
	POP      {pc}
	ADD      r1, r0, #4
	MOV      r0, #0
	PUSH     {lr}
	SUB      sp, #0x6c
	STR      r0, [sp]
	STR      r0, [sp, #0x44]
	MOV      r0, sp
	MOV      r2, #0
	BL       |loc_08004038|
	ADD      sp, #0x6c
	POP      {pc}
	PUSH     {r3, lr}
	LDR      r0, [r0, #4]
	MOV      r1, #0
	BL       |sub_08012588|
	POP      {r3, pc}
	LSL      r0, r0, #0
