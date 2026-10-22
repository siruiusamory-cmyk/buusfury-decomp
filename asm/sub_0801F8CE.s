	CODE16
|sub_0801F8CE|
|unk_0801F8CE|
		LDR r0, [r5, #0x18]
		LDR r1, [r5, #0x20]
		LDR r2, [r5, #0x24]
		ADD r1, r1, r2
		BEQ      |loc_0801F8DC|
		MOV r1, #1
		B        |loc_0801F8DE|
|loc_0801F8DC|
		MOV r1, #0
|loc_0801F8DE|
		STR r1, [r0, #8]
		LDR r0, [r5, #0x1c]
		LDR r1, [sp]
		LDR r2, [r5, #0x20]
		LDR r1, [r1]
		LDR r3, [r5, #0x24]
		SUB r1, #1
		ADD r2, r2, r3
		CMP r1, r2
		BLE      |loc_0801F8F6|
		MOV r1, #1
		B        |loc_0801F8F8|
|loc_0801F8F6|
		MOV r1, #0
|loc_0801F8F8|
		STR r1, [r0, #8]
		B        |loc_0801F90C|
|loc_0801F8FC|
|unk_0801F8FC|
		MOV r1, #0
