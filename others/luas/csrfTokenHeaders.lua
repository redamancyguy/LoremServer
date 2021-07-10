
local function randomStr(len)
    local rankStr = ''
    local randNum = 0
    --math.randomseed(ngx.time())  --seed的两个时间种子相差不大，生成的随机数会很可能相同（100,102 但是random 生成的第一个随机数却是一样的）
    math.randomseed(tostring(ngx.time()):reverse():sub(1, 5)) --解决方法:把time返回的数值字串倒过来（低位变高位）,再取高位5位
    for i=1,len do
      if math.random(1,3)==1 then
        randNum=string.char(math.random(0,25)+65)   --生成大写字母 random(0,25)生成0=< <=25的整数
      elseif math.random(1,3)==2 then
        randNum=string.char(math.random(0,25)+97)   --生成小写字母
      else
        randNum=math.random(0,9)                   --生成0=< and <=9的随机数字
      end
      rankStr=rankStr..randNum
    end
    return rankStr
end

redis = require 'resty.redis';
red = redis:new();
red:set_timeout(redis_connection_timeout);
ok, err = red:connect('127.0.0.1', 6379);
if not ok then
    json = require'cjson'
    data = json.encode({
        code = -1,
        message = 'redisError'
    })
    ngx.say(data)
  return
end

tempTime = 30
sustainTime = 300
local headers = ngx.req.get_headers()
if headers.CsrfToken and string.len(headers.CsrfToken) == 30 then
  newDynamicCode = randomStr(15)
  clientStaticCode = string.sub(headers.CsrfToken,0,15)
  clientDynamicCode = string.sub(headers.CsrfToken,16,30)
  serverDynamicCode = red:hget(clientStaticCode,'dynamicCode')
  red:hset(clientStaticCode,'dynamicCode',newDynamicCode)
  red:expire(clientStaticCode, sustainTime)
  ngx.header.CsrfToken=clientStaticCode..newDynamicCode
  if serverDynamicCode == clientDynamicCode then
    return
  else
    json = require'cjson'
    data = json.encode({
        code = 5,
        message = 'DynamicVerifyError'
    })
--     ngx.status = 500
    ngx.testCode = 'dsadsa'
    ngx.say(data)
  end
else
  newStaticCode = randomStr(15)
  newDynamicCode = randomStr(15)
  red:hset(newStaticCode,'dynamicCode',newDynamicCode)
  red:expire(newStaticCode, tempTime)
  ngx.header.CsrfToken=newStaticCode..newDynamicCode
  json = require'cjson'
  data = json.encode({
      code = 5,
      message = 'TokenBasicError'
  })
--   ngx.status = 500
    ngx.say(data)
end
