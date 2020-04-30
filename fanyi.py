def _build_sign(query: str):
    def n(r, o):
        for t in range(0, len(o) - 2, 3):
            a = o[t + 2]
            if a >= 'a':
                a = ord(a[0]) - 87
            else:
                a = int(a)
            if '+' == o[t + 1]:
                a = r >> a
            else:
                a = r << a
            if '+' == o[t]:
                r = r + a & 4294967295
            else:
                r = r ^ a
        return r

    m, s = [int(i) for i in "320305.131321201".split('.')]
    S = {}
    c = 0
    v = 0
    while v < len(query):
        A = ord(query[v])
        if 128 > A:
            S[c] = A
            c += 1
        else:
            if 2048 > A:
                S[c] = A >> 6 | 192
                c += 1
            else:
                if 55296 == 64512 & A and v + 1 < len(query) and 56320 == 64512 & ord(query[v + 1]):
                    v += 1
                    A = 65536 + ((1023 & A) << 10) + (1023 & ord(query[v]))
                    S[c] = A >> 18 | 240
                    c += 1
                    S[c] = A >> 12 & 63 | 128
                    c += 1
                else:
                    S[c] = A >> 12 | 224
                    c += 1
                    S[c] = A >> 6 & 63 | 128
                    c += 1
                S[c] = 63 & A | 128
                c += 1
        v += 1
    p = m
    F = "+-a^+6"
    D = "+-3^+b+-f"
    for b in range(len(S)):
        p += S[list(S.keys())[b]]
        p = n(p, F)
    p = n(p, D)
    p ^= s
    if 0 > p:
        p = 2147483647 & p + 2147483648
    p %= int(1e6)
    return str(p) + '.' + str(p ^ m)
