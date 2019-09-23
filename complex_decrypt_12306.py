# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2019-09-16 15:51
# @Version     : Python 3.6.8
# @Description :
import json
import re
from _md5 import md5
from _sha256 import sha256
from base64 import b64encode
from time import time

import execjs
import requests

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
              "like Gecko) Chrome/75.0.3770.80 Safari/537.36")
Db = ("appCodeName appMinorVersion appName cpuClass onLine systemLanguage userLanguage historyList "
      "hasLiedLanguages hasLiedResolution hasLiedOs hasLiedBrowser").split(" ")
Jb = ["sessionStorage", "localStorage", "indexedDb", "openDatabase"]
Ib = ["scrAvailWidth", "scrAvailHeight"]
Cb = ["scrDeviceXDPI", "scrColorDepth", "scrWidth", "scrHeight"]
MORE_INFO_SET = {'session_storage', 'local_storage', 'indexed_db', 'open_database', 'do_not_track', 'ie_plugins',
                 'regular_plugins', 'adblock', 'has_lied_languages', 'has_lied_resolution', 'has_lied_os',
                 'has_lied_browser', 'touch_support', 'js_fonts'}
ESSENTIAL_DICT = {
    'Fb': ["sessionStorage", "localStorage", "indexedDb", "openDatabase"],
    'Gb': ["scrDeviceXDPI", "scrColorDepth", "scrWidth", "scrHeight"],
    'Hb': ["scrAvailWidth", "scrAvailHeight"],
    'ba': 8,
    'gb': {
        "plugins": "ks0Q",
        "hasLiedResolution": "3neK",
        "online": "9vyE",
        "systemLanguage": "e6OK",
        "javaEnabled": "yD16",
        "scrWidth": "ssI5",
        "flashVersion": "dzuS",
        "jsFonts": "EOQP",
        "scrAvailHeight": "88tV",
        "browserLanguage": "q4f3",
        "scrHeight": "5Jwy",
        "browserName": "-UVA",
        "userAgent": "0aew",
        "localCode": "lEnu",
        "indexedDb": "3sw-",
        "cookieEnabled": "VPIf",
        "timeZone": "q5aJ",
        "hasLiedBrowser": "2xC5",
        "browserVersion": "d435",
        "touchSupport": "wNLf",
        "hasLiedLanguages": "j5po",
        "scrAvailSize": "TeRS",
        "userLanguage": "hLzX",
        "srcScreenSize": "tOHY",
        "cookieCode": "VySQ",
        "storeDb": "Fvje",
        "openDatabase": "V8vl",
        "appcodeName": "qT7b",
        "localStorage": "XM7l",
        "appMinorVersion": "qBVW",
        "scrAvailWidth": "E-lJ",
        "cpuClass": "Md7A",
        "os": "hAqN",
        "scrColorDepth": "qmyu",
        "mimeTypes": "jp76",
        "adblock": "FMQw",
        "sessionStorage": "HVia",
        "hasLiedOs": "ci5c",
        "historyList": "kU5z",
        "doNotTrack": "VEek",
        "webSmartID": "E3gR",
        "scrDeviceXDPI": "3jCe"
    }
}

