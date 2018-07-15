Arduino-Virtual-Machine
=======================

A parallel Virtual Stack Machine Firmware for Arduino

### Instruction set (mostly taken from comments in the firmware source code)
| Opcode | Mnemonic | Description                                                           |
|--------|----------|-----------------------------------------------------------------------|
| 0      | NOP      | Do nothing                                                            |
| 1      | REAP     | Read port value into stack (disabled)                                 |
| 2      | WRIP     | Write value at top of stack into port (disabled)                      |
| 3      | JMPF     | `ip = ip + A` (relative jump) forward jump only                       |
| 4      | JMPB     | `ip = ip - A` (relative jump) backward jump only                      |
| 5      | JFZ      | if top of stack is 0, `ip = ip + A` (forward jump)                    |
| 6      | JBZ      | if top of stack is 0, `ip = ip - A` (backward jump)                   |
| 7      | JFNZ     | if top of stack not 0, `ip = ip + A` (forward jump)                   |
| 8      | JBNZ     | if top of stack not 0, `ip = ip - A` (backward jump)                  |
| 9      | LOAD     | `top of stack = stack[content of top of stack]`                       |
| 10     | STORE    | `stack[content of (top of stack - 1)] = top of stack`                 |
| 11     | ADD      | `top of stack = top of stack + second of stack`                       |
| 12     | SUB      | `top of stack = second of stack - top of stack`                       |
| 13     | MUL      | `top of stack = top of stack * second of stack`                       |
| 14     | AND      | `top of stack = top of stack && second of stack`                      |
| 15     | OR       | `top of stack = top of stack \|\| second of stack`                    |
| 16     | BAND     | `top of stack = top of stack & second of stack`                       |
| 17     | BOR      | `top of stack = top of stack \| second of stack`                      |
| 18     | BXOR     | `top of stack = top of stack ^ second of stack`                       |
| 19     | EQ       | is `top of stack == second of stack` true?                            |
| 20     | GT       | is `second of stack > top of stack` true?                             |
| 21     | LT       | is `second of stack < top of stack` true?                             |
| 22     | GE       | is `second of stack >= top of stack` true?                            |
| 23     | LE       | is `second of stack <= top of stack` true?                            |
| 24     | NE       | is `second of stack != top of stack` true?                            |
| 25     | DROP     | drop the top of stack                                                 |
| 26     | DUP      | duplicate top of stack on top of stack                                |
| 27     | OVER     | add second of stack on top of stack                                   |
| 28     | RS       | right shift the top of stack                                          |
| 29     | LS       | left shift the top of stack                                           |
| 30     | ED       | Stop execution of this VM                                             |
| 31     | SERO     | Write value at top of stack to UART                                   |
| 32     | PUSH     | Push argument `A` to the stack                                        |
| 33     | OPR      | output ready; used only if multiple VMs are running one after another |
| 34     | PUSHC    | Push top of stack to top of common memory                             |
| 35     | POPC     | Pop top of common memory to the stack                                 |
| 36     | WOPR     | Wait for VM specified by argument `A` to have output ready            |
