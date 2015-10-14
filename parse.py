#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2015 george
#
# Distributed under terms of the MIT license.
__all__ = ["parser", "pretty", "weak_normal_form"]
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
def parse_tokens(tokens):
    result = []
    idx = 0
    while tokens:
        curr = tokens[0]
        tokens = tokens[1:]

        ## lambda pattern
        if curr.startswith("\\"):
            ## extra var name
            var = curr.replace("\\", "")
            result.append(["lam", var, parse_tokens(tokens)])
            break

        ## () pattern
        elif curr == '(':
            pair = find_brackets_pair(tokens)
            result.append(parse_tokens(tokens[:pair-1]))
            tokens = tokens[pair:]

        ## var pattern
        else:
            result.append(["var", curr])

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

def weak_normal_form(lambda_tokens):

    def trans_var_name(lambda_tokens, parents=[]):
        if lambda_tokens[0] == "app":
            trans_var_name(lambda_tokens[1], parents)
            trans_var_name(lambda_tokens[2], parents)
        elif lambda_tokens[0] == "lam":
            trans_var_name.var_idx += 1
            var_name = "@{}".format(trans_var_name.var_idx)
            lambda_tokens[2] = trans_var_name(lambda_tokens[2], parents + [(lambda_tokens[1], "@{}".format(trans_var_name.var_idx))])
            lambda_tokens[1] = var_name
        elif lambda_tokens[0] == "var":
            var_name = dict(parents).get(lambda_tokens[1], False)
            if not var_name:
                trans_var_name.var_idx+=1 
                var_name = "@{}".format(trans_var_name.var_idx)
            lambda_tokens[1] = var_name
        return lambda_tokens
    trans_var_name.var_idx = 0

    
    var_tmp = []
    while lambda_tokens[0] == "app" or var_tmp:

        if lambda_tokens[0] == "app":
            var_tmp.append(lambda_tokens[2])
            lambda_tokens = lambda_tokens[1]
        elif lambda_tokens[0] == "lam":
            var_name = lambda_tokens[1]
            curr = var_tmp.pop()
            var = trans_var_name(copy.deepcopy(curr))

            lambda_tokens = lambda_tokens[2]
            cover_var(lambda_tokens, var_name, var)
        elif lambda_tokens[0] == "var":
            break
        else:
            raise Exception('data type error')

    while var_tmp:
        lambda_tokens = ["app", lambda_tokens, var_tmp.pop()]
        
    return lambda_tokens

        
def normal_form(lambda_tokens):
    if lambda_tokens[0] == "lam":
        lambda_tokens = ["lam", lambda_tokens[1], normal_form(lambda_tokens[2])]
    elif lambda_tokens[0] == "app":
        lambda_tokens = weak_normal_form(lambda_tokens)
        if lambda_tokens[0] == "app":
            lambda_tokens[1] = normal_form(lambda_tokens[1])
            lambda_tokens[2] = normal_form(lambda_tokens[2])
        elif lambda_tokens[0] == "lam":
            lambda_tokens = normal_form(lambda_tokens)

    return lambda_tokens

if __name__ == '__main__':
    result = parser(r"""
    (\a \b \c a c c )(\a \b (a b) (\a \b b))(\a \b b)(\a \b a)

            """)

    result1 = pretty(result)
    parser(result1)

    print weak_normal_form(result)


