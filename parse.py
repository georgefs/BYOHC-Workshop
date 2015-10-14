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
        return r"\%s %s" % (lambda_info[0], pretty(lambda_info[1]))

def cover_var(lambda_tokens, var, value):
    if lambda_tokens[0] == "var" and lambda_tokens[1] == var:
        return value
    elif lambda_tokens[0] == "app":
        lambda_tokens[1] = cover_var(lambda_tokens[1], var, value)
        lambda_tokens[2] = cover_var(lambda_tokens[2], var, value)
    elif lambda_tokens[0] == "lam":
        lambda_tokens[2] = cover_var(lambda_tokens[2], var, value)
    return lambda_tokens

def weak_normal(lambda_tokens):
    var_tmp = []
    while lambda_tokens[0] == "app" or var_tmp:
        if lambda_tokens[0] == "app":
            var_tmp.append(lambda_tokens[2])
            lambda_tokens = lambda_tokens[1]
        elif lambda_tokens[0] == "lam":
            var_name = lambda_tokens[1]
            var = var_tmp.pop()
            lambda_tokens = lambda_tokens[2]
            cover_var(lambda_tokens, var_name, var)
        elif lambda_tokens[0] == "var":
            break
        else:
            raise Exception('data type error')

    while var_tmp:
        lambda_tokens = ["app", lambda_tokens, var_tmp.pop()]
        
    return lambda_tokens

        

if __name__ == '__main__':
    result = parser(r"(\a\b a)b (\a \b b) c")
    print result
    result1 = pretty(result)
    print result1
    var_count = 0
    print parser(result1)
    print weak_normal(result)


