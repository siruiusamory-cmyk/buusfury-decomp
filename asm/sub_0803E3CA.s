	CODE16
|sub_0803E3CA|
	ADD      r3, r0, #0
	MOV      r0, #0
	MOV      r1, #0
|loc_0803E3D0|
	LSL      r2, r1, #6
	ADD      r2, r2, r3
	LDRB     r2, [r2, #0x10]
	LSL      r2, r2, #0x1f
	BEQ      |loc_0803E3DC|
	ADD      r0, #1
|loc_0803E3DC|
	ADD      r1, #1
	CMP      r1, #0x10
	BLT      |loc_0803E3D0|
	BX       lr
