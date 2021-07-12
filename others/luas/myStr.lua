function randomStr(len)
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