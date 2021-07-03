
local function randomStr(len)
    local rankStr = ""
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




redis = require "resty.redis";
red = redis:new();
red:set_timeout(redis_connection_timeout);
ok, err = red:connect("127.0.0.1", 6379);

if not ok then
  ngx.say("failed to connect: ", err)
  return
end
sustainTime = 1800
local headers = ngx.req.get_headers()
if headers['csrfToken'] and string.len(headers['csrfToken']) == 30 then
  newdynamicCode = randomStr(15)
  staticCode = string.sub(headers['csrfToken'],0,15)
  dynamicCode = string.sub(headers['csrfToken'],16,30)
  oldDynamicCode = red:hget(staticCode,'dynamicCode')
  red:hset(staticCode,'dynamicCode',newdynamicCode)
  red:expire(staticCode, sustainTime)
  ngx.header.csrfTtoken=staticCode..newdynamicCode
  if oldDynamicCode == dynamicCode then
    return
  else
    json = require"cjson"
    data = json.encode({
        code = 5,
        message = "DynamicVerifyError"
    })
    ngx.say(data)
    return
  end

else
  staticCode = randomStr(15)
  dynamicCode = randomStr(15)
  red:hset(staticCode,'dynamicCode',dynamicCode)
  red:expire(staticCode, sustainTime)
  ngx.header.csrfTtoken=staticCode..dynamicCode
  json = require"cjson"
  data = json.encode({
      code = 5,
      message = "dynamicVerifyError"
  })
    ngx.say(data)
end
