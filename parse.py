#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2015 george
#
# Distributed under terms of the MIT license.
__all__ = ["parser", "pretty", "weak_normal_form", "cover_var"]
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

def new_var():
    new_var.idx += 1
    return "@{}".format(new_var.idx)
new_var.idx = 0

def trans_var_name(lambda_tokens, env=[], exclude=[]):
    if lambda_tokens[0] == "app":
        trans_var_name(lambda_tokens[1], env)
        trans_var_name(lambda_tokens[2], env)
    elif lambda_tokens[0] == "lam":
        var_name = new_var()
        lambda_tokens[2] = trans_var_name(lambda_tokens[2], env + [(lambda_tokens[1], var_name)])
        lambda_tokens[1] = var_name
    elif lambda_tokens[0] == "var":
        var_name = dict(env).get(lambda_tokens[1], False)
        if not var_name and lambda_tokens[1] in exclude:
            var_name = lambda_tokens[1]
        if not var_name:
            var_name = new_var()
        lambda_tokens[1] = var_name
    return lambda_tokens


def weak_normal_form(lambda_tokens, env=[], exclude=[]):
    var_tmp = []
    while lambda_tokens[0] == "app" or var_tmp:

        if lambda_tokens[0] == "app":
            var_tmp.append(lambda_tokens[2])
            lambda_tokens = lambda_tokens[1]
        elif lambda_tokens[0] == "lam":
            var_name = lambda_tokens[1]
            new_env = env
            if var_name not in dict(env):
                new_env += [(var_name, new_var())]
            curr = var_tmp.pop()
            var = trans_var_name(copy.deepcopy(curr), new_env, exclude)

            lambda_tokens = lambda_tokens[2]
            cover_var(lambda_tokens, var_name, var)
        elif lambda_tokens[0] == "var":
            break
        else:
            raise Exception('data type error')

    while var_tmp:
        lambda_tokens = ["app", lambda_tokens, var_tmp.pop()]
        
    return lambda_tokens

        
def normal_form(lambda_tokens, env=[], exclude=[]):
    if lambda_tokens[0] == "lam":
        lambda_tokens = ["lam", lambda_tokens[1], normal_form(lambda_tokens[2], env, exclude+[lambda_tokens[1]])]
    elif lambda_tokens[0] == "app":
        lambda_tokens = weak_normal_form(lambda_tokens, env, exclude)
        if lambda_tokens[0] == "app":
            lambda_tokens[1] = normal_form(lambda_tokens[1], env, exclude)
            lambda_tokens[2] = normal_form(lambda_tokens[2], env, exclude)
        elif lambda_tokens[0] == "lam":
            lambda_tokens = normal_form(lambda_tokens, env, exclude)

    return lambda_tokens

if __name__ == '__main__':
    result = parser(r"""
            (\true(\false(\not not true)(\p \a \b p b a))(\a \b b))(\a \b a)
            """)

    result1 = pretty(result)
    parser(result1)

    print normal_form(result)


