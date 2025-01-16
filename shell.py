import basic
#======================================================================================================================================================================================================
 
while True:
    text = input('BASIC >  ');
    result, error = basic.run('<From the console>',text)

    if error: print(error.as_string() )
    else: print(result)