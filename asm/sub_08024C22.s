	CODE16
|sub_08024C22|
|unk_08024C22|
		LDR r1, [r0]
		LDR r2, [r1, #0x34]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		BL       |inc_0x03d784_0x041118| + 0xcc
		MOV r0, #0
		DCW     0xE7F5
|loc_08024C34|
|unk_08024C34|
		MOV r0, #1
		DCW     0xE7F3