__X64HASH128_STR = """
         function x64hash128(a, b) {
                a = a || "";
                b = b || 0;
                for (var c = a.length % 16, d = a.length - c, e = [0, b], f = [0, b], h, p, g = [2277735313, 289559509], m = [1291169091, 658871167], l = 0; l < d; l += 16)
                    h = [a.charCodeAt(l + 4) & 255 | (a.charCodeAt(l + 5) & 255) << 8 | (a.charCodeAt(l + 6) & 255) << 16 | (a.charCodeAt(l + 7) & 255) << 24, a.charCodeAt(l) & 255 | (a.charCodeAt(l + 1) & 255) << 8 | (a.charCodeAt(l + 2) & 255) << 16 | (a.charCodeAt(l + 3) & 255) << 24],
                    p = [a.charCodeAt(l + 12) & 255 | (a.charCodeAt(l + 13) & 255) << 8 | (a.charCodeAt(l + 14) & 255) << 16 | (a.charCodeAt(l + 15) & 255) << 24, a.charCodeAt(l + 8) & 255 | (a.charCodeAt(l + 9) & 255) << 8 | (a.charCodeAt(l + 10) & 255) << 16 | (a.charCodeAt(l + 11) & 255) << 24],
                    h = x64Multiply(h, g),
                    h = x64Rotl(h, 31),
                    h = x64Multiply(h, m),
                    e = x64Xor(e, h),
                    e = x64Rotl(e, 27),
                    e = x64Add(e, f),
                    e = x64Add(x64Multiply(e, [0, 5]), [0, 1390208809]),
                    p = x64Multiply(p, m),
                    p = x64Rotl(p, 33),
                    p = x64Multiply(p, g),
                    f = x64Xor(f, p),
                    f = x64Rotl(f, 31),
                    f = x64Add(f, e),
                    f = x64Add(x64Multiply(f, [0, 5]), [0, 944331445]);
                h = [0, 0];
                p = [0, 0];
                switch (c) {
                case 15:
                    p = x64Xor(p, x64LeftShift([0, a.charCodeAt(l + 14)], 48));
                case 14:
                    p = x64Xor(p, x64LeftShift([0, a.charCodeAt(l + 13)], 40));
                case 13:
                    p = x64Xor(p, x64LeftShift([0, a.charCodeAt(l + 12)], 32));
                case 12:
                    p = x64Xor(p, x64LeftShift([0, a.charCodeAt(l + 11)], 24));
                case 11:
                    p = x64Xor(p, x64LeftShift([0, a.charCodeAt(l + 10)], 16));
                case 10:
                    p = x64Xor(p, x64LeftShift([0, a.charCodeAt(l + 9)], 8));
                case 9:
                    p = x64Xor(p, [0, a.charCodeAt(l + 8)]),
                    p = x64Multiply(p, m),
                    p = x64Rotl(p, 33),
                    p = x64Multiply(p, g),
                    f = x64Xor(f, p);
                case 8:
                    h = x64Xor(h, x64LeftShift([0, a.charCodeAt(l + 7)], 56));
                case 7:
                    h = x64Xor(h, x64LeftShift([0, a.charCodeAt(l + 6)], 48));
                case 6:
                    h = x64Xor(h, x64LeftShift([0, a.charCodeAt(l + 5)], 40));
                case 5:
                    h = x64Xor(h, x64LeftShift([0, a.charCodeAt(l + 4)], 32));
                case 4:
                    h = x64Xor(h, x64LeftShift([0, a.charCodeAt(l + 3)], 24));
                case 3:
                    h = x64Xor(h, x64LeftShift([0, a.charCodeAt(l + 2)], 16));
                case 2:
                    h = x64Xor(h, x64LeftShift([0, a.charCodeAt(l + 1)], 8));
                case 1:
                    h = x64Xor(h, [0, a.charCodeAt(l)]),
                    h = x64Multiply(h, g),
                    h = x64Rotl(h, 31),
                    h = x64Multiply(h, m),
                    e = x64Xor(e, h)
                }
                e = x64Xor(e, [0, a.length]);
                f = x64Xor(f, [0, a.length]);
                e = x64Add(e, f);
                f = x64Add(f, e);
                e = x64Fmix(e);
                f = x64Fmix(f);
                e = x64Add(e, f);
                f = x64Add(f, e);
                return ("00000000" + (e[0] >>> 0).toString(16)).slice(-8) + ("00000000" + (e[1] >>> 0).toString(16)).slice(-8) + ("00000000" + (f[0] >>> 0).toString(16)).slice(-8) + ("00000000" + (f[1] >>> 0).toString(16)).slice(-8)
            };
        function x64Multiply(a, b) {
                a = [a[0] >>> 16, a[0] & 65535, a[1] >>> 16, a[1] & 65535];
                b = [b[0] >>> 16, b[0] & 65535, b[1] >>> 16, b[1] & 65535];
                var c = [0, 0, 0, 0];
                c[3] += a[3] * b[3];
                c[2] += c[3] >>> 16;
                c[3] &= 65535;
                c[2] += a[2] * b[3];
                c[1] += c[2] >>> 16;
                c[2] &= 65535;
                c[2] += a[3] * b[2];
                c[1] += c[2] >>> 16;
                c[2] &= 65535;
                c[1] += a[1] * b[3];
                c[0] += c[1] >>> 16;
                c[1] &= 65535;
                c[1] += a[2] * b[2];
                c[0] += c[1] >>> 16;
                c[1] &= 65535;
                c[1] += a[3] * b[1];
                c[0] += c[1] >>> 16;
                c[1] &= 65535;
                c[0] += a[0] * b[3] + a[1] * b[2] + a[2] * b[1] + a[3] * b[0];
                c[0] &= 65535;
                return [c[0] << 16 | c[1], c[2] << 16 | c[3]]
            };
        function x64Rotl(a, b) {
                b %= 64;
                if (32 === b)
                    return [a[1], a[0]];
                if (32 > b)
                    return [a[0] << b | a[1] >>> 32 - b, a[1] << b | a[0] >>> 32 - b];
                b -= 32;
                return [a[1] << b | a[0] >>> 32 - b, a[0] << b | a[1] >>> 32 - b]
            };
        function x64Xor(a, b) {
                return [a[0] ^ b[0], a[1] ^ b[1]]
            };
        function x64Add(a, b) {
                a = [a[0] >>> 16, a[0] & 65535, a[1] >>> 16, a[1] & 65535];
                b = [b[0] >>> 16, b[0] & 65535, b[1] >>> 16, b[1] & 65535];
                var c = [0, 0, 0, 0];
                c[3] += a[3] + b[3];
                c[2] += c[3] >>> 16;
                c[3] &= 65535;
                c[2] += a[2] + b[2];
                c[1] += c[2] >>> 16;
                c[2] &= 65535;
                c[1] += a[1] + b[1];
                c[0] += c[1] >>> 16;
                c[1] &= 65535;
                c[0] += a[0] + b[0];
                c[0] &= 65535;
                return [c[0] << 16 | c[1], c[2] << 16 | c[3]]
            };
        function x64LeftShift(a, b) {
                b %= 64;
                return 0 === b ? a : 32 > b ? [a[0] << b | a[1] >>> 32 - b, a[1] << b] : [a[1] << b - 32, 0]
            };
        function x64Fmix(a) {
                a = x64Xor(a, [0, a[0] >>> 1]);
                a = x64Multiply(a, [4283543511, 3981806797]);
                a = x64Xor(a, [0, a[0] >>> 1]);
                a = x64Multiply(a, [3301882366, 444984403]);
                return a = x64Xor(a, [0, a[0] >>> 1])
            };

        """
