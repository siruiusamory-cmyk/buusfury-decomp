	CODE16
|sub_08010D7C|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	MOV      r1, #0xff
	ADD      r1, #0xcd
	MOV      r0, #0
	STR      r0, [r1, r4]
	MOV      r1, #1
	ADD      r0, r4, #0
	BL       |Record_SelectIndexed|
	LDR      r1, [pc, #0x1a4]
	ADD      r0, r4, #0
	BL       |loc_0800ED18|
	POP      {r4, pc}
