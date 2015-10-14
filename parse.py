#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2015 george 
#
# Distributed under terms of the MIT license.
__all__ = ["parser", "pretty"]
import copy

def find_brackets_pair(tokens):
    left = 0
    idx = 0
    for token in tokens:
        if token == "(":
            left += 1
        if token == ")":
            left -= 1
        idx += 1
        if left == -1:
            return idx
    raise Exception('brackets not pair')

## var count
var_count = 0
def parse_tokens(tokens, parents=[]):
    global var_count
    result = []
    idx = 0
    while tokens:
        curr = tokens[0]
        tokens = tokens[1:]

        ## lambda pattern
        if curr.startswith("\\"):
            ## extra var name 
            var = curr.replace("\\", "")

            ## replace var name 
            var_count += 1
            lambda_pattern = parents + [(var, var_count)]

            result.append(["lam", var_count, parse_tokens(tokens, lambda_pattern)])
            break

        ## () pattern
        elif curr == '(':
            pair = find_brackets_pair(tokens)
            result.append(parse_tokens(tokens[:pair-1], parents))
            tokens = tokens[pair:]

        ## var pattern
        else:
            var = dict(parents).get(curr, False)
            if not var:
                var_count += 1
                var = var_count
            result.append(["var", var])
    
    ## merge 
    while len(result) > 1:
        result = [["app", result[0], result[1]]] + result[2:]

    return result[0]


def parser(lambda_query):
    tokens = lambda_query.replace("(", " ( ").replace(")", " ) ").replace("\\", " \\").strip().split()
    return parse_tokens(tokens)


def pretty(data):           
    lambda_type = data[0]   
    lambda_info = data[1:]  
    if lambda_type == 'app':
        return "(%s)(%s)" % (pretty(lambda_info[0]), pretty(lambda_info[1]))
    elif lambda_type == 'var':
        return lambda_info[0]
    elif lambda_type == 'lam':
        return "\%s %s" % (lambda_info[0], pretty(lambda_info[1]))                                                                                                                                                   

if __name__ == '__main__':
    result = parser(r"(\a\b a)b (\a \b b)")
    print result
    result1 = pretty(result)
    print result1
    var_count = 0
    print parser(result1)