__X64HASH128_COMPILE = execjs.compile(__X64HASH128_STR)
canvas = "canvas winding:yes~canvas fp:data:image/png;base64,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CBAgQIAAAQIECBAgQIAAAQIECBAgMEKBthborT3VqVv3XJDkW0n22e0+Jz3+bP45d2qmDRw8wiyddVmrPH/v0o3pm3P0EMG3JLkmyfVVqrqzgKQlQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIDAngm0vUAf3F6d+pQkdyTZ/dPTkx9clZWnTct0Jfpbxrq269Ucs3R9+uYcN8S4/5HkAued79l/CFcTIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQINC5AnutQG+R16mnJLkpyWd2O4KJq9dm2QlbMuPN4V5T3hlTXLHvmsxauW+29gx1lvwtSS6vUr3RGShSEiBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAoLnAXi3QB7dfp74wyXeTtM5I3/XT9dIruf/4F3Pq67OaRx7H37B4/ydz5jPvzsBhU3eTonXG+RerVK0n+30IECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAYA8ExkSB3trv9qfRFya5MsnEXTJUmzblzqNW5pP/ev8e5Cvn0tsPfzifXTUr9eTJbxOqddb5D5IsrFJtLCe0JAQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIEGifwJgp0Acj16lnJvlJktN2Yai2bMklFyzOzb8/I131hPYx7cU7DVT9uei8JfnNbfNS77PrHxYki5NcVqVasRd36dYECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAY9wJjrkAfFN3+Wvcbkux61vfUe5Zl2TnTMr1/+rifwFABnp/wYk784/q8etbst7nshSQLqlS3FW0gHAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBNokMGYL9Fb+OvV+Sa5oFcW7FOlV77+z4Oylue7B01PVXW3yas9tBqqBXHXqknz/rpNSH3jATjdtFeffSfLTKlVfezbkLgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIEChfYEwX6IP8deruJF9I8vUkPW8Zy5SHnsq9ZyUf3DSjiHE9NOWpnPWnidn0keN2yrM6yXVJbqpStc489yFAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgACBURQYFwX6YN46desM8EuSXJ3k/wVzNdCf+QsW5+7vnZz96wNH0ad9X9VbvZZzrnw8S244NXXXjk/Ut842/3aSW6pU/e3bkDsRIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECgswTGVYG+42jq1OcnuTjJef/7965163PZxctz470fyH7bXv8+9j9vVJvzlY89lpsWzczAoVN32PDtSX5dpfrD2A9hhwQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIEBj/AuO2QB+kr7PtifNPJ7koyelJqkx4YV0uv3R5brjvQ+keo0X65mpzvvbRR/LzX85M//RDkgwkuT/JoiS3V6leH/8/LwkIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECAwfgTGfYG+I3Wd+sjtRXqrTJ+9rUi/8PPPZeGf5+SYet8xMZbVXX25+hPL8tufHZX+6e9K8kSSW5P8qkr1wpjYo00QIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECgAwWKKtB3KtOP2P5E+vwk83LI3QP50jUb89VlJ2X/ekpbZ72p2pTrT3wiP7p2ctafOyHJA0mWtJ44r1Ktbete3IwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIE3lag2AJ957TbX/U+P5M2zs37fndw5t11UE7423vy4TU9OanvqG2vfh+dT51H91udh3tWZ8Ws5/Lgub1Zft6G9E15LMniKtVro3Mb30KAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECoykwWqXxaO6prd9Vpz4oM5YdnYt+2JOTHz0yb/TNzqeeap2rfng2TJyaiQNTcsBA64n1ads2trl6JVuqjdnatTFTt25I8mLunNGb7u7l+fspz+fmL6/J07NXVal62xrEzQgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECgkUDHF+iN9CwmQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgWIEFOjFjFIQAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIEGgioEBvomctAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBQjoEAvZpSCECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgEATAQV6Ez1rCRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQKAYAQV6MaMUhAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgSaCCjQm+hZS4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLFCCjQixmlIAQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECDQRECB3kTPWgIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoRkCBXswoBSFAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgACBJgIK9CZ61hIgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAMQIK9GJGKQgBAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQINBFQoDfRs5YAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEihFQoBczSkEIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAoImAAr2JnrUECBD60sx+AAAFgElEQVQgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgUIyAAr2YUQpCgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAk0EFOhN9KwlQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgWIEFOjFjFIQAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIEGgioEBvomctAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBQjoEAvZpSCECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgEATAQV6Ez1rCRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQKAYAQV6MaMUhAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgSaCCjQm+hZS4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLFCCjQixmlIAQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECDQRECB3kTPWgIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoRkCBXswoBSFAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgACBJgIK9CZ61hIgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAMQIK9GJGKQgBAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQINBFQoDfRs5YAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEihFQoBczSkEIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAoImAAr2JnrUECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgUIyAAr2YUQpCgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAk0EFOhN9KwlQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgWIEFOjFjFIQAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIEGgioEBvomctAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBQjoEAvZpSCECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgEATAQV6Ez1rCRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQKAYAQV6MaMUhAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgSaCCjQm+hZS4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLFCCjQixmlIAQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECDQRECB3kTPWgIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoRkCBXswoBSFAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgACBJgIK9CZ61hIgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAMQIK9GJGKQgBAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQINBFQoDfRs5YAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEihFQoBczSkEIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAoImAAr2JnrUECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgUIyAAr2YUQpCgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAk0EFOhN9KwlQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgWIEFOjFjFIQAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIEGgi8F8L2Dx8EPrRcgAAAABJRU5ErkJggg=="
webgl = "data:image/png;base64,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~extensions:ANGLE_instanced_arrays;EXT_blend_minmax;EXT_color_buffer_half_float;EXT_disjoint_timer_query;EXT_float_blend;EXT_frag_depth;EXT_shader_texture_lod;EXT_texture_filter_anisotropic;WEBKIT_EXT_texture_filter_anisotropic;EXT_sRGB;OES_element_index_uint;OES_standard_derivatives;OES_texture_float;OES_texture_float_linear;OES_texture_half_float;OES_texture_half_float_linear;OES_vertex_array_object;WEBGL_color_buffer_float;WEBGL_compressed_texture_s3tc;WEBKIT_WEBGL_compressed_texture_s3tc;WEBGL_compressed_texture_s3tc_srgb;WEBGL_debug_renderer_info;WEBGL_debug_shaders;WEBGL_depth_texture;WEBKIT_WEBGL_depth_texture;WEBGL_draw_buffers;WEBGL_lose_context;WEBKIT_WEBGL_lose_context~webgl aliased line width range:[1, 1]~webgl aliased point size range:[1, 1024]~webgl alpha bits:8~webgl antialiasing:yes~webgl blue bits:8~webgl depth bits:24~webgl green bits:8~webgl max anisotropy:16~webgl max combined texture image units:32~webgl max cube map texture size:16384~webgl max fragment uniform vectors:1024~webgl max render buffer size:16384~webgl max texture image units:16~webgl max texture size:16384~webgl max varying vectors:30~webgl max vertex attribs:16~webgl max vertex texture image units:16~webgl max vertex uniform vectors:4096~webgl max viewport dims:[16384, 16384]~webgl red bits:8~webgl renderer:WebKit WebGL~webgl shading language version:WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)~webgl stencil bits:0~webgl vendor:WebKit~webgl version:WebGL 1.0 (OpenGL ES 2.0 Chromium)~webgl vertex shader high float precision:23~webgl vertex shader high float precision rangeMin:127~webgl vertex shader high float precision rangeMax:127~webgl vertex shader medium float precision:23~webgl vertex shader medium float precision rangeMin:127~webgl vertex shader medium float precision rangeMax:127~webgl vertex shader low float precision:23~webgl vertex shader low float precision rangeMin:127~webgl vertex shader low float precision rangeMax:127~webgl fragment shader high float precision:23~webgl fragment shader high float precision rangeMin:127~webgl fragment shader high float precision rangeMax:127~webgl fragment shader medium float precision:23~webgl fragment shader medium float precision rangeMin:127~webgl fragment shader medium float precision rangeMax:127~webgl fragment shader low float precision:23~webgl fragment shader low float precision rangeMin:127~webgl fragment shader low float precision rangeMax:127~webgl vertex shader high int precision:0~webgl vertex shader high int precision rangeMin:31~webgl vertex shader high int precision rangeMax:30~webgl vertex shader medium int precision:0~webgl vertex shader medium int precision rangeMin:31~webgl vertex shader medium int precision rangeMax:30~webgl vertex shader low int precision:0~webgl vertex shader low int precision rangeMin:31~webgl vertex shader low int precision rangeMax:30~webgl fragment shader high int precision:0~webgl fragment shader high int precision rangeMin:31~webgl fragment shader high int precision rangeMax:30~webgl fragment shader medium int precision:0~webgl fragment shader medium int precision rangeMin:31~webgl fragment shader medium int precision rangeMax:30~webgl fragment shader low int precision:0~webgl fragment shader low int precision rangeMin:31~webgl fragment shader low int precision rangeMax:30"


