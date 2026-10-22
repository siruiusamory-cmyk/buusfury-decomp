	CODE16
|sub_080159DC|
|unk_080159DC|
		MOV r1, #2
		STRB r1, [r0, #0x10]
		B        |loc_080159D8|
|loc_080159E2|
|unk_080159E2|
		CMP r2, #0
		BLE      |loc_080159EC|
		MOV r1, #0
		STRB r1, [r0, #0x10]
		B        |loc_080159D8|
|loc_080159EC|
		MOV r1, #1
		STRB r1, [r0, #0x10]
		B        |loc_080159D8|
