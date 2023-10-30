#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, random, string

tot_length = 14
char_length = 10
num_length = 2
schar_length = 2
pw = []

num = string.digits
chars = string.ascii_letters
schars = "~!@#$%^*()+:;<>?{}[]"

pw += "".join(random.choice(chars) for i in range(char_length))
pw += "".join(random.choice(num) for i in range(num_length))
pw += "".join(random.choice(schars) for i in range(schar_length))

random.shuffle(pw)

print("".join(pw))
