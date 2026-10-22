	CODE16
|loc_080135D2|
	PUSH     {r4, r5}
	LDR      r3, [r0, #0x24]
	MOV      r1, #0
	MOV      r2, #0x96
	LDR      r5, [pc, #0x34]
|loc_080135DC|
	ADD      r0, r1, r2
	ASR      r0, r0, #1
	LSL      r4, r0, #2
	LDR      r4, [r5, r4]
	CMP      r3, r4
	BCS      |loc_080135EC|
	SUB      r2, r0, #1
	B        |loc_080135F2|
|loc_080135EC|
	CMP      r3, r4
	BLS      |sub_0801360A|
	ADD      r1, r0, #1
|loc_080135F2|
	CMP      r1, r2
	BLT      |loc_080135DC|
	LSL      r2, r1, #2
	LDR      r2, [r5, r2]
	MOV      r0, #1
	CMP      r2, r3
	BLS      |loc_08013602|
	MOV      r0, #0
|loc_08013602|
	ADD      r0, r0, r1
	ADD      r0, #0x31
	POP      {r4, r5}
	BX       lr
