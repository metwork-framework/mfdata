local upload = require("resty.upload")
local mfutil = require("mfutil")
local data_in_dir = os.getenv("MFDATA_DATA_IN_DIR")

local switch_directories = os.getenv("MFDATA_INTERNAL_PLUGINS_SWITCH_DIRECTORIES")
local default_directory = string.match(switch_directories, "([^;]+)")

local function exit_with_ngx_error(code, message)
    ngx.status = code
    ngx.say(string.format("HTTP/%i ERROR: %s", code, message))
    ngx.exit(200) -- yes, it's normal
end

local function make_unique_id()
    return mfutil.get_unique_hexa_identifier()
end

local function get_target_filepath(directory, filename)
    if filename == nil then
        return string.format("%s/%s/%s", data_in_dir, directory, make_unique_id())
    else
        return string.format("%s/%s/%s", data_in_dir, directory, filename)
    end
end

local function process()

    -- Variables
    local request = ngx.req
    local chunk_size = 4096
    local targetpath = nil
    local method = request.get_method()
    local uri = ngx.var.uri
    local regex = nil
    local directory = default_directory
    local filename = nil

    -- Tests
    if method == "POST" then
        regex = "^/([a-zA-Z0-9,;:_%-%.]*)/*$"
        directory = string.match(uri, regex)
        if directory == nil then
            exit_with_ngx_error(400, string.format("POST request uri must match with %s lua pattern", regex))
        elseif directory == "" then
            directory = default_directory
        end
    elseif method == "PUT" then
        regex = "^/([a-zA-Z0-9,;:_%-%.]+)/*$"
        filename = string.match(uri, regex)
        if filename == nil then
            regex = "^/([a-zA-Z0-9,;:_%-%.]+)/([a-zA-Z0-9,;:_%-%.]+)/*$"
            directory, filename = string.match(uri, regex)
            if directory == nil or filename == nil then
                exit_with_ngx_error(400, string.format("PUT request uri must match with %s lua pattern", regex))
            end
        end
    else
        exit_with_ngx_error(405, string.format("only PUT and POST methods are allowed"))
    end
    targetpath = get_target_filepath(directory, filename)

    -- Deal with the request body
    request.read_body()
    local body = request.get_body_data()
    if body == nil then
        local filepath = request.get_body_file()
        if filepath == nil then
            -- The original file is empty (no body data) ==> We create an empty file
            local tmptargetpath = string.format("%s.t", targetpath)
            local file = io.open(tmptargetpath, "w")
            file:close()
            local renameres = os.rename(tmptargetpath, targetpath)
            if renameres ~= true then
                exit_with_ngx_error(500, string.format("can't rename %s to %s", tmptargetpath, targetpath))
            end
        else
            local linkres = mfutil.link(filepath, targetpath)
            if linkres ~= 0 then
                exit_with_ngx_error(500, string.format("can't make a hard link %s => %s different filesystem ?", targetpath, filepath))
            end
        end
    else
        local tmptargetpath = string.format("%s.t", targetpath)
        local file = io.open(tmptargetpath, "w")
        file:write(body)
        file:close()
        local renameres = os.rename(tmptargetpath, targetpath)
        if renameres ~= true then
            exit_with_ngx_error(500, string.format("can't rename %s to %s", tmptargetpath, targetpath))
        end
    end

    -- Output
    ngx.status = 201
    ngx.say("Created")

end

return process
