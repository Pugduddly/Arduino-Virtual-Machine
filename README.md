Arduino-Virtual-Machine
=======================

A parallel Virtual Stack Machine Firmware for Arduino

### Instruction set (mostly taken from comments in the firmware source code)
| Opcode | Opcode (hex) | Mnemonic | Description                                                           |
|--------|--------------|----------|-----------------------------------------------------------------------|
| 0      | 0            | NOP      | Do nothing                                                            |
| 1      | 1            | REAP     | Read port value into stack (disabled)                                 |
| 2      | 2            | WRIP     | Write value at top of stack into port (disabled)                      |
| 3      | 3            | JMPF     | `ip = ip + A` (relative jump) forward jump only                       |
| 4      | 4            | JMPB     | `ip = ip - A` (relative jump) backward jump only                      |
| 5      | 5            | JFZ      | if top of stack is 0, `ip = ip + A` (forward jump)                    |
| 6      | 6            | JBZ      | if top of stack is 0, `ip = ip - A` (backward jump)                   |
| 7      | 7            | JFNZ     | if top of stack not 0, `ip = ip + A` (forward jump)                   |
| 8      | 8            | JBNZ     | if top of stack not 0, `ip = ip - A` (backward jump)                  |
| 9      | 9            | LOAD     | `top of stack = stack[content of top of stack]`                       |
| 10     | A            | STORE    | `stack[content of (top of stack - 1)] = top of stack`                 |
| 11     | B            | ADD      | `top of stack = top of stack + second of stack`                       |
| 12     | C            | SUB      | `top of stack = second of stack - top of stack`                       |
| 13     | D            | MUL      | `top of stack = top of stack * second of stack`                       |
| 14     | E            | AND      | `top of stack = top of stack && second of stack`                      |
| 15     | F            | OR       | `top of stack = top of stack \|\| second of stack`                    |
| 16     | 10           | BAND     | `top of stack = top of stack & second of stack`                       |
| 17     | 11           | BOR      | `top of stack = top of stack \| second of stack`                      |
| 18     | 12           | BXOR     | `top of stack = top of stack ^ second of stack`                       |
| 19     | 13           | EQ       | is `top of stack == second of stack` true?                            |
| 20     | 14           | GT       | is `second of stack > top of stack` true?                             |
| 21     | 15           | LT       | is `second of stack < top of stack` true?                             |
| 22     | 16           | GE       | is `second of stack >= top of stack` true?                            |
| 23     | 17           | LE       | is `second of stack <= top of stack` true?                            |
| 24     | 18           | NE       | is `second of stack != top of stack` true?                            |
| 25     | 19           | DROP     | drop the top of stack                                                 |
| 26     | 1A           | DUP      | duplicate top of stack on top of stack                                |
| 27     | 1B           | OVER     | add second of stack on top of stack                                   |
| 28     | 1C           | RS       | right shift the top of stack                                          |
| 29     | 1D           | LS       | left shift the top of stack                                           |
| 30     | 1E           | ED       | Stop execution of this VM                                             |
| 31     | 1F           | SERO     | Write value at top of stack to UART                                   |
| 32     | 20           | PUSH     | Push argument `A` to the stack                                        |
| 33     | 21           | OPR      | output ready; used only if multiple VMs are running one after another |
| 34     | 22           | STC      | Store top of stack to location specified by argument                  |
| 35     | 23           | LDC      | Push value at location specified by argument to stack                 |
| 36     | 24           | WOPR     | Wait for VM specified by argument `A` to have output ready            |
