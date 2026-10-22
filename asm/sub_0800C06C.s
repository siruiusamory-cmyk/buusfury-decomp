	CODE16
|sub_0800C06C|
	PUSH     {r4, lr}
	LDR      r4, [pc, #0x38]
	ADD      r1, r0, #0
	SUB      r4, #0xc
	LDR      r0, [r4]
	BL       |loc_08011944|
	LDR      r0, [r4, #4]
	ADD      r0, #0x80
	LDR      r0, [r0, #0x10]
	CMP      r0, #0
	BEQ      |loc_0800C092|
	MOV      r0, #0
	BL       |Object_Construct5|
	ADD      r1, r0, #0
	LDR      r0, [r4]
	BL       |List_Append|
|loc_0800C092|
	POP      {r4, pc}
	PUSH     {r3, lr}
	CMP      r1, #0xb
	BNE      |sub_0800C0A2|
	BL       |loc_0800BE90|
	MOV      r0, #0
	POP      {r3, pc}
