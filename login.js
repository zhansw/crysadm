window.xlQuickLogin = {};
(function() {
    var e = void 0,
        a, g, f, b, c, d, h = !!(("ActiveXObject" in window) && !("XMLHttpRequest" in window));
    a = {
        LOGIN_ID: "200",
        LOGIN_TYPE_COOKIE_NAME: "_x_t_",
        AUTO_LOGIN_COOKIE_NAME: "_x_a_",
        AUTO_LOGIN_EXPIRE_TIME: false,
        LOGIN_FUNC: function() {
            location.reload()
        },
        AUTO_CLIENT_LOGIN: false,
        MUST_LOGIN: false,
        CLOSE_FUNC: function() {},
        RETRY_LOGIN_ON_SERVER_ERROR: true,
        SERVER_TIMEOUT: 7000,
        LOGOUT_FUNC: function() {
            location.reload()
        },
        LOGINED_FUNC: function() {},
        DISABLE_CLIENT_LOGIN: false,
        DISABLE_MANUAL_LOGIN: false,
        LOGIN_VERSION: "100",
        MASK: true,
        UI_THEME: "1",
        UI_STYLE: true,
        DOMAIN: "xunlei.com",
        DOMAIN_ALLOWED: ["xunlei.com", "kankan.com", "155.com"],
        REPORT_SERVER: "http://stat.login.xunlei.com:1800/report",
        MD5_PATH: "http://i.xunlei.com/login/lib/md5.js",
        THIRD_LOGIN: "http://i.xunlei.com/login/lib/ThirdLogin.js",
        RSA_PATH: "http://i.xunlei.com/login/lib/rsa.js",
        DEBUG: true
    };
    d = (function() {
        var u, p, r, q, o, l, m, v, i = 0,
            k, n = void 0;

        function s() {
            if (i === -1) {
                return
            }
            if (window.ActiveXObject) {
                k = true;
                try {
                    if (!u) {
                        u = new ActiveXObject("UserAgent.Thunder59Agent")
                    }
                } catch (y) {}
            } else {
                k = false;
                var w, z = ["npxluser_plugin"];
                for (w in z) {
                    if (navigator.mimeTypes["application/" + z[w]]) {
                        if (!u) {
                            u = document.createElement("embed");
                            u.style.visibility = "hidden";
                            u.type = "application/" + z[w];
                            u.width = 0;
                            u.height = 0;
                            document.body.appendChild(u)
                        }
                        break
                    }
                }
            }
            i = -1;
            if (!u) {
                return
            }
            try {
                if (i === 2 || (r === n && "GetJumpkeyByBId" in u)) {
                    var x = k ? 1 : 2;
                    q = t(u.GetJumpkeyByBId(0, x));
                    if (j(q)) {
                        if (k) {
                            o = t(u.GetNickNameByBId(0, x))
                        } else {
                            if ("GetLoginedNickName" in u) {
                                if ("IsThunder59Running" in u && u.IsThunder59Running()) {
                                    o = t(u.GetLoginedNickName())
                                }
                            }
                        }
                        l = t(u.GetUserNameByBId(0, x));
                        v = t(u.GetNewNameByBId(0, x));
                        m = t(u.GetUserIdByBId(0, x));
                        r = true
                    } else {
                        q = n;
                        r = false
                    }
                    i = 2
                } else {
                    if (i === 1 || (r === n && "GetJumpKey" in u)) {
                        if (!k) {
                            p = u.IsThunder59Running();
                            r = u.IsLogined()
                        }
                        if (k || p && r) {
                            q = t(u.GetJumpKey())
                        }
                        if (j(q)) {
                            o = t(u.GetLoginedNickName());
                            l = t(u.GetLoginedUserName());
                            v = t(u.GetLoginedUserNewNumberName());
                            r = true
                        } else {
                            q = n;
                            r = false
                        }
                        i = 1
                    }
                }
            } catch (y) {}
        }

        function t(w) {
            if (w && typeof w === "string") {
                return w.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]+/, "")
            }
            return w
        }

        function j(w) {
            return (w && w.length && w.length === 160) ? true : false
        }
        return {
            detect: s,
            isLogined: function() {
                if (i === 0) {
                    s()
                }
                return !!r
            },
            getJumpkey: function() {
                if (i === 0) {
                    s()
                }
                return q ? q : false
            },
            getNickname: function() {
                if (i === 0) {
                    s()
                }
                return o && o !== "0" ? o : false
            },
            getUsername: function() {
                if (i === 0) {
                    s()
                }
                return l && l !== "0" ? l : false
            },
            getNumber: function() {
                if (i === 0) {
                    s()
                }
                return v && v !== "0" ? v : false
            },
            getUid: function() {
                if (i === 0) {
                    s()
                }
                return m ? m : false
            },
            setUserInfo: function(x, w) {
                if (i === 0) {
                    s()
                }
                try {
                    u.SetUserInfo("UserNo\0", x.toString());
                    u.SetUserInfo("Sessionid\0", w.toString());
                    u.Init(1)
                } catch (y) {}
            }
        }
    })();
    g = (function() {
        var k = [],
            j = void 0,
            i;
        i = {
            randString: function(p, m) {
                var q = "abcdefghijklmnopqrstuvwxyz0123456789",
                    l = q.length;
                m = m ? Math.min(m, l) : l;
                var o, n = [];
                for (o = 0; o < p; o++) {
                    n.push(q.charAt(Math.floor(Math.random() * m)))
                }
                return n.join("")
            },
            loadStyle: function(m, p) {
                var t = document.styleSheets,
                    q;
                for (q in t) {
                    if (t[q].href && t[q].href === m) {
                        if (typeof p === "function") {
                            p()
                        }
                        return
                    }
                }
                var l, s = document.getElementsByTagName("head")[0],
                    r;
                l = document.createElement("link");
                l.rel = "stylesheet";
                l.type = "text/css";
                l.media = "all";
                var o, n = function(u) {
                    if (!r && (u === true || !this.readyState || this.readyState == "loaded" || this.readyState == "complete")) {
                        r = true;
                        clearTimeout(o);
                        if (typeof p === "function") {
                            p()
                        }
                        l.onload = l.onreadystatechange = null
                    }
                };
                o = setTimeout(function() {
                    n(true)
                }, 100);
                l.onload = l.onreadystatechange = n;
                l.href = m;
                s.appendChild(l);
                return l
            },
            loadScript: function(o, l) {
                var n = document.createElement("script"),
                    m = false;
                n.src = o;
                n.type = "text/javascript";
                n.language = "javascript";
                n.onload = n.onreadystatechange = function() {
                    if (!m && (!this.readyState || this.readyState == "loaded" || this.readyState == "complete")) {
                        m = true;
                        if (typeof l === "function") {
                            l()
                        }
                        n.onload = n.onreadystatechange = null;
                        n.parentNode.removeChild(n)
                    }
                };
                document.getElementsByTagName("head")[0].appendChild(n);
                return n
            },
            loadImage: function(p, q, l) {
                var o = new Image(),
                    n, m;
                o.onerror = function() {
                    o.onerror = o.onload = o.onreadystatechange = null;
                    clearTimeout(m);
                    l && l(false)
                };
                o.onload = o.onreadystatechange = function() {
                    if (!n && (!this.readyState || this.readyState == "loaded" || this.readyState == "complete")) {
                        n = true;
                        o.onerror = o.onload = o.onreadystatechange = null;
                        clearTimeout(m);
                        l && l(true)
                    }
                };
                m = setTimeout(function() {
                    o.onerror = o.onload = o.onreadystatechange = null;
                    l && l(false)
                }, q);
                p += (p.indexOf("?") > 0 ? "&" : "?") + "_v_=" + i.randString(8);
                o.src = p
            },
            loadScriptOn: function(m, o, l) {
                var n;
                if (typeof o === "function") {
                    n = o()
                } else {
                    n = !!o
                }
                if (n) {
                    i.loadScript(m, l)
                } else {
                    if (typeof l === "function") {
                        l()
                    }
                }
            },
            isSessionid: function(l) {
                return (l && l.length && (l.length === 128 || l.length === 160)) ? true : false
            },
            isJumpkey: function(l) {
                return (l && l.length && l.length === 192) ? true : false
            },
            getCookie: function(o, m) {
                var u, n = document.cookie,
                    v, r, p;
                m = m === j ? true : m;
                if (o) {
                    u = n.match(new RegExp("(^| )" + o + "=([^;]*)")) == null ? j : (RegExp.$2);
                    if (m && u !== j) {
                        try {
                            u = decodeURIComponent(u)
                        } catch (s) {
                            u = unescape(u)
                        }
                    }
                    return u
                } else {
                    var q = {};
                    n = n.split("; ");
                    for (r = 0, p = n.length; r < p; ++r) {
                        v = n[r].split("=");
                        u = v.pop();
                        if (m && u !== j) {
                            try {
                                u = decodeURIComponent(u)
                            } catch (s) {
                                u = unescape(u)
                            }
                        }
                        q[v.shift()] = u
                    }
                    return q
                }
            },
            setCookie: function(m, p, l, o, r, q) {
                var n, l = l ? new Date(new Date().getTime() + l).toGMTString() : false;
                n = m + "=" + escape(p);
                n += "; path=" + (r ? r : "/");
                if (o) {
                    n += "; domain=" + o
                }
                if (q) {
                    n += "; secure"
                }
                if (l) {
                    n += "; expires=" + l
                }
                document.cookie = n
            },
            delCookie: function(l, m, o, n) {
                i.setCookie(l, "", -60000, m, o, n)
            },
            bind: function(q, o, p, n) {
                if (typeof p !== "function") {
                    return
                }
                if (typeof q === "string") {
                    q = document.getElementById(q)
                }
                if (!q) {
                    throw new Error("bind on an undefined target")
                }

                function m(r) {
                    r = r || window.event;
                    if (!r.target) {
                        r.target = r.srcElement;
                        r.preventDefault = function() {
                            this.returnValue = false
                        };
                        r.stopPropagation = function() {
                            this.cancelBubble = true
                        }
                    }
                    if (false === p.call(n || this, r)) {
                        r.preventDefault();
                        r.stopPropagation()
                    }
                }
                var l = o.split(".").shift();
                k.push({
                    obj: q,
                    handler: m,
                    type: o
                });
                if (q.attachEvent) {
                    q.attachEvent("on" + l, m)
                } else {
                    if (q.addEventListener) {
                        q.addEventListener(l, m, false)
                    }
                }
            },
            unbind: function(r, o) {
                if (typeof r === "string") {
                    r = document.getElementById(r)
                }
                if (!r) {
                    throw new Error("unbind on an undefined target")
                }
                var l, q, p, n, m;
                for (m = k.length - 1; m >= 0; m--) {
                    l = k[m];
                    if (l.obj !== r) {
                        continue
                    }
                    q = l.type.split(".");
                    p = q.shift();
                    n = q.length > 0 ? q.join(".") : false;
                    if (l.type === o || o === p || (n !== false && n === o)) {
                        k.splice(m, 1);
                        if (r.detachEvent) {
                            r.detachEvent("on" + p, l.handler)
                        } else {
                            if (r.removeEventListener) {
                                r.removeEventListener(p, l.handler, false)
                            }
                        }
                    }
                }
            },
            $: function(n, l) {
                var m = document.getElementById(n);
                if (!m && !l) {
                    throw new Error("not find dom by id: " + n)
                }
                return m
            },
            id: function(l) {
                return document.getElementById(l)
            },
            text: function(n, m) {
                if (!n) {
                    return
                }
                var l = false;
                if (n.innerText !== j) {
                    l = "innerText"
                } else {
                    if (n.textContent !== j) {
                        l = "textContent"
                    } else {
                        if (n.value !== j) {
                            l = "value"
                        } else {
                            throw new Error("not support dom innerText or textContent")
                        }
                    }
                }
                return m === j ? n[l] : (n[l] = m)
            },
            iframeRequest: function(l, m, y, r, z) {
                if (!l || !m) {
                    throw new Error("iframeRequest can't accept empty method and url as param")
                }
                var t, u, q, p, o, s = "",
                    w = "",
                    n;
                l = l.toUpperCase();
                o = document.createElement("form");
                o.style.display = "none";
                o.style.position = "absolute";
                o.method = l;
                o.enctype = "application/x-www-form-urlencoded";
                o.acceptCharset = "UTF-8";
                y = y || {};
                if (l === "_GET") {
                    for (t in y) {
                        s += t + "=" + y[t]
                    }
                    if (m.indexOf("#") > 0) {
                        w = "#" + m.split("#").pop();
                        m = m.split("#").shift()
                    }
                    m += (m.indexOf("?") >= 0 ? "&" : "?") + s + w
                } else {
                    for (t in y) {
                        p = document.createElement("textarea");
                        p.name = t;
                        p.value = y[t];
                        o.appendChild(p)
                    }
                }
                document.body.appendChild(o);
                q = "f" + i.randString(8);
                o.target = q;
                o.action = m;
                try {
                    u = document.createElement('<iframe name="' + q + '">')
                } catch (A) {
                    u = document.createElement("iframe");
                    u.name = q
                }
                u.id = q;
                u.style.display = "none";
                o.appendChild(u);

                function v(x) {
                    if (!u.onerror) {
                        return
                    }
                    u.onreadystatechange = u.onerror = u.onload = null;
                    setTimeout(function() {
                        u.parentNode.removeChild(u);
                        u = null;
                        o.parentNode.removeChild(o);
                        o = null
                    }, 500);
                    n && clearTimeout(n);
                    x = typeof x === "string" ? x : j;
                    (typeof r === "function") && r(x)
                }
                if (z > 0) {
                    n = setTimeout(function() {
                        v("TIMEOUT")
                    }, z)
                }
                u.onerror = u.onload = v;
                u.onreadystatechange = function(x) {
                    if (u.readyState == "complete") {
                        v()
                    }
                };
                if (l === "_GET") {
                    u.src = m
                } else {
                    o.submit()
                }
            }
        };
        return i
    })();
    Report = (function() {
        var i = [];
        return {
            add: function(n) {
                var l, m = location.href.split("://").pop().split(/[\/\?|#]/).shift(),
                    j;
                j = {
                    url: "",
                    errorcode: "",
                    responsetime: "",
                    retrynum: "0",
                    serverip: "",
                    cmdid: "",
                    domain: m,
                    b_type: a.LOGIN_ID,
                    platform: "1",
                    clientversion: ""
                };
                for (l in j) {
                    if (n[l] !== e) {
                        j[l] = n[l]
                    }
                }
                i.push(j);
                if (i.length >= 3) {
                    this.exec()
                }
            },
            exec: function() {
                var o, m, p, j = i.length,
                    n = [];
                if (j === 0) {
                    return true
                }
                n.push("cnt=" + j);
                for (o = 0; o < j; ++o) {
                    p = i[o];
                    for (m in p) {
                        if (p.hasOwnProperty(m)) {
                            n.push(m + o + "=" + encodeURIComponent(p[m]))
                        }
                    }
                }
                i = [];
                (new Image()).src = a.REPORT_SERVER + "?" + n.join("&");
                return true
            }
        }
    })();
    f = (function() {
        var k, q = ["http://login", "http://login2", "http://login3"],
            n = ["http://verify", "http://verify2", "http://verify3"],
            i = [1, 1, 1],
            m = [1, 1, 1];

        function p(x, z) {
            var y = x === "captcha" ? n : q,
                r, u, v = y.length,
                t = 0,
                w, s;
            s = g.getCookie("_s." + x + "_");
            if (s && (s = s.split(",")) && s.length === v) {
                r = s
            } else {
                r = x === "captcha" ? m : i
            }
            u = 0;
            while (t++ < v) {
                if (r[u] - 1 === 0) {
                    w = true;
                    break
                } else {
                    u = (u + 1) % v
                }
            }
            if (!w) {
                u = 0;
                r = x === "captcha" ? m : i;
                g.setCookie("_s." + x + "_", r.join(","))
            }
            return y[u] + k + (z ? z : "")
        }

        function j(r, y, x) {
            var t, w, u, z = x === "captcha" ? n : q,
                v = z.length,
                s;
            u = g.getCookie("_s." + x + "_");
            if (u && (u = u.split(",")) && u.length === v) {
                s = u
            } else {
                s = x === "captcha" ? m : i
            }
            r = r.substring(0, r.indexOf(k));
            for (t = z.length - 1; t >= 0; --t) {
                if (r === z[t]) {
                    s[t] = y ? 1 : 0;
                    g.setCookie("_s." + x + "_", s.join(","));
                    w = true;
                    break
                }
            }
            if (!w) {
                throw new Error("not find your server: " + r)
            }
        }

        function l(r, B, x, w, A, s, y, u) {
            var z, t;
            u = u || "blogresult";
            g.delCookie(u, k);
            t = p("login", B);
            var v = (new Date()).getTime();
            g.iframeRequest(r, t, x, function(C) {
                z = g.getCookie(u);
                if (C === "TIMEOUT" || z === e) {
                    z = -1
                } else {
                    if (u !== "check_result") {
                        z = parseInt(z, 10);
                        if (z !== z) {
                            z = -1
                        }
                    }
                }
                if (s && s === true) {
                    s = 1
                }
                Report.add({
                    url: t,
                    errorcode: typeof z === "string" && z.indexOf(":") > 0 ? z.split(":").shift() : z,
                    responsetime: ((new Date().getTime()) - v) / 1000,
                    retrynum: typeof s === "number" ? s - 1 : 0
                });
                if (s && q.length > s && (y && y.indexOf("," + z + ",") >= 0 || z === -1)) {
                    j(t, 0, "login");
                    l(r, B, x, w, A, s + 1, y, u)
                } else {
                    if (z === 0 || (u === "check_result" && z !== -1)) {
                        j(t, 1, "login")
                    } else {
                        j(t, 0, "login")
                    }
                    g.delCookie(u, k);
                    w(z)
                }
            }, A)
        }

        function o(F, J, y) {
            var x, I = {},
                u, D = a.SERVER_TIMEOUT,
                H = a.RETRY_LOGIN_ON_SERVER_ERROR;
            k = "." + a.DOMAIN;
            if (typeof J === "function") {
                y = J
            }
            switch (F) {
                case "login":
                    debugger;
                    if (J.username && J.password && J.captcha && J.check_n && J.check_e) {
                        var s = J.check_n,
                            z = J.check_e,
                            t = new RSAKey();
                        t.setPublic(b64tohex(s), b64tohex(z));
                        var r = J.captcha.toUpperCase();
                        var B = hex2b64(t.encrypt(md5(J.password) + r));
                        I.p = B;
                        I.u = J.username;
                        I.n = s;
                        I.e = z;
                        I.v = a.LOGIN_VERSION;
                        I.verifycode = J.captcha;
                        I.login_enable = J.autologin ? 1 : 0;
                        I.business_type = a.LOGIN_ID
                    } else {
                        throw new Error("post argument error")
                    }
                    u = "post";
                    path = "/sec2login/";
                    l(u, path, I, function(L) {
                        var M;
                        switch (L) {
                            case -1:
                                L = 1;
                                M = "连接超时，请重试";
                                break;
                            case 0:
                                M = "登录成功";
                                break;
                            case 1:
                            case 9:
                            case 10:
                            case 11:
                                L = 2;
                                M = "验证码错误，请重新输入验证码";
                                break;
                            case 2:
                            case 4:
                                L = 3;
                                M = "帐号或密码错误，请重新输入";
                                break;
                            case 3:
                            case 7:
                            case 8:
                            case 16:
                                L = 4;
                                M = "服务器内部错误，请重试";
                                break;
                            case 12:
                            case 13:
                            case 14:
                            case 15:
                                L = 5;
                                M = "登录页面失效";
                                break;
                            case 6:
                                M = "帐号被锁定，请换帐号登录";
                                break;
                            default:
                                L = -1;
                                M = "内部错误，请重试";
                                break
                        }
                        y && y(L, M)
                    }, D, false, ",33333,");
                    break;
                case "sessionlogin":
                    if (J.sessionid && g.isSessionid(J.sessionid)) {
                        I.sessionid = J.sessionid
                    } else {
                        throw new Error("post argument error")
                    }
                    u = "post";
                    path = "/sessionid/";
                    l(u, path, I, function(L) {
                        var M;
                        switch (L) {
                            case -1:
                                M = "连接超时，请重试";
                                break;
                            case 0:
                                M = "登录成功";
                                break;
                            case 1:
                                M = "sessionid 失效，请重新登录";
                            case 2:
                                M = "sessionid 无效，请重新登录";
                            case 5:
                                M = "无效帐号，请换帐号登录";
                                break;
                            case 6:
                                M = "帐号被锁定，请换帐号登录";
                                break;
                            default:
                                M = "内部错误，请重试";
                                break
                        }
                        y && y(L, M)
                    }, D, H, ",3,7,");
                    break;
                case "jumplogin":
                    if (J.jumpkey && g.isJumpkey(J.jumpkey)) {
                        I.jumpkey = J.jumpkey
                    } else {
                        throw new Error("post argument error")
                    }
                    u = "post";
                    path = "/jumplogin/";
                    l(u, path, I, function(L) {
                        var M;
                        switch (L) {
                            case -1:
                                L = 1;
                                M = "连接超时，请重试";
                                break;
                            case 0:
                                M = "登录成功";
                                break;
                            case 1:
                                L = 9;
                                M = "jumpkey 失效，请重新登录";
                            case 2:
                                L = 8;
                                M = "jumpkey 无效，请重新登录";
                            case 5:
                                L = 7;
                                M = "无效帐号，请换帐号登录";
                                break;
                            case 6:
                                M = "帐号被锁定，请换帐号登录";
                                break;
                            default:
                                L = -1;
                                M = "内部错误，请重试";
                                break
                        }
                        y && y(L, M)
                    }, D, H, ",3,7,");
                    break;
                case "checkuser":
                    if (J.username) {
                        I.u = J.username;
                        I.v = a.LOGIN_VERSION
                    } else {
                        throw new Error("post argument error")
                    }
                    u = "get";
                    path = "/check/";
                    l(u, path, I, function(M) {
                        var N = (M + "").split(":"),
                            L;
                        L = parseInt(N.shift());
                        if (L !== L) {
                            L = -1
                        }
                        y && y(L, N.pop())
                    }, D, H, false, "check_result");
                    break;
                case "logout":
                    (new Image()).src = p("login", "/unregister/?sessionid=" + g.getCookie("sessionid"));
                    var C = "VERIFY_KEY,blogresult,active,isspwd,score,downbyte,isvip,jumpkey,logintype,nickname,onlinetime,order,safe,downfile,sessionid,sex,upgrade,userid,usernewno,usernick,usertype,usrname",
                        G, v = C.split(",");
                    for (G = v.length; G > 0; --G) {
                        g.delCookie(v[G - 1], a.DOMAIN)
                    }
                    g.delCookie(a.LOGIN_TYPE_COOKIE_NAME);
                    g.delCookie(a.AUTO_LOGIN_COOKIE_NAME);
                    y && y();
                    break;
                case "captcha":
                    if (!J.img) {
                        throw new Error("post argument error")
                    }
                    var w, K = J.img,
                        A = p("captcha", "/image?cachetime=" + (new Date().getTime())),
                        E = false;
                    K.onerror = function() {
                        K.onerror = K.onload = K.onreadystatechange = null;
                        clearTimeout(w);
                        j(A, 0, "captcha");
                        if (y) {
                            y(1, "获取验证码失败，请手动刷新")
                        }
                    };
                    K.onload = K.onreadystatechange = function() {
                        if (!E && (!this.readyState || this.readyState == "loaded" || this.readyState == "complete")) {
                            E = true;
                            clearTimeout(w);
                            j(A, 1, "captcha");
                            K.onerror = K.onload = K.onreadystatechange = null;
                            if (y) {
                                y(0, "刷新成功")
                            }
                        }
                    };
                    w = setTimeout(function() {
                        K.onerror = K.onload = K.onreadystatechange = null;
                        j(A, 0, "captcha");
                        if (y) {
                            y(1, "获取验证码失败，请手动刷新")
                        }
                    }, D);
                    K.src = A;
                    break;
                default:
                    throw new Error("not support action: " + F)
            }
        }
        return o
    })();
    c = (function() {
        var G, o, v, i = {},
            j = void 0,
            B, l = false,
            w, q, r, K, D, A, z, x, y, F, m;
        var s, u = {
            ORIGIN: -1,
            INITED: 0,
            MANUAL: 1,
            CLIENT: 2,
            AUTOWEB: 3,
            AUTOCLIENT: 4,
            THIRD: 5
        };
        xlQuickLogin.TYPE = u;

        function p(O) {
            var M = a.AUTO_LOGIN_COOKIE_NAME,
                N = a.AUTO_LOGIN_EXPIRE_TIME;
            if (N && (typeof N === "number") && N > 0) {
                O = O || g.getCookie("sessionid");
                if (g.isSessionid(O)) {
                    g.setCookie(M, O, N * 1000)
                } else {
                    g.delCookie(M)
                }
            }
        }

        function I(M) {
            s = M;
            g.delCookie("_s.login_");
            g.delCookie("_s.captcha_");
            g.setCookie(a.LOGIN_TYPE_COOKIE_NAME, M + "_1");
            Report.exec();
            a.LOGIN_FUNC(M)
        }

        function t(M) {
            var P = a.UI_THEME,
                O = a.DEBUG ? "" : ".min",
                Q, N = "http://i.xunlei.com/login/theme/" + P + "/";
            if (o) {
                return
            }
            o = true;
            v = i[P];
            Q = function() {
                var R = typeof v === "string" ? v : N + "style" + O + ".js?v=20130712";
                g.loadScriptOn(R, (!v || typeof v === "string"), function() {
                    o = false;
                    v = i[P];
                    if (!v) {
                        throw new Error("load style error")
                    }
                    x = v.getContainer && v.getContainer();
                    if (x) {
                        y = a.MUST_LOGIN ? false : x.close;
                        x = x.base
                    }
                    if (!v.supportManual && !v.supportClient) {
                        v.supportManual = true
                    }
                    if (v.supportClient && !a.DISABLE_CLIENT_LOGIN) {
                        d.detect();
                        if (g.isJumpkey(d.getJumpkey())) {
                            m = 2;
                            if (v.supportManual && !a.DISABLE_MANUAL_LOGIN) {
                                m = m | 1;
                                g.loadScriptOn(a.MD5_PATH, typeof md5 !== "function");
                                g.loadScriptOn(a.RSA_PATH, true)
                            }
                            var S, T = d.getUid(),
                                V = d.getUsername(),
                                U = d.getNumber();
                            S = T ? "http://img.user.kanimg.com/usrimg/" + T + "/50x50" : "http://imain.xunlei.com/imgus/" + (V || U) + ".gif";
                            v.init && v.init(m, {
                                jumpkey: d.getJumpkey(),
                                avatar: S,
                                uid: T,
                                usernewno: U,
                                username: V,
                                nickname: d.getNickname()
                            });
                            M(m)
                        } else {
                            if (v.supportManual && !a.DISABLE_MANUAL_LOGIN) {
                                m = 1;
                                v.init && v.init(m);
                                M(m);
                                g.loadScriptOn(a.MD5_PATH, typeof md5 !== "function");
                                g.loadScriptOn(a.RSA_PATH, true)
                            } else {
                                M(m)
                            }
                        }
                    } else {
                        if (v.supportManual && !a.DISABLE_MANUAL_LOGIN) {
                            m = 1;
                            v.init && v.init(m);
                            M(m);
                            g.loadScriptOn(a.MD5_PATH, typeof md5 !== "function");
                            g.loadScriptOn(a.RSA_PATH, true)
                        } else {
                            M(m)
                        }
                    }
                })
            };
            if (a.UI_STYLE) {
                if (typeof a.UI_STYLE === "string") {
                    g.loadStyle(a.UI_STYLE, Q)
                } else {
                    g.loadStyle(N + "css/style" + O + ".css", Q)
                }
            } else {
                Q()
            }
        }

        function n() {
            g.setCookie(a.LOGIN_TYPE_COOKIE_NAME, u.THIRD + "")
        }

        function H() {
            if (A) {
                return
            }
            A = true;
            var T, U = 0,
                P, V = true,
                S, N = false;
            K = v.getManualDoms();
            if (K.third_login) {
                g.loadScriptOn(a.THIRD_LOGIN, !xlQuickLogin.ThirdLogin, function() {
                    xlQuickLogin.ThirdLogin.init({
                        target: K.third_login,
                        stat: a.LOGIN_ID,
                        beforeLeave: n
                    })
                })
            }
            R(K.captcha_container, "none");
            K.input_password.value = "";
            K.input_captcha.value = "";
            S = g.text(K.button_submit);

            function M() {
                N = true;
                R(K.captcha_container, "");
                if (typeof v.afterShowCaptcha === "function") {
                    v.afterShowCaptcha()
                }
            }
            g.bind(K.input_username, "blur.x", O);
            O();

            function O() {
                if (U > 2) {
                    return
                }
                var W = K.input_username.value;
                if (!W || /^\s*$/.test(W)) {
                    return
                }
                T = j;
                f("checkuser", {
                    username: W
                }, function(X, Y) {
                    if (X !== 0) {
                        U = 10;
                        if (V) {
                            Q()
                        }
                        M();
                        T = false
                    } else {
                        R(K.captcha_container, "none");
                        T = Y
                    }
                })
            }
            for (P = K.img_captcha_fresh.length - 1; P >= 0; --P) {
                g.bind(K.img_captcha_fresh[P], "click.x", Q)
            }

            function Q() {
                V = false;
                T = false;
                f("captcha", {
                    img: K.img_captcha
                }, function(W, X) {
                    if (W !== 0) {
                        v.showError(X, W)
                    }
                })
            }

            function R(Y, X) {
                if (!Y.pop) {
                    Y = [Y]
                }
                for (var W = Y.length; W > 0; --W) {
                    Y[W - 1].style.display = X
                }
            }
            q = function() {
                var X, Z, aa;
                if (l) {
                    return
                }
                X = K.input_username.value;
                Z = K.input_password.value;
                if (typeof v.beforeManualSubmit === "function") {
                    if (false === v.beforeManualSubmit()) {
                        return
                    }
                }
                aa = T === false ? K.input_captcha.value : T;
                if (!X) {
                    v.showError("用户名不能为空", 10);
                    return
                }
                if (!Z) {
                    v.showError("密码不能为空", 11);
                    return
                }
                if (!aa || aa.length === 0) {
                    if (N) {
                        v.showError("验证码不能为空", 12)
                    } else {
                        v.showError("网络繁忙，稍后再试", 13)
                    }
                    return
                }
                if (aa.length < 4) {
                    v.showError("验证码不正确", 2);
                    Q();
                    return
                }
                if (T === j) {
                    v.showError("网络繁忙，稍后再试", 13);
                    return
                }
                var Y = g.getCookie("check_n"),
                    W = g.getCookie("check_e");
                if (!Y || !W) {
                    v.showError("网络繁忙，稍后再试", 13);
                    return
                }
                if (("check_remember" in K) && !K.check_remember.checked) {
                    a.AUTO_LOGIN_EXPIRE_TIME = false
                }
                l = true;
                g.text(K.button_submit, "登录中...");
                f("login", {
                    username: X,
                    password: Z,
                    captcha: aa,
                    check_n: Y,
                    check_e: W
                }, function(ab, ac) {
                    g.text(K.button_submit, S);
                    l = false;
                    if (ab === 0) {
                        g.delCookie("VERIFY_KEY", a.DOMAIN);
                        p();
                        B.destory();
                        I(u.MANUAL)
                    } else {
                        if (ab !== 1) {
                            K.input_password.value = ""
                        }
                        K.input_captcha.value = "";
                        if (U > 2) {
                            Q();
                            M()
                        } else {
                            O()
                        }
                        v.showError(ac, ab)
                    }
                });
                U++;
                return false
            };
            g.bind(K.button_submit, "click.x", q)
        }

        function k() {
            if (!K || !A) {
                return
            }
            g.unbind(K.input_username, "blur.x");
            g.unbind(K.button_submit, "click.x");
            for (var M = K.img_captcha_fresh.length - 1; M >= 0; --M) {
                g.unbind(K.img_captcha_fresh[M], "click.x")
            }
            q = null;
            K = null;
            A = false
        }

        function C() {
            if (z) {
                return
            }
            z = true;
            D = v.getClientDoms();
            if (D.third_login) {
                g.loadScriptOn(a.THIRD_LOGIN, !xlQuickLogin.ThirdLogin, function() {
                    xlQuickLogin.ThirdLogin.init({
                        target: D.third_login,
                        stat: a.LOGIN_ID,
                        beforeLeave: n
                    })
                })
            }
            r = function() {
                if (l) {
                    return
                }
                var N = d.getJumpkey();
                if (typeof v.beforeClientSubmit === "function") {
                    if (false === v.beforeClientSubmit()) {
                        return
                    }
                }
                if (g.isJumpkey(N)) {
                    l = true;
                    f("jumplogin", {
                        jumpkey: N
                    }, function(O, P) {
                        l = false;
                        if (O === 0) {
                            p();
                            B.destory();
                            I(u.CLIENT)
                        } else {
                            v.showError(P, O)
                        }
                    })
                } else {
                    v.showError("jumpkey 无效，请重新登录", 8)
                }
                return false
            };
            for (var M = D.button_login.length; M > 0; --M) {
                g.bind(D.button_login[M - 1], "click.x", r)
            }
        }

        function L() {
            if (!D || !z) {
                return
            }
            for (var M = D.button_login.length; M > 0; --M) {
                g.unbind(D.button_login[M - 1], "click.x")
            }
            r = null;
            D = null;
            z = false
        }

        function J(M, N) {
            if (typeof M !== "object") {
                return
            }
            var P, O, W, V, X, T = {},
                U = {},
                R = {
                    MD5_PATH: 1,
                    XL_CLIENT_PATH: 1,
                    DEBUG: 1,
                    DOMAIN: 1,
                    DOMAIN_ALLOWED: 1
                };
            for (P in a) {
                if (!a.hasOwnProperty(P) || (P in R)) {
                    continue
                }
                O = P.toLowerCase().replace(/[_\-]/g, "");
                T[O] = a[P];
                U[O] = P
            }
            var S = ",AUTO_LOGIN_EXPIRE_TIME,UI_STYLE,LOGIN_ID,",
                Q = false;
            for (P in M) {
                if (!M.hasOwnProperty(P)) {
                    continue
                }
                O = P.toLowerCase().replace(/[_\-]/g, "");
                if (O in T) {
                    V = T[O];
                    W = M[P];
                    X = typeof V;
                    O = U[O];
                    if (X === "boolean" && S.indexOf(O) === -1) {
                        W = !!W
                    }
                    if (W === V && O !== "LOGIN_ID") {
                        continue
                    }
                    if ((X === typeof W) || S.indexOf(O) >= 0) {
                        if (O === "LOGIN_ID") {
                            Q = true
                        }
                        a[O] = W
                    } else {
                        throw new Error("config key(" + P + ") error, type not match")
                    }
                } else {
                    throw new Error("config key(" + P + ") not exists")
                }
            }
            if (N && !Q) {
                throw new Error("not init loginID， please init it")
            }
        }

        function E(M) {
            if (G) {
                return
            }
            var R, T, W = location.host,
                N, Q;
            G = true;
            N = W.split(".");
            Q = N.pop();
            Q = (N.pop() + "." + Q).toLowerCase();
            for (R = a.DOMAIN_ALLOWED.length; R > 0; --R) {
                if (Q === a.DOMAIN_ALLOWED[R - 1]) {
                    T = true;
                    break
                }
            }
            if (!T) {
                throw new Error("你的域名不支持此快速登录")
            }
            a.DOMAIN = Q;
            J(M, true);
            var U = g.getCookie(),
                V = U[a.AUTO_LOGIN_COOKIE_NAME],
                P = "0",
                O = a.LOGIN_TYPE_COOKIE_NAME;
            s = U[O];
            if (typeof s === "string") {
                s = s.split("_");
                P = s[1] === "1" ? "1" : "0"
            }
            s = s === j ? -1 : parseInt(s);
            if (s === j || s !== s || s < -1 || s > 4) {
                s = -1
            }
            if (!(g.isSessionid(U.sessionid) && U.userid && U.userid > 0)) {
                if (V && g.isSessionid(V)) {
                    l = true;
                    f("sessionlogin", {
                        sessionid: V
                    }, function(X, Y) {
                        l = false;
                        if (X !== 0) {
                            g.delCookie(a.AUTO_LOGIN_COOKIE_NAME);
                            if (w === 1) {
                                B.popup();
                                w = 0
                            }
                            return
                        } else {
                            p(V);
                            I(u.AUTOWEB)
                        }
                    })
                } else {
                    if (a.AUTO_CLIENT_LOGIN) {
                        d.detect();
                        var S = d.getJumpkey();
                        if (g.isJumpkey(S)) {
                            l = true;
                            f("jumplogin", {
                                jumpkey: S
                            }, function(X, Y) {
                                l = false;
                                if (X === 0) {
                                    p();
                                    I(u.AUTOCLIENT)
                                } else {
                                    if (w === 1) {
                                        B.popup();
                                        w = 0
                                    }
                                }
                            })
                        }
                    }
                }
                if (s !== -1) {
                    g.setCookie(O, "0")
                }
            } else {
                if (P === "0") {
                    if (s === u.THIRD) {
                        p(U.sessionid)
                    }
                    if (d && ("setUserInfo" in d)) {
                        d.setUserInfo(U.userid, U.sessionid)
                    }
                }
                if (typeof a.LOGINED_FUNC === "function") {
                    a.LOGINED_FUNC(s)
                }
                if (s > 0 && P === "0") {
                    g.setCookie(O, s + "_1")
                }
            }
        }
        B = {
            register: function(M, N) {
                i[M] = N
            },
            popup: function() {
                if (l) {
                    w = 1;
                    return
                }
                B.destory();
                t(function(O) {
                    var N, M;
                    if (!O) {
                        return
                    }
                    if (x) {
                        if (a.MASK) {
                            if (typeof a.MASK === "string") {
                                F = g.id(a.MASK)
                            }
                            if (!F) {
                                F = document.createElement("div");
                                a.MASK = g.randString(8);
                                F.id = a.MASK;
                                N = F.style;
                                N.opacity = "0.4";
                                N.filter = "alpha(opacity=40)";
                                N.backgroundColor = "black";
                                N.position = h ? "absolute" : "fixed";
                                N.left = "0";
                                N.top = "0";
                                N.bottom = "0";
                                N.right = "0";
                                N.zIndex = "999999";
                                document.body.appendChild(F)
                            }
                            F.style.display = ""
                        }
                        x.style.zIndex = "1000000";
                        x.style.display = "";
                        y && g.bind(y, "click.x", function() {
                            B.destory();
                            if (typeof a.CLOSE_FUNC === "function") {
                                a.CLOSE_FUNC()
                            }
                        })
                    }
                    if (O & 1) {
                        H()
                    }
                    if (O & 2) {
                        C()
                    }
                    g.setCookie(a.LOGIN_TYPE_COOKIE_NAME, u.INITED + "");
                    g.bind(document, "keydown.xl", function(Q) {
                        if (Q.keyCode == "13") {
                            var P = v.getCurrentTab && v.getCurrentTab();
                            if (O === 1 || P === "manual") {
                                q()
                            } else {
                                if (O === 2 || P === "client") {
                                    r()
                                }
                            }
                        } else {
                            if (Q.keyCode == "27") {
                                if (M) {
                                    return
                                }
                                M = true;
                                if (x) {
                                    B.destory()
                                }
                            }
                        }
                    })
                })
            },
            destory: function() {
                if (F) {
                    F.style.display = "none";
                    F = null
                }
                if (x) {
                    x.style.display = "none";
                    x = null
                }
                m = j;
                g.unbind(document, "keydown.xl");
                y && g.unbind(y, "click.x");
                y = j;
                k();
                L();
                if (xlQuickLogin.ThirdLogin && xlQuickLogin.ThirdLogin.destory) {
                    xlQuickLogin.ThirdLogin.destory()
                }
                if (v && (typeof v.destory === "function")) {
                    v.destory()
                }
            },
            config: J,
            init: E
        };
        return B
    })();
    (function() {
        var i = false,
            l, j;
        l = {
            Util: g,
            registerUI: c.register,
            init: function(k) {
                if (i === true) {
                    return
                }
                i = true;
                c.init(k)
            },
            config: c.config,
            login: function(n, m) {
                if (!i) {
                    throw new Error("please init first: xlQuickLogin.init()")
                }
                for (var k = 0; k < 2; k++) {
                    if (typeof arguments[k] === "function") {
                        n = arguments[k]
                    } else {
                        if (typeof arguments[k] === "object") {
                            m = arguments[k]
                        }
                    }
                }
                if (typeof n === "function") {
                    m = m || {};
                    m.loginFunc = n
                }
                if (typeof m === "object") {
                    c.config(m)
                }
                if (l.isLogined()) {
                    return
                }
                c.popup()
            },
            logout: function(k) {
                if (!i) {
                    throw new Error("please init first: xlQuickLogin.init()")
                }
                if (!l.isLogined()) {
                    return
                }
                if (typeof k === "function") {
                    a.LOGOUT_FUNC = k
                }
                f("logout", function() {
                    a.LOGOUT_FUNC()
                })
            },
            isLogined: function() {
                if (!i) {
                    throw new Error("please init first: xlQuickLogin.init()")
                }
                var k = g.getCookie();
                if (g.isSessionid(k.sessionid) && k.userid && k.userid > 0) {
                    return true
                }
                return false
            },
            checkServers: function(r, q, k) {
                if (!r.length || r.length < 0) {
                    return false
                }
                var n, m = r.length,
                    s = [],
                    p = (new Date().getTime() - 0) % 10;
                for (n = 0; n < m; ++n) {
                    s[n] = r[n].replace(/^\s+|\/?\s*$/g, "");
                    if (s[n].indexOf("http://") < 0) {
                        s[n] = "http://" + s[n]
                    }
                    s[n] = s[n] + "/stat/" + ((p++) % 10) + ".gif"
                }
                n = 0;
                g.loadImage(s[n], q, o);

                function o(t) {
                    if (t) {
                        k && k(r[n])
                    } else {
                        if (n === m - 1) {
                            k && k(false)
                        } else {
                            ++n;
                            g.loadImage(s[n], q, o)
                        }
                    }
                }
            }
        };
        for (j in l) {
            if (l.hasOwnProperty(j)) {
                xlQuickLogin[j] = l[j]
            }
        }
    })()
})();