def __x64hash128(paint_text: str):
    return __X64HASH128_COMPILE.call("x64hash128", paint_text, 31)


def __get_machine_code():
    return [
        {"cookieCode": "new"},  # uuid
        {"cookieCode": "new"},  # cookieCode
        {"userAgent": USER_AGENT},  # userAgent
        {"scrHeight": "1080"},  # 屏幕高度
        {"scrWidth": "1920"},  # 屏幕宽度
        {"scrAvailHeight": "1040"},  # 可用的屏幕高度
        {"scrAvailWidth": "1920"},  # 可用的屏幕宽度
        {"scrColorDepth": "24"},  # 颜色深度
        {"scrDeviceXDPI": ""},
        {"appCodeName": "Mozilla"},
        {"appName": "Netscape"},
        {"javaEnabled": "0"},  # '1', '0'
        {"mimeTypes": __get_mime_type()},  # "52d67b2a5aa5e031084733d5006cc664"
        {"os": "Win32"},  # 平台名称
        {"appMinorVersion": ""},
        {"browserLanguage": "zh-CN"},  # 浏览器语言
        {"cookieEnabled": "1"},  # '1', '0'
        {"cpuClass": ""},
        {"onLine": "true"},  # 'true', 'false'
        {"systemLanguage": ""},
        {"userLanguage": ""},
        {"timeZone": -8},  # 时区偏移量
        {"flashVersion": 0},
        {"historyList": 3},
        {"custID": "133"},  # 133
        {"platform": "WEB"},  # "WEB", "WAP"
    ]


