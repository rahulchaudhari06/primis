import primis
#======================================================================================================================================================================================================
 
while True:
    text = input('BASIC >  ');
    result, error = primis.run('<From the console>',text)

    if error: print(error.as_string() )
    else: print(f"\n{result}\n")