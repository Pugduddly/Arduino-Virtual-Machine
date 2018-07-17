#!/usr/bin/env python2.7
import sys, struct

INST_NOP = 0
INST_REAP = 1
INST_WRIP = 2
INST_JMPF = 3
INST_JMPB = 4
INST_JFZ = 5
INST_JBZ = 6
INST_JFNZ = 7
INST_JBNZ = 8
INST_LOAD = 9
INST_STORE = 10
INST_ADD = 11
INST_SUB = 12
INST_MUL = 13
INST_AND = 14
INST_OR = 15
INST_BAND = 16
INST_BOR = 17
INST_BXOR = 18
INST_EQ = 19
INST_GT = 20
INST_LT = 21
INST_GE = 22
INST_LE = 23
INST_NE = 24
INST_DROP = 25
INST_DUP = 26
INST_OVER = 27
INST_RS = 28
INST_LS = 29
INST_ED = 30
INST_SERO = 31
INST_PUSH = 32
INST_OPR = 33
INST_STC = 34
INST_LDC = 35
INST_WOPR = 36
INST_LDCR = 37
INST_STCR = 38
INST_JMP = 39
INST_JZ = 40
INST_JNZ = 41
INST_CALL = 42
INST_RET = 43

TYPE_STRING = 0
TYPE_NUMBER = 1
TYPE_VARIABLE = 2

# Jump table (set programmatically)
JUMP_PRINTHEX = 0
JUMP_PRINTSTR = 0

def compilePrint(args):
    if len(args) < 1:
        error("Not enough arguments")
    result = []
    for arg in args:
        if arg["type"] == TYPE_NUMBER:
            stringToPrint = ("%d" % arg["value"])[::-1] # Convert value to string, then reverse it
            result += [INST_PUSH, 0]
            for char in stringToPrint:
                result += [INST_PUSH, ord(char)]
                #result += [INST_PUSH, ord(char), INST_SERO, INST_DROP]
            result += jumpTo(JUMP_PRINTSTR)
        elif arg["type"] == TYPE_STRING:
            stringToPrint = arg["value"][::-1] # Reverse string
            result += [INST_PUSH, 0]
            for char in stringToPrint:
                result += [INST_PUSH, ord(char)]
                #result += [INST_PUSH, ord(char), INST_SERO, INST_DROP]
            result += jumpTo(JUMP_PRINTSTR)
        elif arg["type"] == TYPE_VARIABLE:
            ofs = getVarOffset(arg["value"])
            size = getVarSize(arg["value"])
            if (size == 1):
                result += [
                    # Store value of variable to temporary register
                    INST_LDC, ofs,
                    INST_STC, 16,
                    INST_DROP
                ]
                # Call PRINTHEX routine
                result += jumpTo(JUMP_PRINTHEX)
            else:
                # Setup code
                result += [
                    # Store address of variable to temporary register
                    INST_PUSH, ofs - 1,
                    INST_STC, 17,
                    INST_DROP,
                ]
                result2 = [
                    # Increment variable address
                    INST_LDC, 17,
                    INST_PUSH, 1,
                    INST_ADD,
                    INST_STC, 17,
                    INST_DROP,
                    # Load address from temporary register
                    INST_LDC, 17,
                    # Use that to get variable value
                    INST_LDCR,
                    
                    # Store that in temporary register
                    INST_STC, 16,
                    INST_DROP, INST_DROP,
                ]
                # Call PRINTHEX routine
                result2 += jumpTo(JUMP_PRINTHEX)
                result2 += [
                    # Get variable address
                    INST_LDC, 17,
                    INST_PUSH, ofs + size - 1,
                    # Is variable address < ofs + size
                    INST_LT,
                    # If so, print next byte
                    INST_JNZ
                ]
                result2 += intToBytes(outputLength + len(result) - 1)
                
                result += result2
    return result

def compileGoto(args):
    pass

def compileDeclare(args):
    if len(args) < 2:
        error("Not enough arguments")
    if args[0]["type"] != TYPE_VARIABLE:
        error("Argument 0 != variable")
    if args[1]["type"] != TYPE_NUMBER:
        error("Argument 1 != number (size)")
    declareNewVar(args[0]["value"], args[1]["value"])

