local function randomStr(len)
    local rankStr = ''
    local randNum = 0
    math.randomseed(tostring(ngx.time()):reverse():sub(1, 5)) 
    for i=1,len do
      if math.random(1,3)==1 then
        randNum=string.char(math.random(0,25)+65)  
      elseif math.random(1,3)==2 then
        randNum=string.char(math.random(0,25)+97) 
      else
        randNum=math.random(0,9)
      end
      rankStr=rankStr..randNum
    end
    return rankStr
end
function get_cookie(s_cookie)
    local cookie = {}
    for item in string.gmatch(s_cookie, "[^;]+") do
        local _, _, k, v = string.find(item, "^%s*(%S+)%s*=%s*(%S+)%s*")

        if k ~= nil and v~= nil then
            cookie[k] = v
        end
    end

    return cookie
end
json = require'cjson'
redis = require 'resty.redis';
red = redis:new();
red:set_timeout(redis_connection_timeout);
ok, err = red:connect('127.0.0.1', 6379);
if not ok then
    data = json.encode({
        code = -1,
        message = 'redisError'
    })
    ngx.say(data)
  return
end

local function writeFile(fileName,content)
    local f = assert(io.open(fileName,'a+'))
    f:write(content)
    f:close()
end
tempTime = 15
sustainTime = 300
local cookie = ngx.req.get_headers()['Cookie']
newDynamicCode = randomStr(15)
if ngx.req.get_headers()['Cookie'] then
    local cToken = get_cookie(cookie).CsrfToken
    if cToken and string.len(cToken) == 30 then
        cToken1 = string.sub(cToken,0,15)
        cToken2 = string.sub(cToken,16,30)
        if cToken2 == red:hget(cToken1,'dynamicCode') then
            flag = 1
        else
            flag = 0
        end
    else
        flag = -1
    end
else
     flag = -1
end
if flag == -1 then
    local newStaticCode = randomStr(15)
    red:hset(newStaticCode,'dynamicCode',newDynamicCode)
    red:expire(newStaticCode, tempTime)
    ngx.header['Set-Cookie'] = {'CsrfToken='..newStaticCode..newDynamicCode,}
    data = json.encode({
        code = 5,
        message = 'TokenBasicError'
    })
    ngx.say(data)
else
    red:hset(cToken1,'dynamicCode',newDynamicCode)
    red:expire(cToken1, sustainTime)
    ngx.header['Set-Cookie'] = {'CsrfToken='..cToken1..newDynamicCode,}
end