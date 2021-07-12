local json = require 'cjson'
local redis = require 'resty.redis'

local red = redis:new()
red:set_timeout(15)
local ok, err = red:connect('127.0.0.1', 6379)
if not ok then
    ngx.header['Content-Type'] = 'application/json; charset=utf-8'
    ngx.say(json.encode({
        redisStatus = -1,
        message = 'redisError'
    }))
  return
end
red:select(5)
-- local ok, err = red:set_keepalive(60000, 20)
function decodeCookie(s_cookie)
    local cookie = {}
    for item in string.gmatch(s_cookie, "[^;]+") do
        local _, _, k, v = string.find(item, "^%s*(%S+)%s*=%s*(%S+)%s*")
        if k ~= nil and v~= nil then
            cookie[k] = v
        end
    end
    return cookie
end

math.randomseed(tonumber(tostring(ngx.now()*1000):reverse():sub(1, 9)))
local cookie = ngx.req.get_headers()['Cookie']
if ngx.req.get_headers()['Cookie'] then
    local cToken = decodeCookie(cookie).CsrfToken
    if cToken and string.len(cToken) == 20 then
        cToken1 = string.sub(cToken,0,10)
        cToken2 = string.sub(cToken,11,20)
        if cToken2 == red:hget(cToken1,'dynamicCode') then
            flag = 0
        else
            flag = -1
        end
    else
        flag = -2
    end
else
     flag = -2
end
local newDynamicCode = math.random(1000000000,9999999999)
if flag ~= 0 then
    local newStaticCode = math.random(1000000000,9999999999)
    red:hset(newStaticCode,'dynamicCode',newDynamicCode)
    red:expire(newStaticCode, 5)
    red:close()
    ngx.header['Set-Cookie'] = {'CsrfToken='..newStaticCode..newDynamicCode,}
    ngx.header['Content-Type'] = 'application/json; charset=utf-8'
    if flag == -1 then
        ngx.say(json.encode({
            tokenStatus = flag,
            message = 'VerifyTokenError'
        }))
    elseif flag == -2 then
        ngx.say(json.encode({
            tokenStatus = flag,
            message = 'NoneTokenError'
        }))
    else
        ngx.say(json.encode({
            tokenStatus = flag,
            message = 'UnknownTokenError'
        }))
    end
else
    red:hset(cToken1,'dynamicCode',newDynamicCode)
    red:expire(cToken1, 300)
    red:close()
    ngx.header['Set-Cookie'] = {'CsrfToken='..cToken1..newDynamicCode,}
end