def compileLet(args):
    if len(args) < 2:
        error("Not enough arguments")
    if args[0]["type"] != TYPE_VARIABLE:
        error("Argument 0 != variable")
    
    ofs = getVarOffset(args[0]["value"])
    
    if args[1]["type"] == TYPE_NUMBER:
        val = args[1]["value"]
        return [INST_PUSH, val, INST_STC, ofs, INST_DROP]
    elif args[1]["type"] == TYPE_VARIABLE:
        ofs2 = getVarOffset(args[1]["value"])
        return [INST_LDC, ofs2, INST_STC, ofs, INST_DROP]
    
    error("Argument 1 != number or variable")

def compileExit(args):
    return [INST_ED]

def jumpTo(address):
    byte1, byte2 = intToBytes(address)
    return [INST_CALL, byte1, byte2]

compile = {
    "Print"   : compilePrint,
#    "Input"   : "I",
#    "ClrHome" : "C",
#    If       :  i
#    "Goto"    : compileGoto,
#    LABEL    :  L
    "Declare" : compileDeclare,
    "Let"     : compileLet,
#    Def      :  D
#    For      :  F
    "Exit"    : compileExit,
}

vartable = []
currentLine = 0
isPrecompile = False
outputLength = 0

def error(msg):
    print "Error on line %d: %s" % (currentLine, msg)
    exit(0)

def declareNewVar(name, size):
    global vartable, isPrecompile
    if not isPrecompile:
        return
    if size < 1:
        error("Variable size can not be less than 1")
    vartable += [(name, size)]

def getVarOffset(varname):
    global vartable
    ofs = 18
    for var in vartable:
        if (var[0] == varname):
            return ofs
        ofs += var[1]

def getVarSize(varname):
    global vartable
    for var in vartable:
        if (var[0] == varname):
            return var[1]

def intToBytes(number):
    return struct.unpack('>BB', struct.pack('>H', number))

def wStrip(array):
    c = 0
    for line in array:
        array[c] = line.lstrip().rstrip()
        c += 1
    return array

whileLoops = []

def doCompile(line, output):
    global whileLoops, outputLength
    success = False
    successed = False
    compileFunction = None
    buffer = ""
    keyword = ""
    i = 0
    line = line.lstrip().rstrip()
    
    if line == "" or line[0] == "#":
        return
    
    #if line[0] == ":":
    #    output += ["L" + line[1:]]
    #    return
    
    for key, value in compile.iteritems():
        if successed:
            break
            
        i = 0
        buffer = ""
            
        for char in line:
            #print i, char, key[i], char == key[i]
            if i == len(key) - 1 and char.lower() == key[i].lower() and success:
                keyword = key
                compileFunction = value
                successed = True
                break
            elif i < len(key):
                success = char.lower() == key[i].lower()
            elif len(key) < len(line) and i > len(key) and i < len(line) - 1 and success:
                buffer += char
            i += 1
    
    if successed:
        args = []
        buffer = ""
        i += 1
        if i < len(line) and line[i] == "(":
            while i < len(line) and line[i] != ")":
                i += 1
                buffer = ""
                isString = False
                while (isString or (line[i] != ")" and line[i] != ",")) and i < len(line):
                    if line[i] == "\"" and line[i - 1] != "\\":
                        isString = not isString
                    if line[i] == "n" and line[i - 1] == "\\":
                        buffer += "\n"
                    elif line[i] != "\\":
                        buffer += line[i]
                    i += 1
                
                if i >= len(line) and isString:
                    error("No closing quote")
                elif i >= len(line):
                    error("No closing bracket")
                
                # Ignore blanks
                while buffer[0] == " ":
                    buffer = buffer[1:]
                while buffer[len(buffer) - 1] == " ":
                    buffer = buffer[:-1]
                
                arg = {}
                if arg == {} and buffer[0] == "\"" and buffer[len(buffer) - 1] == "\"":
                    arg["type"] = TYPE_STRING
                    arg["value"] = buffer[1:-1].replace("\\\"", "\"")
                if arg == {} and ord(buffer[0]) >= ord("0") and ord(buffer[0]) <= ord("9"):
                    j = 0
                    isNumber = True
                    while j < len(buffer):
                        if ord(buffer[0]) < ord("0") or ord(buffer[0]) > ord("9"):
                            isNumber = False
                            break
                        j += 1
                    if (isNumber):
                        arg["type"] = TYPE_NUMBER
                        arg["value"] = int(buffer)
                if arg == {}:
                    isVariable = False
                    for var in vartable:
                        if buffer == var[0]:
                            isVariable = True
                            break
                    if isVariable or keyword == "Declare":
                        arg["type"] = TYPE_VARIABLE
                        arg["value"] = buffer
                    else:
                        error("Unknown argument type")
                args += [arg]
            if i >= len(line):
                error("No closing bracket")
        result = compileFunction(args)
        if result != None:
            output += result
            outputLength += len(result)
    else:
        error("Unknown command")