def __get_mime_type(mime_type_list: list = None):
    # "application/pdf#application/x-google-chrome-pdf#application/x-nacl#application/x-pnacl"
    if mime_type_list is None:
        mime_type_list = ['application/pdf', 'application/x-google-chrome-pdf',
                          'application/x-nacl', 'application/x-pnacl']
    return md5('#'.join(mime_type_list).encode()).hexdigest()


def __more_info():
    _base_info_list = [
        {"user_agent": USER_AGENT.replace('/', '')},
        {"language": "zh-CN"},  # 语言
        {"color_depth": 24},  # 颜色深度
        {"pixel_ratio": 1},  # 像素密度
        {"resolution": [1920, 1080]},  # 屏幕宽、高度
        {"available_resolution": [1920, 1040]},  # 可用屏幕宽、高度
        {"timezone_offset": -480},  # 时区偏移量
        {"session_storage": 1},  # 1
        {"local_storage": 1},  # 1
        {"indexed_db": 1},  # 1
        {"open_database": 1},  # 1
        {"cpu_class": "unknown"},  # 需要获取的cpuClass, "unknown"
        {"navigator_platform": "Win32"},  # 平台名称
        {"do_not_track": "unknown"},
        {"regular_plugins": ["Chrome PDF Plugin::Portable Document Format::application/x-google-chrome-pdf~pdf",
                             "Chrome PDF Viewer::::application/pdf~pdf",
                             "Native Client::::application/x-nacl~,application/x-pnacl~"]},
        {"canvas": canvas},
        {"webgl": webgl},
        {"adblock": "0"},  # "0", "1"
        {"has_lied_languages": "false"},  # False
        {"has_lied_resolution": "false"},  # False
        {"has_lied_os": "false"},  # False
        {"has_lied_browser": "false"},  # False
        {"touch_support": ["0", "false", "false"]},  # [0, False, False]
        {"js_fonts": ["Arial", "Arial Black", "Arial Narrow", "Book Antiqua", "Bookman Old Style",
                      "Calibri", "Cambria", "Cambria Math", "Century", "Century Gothic", "Century Schoolbook",
                      "Comic Sans MS", "Consolas", "Courier", "Courier New", "Garamond", "Georgia", "Helvetica",
                      "Impact", "Lucida Bright", "Lucida Calligraphy", "Lucida Console", "Lucida Fax",
                      "Lucida Handwriting", "Lucida Sans", "Lucida Sans Typewriter", "Lucida Sans Unicode",
                      "Microsoft Sans Serif", "Monotype Corsiva", "MS Gothic", "MS PGothic",
                      "MS Reference Sans Serif", "MS Sans Serif", "MS Serif", "Palatino Linotype",
                      "Segoe Print", "Segoe Script", "Segoe UI", "Segoe UI Light", "Segoe UI Semibold",
                      "Segoe UI Symbol", "Tahoma", "Times", "Times New Roman", "Trebuchet MS", "Verdana",
                      "Wingdings", "Wingdings 2", "Wingdings 3"]}  # 可以随机去掉一些
    ]

    _new_base_info_list = []
    for _base_dict in _base_info_list:
        key, value = list(_base_dict.items())[0]
        if isinstance(value, list):
            value = ';'.join([str(v) for v in value])
        else:
            value = str(value)
        _new_base_info_list.append(value)
    _info_str = "~~~".join(_new_base_info_list)
    more_info_list = [
        {"webSmartID": __x64hash128(_info_str)}  # webSmartID
    ]
    for _base_dict in _base_info_list:
        key, value = list(_base_dict.items())[0]
        if key == 'session_storage':
            more_info_list.append({"sessionStorage": str(value)})
        if key == 'local_storage':
            more_info_list.append({"localStorage": str(value)})
        if key == 'indexed_db':
            more_info_list.append({"indexedDb": str(value)})
        if key == 'open_database':
            more_info_list.append({"openDatabase": str(value)})
        if key == 'do_not_track':
            more_info_list.append({"doNotTrack": str(value)})
        if key == 'regular_plugins':
            more_info_list.append(
                {"plugins": md5("Chrome PDF Plugin#Chrome PDF Viewer#Native Client#".encode()).hexdigest()})
        if key == 'adblock':
            more_info_list.append({"adblock": str(value)})
        if key == 'has_lied_languages':
            more_info_list.append({"hasLiedLanguages": str(value)})
        if key == 'has_lied_resolution':
            more_info_list.append({"hasLiedResolution": str(value)})
        if key == 'has_lied_os':
            more_info_list.append({"hasLiedOs": str(value)})
        if key == 'has_lied_browser':
            more_info_list.append({"hasLiedBrowser": str(value)})
        if key == 'touch_support':
            more_info_list.append({"touchSupport": md5('#'.join(value).encode()).hexdigest()})
        if key == 'js_fonts':
            more_info_list.append({"jsFonts": md5('#'.join(value).encode()).hexdigest()})
    return more_info_list


