	CODE16
|sub_080071BE|
	LSR      r7, r0, #0x20
	ADD      r0, r3, r4
	LSL      r0, r0, #0xc
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_080071DC|
	MOV      r0, #0x18
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080071DC|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