def main():
    global currentLine, isPrecompile, outputLength, JUMP_PRINTHEX, JUMP_PRINTSTR
    with open(sys.argv[1], "r") as f:
        content = f.read()
    
    output = [
        INST_PUSH, ord("0"), INST_STC, 0, INST_DROP,
        INST_PUSH, ord("1"), INST_STC, 1, INST_DROP,
        INST_PUSH, ord("2"), INST_STC, 2, INST_DROP,
        INST_PUSH, ord("3"), INST_STC, 3, INST_DROP,
        INST_PUSH, ord("4"), INST_STC, 4, INST_DROP,
        INST_PUSH, ord("5"), INST_STC, 5, INST_DROP,
        INST_PUSH, ord("6"), INST_STC, 6, INST_DROP,
        INST_PUSH, ord("7"), INST_STC, 7, INST_DROP,
        INST_PUSH, ord("8"), INST_STC, 8, INST_DROP,
        INST_PUSH, ord("9"), INST_STC, 9, INST_DROP,
        INST_PUSH, ord("A"), INST_STC, 10, INST_DROP,
        INST_PUSH, ord("B"), INST_STC, 11, INST_DROP,
        INST_PUSH, ord("C"), INST_STC, 12, INST_DROP,
        INST_PUSH, ord("D"), INST_STC, 13, INST_DROP,
        INST_PUSH, ord("E"), INST_STC, 14, INST_DROP,
        INST_PUSH, ord("F"), INST_STC, 15, INST_DROP
    ]
    
    jumpLocation = len(output) + 1
    
    output += [INST_JMP, 0, 0] # To be filled in after compilation
    
    JUMP_PRINTHEX = len(output)
    print "printhex is %s" % JUMP_PRINTHEX
    # Print number routine
    output += [
        # Print first digit #
        # Push 15 on to the stack
        INST_PUSH, 15,
        # Load temp value
        INST_LDC, 16,
        # Divide by 16 (right shift 4 times)
        INST_RS, INST_RS, INST_RS, INST_RS,
        # Binary AND with 15 (that explains the value)
        INST_BAND,
        # Get hex digit character from lookup table
        INST_LDCR,
        # Output to serial
        INST_SERO,
        # Clean up stack
        INST_DROP, INST_DROP,
        # Print second digit #
        # Push 15 on to the stack
        INST_PUSH, 15,
        # Load temp value
        INST_LDC, 16,
        # Binary AND with 15 (that explains the value)
        INST_BAND,
        # Get hex digit character from lookup table
        INST_LDCR,
        # Output to serial
        INST_SERO,
        # Clean up stack
        INST_DROP, INST_DROP,
        # Return to main code
        INST_RET
    ]
    
    JUMP_PRINTSTR = len(output)
    print "printstr is %s" % JUMP_PRINTSTR
    output2 = [
        # Save return address to temp register
        INST_STC, 17,
        INST_DROP,
        INST_STC, 16,
        INST_DROP
    ]
    jumpPrintstrBytes = intToBytes(JUMP_PRINTSTR + len(output2))
    output += output2
    output += [
        # Print the top of stack to UART
        INST_SERO,
        # Discard the top of stack
        INST_DROP,
        # If top of stack is not zero, repeat
        INST_JNZ, jumpPrintstrBytes[0], jumpPrintstrBytes[1],
        # otherwise, discard top of stack and return
        INST_DROP,
        INST_LDC, 16,
        INST_LDC, 17,
        INST_RET
    ]
    
    byte1, byte2 = intToBytes(len(output))
    output[jumpLocation] = byte1
    output[jumpLocation + 1] = byte2
    
    isPrecompile = True
    currentLine = 1
    outputLength = len(output)
    output2 = []
    for line in content.split("\n"):
        doCompile(line, output2)
        currentLine += 1
    
    currentLine = 1
    outputLength = len(output)
    isPrecompile = False
    for line in content.split("\n"):
        doCompile(line, output)
        currentLine += 1
    
    print output
    
    with open(sys.argv[2], "wb") as f:
        if len(output) > 0:
            for byte in output:
                f.write(chr(byte))

if __name__ == "__main__":
    main()