def __get_pact_str():
    b = __get_machine_code()
    b.extend(__more_info())
    return sorted(b, key=lambda x: list(x.keys())[0])


# def __hash_alg_1(a, b, c):
#     # 2019-09-17
#     hb = ESSENTIAL_DICT['gb']
#     a = sorted(a, key=lambda x: list(x.keys())[0])
#     for d in range(a.__len__()):
#         key, value = list(a[d].items())[0]
#         e = key.replace('%', '')
#         if isinstance(value, str):
#             f = value.replace('%', '')
#         elif isinstance(value, (int, float)):
#             f = str(value)
#         elif isinstance(value, list):
#             f = ','.join(value)
#         else:
#             f = value
#         if f != '':
#             c += e + f
#             if e in hb:
#                 b += '\\x26' + hb[e] + '\\x3d' + f
#             else:
#                 b += '\\x26' + e + '\\x3d' + f
#
#     a = c[::-1]
#     d = a[::-1]
#     e = d.__len__()
#     f = e // 3 if e % 3 is 0 else e // 3 + 1
#     if 3 > e:
#         a = d
#     else:
#         a = d[:f]
#         c = d[f: 2 * f]
#         d = d[2 * f: e]
#         a = c + d + a
#
#     c = a.__len__()
#     d = c // 3 if c % 3 is 0 else c // 3 + 1
#     if 3 <= c:
#         e = a[:d]
#         f = a[d: 2 * d]
#         a = a[2 * d:c] + e + f
#     c = a.__len__()
#     d = list(a)
#     for e in range(c // 2):
#         if e % 2 is 0:
#             d[e], d[c - 1 - e] = d[c - 1 - e], a[e]
#     c = ''.join(d)
#     # lfJiWHUM5UBcZMmc4b0BoGLtq6dDgsPqGkVnj7Ku73g
#     c = b64encode(sha256(c.encode()).digest(), b'-_').decode().replace('=', '')
#     return {b: c}

