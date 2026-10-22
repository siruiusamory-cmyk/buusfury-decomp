	CODE16
|sub_0801F3DC|
	PUSH     {r4, r5, r6, r7}
	CMP      r3, #0
	BNE      |sub_0801F3E8|
	MOV      r0, #0
	POP      {r4, r5, r6, r7}
	BX       lr
