	CODE16
|sub_08036E7A|
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r3, [r1, #0x74]
	ADD      r3, r3, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98e
	MOV      r0, #1
	POP      {r3, pc}
	EXPORT	|unk_08036E8E|