def __hash_alg(a, b, c):
    """
    12306哈希算法，改版很快 15天内必改版
    """
    hb = ESSENTIAL_DICT['gb']
    d = {}
    for i in a:
        d.update(i)
    a = dict(sorted(d.items(), key=lambda x: x[0]))
    # a = sorted(a, key=lambda x: list(x.keys())[0])
    for key, value in a.items():
        e = key.replace('%', '')
        if isinstance(value, str):
            f = value.replace('%', '')
        elif isinstance(value, (int, float)):
            f = str(value)
        elif isinstance(value, list):
            f = ','.join(value)
        else:
            f = value
        if f != '':
            c += e + f
            if e in hb:
                b += '\x26' + hb[e] + '\x3d' + f
            else:
                b += '\x26' + e + '\x3d' + f
    a = c
    c = a.__len__()
    if a.__len__() % 2 is 0:
        d = a[c // 2: c] + a[0: c // 2]
    else:
        d = a[c // 2 + 1: c] + a[c // 2] + a[0: c // 2]
    a = b64encode(sha256(d.encode()).digest(), b'-_').decode().replace('=', '')
    c = a[::-1]
    c = b64encode(sha256(c.encode()).digest(), b'-_').decode().replace('=', '')
    return b, c

def get_device_api():
    a = ''
    e = ''
    l = __get_pact_str()
    k = []
    n = []
    q = []
    h = []
    for m in range(l.__len__()):
        key, value = list(l[m].items())[0]
        if 'new' != value and key not in Db:
            if key in Jb:
                n.append(l[m])
            elif key in Ib:
                q.append(l[m])
            elif key in Cb:
                h.append(l[m])
            else:
                k.append(l[m])

    l = ''
    for m in range(n.__len__()):
        key, value = list(n[m].items())[0]
        l = l + key[0] + value

    n = ''
    for m in range(h.__len__()):
        key, value = list(h[m].items())[0]
        n = n + value if m is 0 else n + 'x' + value
    h = ''
    for m in range(q.__len__()):
        key, value = list(q[m].items())[0]
        h = h + value if m is 0 else h + 'x' + value
    k.append({'storeDb': l})
    k.append({'srcScreenSize': n})
    k.append({'scrAvailSize': h})
    a, e = __hash_alg(k, a, e)
    a = a.replace('\\x26', '&').replace('\\x3d', '=')
    a += f'\x26timestamp\x3d{int(time() * 1000)}'
    js_api = 'https://kyfw.12306.cn/otn/HttpZF/GetJS'
    js_text = requests.request(method='get', url=js_api, headers={'user-agent': USER_AGENT}).text
    device_api = ("https://kyfw.12306.cn/otn/HttpZF/logdevice"
                  + re.search(r'(\?algID.*?hashCode\\x3d)', js_text).group(1).replace('\\x26', '&').replace('\\x3d', '=') + e + a)
    return device_api


if __name__ == '__main__':
    """
         x64hash128: function(a, b) {
                a = a || "";
                b = b || 0;
                for (var c = a.length % 16, d = a.length - c, e = [0, b], f = [0, b], h, p, g = [2277735313, 289559509], m = [1291169091, 658871167], l = 0; l < d; l += 16)
                    h = [a.charCodeAt(l + 4) & 255 | (a.charCodeAt(l + 5) & 255) << 8 | (a.charCodeAt(l + 6) & 255) << 16 | (a.charCodeAt(l + 7) & 255) << 24, a.charCodeAt(l) & 255 | (a.charCodeAt(l + 1) & 255) << 8 | (a.charCodeAt(l + 2) & 255) << 16 | (a.charCodeAt(l + 3) & 255) << 24],
                    p = [a.charCodeAt(l + 12) & 255 | (a.charCodeAt(l + 13) & 255) << 8 | (a.charCodeAt(l + 14) & 255) << 16 | (a.charCodeAt(l + 15) & 255) << 24, a.charCodeAt(l + 8) & 255 | (a.charCodeAt(l + 9) & 255) << 8 | (a.charCodeAt(l + 10) & 255) << 16 | (a.charCodeAt(l + 11) & 255) << 24],
                    h = this.x64Multiply(h, g),
                    h = this.x64Rotl(h, 31),
                    h = this.x64Multiply(h, m),
                    e = this.x64Xor(e, h),
                    e = this.x64Rotl(e, 27),
                    e = this.x64Add(e, f),
                    e = this.x64Add(this.x64Multiply(e, [0, 5]), [0, 1390208809]),
                    p = this.x64Multiply(p, m),
                    p = this.x64Rotl(p, 33),
                    p = this.x64Multiply(p, g),
                    f = this.x64Xor(f, p),
                    f = this.x64Rotl(f, 31),
                    f = this.x64Add(f, e),
                    f = this.x64Add(this.x64Multiply(f, [0, 5]), [0, 944331445]);
                h = [0, 0];
                p = [0, 0];
                switch (c) {
                case 15:
                    p = this.x64Xor(p, this.x64LeftShift([0, a.charCodeAt(l + 14)], 48));
                case 14:
                    p = this.x64Xor(p, this.x64LeftShift([0, a.charCodeAt(l + 13)], 40));
                case 13:
                    p = this.x64Xor(p, this.x64LeftShift([0, a.charCodeAt(l + 12)], 32));
                case 12:
                    p = this.x64Xor(p, this.x64LeftShift([0, a.charCodeAt(l + 11)], 24));
                case 11:
                    p = this.x64Xor(p, this.x64LeftShift([0, a.charCodeAt(l + 10)], 16));
                case 10:
                    p = this.x64Xor(p, this.x64LeftShift([0, a.charCodeAt(l + 9)], 8));
                case 9:
                    p = this.x64Xor(p, [0, a.charCodeAt(l + 8)]),
                    p = this.x64Multiply(p, m),
                    p = this.x64Rotl(p, 33),
                    p = this.x64Multiply(p, g),
                    f = this.x64Xor(f, p);
                case 8:
                    h = this.x64Xor(h, this.x64LeftShift([0, a.charCodeAt(l + 7)], 56));
                case 7:
                    h = this.x64Xor(h, this.x64LeftShift([0, a.charCodeAt(l + 6)], 48));
                case 6:
                    h = this.x64Xor(h, this.x64LeftShift([0, a.charCodeAt(l + 5)], 40));
                case 5:
                    h = this.x64Xor(h, this.x64LeftShift([0, a.charCodeAt(l + 4)], 32));
                case 4:
                    h = this.x64Xor(h, this.x64LeftShift([0, a.charCodeAt(l + 3)], 24));
                case 3:
                    h = this.x64Xor(h, this.x64LeftShift([0, a.charCodeAt(l + 2)], 16));
                case 2:
                    h = this.x64Xor(h, this.x64LeftShift([0, a.charCodeAt(l + 1)], 8));
                case 1:
                    h = this.x64Xor(h, [0, a.charCodeAt(l)]),
                    h = this.x64Multiply(h, g),
                    h = this.x64Rotl(h, 31),
                    h = this.x64Multiply(h, m),
                    e = this.x64Xor(e, h)
                }
                e = this.x64Xor(e, [0, a.length]);
                f = this.x64Xor(f, [0, a.length]);
                e = this.x64Add(e, f);
                f = this.x64Add(f, e);
                e = this.x64Fmix(e);
                f = this.x64Fmix(f);
                e = this.x64Add(e, f);
                f = this.x64Add(f, e);
                return ("00000000" + (e[0] >>> 0).toString(16)).slice(-8) + ("00000000" + (e[1] >>> 0).toString(16)).slice(-8) + ("00000000" + (f[0] >>> 0).toString(16)).slice(-8) + ("00000000" + (f[1] >>> 0).toString(16)).slice(-8)
            },
        x64Multiply: function(a, b) {
                a = [a[0] >>> 16, a[0] & 65535, a[1] >>> 16, a[1] & 65535];
                b = [b[0] >>> 16, b[0] & 65535, b[1] >>> 16, b[1] & 65535];
                var c = [0, 0, 0, 0];
                c[3] += a[3] * b[3];
                c[2] += c[3] >>> 16;
                c[3] &= 65535;
                c[2] += a[2] * b[3];
                c[1] += c[2] >>> 16;
                c[2] &= 65535;
                c[2] += a[3] * b[2];
                c[1] += c[2] >>> 16;
                c[2] &= 65535;
                c[1] += a[1] * b[3];
                c[0] += c[1] >>> 16;
                c[1] &= 65535;
                c[1] += a[2] * b[2];
                c[0] += c[1] >>> 16;
                c[1] &= 65535;
                c[1] += a[3] * b[1];
                c[0] += c[1] >>> 16;
                c[1] &= 65535;
                c[0] += a[0] * b[3] + a[1] * b[2] + a[2] * b[1] + a[3] * b[0];
                c[0] &= 65535;
                return [c[0] << 16 | c[1], c[2] << 16 | c[3]]
            },
        x64Rotl: function(a, b) {
                b %= 64;
                if (32 === b)
                    return [a[1], a[0]];
                if (32 > b)
                    return [a[0] << b | a[1] >>> 32 - b, a[1] << b | a[0] >>> 32 - b];
                b -= 32;
                return [a[1] << b | a[0] >>> 32 - b, a[0] << b | a[1] >>> 32 - b]
            },
        x64Xor: function(a, b) {
                return [a[0] ^ b[0], a[1] ^ b[1]]
            },
        x64Add: function(a, b) {
                a = [a[0] >>> 16, a[0] & 65535, a[1] >>> 16, a[1] & 65535];
                b = [b[0] >>> 16, b[0] & 65535, b[1] >>> 16, b[1] & 65535];
                var c = [0, 0, 0, 0];
                c[3] += a[3] + b[3];
                c[2] += c[3] >>> 16;
                c[3] &= 65535;
                c[2] += a[2] + b[2];
                c[1] += c[2] >>> 16;
                c[2] &= 65535;
                c[1] += a[1] + b[1];
                c[0] += c[1] >>> 16;
                c[1] &= 65535;
                c[0] += a[0] + b[0];
                c[0] &= 65535;
                return [c[0] << 16 | c[1], c[2] << 16 | c[3]]
            },
        x64LeftShift: function(a, b) {
                b %= 64;
                return 0 === b ? a : 32 > b ? [a[0] << b | a[1] >>> 32 - b, a[1] << b] : [a[1] << b - 32, 0]
            },
        x64Fmix: function(a) {
                a = this.x64Xor(a, [0, a[0] >>> 1]);
                a = this.x64Multiply(a, [4283543511, 3981806797]);
                a = this.x64Xor(a, [0, a[0] >>> 1]);
                a = this.x64Multiply(a, [3301882366, 444984403]);
                return a = this.x64Xor(a, [0, a[0] >>> 1])
            },

        """
    r = get_device_api()
    print(r)
    # "&FMQw=0&q4f3=zh-CN&VySQ=FGGErMmK7AdYX7X-L-FMMUAJVSppDtb6&VPIf=1&custID=133&VEek=unknown&dzuS=0&yD16=0&EOQP=8f58b1186770646318a429cb33977d8c&jp76=52d67b2a5aa5e031084733d5006cc664&hAqN=Win32&platform=WEB&ks0Q=d22ca0b81584fbea62237b14bd04c866&TeRS=1040x1920&tOHY=24xx1080x1920&Fvje=i1l1o1s1&q5aJ=-8&wNLf=99115dfb07133750ba677d055874de87&0aew=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36&E3gR=17b91be3308dea9c9dcb97c3c8f8fdbf"
