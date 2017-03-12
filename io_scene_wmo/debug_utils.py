###############################
## Debug output system
###############################
    
def Log(spacing, header, *message):
    
    string = ""
    
    for item in message:
        string += str(item) + " "
        
    if spacing:
        for i in range(0, spacing):
            print("")
    
    if header:
        print("###############################")
        print("##", string)
        print("###############################")
    
    else:
        print(string)
    
     
def LogDebug(spacing, header, *message):
    
    string = ""
    
    for item in message:
        string += str(item) + " "
    
    if spacing:
        for i in range(0, spacing):
            print("")
    
    if header:
        print("###############################")
        print("##", "DEBUG:", string)
        print("###############################")
    
    else:
        print(string)
    
def LogError(spacing, *message):
    
    string = ""
    
    for item in message:
        for char in str(item):
            string += char + " "
    
    if spacing:
        for i in range(0, spacing):
            print("")
            
    raise Exception(string)
    