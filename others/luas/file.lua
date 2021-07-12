local function writeFile(fileName,content)
    local f = assert(io.open(fileName,'a+'))
    f:write(content)
    f:close()
end