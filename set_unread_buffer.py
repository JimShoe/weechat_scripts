import weechat

# NOTE: This will probably be deprecated with task 13074 (https://savannah.nongnu.org/task/?13074)

def set_unread(data, buffer, args):
  args = args.strip()
  if args == "":
      weechat.prnt("", "ERROR: NO ARGS")
      return weechat.WEECHAT_RC_OK
  buffer = weechat.buffer_search("",args)
  if not buffer:
      weechat.prnt("", "ERROR: couldn't find buffer: "+args)
  weechat.command(buffer, "/input set_unread_current_buffer")
  return weechat.WEECHAT_RC_OK

weechat.register("set_unread_buffer", "JimShoe", "1.0", "GPL3", "Sets unread marker on buffer.", "", "")
weechat.hook_command("set_unread", "Set unread marker on buffer", "", "", "", "set_unread", "")
