	CODE16
|loc_080159CC|
	CMP      r3, r4
	BLT      |loc_080159E2|
	CMP      r1, #0
	BLE      |sub_080159DC|
	MOV      r1, #3
	STRB     r1, [r0, #0x10]
|loc_080159D8|
	POP      {r4}
	BX       lr
